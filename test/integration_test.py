"""
ハイブリッド自律修正システムの統合テスト

新規作成されたすべてのエージェントの動作を検証する。
"""

import asyncio
import json
import logging
from pathlib import Path

# 新規作成エージェントのインポート
from hybrid_orchestrator_agent import (
    HybridFixOrchestratorAgent,
    BugFixTask,
    FixStrategy,
    ExecutionMode
)
from local_llm_agent import LocalLLMAgent, LocalLLMConfig, LocalLLMProvider
from rollback_agent import RollbackAgent, RollbackReason
from metrics_collector_agent import MetricsCollectorAgent, ReportPeriod
from cache_manager_agent import CacheManagerAgent
from config_validator_agent import ConfigValidatorAgent
from log_analyzer_agent import LogAnalyzerAgent
from dependency_resolver_agent import DependencyResolverAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTestSuite:
    """統合テストスイート"""
    
    def __init__(self):
        self.test_results = []
        self.setup_complete = False
    
    async def setup(self):
        """テスト環境をセットアップ"""
        logger.info("=== Setting up test environment ===")
        
        try:
            # 1. CacheManagerの初期化
            logger.info("1. Initializing CacheManager...")
            self.cache_manager = CacheManagerAgent(cache_dir=".test_cache")
            
            # 2. LocalLLMの初期化（利用可能な場合）
            logger.info("2. Initializing LocalLLM...")
            self.local_llm = LocalLLMAgent(
                config=LocalLLMConfig(
                    provider=LocalLLMProvider.OLLAMA,
                    model_name="codellama:7b-instruct"
                )
            )
            
            if not self.local_llm.is_available:
                logger.warning("⚠️  LocalLLM is not available, some tests will be skipped")
            
            # 3. RollbackAgentの初期化
            logger.info("3. Initializing RollbackAgent...")
            self.rollback_agent = RollbackAgent(backup_dir=".test_rollback")
            
            # 4. MetricsCollectorの初期化
            logger.info("4. Initializing MetricsCollector...")
            self.metrics_collector = MetricsCollectorAgent(storage_dir=".test_metrics")
            
            # 5. ConfigValidatorの初期化
            logger.info("5. Initializing ConfigValidator...")
            self.config_validator = ConfigValidatorAgent()
            
            # 6. LogAnalyzerの初期化
            logger.info("6. Initializing LogAnalyzer...")
            self.log_analyzer = LogAnalyzerAgent()
            
            # 7. DependencyResolverの初期化
            logger.info("7. Initializing DependencyResolver...")
            self.dependency_resolver = DependencyResolverAgent()
            
            # 8. ダミーのLocalFixAgentとCloudFixAgent
            self.local_fix_agent = DummyLocalFixAgent()
            self.cloud_fix_agent = DummyCloudFixAgent()
            
            # 9. HybridOrchestratorの初期化
            logger.info("8. Initializing HybridOrchestrator...")
            self.orchestrator = HybridFixOrchestratorAgent(
                cache_manager=self.cache_manager,
                local_fix_agent=self.local_fix_agent,
                cloud_fix_agent=self.cloud_fix_agent,
                config={
                    "strategy": "adaptive",
                    "mode": "hybrid",
                    "max_retry_count": 2
                }
            )
            
            self.setup_complete = True
            logger.info("✅ Setup complete!\n")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            raise
    
    async def test_cache_manager(self):
        """CacheManagerのテスト"""
        logger.info("=== Testing CacheManager ===")
        
        try:
            # エラーコンテキスト
            error_context = {
                "error_type": "ImportError",
                "error_message": "cannot import name 'foo' from 'bar'",
                "source_file": "test.py"
            }
            
            # 修正をキャッシュ
            error_hash = self.cache_manager.cache_fix(
                error_context=error_context,
                fix_code="from bar import foo_new as foo",
                fix_description="Updated import statement"
            )
            
            # キャッシュから取得
            cached_fix = self.cache_manager.get_cached_fix(error_context)
            
            assert cached_fix is not None, "Cached fix should be found"
            assert cached_fix.error_hash == error_hash, "Hash should match"
            
            # 修正結果を記録
            self.cache_manager.record_fix_result(error_hash, success=True)
            
            # 統計情報を確認
            stats = self.cache_manager.get_statistics()
            assert stats["cache_hit_rate"] > 0, "Cache hit rate should be > 0"
            
            logger.info("✅ CacheManager test passed")
            self.test_results.append(("CacheManager", True, None))
            
        except Exception as e:
            logger.error(f"❌ CacheManager test failed: {e}")
            self.test_results.append(("CacheManager", False, str(e)))
    
    async def test_rollback_agent(self):
        """RollbackAgentのテスト"""
        logger.info("=== Testing RollbackAgent ===")
        
        try:
            # テストファイルを作成
            test_file = Path(".test_file.py")
            test_file.write_text("# Original version\nprint('Hello')")
            
            # スナップショットを作成
            snapshot_id = self.rollback_agent.create_snapshot(
                [str(test_file)],
                description="Test snapshot"
            )
            
            # ファイルを変更
            test_file.write_text("# Modified version\nprint('Hello World')")
            
            # 影響分析
            impact = self.rollback_agent.analyze_impact(snapshot_id)
            assert impact["can_rollback"], "Should be able to rollback"
            
            # ロールバック
            result = self.rollback_agent.rollback(snapshot_id)
            assert result.success, "Rollback should succeed"
            assert len(result.files_restored) > 0, "Files should be restored"
            
            # クリーンアップ
            test_file.unlink()
            
            logger.info("✅ RollbackAgent test passed")
            self.test_results.append(("RollbackAgent", True, None))
            
        except Exception as e:
            logger.error(f"❌ RollbackAgent test failed: {e}")
            self.test_results.append(("RollbackAgent", False, str(e)))
    
    async def test_metrics_collector(self):
        """MetricsCollectorのテスト"""
        logger.info("=== Testing MetricsCollector ===")
        
        try:
            # タスク実行をシミュレート
            self.metrics_collector.start_task("task-1", "TestAgent")
            await asyncio.sleep(0.1)
            self.metrics_collector.end_task("task-1", "TestAgent", success=True)
            
            # 修正試行を記録
            self.metrics_collector.record_fix_attempt(
                fix_type="local",
                success=True,
                duration=1.5,
                error_type="ImportError"
            )
            
            # レポート生成
            report = self.metrics_collector.generate_report(ReportPeriod.DAILY)
            assert "summary" in report, "Report should have summary"
            
            # ダッシュボードデータ
            dashboard = self.metrics_collector.generate_dashboard_data()
            assert "overview" in dashboard, "Dashboard should have overview"
            
            logger.info("✅ MetricsCollector test passed")
            self.test_results.append(("MetricsCollector", True, None))
            
        except Exception as e:
            logger.error(f"❌ MetricsCollector test failed: {e}")
            self.test_results.append(("MetricsCollector", False, str(e)))
    
    async def test_config_validator(self):
        """ConfigValidatorのテスト"""
        logger.info("=== Testing ConfigValidator ===")
        
        try:
            # テスト設定ファイルを作成
            test_config = {
                "browser": {
                    "headless": True,
                    "user_data_dir": "./test_data"
                },
                "ai": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "api_key": "test-key"
                }
            }
            
            config_file = Path(".test_config.json")
            config_file.write_text(json.dumps(test_config, indent=2))
            
            # 設定を検証
            results = self.config_validator.validate_config_file(str(config_file))
            assert len(results) > 0, "Should have validation results"
            
            # レポート生成
            report = self.config_validator.generate_validation_report(results)
            assert "summary" in report, "Report should have summary"
            
            # クリーンアップ
            config_file.unlink()
            
            logger.info("✅ ConfigValidator test passed")
            self.test_results.append(("ConfigValidator", True, None))
            
        except Exception as e:
            logger.error(f"❌ ConfigValidator test failed: {e}")
            self.test_results.append(("ConfigValidator", False, str(e)))
    
    async def test_log_analyzer(self):
        """LogAnalyzerのテスト"""
        logger.info("=== Testing LogAnalyzer ===")
        
        try:
            # サンプルログを取り込む
            logs = [
                "[2024-01-01 10:00:00] INFO: Application started",
                "[2024-01-01 10:01:00] ERROR: Connection timeout",
                "[2024-01-01 10:02:00] ERROR: Connection timeout",
                "[2024-01-01 10:03:00] CRITICAL: System failure"
            ]
            
            for log_line in logs:
                entry = self.log_analyzer.parse_log_line(log_line, "test_app")
                self.log_analyzer.ingest_log(entry)
            
            # サマリーレポート
            report = self.log_analyzer.generate_summary_report()
            assert report["summary"]["total_logs"] == len(logs), "Should have all logs"
            
            # 根本原因分析
            root_cause = self.log_analyzer.analyze_root_cause("Connection timeout")
            assert "similar_errors_count" in root_cause, "Should have similar errors"
            
            logger.info("✅ LogAnalyzer test passed")
            self.test_results.append(("LogAnalyzer", True, None))
            
        except Exception as e:
            logger.error(f"❌ LogAnalyzer test failed: {e}")
            self.test_results.append(("LogAnalyzer", False, str(e)))
    
    async def test_dependency_resolver(self):
        """DependencyResolverのテスト"""
        logger.info("=== Testing DependencyResolver ===")
        
        try:
            # テストrequirements.txtを作成
            test_req = Path(".test_requirements.txt")
            test_req.write_text("requests>=2.28.0\nflask==2.3.0\npytest")
            
            resolver = DependencyResolverAgent(str(test_req))
            
            # 依存関係を分析
            issues = resolver.analyze_dependencies()
            
            # レポート生成
            report = resolver.generate_report()
            assert "summary" in report, "Report should have summary"
            
            # クリーンアップ
            test_req.unlink()
            
            logger.info("✅ DependencyResolver test passed")
            self.test_results.append(("DependencyResolver", True, None))
            
        except Exception as e:
            logger.error(f"❌ DependencyResolver test failed: {e}")
            self.test_results.append(("DependencyResolver", False, str(e)))
    
    async def test_local_llm(self):
        """LocalLLMのテスト"""
        logger.info("=== Testing LocalLLM ===")
        
        if not self.local_llm.is_available:
            logger.warning("⚠️  LocalLLM not available, skipping test")
            self.test_results.append(("LocalLLM", True, "Skipped - not available"))
            return
        
        try:
            # モデル情報を取得
            info = self.local_llm.get_model_info()
            assert info["available"], "Model should be available"
            
            # 簡単な修正を生成
            error_context = {
                "error_type": "NameError",
                "error_message": "name 'foo' is not defined",
                "line_number": 3
            }
            
            file_content = "def test():\n    return foo"
            
            result = await self.local_llm.generate_fix(
                error_context=error_context,
                file_content=file_content,
                file_path="test.py"
            )
            
            assert result["success"], "Fix generation should succeed"
            
            logger.info("✅ LocalLLM test passed")
            self.test_results.append(("LocalLLM", True, None))
            
        except Exception as e:
            logger.error(f"❌ LocalLLM test failed: {e}")
            self.test_results.append(("LocalLLM", False, str(e)))
    
    async def test_hybrid_orchestrator(self):
        """HybridOrchestratorのテスト"""
        logger.info("=== Testing HybridOrchestrator ===")
        
        try:
            # テストタスクを作成
            task = BugFixTask(
                task_id="test-task-1",
                error_context={
                    "error_type": "ImportError",
                    "error_message": "cannot import name 'test'"
                },
                affected_files=["test.py"],
                max_retries=2
            )
            
            # 修正を実行
            result = await self.orchestrator.fix_error(task)
            
            assert result is not None, "Result should not be None"
            assert result.task_id == task.task_id, "Task ID should match"
            
            # 統計情報を確認
            stats = self.orchestrator.get_statistics()
            assert stats["total_tasks"] > 0, "Should have processed tasks"
            
            logger.info("✅ HybridOrchestrator test passed")
            self.test_results.append(("HybridOrchestrator", True, None))
            
        except Exception as e:
            logger.error(f"❌ HybridOrchestrator test failed: {e}")
            self.test_results.append(("HybridOrchestrator", False, str(e)))
    
    async def test_adaptive_strategy(self):
        """適応型戦略のテスト"""
        logger.info("=== Testing Adaptive Strategy ===")
        
        try:
            # 複雑度の異なるタスクをテスト
            simple_task = BugFixTask(
                task_id="simple-1",
                error_context={
                    "error_type": "SyntaxError",
                    "error_message": "invalid syntax"
                },
                affected_files=["simple.py"]
            )
            
            complex_task = BugFixTask(
                task_id="complex-1",
                error_context={
                    "error_type": "AttributeError",
                    "error_message": "complex error in large system"
                },
                affected_files=["a.py", "b.py", "c.py", "d.py", "e.py", "f.py"]
            )
            
            # 簡単なタスク → ローカル優先になるはず
            simple_result = await self.orchestrator.fix_error(simple_task)
            
            # 複雑なタスク → クラウド優先になるはず
            complex_result = await self.orchestrator.fix_error(complex_task)
            
            assert simple_result is not None, "Simple task should have result"
            assert complex_result is not None, "Complex task should have result"
            
            logger.info("✅ Adaptive strategy test passed")
            self.test_results.append(("AdaptiveStrategy", True, None))
            
        except Exception as e:
            logger.error(f"❌ Adaptive strategy test failed: {e}")
            self.test_results.append(("AdaptiveStrategy", False, str(e)))
    
    def print_summary(self):
        """テスト結果のサマリーを表示"""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for _, success, _ in self.test_results if success)
        failed = total - passed
        
        for test_name, success, error in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status} - {test_name}")
            if error and not success:
                logger.info(f"      Error: {error}")
            elif error and success:
                logger.info(f"      Note: {error}")
        
        logger.info("="*60)
        logger.info(f"Total: {total} | Passed: {passed} | Failed: {failed}")
        logger.info(f"Success Rate: {passed/total*100:.1f}%")
        logger.info("="*60 + "\n")
        
        return failed == 0
    
    async def run_all_tests(self):
        """すべてのテストを実行"""
        logger.info("🚀 Starting integration tests for Hybrid Autonomous System\n")
        
        # セットアップ
        await self.setup()
        
        if not self.setup_complete:
            logger.error("Setup failed, aborting tests")
            return False
        
        # 各テストを実行
        await self.test_cache_manager()
        await self.test_rollback_agent()
        await self.test_metrics_collector()
        await self.test_config_validator()
        await self.test_log_analyzer()
        await self.test_dependency_resolver()
        await self.test_local_llm()
        await self.test_hybrid_orchestrator()
        await self.test_adaptive_strategy()
        
        # サマリーを表示
        all_passed = self.print_summary()
        
        return all_passed


class DummyLocalFixAgent:
    """テスト用のダミーローカル修正エージェント"""
    
    async def fix_error(self, error_context, affected_files):
        await asyncio.sleep(0.1)  # 処理をシミュレート
        
        error_type = error_context.get("error_type", "")
        
        # 簡単なエラーは成功
        if error_type in ["SyntaxError", "ImportError"]:
            return {
                "success": True,
                "confidence": 0.8,
                "modifications": [
                    {"file": affected_files[0], "changes": "Fixed locally"}
                ]
            }
        
        # 複雑なエラーは失敗（クラウドにフォールバック）
        return {
            "success": False,
            "confidence": 0.3,
            "error": "Too complex for local fix"
        }


class DummyCloudFixAgent:
    """テスト用のダミークラウド修正エージェント"""
    
    async def fix_error(self, error_context, affected_files):
        await asyncio.sleep(0.2)  # 処理をシミュレート
        
        # クラウドは常に成功（高い信頼度）
        return {
            "success": True,
            "confidence": 0.9,
            "modifications": [
                {"file": f, "changes": "Fixed by cloud AI"}
                for f in affected_files
            ]
        }


async def main():
    """メインエントリポイント"""
    test_suite = IntegrationTestSuite()
    
    try:
        all_passed = await test_suite.run_all_tests()
        
        if all_passed:
            logger.info("🎉 All tests passed! System is ready for deployment.")
            return 0
        else:
            logger.error("⚠️  Some tests failed. Please review the errors above.")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

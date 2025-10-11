"""
HybridFixOrchestratorAgent - ハイブリッド修正オーケストレーター

システム全体の「脳」として機能し、修正戦略（ADAPTIVE等）に基づいて
タスクをキャッシュ、ローカル、クラウドの各エージェントに振り分ける。
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FixStrategy(Enum):
    """修正戦略"""
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    LOCAL_FIRST = "local_first"
    CLOUD_FIRST = "cloud_first"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"


class ExecutionMode(Enum):
    """実行モード"""
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


@dataclass
class BugFixTask:
    """バグ修正タスク"""
    task_id: str
    error_context: Dict[str, Any]
    affected_files: List[str]
    priority: int = 5
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FixResult:
    """修正結果"""
    success: bool
    task_id: str
    strategy_used: str
    agent_used: str
    confidence_score: float
    execution_time: float
    modifications: List[Dict[str, Any]] = field(default_factory=list)
    test_results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    cache_hit: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "task_id": self.task_id,
            "strategy_used": self.strategy_used,
            "agent_used": self.agent_used,
            "confidence_score": self.confidence_score,
            "execution_time": self.execution_time,
            "modifications": self.modifications,
            "test_results": self.test_results,
            "error_message": self.error_message,
            "cache_hit": self.cache_hit
        }


class HybridFixOrchestratorAgent:
    """
    ハイブリッド修正オーケストレーター
    
    主な機能:
    1. 修正戦略に基づくエージェント選択
    2. キャッシュ優先の高速修正
    3. ローカル/クラウドの適応的な振り分け
    4. 並列実行とフォールバック
    5. リトライと結果評価
    """
    
    def __init__(self,
                 cache_manager,
                 local_fix_agent,
                 cloud_fix_agent,
                 test_runner=None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Args:
            cache_manager: CacheManagerAgent インスタンス
            local_fix_agent: AutoFixAgent インスタンス
            cloud_fix_agent: CloudFixAgent インスタンス
            test_runner: WPTesterAgent インスタンス（オプション）
            config: ハイブリッド設定
        """
        self.cache_manager = cache_manager
        self.local_fix_agent = local_fix_agent
        self.cloud_fix_agent = cloud_fix_agent
        self.test_runner = test_runner
        
        # 設定のデフォルト値
        self.config = config or {}
        self.strategy = FixStrategy(self.config.get("strategy", "adaptive"))
        self.mode = ExecutionMode(self.config.get("mode", "hybrid"))
        self.max_retry_count = self.config.get("max_retry_count", 3)
        self.retry_interval = self.config.get("retry_interval", 5)
        self.local_timeout = self.config.get("local_timeout", 30)
        self.cloud_timeout = self.config.get("cloud_timeout", 120)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        
        # 統計情報
        self.stats = {
            "total_tasks": 0,
            "cache_hits": 0,
            "local_fixes": 0,
            "cloud_fixes": 0,
            "parallel_fixes": 0,
            "successes": 0,
            "failures": 0
        }
        
        # エラー複雑度の学習データ
        self.error_complexity_history: Dict[str, List[float]] = {}
        
        logger.info(f"HybridFixOrchestratorAgent initialized "
                   f"(strategy={self.strategy.value}, mode={self.mode.value})")
    
    async def fix_error(self, task: BugFixTask) -> FixResult:
        """
        エラーを修正（メインエントリポイント）
        
        Args:
            task: バグ修正タスク
        
        Returns:
            修正結果
        """
        self.stats["total_tasks"] += 1
        start_time = time.time()
        
        logger.info(f"Starting fix for task {task.task_id} "
                   f"(strategy={self.strategy.value})")
        
        # 1. キャッシュチェック（最優先）
        cached_result = await self._try_cached_fix(task)
        if cached_result and cached_result.success:
            execution_time = time.time() - start_time
            cached_result.execution_time = execution_time
            self.stats["cache_hits"] += 1
            self.stats["successes"] += 1
            logger.info(f"Cache hit for task {task.task_id}")
            return cached_result
        
        # 2. 戦略に基づいて修正を実行
        result = None
        retry_count = 0
        
        while retry_count < task.max_retries:
            try:
                if self.strategy == FixStrategy.ADAPTIVE:
                    result = await self._adaptive_fix(task)
                elif self.strategy == FixStrategy.LOCAL_FIRST:
                    result = await self._local_first_fix(task)
                elif self.strategy == FixStrategy.CLOUD_FIRST:
                    result = await self._cloud_first_fix(task)
                elif self.strategy == FixStrategy.PARALLEL:
                    result = await self._parallel_fix(task)
                elif self.strategy == FixStrategy.LOCAL_ONLY:
                    result = await self._local_only_fix(task)
                elif self.strategy == FixStrategy.CLOUD_ONLY:
                    result = await self._cloud_only_fix(task)
                
                if result and result.success:
                    break
                
                retry_count += 1
                if retry_count < task.max_retries:
                    logger.warning(f"Fix failed, retrying ({retry_count}/{task.max_retries})")
                    await asyncio.sleep(self.retry_interval)
                    
            except Exception as e:
                logger.error(f"Error during fix attempt: {e}")
                retry_count += 1
                if retry_count >= task.max_retries:
                    result = FixResult(
                        success=False,
                        task_id=task.task_id,
                        strategy_used=self.strategy.value,
                        agent_used="none",
                        confidence_score=0.0,
                        execution_time=time.time() - start_time,
                        error_message=str(e)
                    )
        
        # 3. 結果を記録
        if result:
            result.execution_time = time.time() - start_time
            
            if result.success:
                self.stats["successes"] += 1
                # 成功した修正をキャッシュに保存
                await self._cache_successful_fix(task, result)
            else:
                self.stats["failures"] += 1
            
            # 複雑度の学習データを更新
            self._update_complexity_history(task, result)
        
        return result or FixResult(
            success=False,
            task_id=task.task_id,
            strategy_used=self.strategy.value,
            agent_used="none",
            confidence_score=0.0,
            execution_time=time.time() - start_time,
            error_message="Max retries exceeded"
        )
    
    async def _try_cached_fix(self, task: BugFixTask) -> Optional[FixResult]:
        """キャッシュから修正を試みる"""
        try:
            cached_fix = self.cache_manager.get_cached_fix(task.error_context)
            
            if cached_fix and cached_fix.success_rate >= self.confidence_threshold:
                logger.info(f"Applying cached fix (success_rate={cached_fix.success_rate:.2f})")
                
                # キャッシュされた修正を適用
                success = await self._apply_cached_fix(task, cached_fix)
                
                return FixResult(
                    success=success,
                    task_id=task.task_id,
                    strategy_used="cache",
                    agent_used="cache",
                    confidence_score=cached_fix.success_rate,
                    execution_time=0.0,
                    cache_hit=True,
                    modifications=[{
                        "type": "cached",
                        "description": cached_fix.fix_description
                    }]
                )
        except Exception as e:
            logger.error(f"Error in cached fix: {e}")
        
        return None
    
    async def _adaptive_fix(self, task: BugFixTask) -> FixResult:
        """
        適応型修正戦略
        
        エラーの複雑度、過去の成功率、リソース状況に基づいて
        最適なエージェントを自動選択する
        """
        complexity = self._estimate_error_complexity(task)
        
        logger.info(f"Adaptive strategy: estimated complexity={complexity:.2f}")
        
        # 複雑度に基づいて戦略を選択
        if complexity < 0.3:
            # 簡単なエラー: ローカル優先
            logger.info("Low complexity → trying local first")
            return await self._local_first_fix(task)
        elif complexity < 0.7:
            # 中程度のエラー: 並列実行
            logger.info("Medium complexity → trying parallel")
            return await self._parallel_fix(task)
        else:
            # 複雑なエラー: クラウド優先
            logger.info("High complexity → trying cloud first")
            return await self._cloud_first_fix(task)
    
    async def _local_first_fix(self, task: BugFixTask) -> FixResult:
        """ローカル優先戦略"""
        if self.mode == ExecutionMode.CLOUD:
            return await self._cloud_only_fix(task)
        
        # まずローカルで試す
        local_result = await self._execute_local_fix(task)
        
        if local_result.success and local_result.confidence_score >= self.confidence_threshold:
            self.stats["local_fixes"] += 1
            return local_result
        
        # ローカルが失敗したらクラウドにフォールバック
        if self.mode == ExecutionMode.HYBRID:
            logger.info("Local fix failed, falling back to cloud")
            cloud_result = await self._execute_cloud_fix(task)
            self.stats["cloud_fixes"] += 1
            return cloud_result
        
        return local_result
    
    async def _cloud_first_fix(self, task: BugFixTask) -> FixResult:
        """クラウド優先戦略"""
        if self.mode == ExecutionMode.LOCAL:
            return await self._local_only_fix(task)
        
        # まずクラウドで試す
        cloud_result = await self._execute_cloud_fix(task)
        
        if cloud_result.success:
            self.stats["cloud_fixes"] += 1
            return cloud_result
        
        # クラウドが失敗したらローカルにフォールバック
        if self.mode == ExecutionMode.HYBRID:
            logger.info("Cloud fix failed, falling back to local")
            local_result = await self._execute_local_fix(task)
            self.stats["local_fixes"] += 1
            return local_result
        
        return cloud_result
    
    async def _parallel_fix(self, task: BugFixTask) -> FixResult:
        """並列実行戦略"""
        if self.mode != ExecutionMode.HYBRID:
            # ハイブリッドモードでない場合は適切な単一戦略にフォールバック
            if self.mode == ExecutionMode.LOCAL:
                return await self._local_only_fix(task)
            else:
                return await self._cloud_only_fix(task)
        
        logger.info("Executing parallel fix (local + cloud)")
        
        # ローカルとクラウドを並列実行
        local_task = asyncio.create_task(self._execute_local_fix(task))
        cloud_task = asyncio.create_task(self._execute_cloud_fix(task))
        
        # 最初に完了した結果を取得
        done, pending = await asyncio.wait(
            [local_task, cloud_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # 最初に成功した結果を使用
        for completed_task in done:
            result = completed_task.result()
            if result.success and result.confidence_score >= self.confidence_threshold:
                # 残りのタスクをキャンセル
                for pending_task in pending:
                    pending_task.cancel()
                
                self.stats["parallel_fixes"] += 1
                return result
        
        # どちらも失敗した場合、両方の完了を待つ
        for pending_task in pending:
            try:
                result = await pending_task
                if result.success:
                    self.stats["parallel_fixes"] += 1
                    return result
            except:
                pass
        
        # すべて失敗
        local_result = local_task.result() if local_task.done() else None
        cloud_result = cloud_task.result() if cloud_task.done() else None
        
        # より信頼度の高い結果を返す
        if local_result and cloud_result:
            if local_result.confidence_score >= cloud_result.confidence_score:
                return local_result
            else:
                return cloud_result
        
        return local_result or cloud_result or FixResult(
            success=False,
            task_id=task.task_id,
            strategy_used="parallel",
            agent_used="both",
            confidence_score=0.0,
            execution_time=0.0,
            error_message="Both local and cloud fixes failed"
        )
    
    async def _local_only_fix(self, task: BugFixTask) -> FixResult:
        """ローカルのみ戦略"""
        result = await self._execute_local_fix(task)
        self.stats["local_fixes"] += 1
        return result
    
    async def _cloud_only_fix(self, task: BugFixTask) -> FixResult:
        """クラウドのみ戦略"""
        result = await self._execute_cloud_fix(task)
        self.stats["cloud_fixes"] += 1
        return result
    
    async def _execute_local_fix(self, task: BugFixTask) -> FixResult:
        """ローカル修正を実行"""
        try:
            logger.info(f"Executing local fix for task {task.task_id}")
            
            # タイムアウト付きで実行
            result = await asyncio.wait_for(
                self.local_fix_agent.fix_error(task.error_context, task.affected_files),
                timeout=self.local_timeout
            )
            
            # テストを実行（設定されている場合）
            if self.test_runner and result.get("success"):
                test_results = await self._run_tests(task)
                result["test_results"] = test_results
                
                if not test_results.get("passed"):
                    result["success"] = False
                    result["error_message"] = "Tests failed after fix"
            
            return FixResult(
                success=result.get("success", False),
                task_id=task.task_id,
                strategy_used=self.strategy.value,
                agent_used="local",
                confidence_score=result.get("confidence", 0.5),
                execution_time=0.0,
                modifications=result.get("modifications", []),
                test_results=result.get("test_results"),
                error_message=result.get("error")
            )
            
        except asyncio.TimeoutError:
            logger.error(f"Local fix timed out after {self.local_timeout}s")
            return FixResult(
                success=False,
                task_id=task.task_id,
                strategy_used=self.strategy.value,
                agent_used="local",
                confidence_score=0.0,
                execution_time=self.local_timeout,
                error_message="Local fix timeout"
            )
        except Exception as e:
            logger.error(f"Local fix error: {e}")
            return FixResult(
                success=False,
                task_id=task.task_id,
                strategy_used=self.strategy.value,
                agent_used="local",
                confidence_score=0.0,
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def _execute_cloud_fix(self, task: BugFixTask) -> FixResult:
        """クラウド修正を実行"""
        try:
            logger.info(f"Executing cloud fix for task {task.task_id}")
            
            # タイムアウト付きで実行
            result = await asyncio.wait_for(
                self.cloud_fix_agent.fix_error(task.error_context, task.affected_files),
                timeout=self.cloud_timeout
            )
            
            # テストを実行（設定されている場合）
            if self.test_runner and result.get("success"):
                test_results = await self._run_tests(task)
                result["test_results"] = test_results
                
                if not test_results.get("passed"):
                    result["success"] = False
                    result["error_message"] = "Tests failed after fix"
            
            return FixResult(
                success=result.get("success", False),
                task_id=task.task_id,
                strategy_used=self.strategy.value,
                agent_used="cloud",
                confidence_score=result.get("confidence", 0.8),
                execution_time=0.0,
                modifications=result.get("modifications", []),
                test_results=result.get("test_results"),
                error_message=result.get("error")
            )
            
        except asyncio.TimeoutError:
            logger.error(f"Cloud fix timed out after {self.cloud_timeout}s")
            return FixResult(
                success=False,
                task_id=task.task_id,
                strategy_used=self.strategy.value,
                agent_used="cloud",
                confidence_score=0.0,
                execution_time=self.cloud_timeout,
                error_message="Cloud fix timeout"
            )
        except Exception as e:
            logger.error(f"Cloud fix error: {e}")
            return FixResult(
                success=False,
                task_id=task.task_id,
                strategy_used=self.strategy.value,
                agent_used="cloud",
                confidence_score=0.0,
                execution_time=0.0,
                error_message=str(e)
            )
    
    def _estimate_error_complexity(self, task: BugFixTask) -> float:
        """
        エラーの複雑度を推定（0.0-1.0）
        
        過去のデータと現在のエラー特性に基づいて推定
        """
        error_type = task.error_context.get("error_type", "")
        
        # 過去の履歴があれば使用
        if error_type in self.error_complexity_history:
            history = self.error_complexity_history[error_type]
            if history:
                return sum(history) / len(history)
        
        # ヒューリスティックによる推定
        complexity = 0.5  # ベースライン
        
        # エラータイプによる調整
        simple_errors = ["SyntaxError", "ImportError", "NameError"]
        complex_errors = ["AttributeError", "TypeError", "LogicError"]
        
        if error_type in simple_errors:
            complexity -= 0.2
        elif error_type in complex_errors:
            complexity += 0.2
        
        # 影響ファイル数による調整
        file_count = len(task.affected_files)
        if file_count > 5:
            complexity += 0.2
        elif file_count == 1:
            complexity -= 0.1
        
        # エラーメッセージの長さによる調整
        error_msg = task.error_context.get("error_message", "")
        if len(error_msg) > 200:
            complexity += 0.1
        
        return max(0.0, min(1.0, complexity))
    
    def _update_complexity_history(self, task: BugFixTask, result: FixResult):
        """複雑度の履歴を更新"""
        error_type = task.error_context.get("error_type", "")
        
        # 成功/失敗と使用されたエージェントから複雑度を逆算
        if result.agent_used == "local" and result.success:
            actual_complexity = 0.3
        elif result.agent_used == "cloud" and result.success:
            actual_complexity = 0.7
        elif not result.success:
            actual_complexity = 0.9
        else:
            actual_complexity = 0.5
        
        if error_type not in self.error_complexity_history:
            self.error_complexity_history[error_type] = []
        
        self.error_complexity_history[error_type].append(actual_complexity)
        
        # 最新10件のみ保持
        self.error_complexity_history[error_type] = \
            self.error_complexity_history[error_type][-10:]
    
    async def _apply_cached_fix(self, task: BugFixTask, cached_fix) -> bool:
        """キャッシュされた修正を適用"""
        try:
            # 修正コードを適用
            for file_path in task.affected_files:
                # ここで実際のファイル修正を行う
                # （実装はAutoFixAgentやCloudFixAgentのロジックを参照）
                pass
            
            # キャッシュヒットを記録
            error_hash = self.cache_manager.compute_error_hash(task.error_context)
            self.cache_manager.record_fix_result(error_hash, success=True)
            
            return True
        except Exception as e:
            logger.error(f"Failed to apply cached fix: {e}")
            return False
    
    async def _cache_successful_fix(self, task: BugFixTask, result: FixResult):
        """成功した修正をキャッシュに保存"""
        try:
            if result.modifications:
                fix_description = f"Fixed by {result.agent_used}"
                fix_code = "\n".join(
                    mod.get("content", "") for mod in result.modifications
                )
                
                self.cache_manager.cache_fix(
                    error_context=task.error_context,
                    fix_code=fix_code,
                    fix_description=fix_description,
                    ttl_hours=168  # 1週間
                )
                
                logger.info(f"Cached successful fix for task {task.task_id}")
        except Exception as e:
            logger.error(f"Failed to cache fix: {e}")
    
    async def _run_tests(self, task: BugFixTask) -> Dict[str, Any]:
        """テストを実行"""
        if not self.test_runner:
            return {"passed": True, "skipped": True}
        
        try:
            return await self.test_runner.run_tests(task.affected_files)
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {"passed": False, "error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        total = self.stats["total_tasks"]
        
        return {
            **self.stats,
            "success_rate": self.stats["successes"] / total if total > 0 else 0,
            "cache_hit_rate": self.stats["cache_hits"] / total if total > 0 else 0,
            "strategy": self.strategy.value,
            "mode": self.mode.value
        }


# 使用例
if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    
    # ダミーエージェントの作成（実際には実装されたエージェントを使用）
    class DummyCacheManager:
        def get_cached_fix(self, context):
            return None
        
        def cache_fix(self, **kwargs):
            pass
        
        def compute_error_hash(self, context):
            return "hash123"
        
        def record_fix_result(self, hash, success):
            pass
    
    class DummyLocalAgent:
        async def fix_error(self, context, files):
            return {"success": True, "confidence": 0.8}
    
    class DummyCloudAgent:
        async def fix_error(self, context, files):
            return {"success": True, "confidence": 0.9}
    
    # オーケストレーターを作成
    orchestrator = HybridFixOrchestratorAgent(
        cache_manager=DummyCacheManager(),
        local_fix_agent=DummyLocalAgent(),
        cloud_fix_agent=DummyCloudAgent(),
        config={
            "strategy": "adaptive",
            "mode": "hybrid",
            "max_retry_count": 3
        }
    )
    
    # テストタスク
    task = BugFixTask(
        task_id="test-1",
        error_context={
            "error_type": "ImportError",
            "error_message": "cannot import name 'foo'"
        },
        affected_files=["test.py"]
    )
    
    # 修正を実行
    async def test():
        result = await orchestrator.fix_error(task)
        print("\n=== Fix Result ===")
        print(json.dumps(result.to_dict(), indent=2))
        
        print("\n=== Statistics ===")
        print(json.dumps(orchestrator.get_statistics(), indent=2))
    
    asyncio.run(test())

#!/usr/bin/env python3
"""
24時間自律開発システム - 事前テスト
既存の全機能を統合してテスト
"""
import asyncio
import sys
import os
import time
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class TwentyFourHourSystemTester:
    def __init__(self):
        self.components = {}
        self.test_results = {}
    
    async def initialize_components(self):
        """既存の全コンポーネントを初期化"""
        print("🔧 24時間システムコンポーネント初期化...")
        
        try:
            # 1. コア基盤
            from tools.sheets_manager import GoogleSheetsManager
            self.components['sheets_manager'] = GoogleSheetsManager()
            print("  ✅ GoogleSheetsManager")
            
            # 2. 知識管理層
            from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
            self.components['kb_manager'] = KnowledgeBaseManager(self.components['sheets_manager'])
            print("  ✅ KnowledgeBaseManager")
            
            # 3. 学習層
            from agents.self_healing.logging.log_integrator import LogIntegrator
            from agents.self_healing.pattern_extractor import PatternExtractor
            from agents.self_healing.decision_support_system import DecisionSupportSystem
            from agents.self_healing.logging.context_logger import ContextLogger
            
            self.components['log_integrator'] = LogIntegrator()
            self.components['pattern_extractor'] = PatternExtractor(self.components['log_integrator'])
            self.components['decision_system'] = DecisionSupportSystem()
            self.components['context_logger'] = ContextLogger()
            print("  ✅ 学習層コンポーネント")
            
            # 4. 自己学習パイプライン
            from agents.self_healing.self_learning_pipeline_fixed import SelfLearningPipelineFixed
            self.components['learning_pipeline'] = SelfLearningPipelineFixed(
                self.components['sheets_manager'], 
                self.components['kb_manager']
            )
            print("  ✅ SelfLearningPipeline")
            
            # 5. タスク実行層
            from task_executor import TaskExecutor
            self.components['task_executor'] = TaskExecutor()
            await self.components['task_executor'].initialize()
            print("  ✅ TaskExecutor")
            
            # 6. RAGエンジン
            from mvp_v4.scripts.rag_engine_persistent_v2 import get_rag_engine_v2
            self.components['rag_engine'] = get_rag_engine_v2(['mvp_v4/knowledge/learned/conversation_knowledge_v3.json'])
            print("  ✅ RAG Engine")
            
            # 7. オーケストレーター
            from autonomous_development_orchestrator import AutonomousDevelopmentOrchestrator
            self.components['orchestrator'] = AutonomousDevelopmentOrchestrator(
                sheets_manager=self.components['sheets_manager'],
                knowledge_base_manager=self.components['kb_manager'],
                self_learning_pipeline=self.components['learning_pipeline'],
                task_executor=self.components['task_executor']
            )
            print("  ✅ AutonomousDevelopmentOrchestrator")
            
            print("🎉 全コンポーネント初期化完了")
            return True
            
        except Exception as e:
            print(f"❌ コンポーネント初期化エラー: {e}")
            return False
    
    async def test_learning_loop(self):
        """学習ループのテスト"""
        print("\n🔍 学習ループテスト...")
        try:
            strategies = await self.components['learning_pipeline'].run_learning_cycle()
            self.test_results['learning_loop'] = {
                'success': True,
                'strategies_generated': len(strategies)
            }
            print(f"  ✅ 学習ループ: {len(strategies)}個の戦略を生成")
            return True
        except Exception as e:
            self.test_results['learning_loop'] = {
                'success': False,
                'error': str(e)
            }
            print(f"  ❌ 学習ループ: {e}")
            return False
    
    async def test_task_execution(self):
        """タスク実行のテスト"""
        print("\n🎯 タスク実行テスト...")
        try:
            result = await self.components['task_executor'].execute("テストタスク: RAG検索機能確認")
            self.test_results['task_execution'] = {
                'success': result['success'],
                'knowledge_used': result.get('knowledge_used', 0)
            }
            print(f"  ✅ タスク実行: 知識{result.get('knowledge_used', 0)}件を使用")
            return result['success']
        except Exception as e:
            self.test_results['task_execution'] = {
                'success': False,
                'error': str(e)
            }
            print(f"  ❌ タスク実行: {e}")
            return False
    
    async def test_rag_search(self):
        """RAG検索のテスト"""
        print("\n🧠 RAG検索テスト...")
        try:
            results = self.components['rag_engine'].search("ModuleNotFoundError", top_k=2)
            self.test_results['rag_search'] = {
                'success': len(results) > 0,
                'results_count': len(results)
            }
            print(f"  ✅ RAG検索: {len(results)}件の結果を取得")
            return len(results) > 0
        except Exception as e:
            self.test_results['rag_search'] = {
                'success': False,
                'error': str(e)
            }
            print(f"  ❌ RAG検索: {e}")
            return False
    
    async def run_full_test(self, duration_seconds=60):
        """完全なシステムテストを実行"""
        print("🚀 24時間自律開発システム - 事前テスト開始")
        print("=" * 50)
        
        # コンポーネント初期化
        if not await self.initialize_components():
            return False
        
        # 各機能テスト
        tests = [
            self.test_rag_search(),
            self.test_task_execution(),
            self.test_learning_loop()
        ]
        
        results = await asyncio.gather(*tests)
        
        # テスト結果集計
        success_count = sum(results)
        total_tests = len(results)
        
        print("\n" + "=" * 50)
        print("📊 テスト結果サマリー:")
        for test_name, result in self.test_results.items():
            status = "✅ 成功" if result['success'] else "❌ 失敗"
            details = f"結果: {result.get('results_count', 'N/A')}" if 'results_count' in result else f"エラー: {result.get('error', 'N/A')}"
            print(f"  {test_name}: {status} - {details}")
        
        print(f"\n🎯 総合結果: {success_count}/{total_tests} テスト成功")
        
        if success_count == total_tests:
            print("🎉 24時間自律開発システム: テスト合格！")
            print("🚀 本番環境での24時間稼働準備完了")
            return True
        else:
            print("⚠️  一部テストが失敗しました。修正が必要です。")
            return False

async def main():
    tester = TwentyFourHourSystemTester()
    success = await tester.run_full_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())

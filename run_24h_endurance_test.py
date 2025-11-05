#!/usr/bin/env python3
"""
24時間耐久テスト - 実際の自律開発システムを実行
"""
import asyncio
import sys
import os
import time
import signal
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class EnduranceTest:
    def __init__(self):
        self.running = True
        self.cycle_count = 0
        self.successful_cycles = 0
        self.components = {}
        
        # シグナルハンドラ設定
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """終了シグナルを処理"""
        print(f"\n🛑 終了シグナル受信: {signum}")
        self.running = False
    
    async def initialize_system(self):
        """システムを初期化"""
        print("🔧 24時間耐久テストシステム初期化...")
        
        try:
            # コンポーネント初期化
            from tools.sheets_manager import GoogleSheetsManager
            from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
            from agents.self_healing.self_learning_pipeline_fixed import SelfLearningPipelineFixed
            from task_executor import TaskExecutor
            from autonomous_development_orchestrator import AutonomousDevelopmentOrchestrator
            
            sheets = GoogleSheetsManager()
            kb = KnowledgeBaseManager(sheets)
            pipeline = SelfLearningPipelineFixed(sheets, kb)
            executor = TaskExecutor()
            await executor.initialize()
            
            self.components = {
                'sheets': sheets,
                'kb': kb,
                'pipeline': pipeline,
                'executor': executor
            }
            
            print("✅ システム初期化完了")
            return True
            
        except Exception as e:
            print(f"❌ システム初期化失敗: {e}")
            return False
    
    async def run_learning_cycle(self):
        """学習サイクルを実行"""
        try:
            strategies = await self.components['pipeline'].run_learning_cycle()
            return len(strategies)
        except Exception as e:
            print(f"❌ 学習サイクルエラー: {e}")
            return 0
    
    async def run_task_cycle(self):
        """タスクサイクルを実行"""
        try:
            # 模擬タスクを実行
            tasks = [
                "コードの品質チェックを実行",
                "ナレッジベースを更新", 
                "エラーパターンを分析",
                "パフォーマンスを最適化"
            ]
            
            import random
            task = random.choice(tasks)
            result = await self.components['executor'].execute(task)
            return result['success']
        except Exception as e:
            print(f"❌ タスクサイクルエラー: {e}")
            return False
    
    async def monitor_system_health(self):
        """システム健全性を監視"""
        try:
            # RAGエンジンの状態確認
            from mvp_v4.scripts.rag_engine_persistent_v2 import get_rag_engine_v2
            rag = get_rag_engine_v2(['mvp_v4/knowledge/learned/conversation_knowledge_v3.json'])
            stats = rag.get_stats()
            
            health_info = {
                'rag_documents': stats['count'],
                'cycle_count': self.cycle_count,
                'success_rate': (self.successful_cycles / max(self.cycle_count, 1)) * 100
            }
            
            print(f"📊 システム健全性: {health_info}")
            return health_info
            
        except Exception as e:
            print(f"❌ 健全性監視エラー: {e}")
            return {}
    
    async def run_endurance_test(self, duration_hours=24):
        """耐久テストを実行"""
        print(f"🚀 24時間耐久テスト開始 - 目標: {duration_hours}時間")
        print("=" * 60)
        
        if not await self.initialize_system():
            return False
        
        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)
        
        while self.running and time.time() < end_time:
            self.cycle_count += 1
            current_time = time.time() - start_time
            hours = current_time / 3600
            
            print(f"\n🔄 サイクル {self.cycle_count} - 経過時間: {hours:.2f}時間")
            
            # 学習サイクル実行
            strategies_count = await self.run_learning_cycle()
            
            # タスクサイクル実行
            task_success = await self.run_task_cycle()
            
            # 成功カウント
            if strategies_count > 0 or task_success:
                self.successful_cycles += 1
            
            # 健全性監視（10サイクルごと）
            if self.cycle_count % 10 == 0:
                await self.monitor_system_health()
            
            # 30秒間隔で実行
            await asyncio.sleep(30)
        
        # テスト結果報告
        await self.report_test_results(start_time)
        return True
    
    async def report_test_results(self, start_time):
        """テスト結果を報告"""
        total_time = time.time() - start_time
        hours = total_time / 3600
        success_rate = (self.successful_cycles / max(self.cycle_count, 1)) * 100
        
        print("\n" + "=" * 60)
        print("📈 24時間耐久テスト結果")
        print("=" * 60)
        print(f"⏱️  総実行時間: {hours:.2f}時間")
        print(f"🔄 総サイクル数: {self.cycle_count}")
        print(f"✅ 成功サイクル: {self.successful_cycles}")
        print(f"📊 成功率: {success_rate:.1f}%")
        print(f"🔧 平均サイクル時間: {total_time/max(self.cycle_count, 1):.2f}秒")
        
        if success_rate >= 80:
            print("🎉 耐久テスト: 成功！24時間自律開発システムは安定して動作します")
        else:
            print("⚠️  耐久テスト: 要改善。成功率が目標に達していません")

async def main():
    tester = EnduranceTest()
    
    # テスト時間を指定（時間単位）
    test_hours = 24  # 本番は24時間
    
    try:
        success = await tester.run_endurance_test(test_hours)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 ユーザーによってテストが中断されました")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

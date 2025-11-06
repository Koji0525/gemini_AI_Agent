"""
24時間自律開発システム Orchestrator
Loop 1: 学習・修復ループ（30秒毎）
Loop 2: タスク実行 + 品質フィードバックループ（3分毎）
"""
import asyncio
import logging
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from task_executor.task_executor_main import TaskExecutor
from core_agents.pm_agent import PMAgent
from core_agents.review_agent import ReviewAgent, QualityFeedbackLoop
from agents.self_healing.self_learning_pipeline import SelfLearningPipeline
from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


class AutonomousDevelopmentOrchestrator:
    """24時間自律開発システムの統合オーケストレータ"""
    
    def __init__(self):
        # ナレッジベース自動同期
        from tools.knowledge_sync import sync_knowledge_on_startup
        sync_knowledge_on_startup()

        # ナレッジベース自動同期
        from tools.knowledge_sync import sync_knowledge_on_startup
        sync_knowledge_on_startup()

        logger.info("=" * 60)
        logger.info("🚀 24時間自律開発システム起動中...")
        logger.info("=" * 60)
        
        # コア基盤初期化
        self.sheets_manager = GoogleSheetsManager()
        self.sheets = SafeSheetsWrapper(self.sheets_manager)
        
        # タスク実行層
        self.task_executor = TaskExecutor(self.sheets_manager)
        
        # PM層
        self.pm_agent = PMAgent(self.sheets)
        
        # 品質管理層（新規）
        self.review_agent = ReviewAgent(self.sheets)
        self.quality_loop = QualityFeedbackLoop(self.review_agent, self.task_executor)
        
        # 学習層
        self.kb_manager = KnowledgeBaseManager(self.sheets_manager)
        self.learning_pipeline = SelfLearningPipeline(self.sheets_manager, self.kb_manager)
        
        # 統計情報
        self.stats = {
            'start_time': datetime.now(),
            'learning_cycles': 0,
            'task_cycles': 0,
            'tasks_executed': 0,
            'fixes_applied': 0,
            'quality_reviews': 0,
            'quality_retries': 0
        }
        
        logger.info("✅ すべてのコンポーネントを初期化しました")
    
    async def run_forever(self):
        """24時間自律稼働メインループ"""
        logger.info("=" * 60)
        logger.info("🚀 24時間自律開発システム 起動完了")
        logger.info("=" * 60)
        logger.info("🧠 学習ループ: 30秒毎")
        logger.info("📋 タスクループ: 3分毎")
        logger.info("📊 ステータスモニター: 5分毎")
        logger.info("💓 ヘルスチェック: 1分毎")
        logger.info("=" * 60)
        logger.info("")
        
        # 並行実行タスク作成
        tasks = [
            asyncio.create_task(self._learning_loop()),
            asyncio.create_task(self._task_loop()),
            asyncio.create_task(self._status_monitor()),
            asyncio.create_task(self._health_check())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("\n🛑 システム停止要求を受信")
            await self._shutdown()
    
    async def _learning_loop(self):
        """Loop 1: 学習・修復ループ（30秒毎）"""
        logger.info("🧠 学習ループを開始します")
        
        while True:
            try:
                self.stats['learning_cycles'] += 1
                logger.info("━" * 40)
                logger.info(f"🧠 学習サイクル #{self.stats['learning_cycles']}")
                
                # 学習サイクル実行
                results = await self.learning_pipeline.run_learning_cycle()
                
                # 修正が必要な場合は適用
                if results.get('fixes'):
                    self.stats['fixes_applied'] += len(results['fixes'])
                    logger.info(f"🔧 修正適用: {len(results['fixes'])}件")
                
                logger.info(f"✅ 学習サイクル完了（累計: {self.stats['learning_cycles']}回）")
                
            except Exception as e:
                logger.error(f"❌ 学習ループエラー: {e}")
            
            await asyncio.sleep(30)  # 30秒待機
    
    async def _task_loop(self):
        """Loop 2: タスク実行 + 品質フィードバックループ（3分毎）"""
        logger.info("📋 タスクループを開始します")
        
        while True:
            try:
                self.stats['task_cycles'] += 1
                logger.info("━" * 40)
                logger.info(f"📋 タスクサイクル #{self.stats['task_cycles']}")
                
                # pending タスク取得
                tasks = await self._get_pending_tasks()
                
                if not tasks:
                    logger.info("ℹ️  実行可能なタスクがありません")
                    await asyncio.sleep(180)
                    continue
                
                # タスク実行（品質フィードバック付き）
                for task in tasks[:5]:  # 最大5タスク
                    result = await self.quality_loop.process_task_with_feedback(task)
                    
                    self.stats['tasks_executed'] += 1
                    self.stats['quality_reviews'] += 1
                    
                    if result.get('retry_count', 0) > 0:
                        self.stats['quality_retries'] += result['retry_count']
                    
                    logger.info(f"✅ タスク完了: {task.get('task_id', 'N/A')}")
                    logger.info(f"   品質スコア: {result.get('review', {}).get('quality_score', 'N/A')}/10")
                
                logger.info(f"✅ タスクサイクル完了（累計: {self.stats['task_cycles']}回）")
                
            except Exception as e:
                logger.error(f"❌ タスクループエラー: {e}")
            
            await asyncio.sleep(180)  # 3分待機
    
    async def _get_pending_tasks(self) -> list:
        """pending タスクを取得"""
        try:
            data = await self.sheets.safe_read('pm_tasks', default=[])
            
            if not data or len(data) < 2:
                return []
            
            # ヘッダー取得
            headers = data[0]
            task_id_idx = headers.index('task_id') if 'task_id' in headers else 0
            status_idx = headers.index('status') if 'status' in headers else -1
            
            # pending タスク抽出
            pending_tasks = []
            for row in data[1:]:
                if len(row) > status_idx and status_idx >= 0:
                    status = row[status_idx].strip().lower()
                    if status == 'pending':
                        task = {
                            'task_id': row[task_id_idx] if len(row) > task_id_idx else 'N/A',
                            'status': status,
                            'raw_row': row
                        }
                        pending_tasks.append(task)
            
            logger.info(f"📋 pending タスク: {len(pending_tasks)}件")
            return pending_tasks
            
        except Exception as e:
            logger.error(f"❌ タスク取得エラー: {e}")
            return []
    
    async def _status_monitor(self):
        """ステータスモニター（5分毎）"""
        await asyncio.sleep(60)  # 初回は1分後
        
        while True:
            try:
                runtime = datetime.now() - self.stats['start_time']
                
                logger.info("")
                logger.info("=" * 60)
                logger.info("📊 24時間自律開発システム 稼働状況")
                logger.info("=" * 60)
                logger.info(f"⏱️  稼働時間: {runtime}")
                logger.info(f"🧠 学習サイクル: {self.stats['learning_cycles']}回")
                logger.info(f"📋 タスクサイクル: {self.stats['task_cycles']}回")
                logger.info(f"✅ 実行タスク数: {self.stats['tasks_executed']}個")
                logger.info(f"🔍 品質レビュー: {self.stats['quality_reviews']}回")
                logger.info(f"🔄 品質リトライ: {self.stats['quality_retries']}回")
                logger.info(f"🔧 修正適用数: {self.stats['fixes_applied']}個")
                logger.info("=" * 60)
                logger.info("")
                
            except Exception as e:
                logger.error(f"❌ ステータスモニターエラー: {e}")
            
            await asyncio.sleep(300)  # 5分待機
    
    async def _health_check(self):
        """ヘルスチェック（1分毎）"""
        while True:
            try:
                # シンプルなヘルスチェック
                await asyncio.sleep(60)
                # 必要に応じてコンポーネントの状態確認を追加
                
            except Exception as e:
                logger.error(f"❌ ヘルスチェックエラー: {e}")
    
    async def _shutdown(self):
        """シャットダウン処理"""
        logger.info("🛑 シャットダウン処理開始...")
        logger.info(f"📊 最終統計: {self.stats}")
        logger.info("✅ シャットダウン完了")


async def main():
    """メインエントリーポイント"""
    orchestrator = AutonomousDevelopmentOrchestrator()
    await orchestrator.run_forever()


if __name__ == "__main__":
    asyncio.run(main())

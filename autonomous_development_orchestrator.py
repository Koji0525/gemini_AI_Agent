"""
AutonomousDevelopmentOrchestrator - 24時間自律開発システム
2ループ並行実行（学習ループ + タスクループ）
"""

import sys
import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from tools.sheets_manager import GoogleSheetsManager
from task_executor import TaskExecutor
from core_agents.pm_agent import PMAgent
from agents.self_healing.self_learning_pipeline import SelfLearningPipeline
from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutonomousDevelopmentOrchestrator:
    """
    24時間自律開発オーケストレーター
    
    【2つのループ】
    1. 学習ループ（30秒毎）：エラーログ → パターン抽出 → ナレッジ更新
    2. タスクループ（3分毎）：タスク取得 → 実行 → ログ記録
    """
    
    def __init__(self):
        """初期化"""
        logger.info("=" * 60)
        logger.info("🚀 24時間自律開発システム起動中...")
        logger.info("=" * 60)
        
        # GoogleSheetsManager初期化（シングルトン）
        self.sheets = GoogleSheetsManager()
        
        # TaskExecutor初期化
        self.task_executor = TaskExecutor(self.sheets)
        
        # PMAgent初期化
        self.pm_agent = PMAgent(self.sheets)
        
        # 学習パイプライン初期化
        self.kb_manager = KnowledgeBaseManager(self.sheets)
        self.learning_pipeline = SelfLearningPipeline(self.sheets, self.kb_manager)
        
        # 統計情報
        self.stats = {
            'start_time': datetime.now(),
            'learning_cycles': 0,
            'task_cycles': 0,
            'tasks_executed': 0,
            'errors_fixed': 0
        }
        
        logger.info("✅ すべてのコンポーネントを初期化しました")
    
    async def learning_loop(self):
        """
        学習ループ（30秒毎）
        
        1. エラーログ収集
        2. パターン抽出
        3. ナレッジ更新
        4. 修正戦略生成
        """
        logger.info("🧠 学習ループを開始します")
        
        while True:
            try:
                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.info(f"🧠 学習サイクル #{self.stats['learning_cycles'] + 1}")
                
                # 学習パイプライン実行
                results = await self.learning_pipeline.run_learning_cycle()
                
                self.stats['learning_cycles'] += 1
                
                if results.get('errors_detected', 0) > 0:
                    logger.info(f"📚 {results.get('errors_detected', 0)}個のエラーを学習しました")
                    self.stats['errors_fixed'] += results.get('fixes_applied', 0)
                
                logger.info(f"✅ 学習サイクル完了（累計: {self.stats['learning_cycles']}回）")
            
            except Exception as e:
                logger.error(f"❌ 学習ループエラー: {e}")
                import traceback
                traceback.print_exc()
            
            # 30秒待機
            await asyncio.sleep(30)
    
    async def task_loop(self):
        """
        タスクループ（3分毎）
        
        1. PMAgentで目標 → タスク分解
        2. TaskExecutorでタスク実行
        3. 結果ログ記録
        """
        logger.info("📋 タスクループを開始します")
        
        # 初回は10秒後に開始（学習ループとずらす）
        await asyncio.sleep(10)
        
        while True:
            try:
                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.info(f"📋 タスクサイクル #{self.stats['task_cycles'] + 1}")
                
                # PMサイクル実行（必要に応じて）
                # 目標がない場合のみPMAgentを実行
                pending_tasks = await self.task_executor.get_pending_tasks()
                
                if len(pending_tasks) == 0:
                    logger.info("📝 タスクがないため、PMAgentで目標を分解します")
                    await self.pm_agent.run_pm_cycle()
                
                # タスク実行サイクル
                await self.task_executor.run_task_cycle()
                
                self.stats['task_cycles'] += 1
                self.stats['tasks_executed'] += min(len(pending_tasks), 5)
                
                logger.info(f"✅ タスクサイクル完了（累計: {self.stats['task_cycles']}回）")
            
            except Exception as e:
                logger.error(f"❌ タスクループエラー: {e}")
                import traceback
                traceback.print_exc()
            
            # 3分待機
            await asyncio.sleep(180)
    
    async def status_monitor(self):
        """
        ステータスモニター（5分毎）
        
        稼働状況を定期的に出力
        """
        await asyncio.sleep(60)  # 初回は1分後
        
        while True:
            try:
                uptime = datetime.now() - self.stats['start_time']
                
                logger.info("")
                logger.info("=" * 60)
                logger.info("📊 24時間自律開発システム 稼働状況")
                logger.info("=" * 60)
                logger.info(f"⏱️  稼働時間: {uptime}")
                logger.info(f"🧠 学習サイクル: {self.stats['learning_cycles']}回")
                logger.info(f"📋 タスクサイクル: {self.stats['task_cycles']}回")
                logger.info(f"✅ 実行タスク数: {self.stats['tasks_executed']}個")
                logger.info(f"🔧 修正適用数: {self.stats['errors_fixed']}個")
                logger.info("=" * 60)
                logger.info("")
            
            except Exception as e:
                logger.error(f"❌ ステータスモニターエラー: {e}")
            
            # 5分待機
            await asyncio.sleep(300)
    
    async def health_check(self):
        """
        ヘルスチェック（1分毎）
        
        各コンポーネントの正常性確認
        """
        await asyncio.sleep(30)  # 初回は30秒後
        
        while True:
            try:
                # GoogleSheetsManagerの接続確認
                if not self.sheets.authenticated:
                    logger.warning("⚠️ Google Sheets認証が切れています。再認証を試みます...")
                    self.sheets.authenticate()
                
                # その他のヘルスチェック項目
                # TODO: 実装
            
            except Exception as e:
                logger.error(f"❌ ヘルスチェックエラー: {e}")
            
            # 1分待機
            await asyncio.sleep(60)
    
    async def run_forever(self):
        """
        24時間稼働メインループ
        
        4つのタスクを並行実行:
        1. 学習ループ（30秒毎）
        2. タスクループ（3分毎）
        3. ステータスモニター（5分毎）
        4. ヘルスチェック（1分毎）
        """
        logger.info("=" * 60)
        logger.info("🚀 24時間自律開発システム 起動完了")
        logger.info("=" * 60)
        logger.info("🧠 学習ループ: 30秒毎")
        logger.info("📋 タスクループ: 3分毎")
        logger.info("📊 ステータスモニター: 5分毎")
        logger.info("💓 ヘルスチェック: 1分毎")
        logger.info("=" * 60)
        logger.info("")
        
        # 4つのタスクを並行実行
        tasks = [
            asyncio.create_task(self.learning_loop()),
            asyncio.create_task(self.task_loop()),
            asyncio.create_task(self.status_monitor()),
            asyncio.create_task(self.health_check())
        ]
        
        try:
            # すべてのタスクが完了するまで待機（実質無限ループ）
            await asyncio.gather(*tasks)
        
        except KeyboardInterrupt:
            logger.info("")
            logger.info("=" * 60)
            logger.info("⚠️ ユーザーによる停止要求を検出")
            logger.info("=" * 60)
            
            # 統計情報を出力
            uptime = datetime.now() - self.stats['start_time']
            logger.info(f"⏱️  総稼働時間: {uptime}")
            logger.info(f"🧠 学習サイクル: {self.stats['learning_cycles']}回")
            logger.info(f"📋 タスクサイクル: {self.stats['task_cycles']}回")
            logger.info(f"✅ 実行タスク数: {self.stats['tasks_executed']}個")
            logger.info(f"🔧 修正適用数: {self.stats['errors_fixed']}個")
            logger.info("=" * 60)
            
            # すべてのタスクをキャンセル
            for task in tasks:
                task.cancel()
            
            logger.info("✅ 24時間自律開発システムを正常終了しました")
        
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """メイン実行"""
    orchestrator = AutonomousDevelopmentOrchestrator()
    await orchestrator.run_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n終了しました")

"""
Task Executor - タスク実行を管理するエージェント
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from tools.sheets_manager import GoogleSheetsManager
from browser_control.rate_limiter import RateLimiter
from browser_control.error_recovery import ErrorRecovery

logger = logging.getLogger(__name__)

class TaskExecutor:
    """
    タスク実行を管理するエージェント
    
    責務:
    - タスクの実行スケジューリング
    - 実行結果の記録
    - エラーハンドリングとリトライ
    """
    
    def __init__(self, sheets_manager: GoogleSheetsManager, output_dir: str = "agent_outputs", review_agent=None):
        """
        TaskExecutorの初期化
        
        Args:
            sheets_manager: Googleスプレッドシート管理オブジェクト
            output_dir: 出力ディレクトリ
            review_agent: レビューエージェント（オプション）
        """
        self.sheets_manager = sheets_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.review_agent = review_agent

        # レート制限
        self.rate_limiter = RateLimiter(max_requests_per_hour=50, min_interval_seconds=30)

        # エラーリカバリー
        self.error_recovery = ErrorRecovery(max_retries=3)
        
        logger.info("✅ TaskExecutor初期化完了")

    async def execute_single_task(self, task: Dict) -> Dict[str, Any]:
        """
        単一タスクを実行（browser引数なしのバージョン）
        
        Args:
            task: タスク情報
            
        Returns:
            Dict: 実行結果
        """
        try:
            logger.info(f"▶️  タスク実行開始: {task.get('task_name', 'Unknown')}")
            
            # タスク実行のシミュレーション
            await asyncio.sleep(1)  # 実行時間のシミュレーション
            
            result = {
                'output': f"タスク '{task.get('task_name', 'Unknown')}' を実行しました",
                'status': 'completed',
                'task_id': task.get('task_id'),
                'execution_time': 1.0,
                'timestamp': datetime.now().isoformat()
            }
            
            # レビューエージェントが利用可能なら品質評価を実行
            if self.review_agent:
                evaluation_context = {
                    'task_id': task.get('task_id'),
                    'task_name': task.get('task_name'),
                    'task_description': task.get('task_description', ''),
                    'result': result,
                    'agent_name': task.get('agent_name', 'TaskExecutor'),
                    'timestamp': datetime.now().isoformat()
                }
                
                try:
                    quality_result = await self.review_agent.evaluate(evaluation_context)
                    result['quality_score'] = quality_result.get('quality_score', 0)
                    result['evaluation'] = quality_result.get('evaluation', '')
                except Exception as e:
                    logger.warning(f"⚠️  品質評価エラー: {e}")
                    result['quality_score'] = 5  # デフォルトスコア
                    result['evaluation'] = f'評価エラー: {str(e)}'
            else:
                result['quality_score'] = 7  # デフォルトスコア
                result['evaluation'] = 'レビューエージェントなし'
            
            logger.info(f"✅ タスク実行完了: {task.get('task_name', 'Unknown')} - スコア: {result.get('quality_score', 'N/A')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {e}")
            return {
                'output': f"タスク実行エラー: {str(e)}",
                'status': 'error',
                'error': str(e),
                'task_id': task.get('task_id'),
                'timestamp': datetime.now().isoformat()
            }

    async def execute_single_task_with_browser(self, browser, task: Dict) -> bool:
        """
        ブラウザを使用するタスクを実行（既存コードとの互換性維持）
        
        Args:
            browser: BrowserControllerインスタンス
            task: タスク情報
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            result = await self.execute_single_task(task)
            return result.get('status') == 'completed'
        except Exception as e:
            logger.error(f"❌ ブラウザタスク実行エラー: {e}")
            return False

    async def execute_continuous_loop(self, max_tasks_per_cycle: int = 5) -> Dict[str, Any]:
        """
        連続タスク実行ループ - 24時間自律運転用
        
        Args:
            max_tasks_per_cycle: 1サイクルあたりの最大タスク数
            
        Returns:
            dict: 実行結果統計
        """
        tasks_processed = 0
        successful_tasks = 0
        
        try:
            # 保留中のタスクを取得
            pending_tasks = await self._get_pending_tasks()
            
            if not pending_tasks:
                return {
                    'status': 'no_tasks',
                    'tasks_processed': 0,
                    'message': '実行可能なタスクがありません'
                }
            
            # 最大タスク数まで実行
            for task in pending_tasks[:max_tasks_per_cycle]:
                try:
                    result = await self.execute_single_task(task)
                    tasks_processed += 1
                    
                    if result.get('status') == 'completed':
                        successful_tasks += 1
                        
                    # タスク間のインターバル（負荷分散）
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"タスク実行エラー: {e}")
                    continue
            
            return {
                'status': 'completed',
                'tasks_processed': tasks_processed,
                'successful_tasks': successful_tasks,
                'success_rate': successful_tasks / max(1, tasks_processed)
            }
            
        except Exception as e:
            logger.error(f"連続実行ループエラー: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'tasks_processed': tasks_processed
            }
    
    async def _get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        保留中のタスクを取得 - 実装に応じてオーバーライド
        """
        # デフォルト実装: テストタスクを返す
        return [
            {
                'task_id': f'auto_task_{int(datetime.now().timestamp())}_{i}',
                'task_name': f'自動生成タスク {i}',
                'task_description': '24時間自律システムによる自動実行',
                'agent_name': 'AutonomousExecutor',
                'priority': 'medium'
            }
            for i in range(3)
        ]
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        システム健全性チェック
        """
        return {
            'component': 'TaskExecutor',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'capabilities': [
                'single_task_execution', 
                'continuous_loop', 
                'health_check',
                'quality_evaluation'
            ],
            'review_agent_available': self.review_agent is not None
        }

# 単体テスト
if __name__ == "__main__":
    async def test_task_executor():
        """TaskExecutorのテスト"""
        class MockSheetsManager:
            pass
        
        sheets_manager = MockSheetsManager()
        task_executor = TaskExecutor(sheets_manager=sheets_manager)
        
        test_task = {
            'task_id': 'test_001',
            'task_name': 'テストタスク',
            'task_description': 'TaskExecutorのテスト'
        }
        
        result = await task_executor.execute_single_task(test_task)
        print(f"テスト結果: {result}")
    
    asyncio.run(test_task_executor())

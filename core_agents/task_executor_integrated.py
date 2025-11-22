#!/usr/bin/env python3
"""
タスク実行システム統合版 v1.0

【役割】
- pm_tasksシートのpendingタスク自動検出
- ナレッジベースからの類似情報参照
- タスク実行と結果生成
- agent_outputs/への結果保存
- task_execution_logへのログ記録
- pm_tasksシートのステータス更新
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# プロジェクトルート追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.base_data_accessor import BaseDataAccessor

# ナレッジベース
try:
    from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False
    print("⚠️ ナレッジベース未利用（インポート失敗）")

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskExecutorIntegrated(BaseDataAccessor):
    """タスク実行システム統合版"""
    
    def __init__(self, sheets_manager: Optional[GoogleSheetsManager] = None):
        """初期化"""
        super().__init__(sheets_manager)
        self.output_dir = project_root / "agent_outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        # ナレッジマネージャー
        if KNOWLEDGE_AVAILABLE:
            try:
                self.knowledge_manager = KnowledgeManager()
                logger.info("✅ ナレッジベース接続成功")
            except Exception as e:
                logger.warning(f"⚠️ ナレッジベース初期化失敗: {e}")
                self.knowledge_manager = None
        else:
            self.knowledge_manager = None
    
    def get_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """pendingタスクを取得"""
        logger.info(f"🔍 pendingタスク取得中（最大{limit}件）")
        
        tasks = self.read_sheet_as_dicts(
            'pm_tasks',
            filter_func=lambda t: t.get('status') == 'pending'
        )
        
        result = tasks[:limit] if tasks else []
        logger.info(f"   取得: {len(result)}件")
        return result
    
    def search_knowledge(self, task: Dict[str, Any]) -> Optional[Dict]:
        """ナレッジベースから類似情報を検索"""
        if not self.knowledge_manager:
            return None
        
        try:
            query = f"{task.get('description', '')} {task.get('purpose', '')}"
            results = self.knowledge_manager.search_knowledge(
                query=query,
                limit=3
            )
            
            if results:
                logger.info(f"   ナレッジ検索: {len(results)}件ヒット")
                return results[0] if results else None
            
        except Exception as e:
            logger.warning(f"⚠️ ナレッジ検索エラー: {e}")
        
        return None
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タスクを実行"""
        task_id = task.get('task_id', 'unknown')
        description = task.get('description', '')
        
        logger.info(f"🚀 タスク実行開始: {task_id}")
        logger.info(f"   説明: {description[:50]}...")
        
        start_time = datetime.now()
        
        try:
            # ナレッジ検索
            knowledge = self.search_knowledge(task)
            
            # タスク実行（シミュレーション）
            result = self._execute_task_logic(task, knowledge)
            
            # 結果保存
            output_file = self._save_result(task_id, result)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'task_id': task_id,
                'output_file': str(output_file),
                'elapsed_time': elapsed,
                'knowledge_used': knowledge is not None,
                'result_summary': result.get('summary', '実行完了'),
                'quality_score': result.get('quality_score', 8.0)
            }
        
        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {e}")
            return {
                'success': False,
                'task_id': task_id,
                'error': str(e),
                'elapsed_time': (datetime.now() - start_time).total_seconds()
            }
    
    def _execute_task_logic(self, task: Dict, knowledge: Optional[Dict]) -> Dict:
        """タスク実行ロジック（実装例）"""
        description = task.get('description', '')
        purpose = task.get('purpose', '')
        
        # 実際のタスク実行ロジックをここに実装
        # 今回はシミュレーション
        
        result = {
            'summary': f"タスク '{description[:30]}...' を実行しました",
            'details': {
                'purpose': purpose,
                'knowledge_referenced': knowledge is not None,
                'execution_method': 'automated'
            },
            'quality_score': 8.5 if knowledge else 7.5
        }
        
        return result
    
    def _save_result(self, task_id: str, result: Dict) -> Path:
        """結果をファイルに保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"task_{task_id}_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"タスクID: {task_id}\n")
            f.write(f"実行時刻: {datetime.now()}\n")
            f.write(f"\n--- 実行結果 ---\n")
            f.write(f"{result.get('summary', '')}\n")
            f.write(f"\n--- 詳細 ---\n")
            for key, value in result.get('details', {}).items():
                f.write(f"{key}: {value}\n")
        
        logger.info(f"   結果保存: {filepath}")
        return filepath
    
    def log_execution(self, task: Dict[str, Any], result: Dict[str, Any]):
        """task_execution_logに記録"""
        log_entry = [
            '',  # log_id（自動生成）
            result.get('task_id', ''),
            task.get('description', ''),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            task.get('required_role', 'TaskExecutor'),
            result.get('result_summary', ''),
            result.get('output_file', ''),
            'completed' if result.get('success') else 'failed',
            result.get('quality_score', 0.0),
            '',  # Quality_description
            result.get('elapsed_time', 0.0),
            0,  # retry_count
            result.get('error', ''),
            ''   # fix_applied
        ]
        
        try:
            self.sheets.append_rows('task_execution_log', [log_entry])
            logger.info(f"✅ ログ記録成功: {result.get('task_id')}")
        except Exception as e:
            logger.error(f"❌ ログ記録失敗: {e}")
    
    def update_task_status(self, task_id: str, new_status: str):
        """pm_tasksシートのステータスを更新"""
        valid_statuses = ['completed', 'failed', 'skipped', 'cancelled']
        
        if new_status not in valid_statuses:
            logger.error(f"❌ 無効なステータス: {new_status}")
            return False
        
        try:
            # タスク行を検索
            tasks = self.read_sheet_as_dicts('pm_tasks')
            
            for i, t in enumerate(tasks, start=2):  # A2から開始
                if t.get('task_id') == task_id:
                    # ステータス列（E列=5列目）を更新
                    range_name = f'pm_tasks!E{i}'
                    self.sheets.update_range(range_name, [[new_status]])
                    logger.info(f"✅ ステータス更新: {task_id} -> {new_status}")
                    return True
            
            logger.warning(f"⚠️ タスクID {task_id} が見つかりません")
            return False
        
        except Exception as e:
            logger.error(f"❌ ステータス更新エラー: {e}")
            return False
    
    def run_cycle(self, limit: int = 5):
        """1サイクル実行"""
        logger.info("="*60)
        logger.info("🔄 タスク実行サイクル開始")
        logger.info("="*60)
        
        # pendingタスク取得
        pending_tasks = self.get_pending_tasks(limit=limit)
        
        if not pending_tasks:
            logger.info("✅ 実行すべきタスクなし")
            return
        
        logger.info(f"📋 実行対象: {len(pending_tasks)}件")
        
        for i, task in enumerate(pending_tasks, 1):
            task_id = task.get('task_id', f'unknown_{i}')
            
            logger.info(f"\n--- タスク {i}/{len(pending_tasks)} ---")
            
            # タスク実行
            result = self.execute_task(task)
            
            # ログ記録
            self.log_execution(task, result)
            
            # ステータス更新
            new_status = 'completed' if result.get('success') else 'failed'
            self.update_task_status(task_id, new_status)
        
        logger.info("\n" + "="*60)
        logger.info("✅ サイクル完了")
        logger.info("="*60)


def main():
    """メイン実行"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="タスク実行システム統合版 v1.0"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='実行するタスク数の上限（デフォルト: 5）'
    )
    parser.add_argument(
        '--task-id',
        type=str,
        help='特定のタスクIDを指定して実行'
    )
    
    args = parser.parse_args()
    
    executor = TaskExecutorIntegrated()
    
    if args.task_id:
        # 特定タスクの実行
        tasks = executor.read_sheet_as_dicts(
            'pm_tasks',
            filter_func=lambda t: t.get('task_id') == args.task_id
        )
        
        if tasks:
            result = executor.execute_task(tasks[0])
            executor.log_execution(tasks[0], result)
            executor.update_task_status(
                args.task_id,
                'completed' if result.get('success') else 'failed'
            )
        else:
            logger.error(f"❌ タスクID {args.task_id} が見つかりません")
    else:
        # 通常サイクル
        executor.run_cycle(limit=args.limit)


if __name__ == "__main__":
    main()

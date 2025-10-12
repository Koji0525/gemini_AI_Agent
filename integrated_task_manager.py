#!/usr/bin/env python3
"""
統合タスクマネージャー
- Google Sheets からタスク取得
- WordPress に投稿
- ステータス更新 (pending → complete)
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json

from tools.sheets_manager import GoogleSheetsManager
from scripts.wordpress_task_executor import WordPressTaskExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedTaskManager:
    """統合タスクマネージャー"""
    
    def __init__(self):
        # 正しいスプレッドシートID
        self.spreadsheet_id = '1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s'
        self.sheet_name = 'tasks'  # シート名（実際の名前に合わせる）
        self.sheets = None
        self.wp_executor = None
        self.error_log_path = Path("error_logs")
        self.error_log_path.mkdir(exist_ok=True)
    
    async def initialize(self):
        """初期化"""
        logger.info("=" * 80)
        logger.info("🚀 統合タスクマネージャー 起動")
        logger.info("=" * 80)
        logger.info(f"📊 スプレッドシートID: {self.spreadsheet_id}")
        
        try:
            # Google Sheets接続
            logger.info("📊 Google Sheets 接続中...")
            self.sheets = GoogleSheetsManager(spreadsheet_id=self.spreadsheet_id)
            logger.info("✅ Google Sheets 接続完了")
            
            # WordPress エグゼキューター初期化
            logger.info("🌐 WordPress エグゼキューター 初期化中...")
            self.wp_executor = WordPressTaskExecutor()
            if not await self.wp_executor.initialize():
                return False
            logger.info("✅ WordPress エグゼキューター 初期化完了")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def get_pending_tasks(self):
        """pending タスクを取得"""
        logger.info("\n📋 pending タスクを検索中...")
        
        try:
            # sheetsオブジェクトの利用可能なメソッドを確認
            methods = [m for m in dir(self.sheets) if not m.startswith('_') and callable(getattr(self.sheets, m))]
            logger.info(f"📝 利用可能なメソッド: {methods}")
            
            # データ読み取りを試行
            data = None
            
            if hasattr(self.sheets, 'read_range'):
                try:
                    data = self.sheets.read_range(f'{self.sheet_name}!A2:I1000')
                except:
                    data = self.sheets.read_range('A2:I1000')
            elif hasattr(self.sheets, 'get_all_values'):
                data = self.sheets.get_all_values()
            elif hasattr(self.sheets, 'get_values'):
                data = self.sheets.get_values('A2:I1000')
            else:
                logger.error("❌ データ読み取りメソッドが見つかりません")
                return []
            
            if not data:
                logger.warning("⚠️ データが空です")
                return []
            
            logger.info(f"✅ {len(data)} 行のデータを取得")
            
            # pending タスクをフィルター
            pending_tasks = []
            for i, row in enumerate(data):
                if len(row) >= 5:
                    status = str(row[4]).strip().lower() if row[4] else ''
                    if status == 'pending':
                        task = {
                            'row': i + 2,  # 行番号（ヘッダー分+1）
                            'task_id': row[0] if len(row) > 0 else '',
                            'parent': row[1] if len(row) > 1 else '',
                            'description': row[2] if len(row) > 2 else '',
                            'required_role': row[3] if len(row) > 3 else '',
                            'status': row[4] if len(row) > 4 else '',
                            'priority': row[5] if len(row) > 5 else '',
                            'estimated_time': row[6] if len(row) > 6 else '',
                            'dependencies': row[7] if len(row) > 7 else '',
                            'created_at': row[8] if len(row) > 8 else '',
                        }
                        pending_tasks.append(task)
                        logger.info(f"   ✓ {task['task_id']}: {task['description'][:50]}...")
            
            logger.info(f"✅ {len(pending_tasks)} 件の pending タスク")
            return pending_tasks
            
        except Exception as e:
            logger.error(f"❌ タスク取得エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def update_status(self, task: dict, status: str):
        """ステータス更新"""
        row = task['row']
        task_id = task['task_id']
        
        logger.info(f"📝 ステータス更新: {task_id} (行{row}) → {status}")
        
        try:
            # E列（5列目）を更新
            if hasattr(self.sheets, 'update_cell'):
                self.sheets.update_cell(row=row, col=5, value=status)
            elif hasattr(self.sheets, 'update_range'):
                self.sheets.update_range(f'E{row}', [[status]])
            else:
                logger.warning("⚠️ 更新メソッドが見つかりません")
                
            logger.info(f"✅ ステータス更新完了: {task_id} → {status}")
            
        except Exception as e:
            logger.error(f"❌ 更新エラー: {e}")
    
    async def execute_task(self, task: dict):
        """タスク実行"""
        task_id = task['task_id']
        description = task['description']
        role = task['required_role']
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 タスク実行: {task_id}")
        logger.info(f"   説明: {description}")
        logger.info(f"   ロール: {role}")
        logger.info(f"{'='*80}")
        
        try:
            # ロールに応じて実行
            if role == 'wp_dev':
                # WordPress記事作成
                wp_task = {
                    'title': description,
                    'content': f'<p>{description}</p>',
                    'post_status': 'draft'
                }
                result = await self.wp_executor.create_draft(wp_task)
                
            else:
                logger.warning(f"⚠️ 未対応ロール: {role}")
                result = {'success': True, 'skipped': True}
            
            return result
            
        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_cycle(self):
        """1サイクル実行"""
        logger.info("\n" + "=" * 80)
        logger.info("🔄 タスク実行サイクル開始")
        logger.info("=" * 80)
        
        # pending タスクを取得
        pending_tasks = await self.get_pending_tasks()
        
        if not pending_tasks:
            logger.info("ℹ️ 実行可能なタスクがありません")
            return
        
        # 優先度順にソート
        priority_map = {'high': 3, 'medium': 2, 'low': 1, '': 0}
        pending_tasks.sort(
            key=lambda t: priority_map.get(t.get('priority', '').lower(), 0),
            reverse=True
        )
        
        # タスク実行（最大3タスク）
        for task in pending_tasks[:3]:
            result = await self.execute_task(task)
            
            # ステータス更新
            if result.get('success'):
                if result.get('skipped'):
                    await self.update_status(task, 'skipped')
                else:
                    await self.update_status(task, 'complete')
                logger.info(f"✅ タスク完了: {task['task_id']}")
            else:
                await self.update_status(task, 'failed')
                logger.error(f"❌ タスク失敗: {task['task_id']}")
                
                # エラーログ保存
                self._save_error_log(task, result)
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 サイクル完了")
        logger.info("=" * 80)
    
    def _save_error_log(self, task: dict, result: dict):
        """エラーログ保存"""
        error_file = self.error_log_path / f"task_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump({
                'task': task,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 エラーログ: {error_file}")
    
    async def cleanup(self):
        """クリーンアップ"""
        if self.wp_executor:
            await self.wp_executor.cleanup()

async def main():
    manager = IntegratedTaskManager()
    
    if await manager.initialize():
        await manager.run_cycle()
    else:
        logger.error("❌ 初期化失敗")
    
    await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

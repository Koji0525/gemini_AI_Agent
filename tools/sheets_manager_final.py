import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
import logging
from datetime import datetime
from collections import Counter

class GoogleSheetsManagerFinal:
    def __init__(self, spreadsheet_id: str, service_account_file: str):
        self.spreadsheet_id = spreadsheet_id
        self.scope = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = Credentials.from_service_account_file(service_account_file, scopes=self.scope)
        self.gc = gspread.authorize(self.creds)
        self.logger = logging.getLogger(__name__)

    async def load_tasks_from_sheet(self, sheet_name: str = "pm_tasks") -> List[Dict]:
        """タスクをシートから読み込み（重複ヘッダー対策）"""
        try:
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # 生データを取得して手動で処理
            all_data = worksheet.get_all_values()
            
            if not all_data or len(all_data) < 2:
                return []
            
            # ヘッダー行を修正
            headers = self._fix_headers(all_data[0])
            
            tasks = []
            for i, row in enumerate(all_data[1:], start=2):
                if not any(row):  # 空行をスキップ
                    continue
                    
                task = {"row_number": i}
                
                # 各列をマッピング
                for col_idx, header in enumerate(headers):
                    if col_idx < len(row):
                        task[header] = row[col_idx]
                    else:
                        task[header] = ""
                
                # タスクIDを数値に変換
                if 'task_id' in task and task['task_id'].isdigit():
                    task['task_id'] = int(task['task_id'])
                
                tasks.append(task)
            
            self.logger.info(f"📊 タスク読み込み: {len(tasks)}件（シート: {sheet_name}）")
            return tasks
            
        except Exception as e:
            self.logger.error(f"❌ タスク読み込み失敗: {e}")
            return []

    def _fix_headers(self, headers: List[str]) -> List[str]:
        """ヘッダー行を修正（重複・空ヘッダー対策）"""
        header_count = Counter()
        fixed_headers = []
        
        for i, header in enumerate(headers):
            if not header.strip():  # 空のヘッダー
                fixed_header = f"column_{i+1}"
            elif header in header_count:  # 重複ヘッダー
                header_count[header] += 1
                fixed_header = f"{header}_{header_count[header]}"
            else:
                header_count[header] = 1
                fixed_header = header
            
            fixed_headers.append(fixed_header)
        
        return fixed_headers

    async def update_task_status(self, task_id: int, status: str, sheet_name: str = "pm_tasks") -> bool:
        """タスクステータスを更新"""
        try:
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # タスクを検索
            tasks = await self.load_tasks_from_sheet(sheet_name)
            target_row = None
            
            for task in tasks:
                if task.get('task_id') == task_id:
                    target_row = task.get('row_number')
                    break
            
            if not target_row:
                self.logger.error(f"❌ タスク {task_id} が見つかりません")
                return False
            
            # ステータス列を見つける
            all_data = worksheet.get_all_values()
            headers = self._fix_headers(all_data[0])
            
            status_col_index = None
            for i, header in enumerate(headers):
                if 'status' in header.lower():
                    status_col_index = i + 1
                    break
            
            if not status_col_index:
                self.logger.error("❌ ステータス列が見つかりません")
                return False
            
            # 更新実行
            worksheet.update_cell(target_row, status_col_index, status)
            self.logger.info(f"✅ タスク {task_id} のステータスを '{status}' に更新しました")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ステータス更新失敗: {e}")
            return False

    async def log_task_execution(self, task_data: Dict) -> bool:
        """タスク実行結果をログに記録（重複ヘッダー対策版）"""
        try:
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # task_execution_logシートを取得または作成
            try:
                log_sheet = spreadsheet.worksheet('task_execution_log')
            except gspread.WorksheetNotFound:
                # シートがなければ作成
                log_sheet = spreadsheet.add_worksheet(title='task_execution_log', rows=1000, cols=10)
                # ヘッダーを設定
                headers = [
                    'log_id', 'task_id', 'task_description', 'execution_time', 
                    'agent_role', 'output_summary', 'output_data', 'status',
                    'quality_score', 'quality_evaluation'
                ]
                log_sheet.append_row(headers)
            
            # 生データを取得して手動で処理
            all_data = log_sheet.get_all_values()
            next_log_id = len(all_data)  # ヘッダー行を含む
            
            # ログデータを準備
            log_row = [
                next_log_id,  # log_id
                task_data.get('task_id', ''),
                task_data.get('task_description', '')[:100],
                task_data.get('execution_time', datetime.now().isoformat()),
                task_data.get('agent_role', ''),
                task_data.get('output_summary', '')[:100],
                task_data.get('output_data', '')[:500],
                task_data.get('status', ''),
                task_data.get('quality_score', ''),
                task_data.get('quality_evaluation', '')[:200]  # J列: 評価の根拠
            ]
            
            log_sheet.append_row(log_row)
            self.logger.info(f"✅ タスク {task_data.get('task_id')} の実行をログに記録")
            self.logger.info(f"   📊 品質スコア: {task_data.get('quality_score', 'N/A')}/10")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ログ記録失敗: {e}")
            return False

    async def get_failed_tasks(self, sheet_name: str = "pm_tasks") -> List[Dict]:
        """失敗したタスクを取得"""
        tasks = await self.load_tasks_from_sheet(sheet_name)
        failed_tasks = [t for t in tasks if t.get('status', '').lower() == 'failed']
        return failed_tasks

    async def reset_failed_tasks(self, task_ids: List[int], sheet_name: str = "pm_tasks") -> bool:
        """失敗したタスクをpending状態にリセット"""
        try:
            for task_id in task_ids:
                await self.update_task_status(task_id, "pending", sheet_name)
            self.logger.info(f"✅ {len(task_ids)}件の失敗タスクをpendingにリセット")
            return True
        except Exception as e:
            self.logger.error(f"❌ 失敗タスクリセット失敗: {e}")
            return False


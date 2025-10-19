"""
SheetsManager に追加するメソッド
tools/sheets_manager.py に追加してください
"""

def update_task_status(
    self,
    task_id: str,
    status: str,
    result: Optional[Dict] = None,
    error_message: Optional[str] = None,
    output_file: Optional[str] = None
) -> bool:
    """
    タスクの実行結果をスプレッドシートに書き戻す
    
    Args:
        task_id: タスクID
        status: ステータス ('completed', 'failed', 'in_progress')
        result: 実行結果（Dict）
        error_message: エラーメッセージ（失敗時）
        output_file: 出力ファイルパス
        
    Returns:
        bool: 書き込み成功したかどうか
    """
    try:
        self._ensure_client()
        
        # スプレッドシートを開く
        sheet = self.gc.open_by_key(self.spreadsheet_id)
        task_sheet = sheet.worksheet("tasks")  # タスクシート名
        
        # タスクIDの列を探す（通常は1列目）
        task_id_col = 1
        
        # タスクIDで行を検索
        cell = task_sheet.find(str(task_id))
        
        if not cell:
            print(f"⚠️  タスクID {task_id} が見つかりません")
            return False
        
        row = cell.row
        
        # ステータス列に書き込み（例：D列 = 4）
        status_col = 4
        task_sheet.update_cell(row, status_col, status)
        
        # 完了日時を記録（例：E列 = 5）
        timestamp_col = 5
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_sheet.update_cell(row, timestamp_col, timestamp)
        
        # 結果の詳細を記録（例：F列 = 6）
        if result:
            result_col = 6
            result_text = str(result.get('summary', ''))[:500]  # 500文字まで
            task_sheet.update_cell(row, result_col, result_text)
        
        # エラーメッセージを記録（例：G列 = 7）
        if error_message:
            error_col = 7
            task_sheet.update_cell(row, error_col, error_message[:500])
        
        # 出力ファイルパスを記録（例：H列 = 8）
        if output_file:
            output_col = 8
            task_sheet.update_cell(row, output_col, output_file)
        
        print(f"✅ タスクID {task_id} の結果を書き込みました")
        return True
        
    except Exception as e:
        print(f"❌ Sheets書き込みエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def batch_update_task_statuses(
    self,
    updates: List[Dict]
) -> bool:
    """
    複数のタスクステータスを一括更新（効率化）
    
    Args:
        updates: 更新内容のリスト
            [
                {"task_id": "1", "status": "completed", "result": {...}},
                {"task_id": "2", "status": "failed", "error": "..."},
            ]
    
    Returns:
        bool: 成功したかどうか
    """
    try:
        self._ensure_client()
        sheet = self.gc.open_by_key(self.spreadsheet_id)
        task_sheet = sheet.worksheet("tasks")
        
        # バッチ更新用のリスト
        batch_data = []
        
        for update in updates:
            task_id = update.get("task_id")
            
            # タスクIDで行を検索
            cell = task_sheet.find(str(task_id))
            if not cell:
                continue
            
            row = cell.row
            
            # 更新データを準備
            batch_data.append({
                "range": f"D{row}",  # ステータス列
                "values": [[update.get("status", "unknown")]]
            })
            
            # タイムスタンプ
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            batch_data.append({
                "range": f"E{row}",
                "values": [[timestamp]]
            })
        
        # バッチ更新実行
        if batch_data:
            task_sheet.batch_update(batch_data)
            print(f"✅ {len(updates)}件のタスクを一括更新しました")
        
        return True
        
    except Exception as e:
        print(f"❌ バッチ更新エラー: {e}")
        return False


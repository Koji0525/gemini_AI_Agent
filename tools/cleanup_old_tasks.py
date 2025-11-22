"""
古いタスクのクリーンアップ
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager

def cleanup_old_tasks():
    """古い不完全タスクをクリーンアップ"""
    sheets = GoogleSheetsManager()
    
    # タスクを取得
    result = sheets.service.spreadsheets().values().get(
        spreadsheetId=sheets.spreadsheet_id,
        range="pm_tasks!A2:M1000"
    ).execute()
    
    values = result.get('values', [])
    
    print("🔍 古いタスクを検索中...")
    print()
    
    tasks_to_fix = []
    for i, row in enumerate(values, 2):
        if len(row) < 5:
            continue
        
        task_id = row[0]
        status = row[4] if len(row) > 4 else ''
        
        # 不完全なタスクIDを検出
        if status == 'pending' and len(task_id) <= 5:
            tasks_to_fix.append({
                'row_index': i,
                'task_id': task_id,
                'status': status
            })
    
    if not tasks_to_fix:
        print("✅ クリーンアップ不要です")
        return
    
    print(f"⚠️  {len(tasks_to_fix)}個の不完全タスクを発見:")
    for task in tasks_to_fix:
        print(f"  - 行{task['row_index']}: {task['task_id']}")
    
    print()
    response = input("これらのタスクをskippedに変更しますか？ [y/N] ")
    
    if response.lower() == 'y':
        for task in tasks_to_fix:
            sheets.service.spreadsheets().values().update(
                spreadsheetId=sheets.spreadsheet_id,
                range=f"pm_tasks!E{task['row_index']}",
                valueInputOption="RAW",
                body={"values": [["skipped"]]}
            ).execute()
            print(f"✅ 更新: {task['task_id']} → skipped")
        
        print(f"\n✅ {len(tasks_to_fix)}個のタスクをクリーンアップしました")
    else:
        print("キャンセルしました")

if __name__ == "__main__":
    cleanup_old_tasks()


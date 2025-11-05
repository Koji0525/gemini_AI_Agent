"""
スプレッドシートの不正データをクリーンアップ
125行目以降の不正なpm_tasksデータを削除
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
from configuration.spreadsheet_schema import PM_TASKS_SCHEMA

def cleanup_pm_tasks():
    """pm_tasksシートの不正データをクリーンアップ"""
    print("🧹 pm_tasksシートのクリーンアップ開始...")
    
    sheets = GoogleSheetsManager()
    
    if not sheets.authenticated:
        print("⚠️ ダミーモードのため、クリーンアップはスキップします")
        return
    
    # 全データを読み込み
    all_data = sheets.read_sheet("pm_tasks")
    
    print(f"  現在の行数: {len(all_data)}行")
    
    # 正しいデータのみを抽出
    valid_data = []
    invalid_count = 0
    
    for i, row in enumerate(all_data, start=2):  # ヘッダーを除く
        # 列数チェック
        if len(row) != PM_TASKS_SCHEMA["total_columns"]:
            print(f"  ⚠️ {i}行目: 列数不正（{len(row)}列）- スキップ")
            invalid_count += 1
            continue
        
        # 必須フィールドチェック
        if not row[0]:  # task_id
            print(f"  ⚠️ {i}行目: task_id空欄 - スキップ")
            invalid_count += 1
            continue
        
        if not row[2]:  # description
            print(f"  ⚠️ {i}行目: description空欄 - スキップ")
            invalid_count += 1
            continue
        
        valid_data.append(row)
    
    print(f"  削除対象: {invalid_count}行")
    print(f"  保持: {len(valid_data)}行")
    
    # ここでは実際の削除は行わず、レポートのみ
    print("✅ クリーンアップ診断完了")
    
    return {
        "total": len(all_data),
        "valid": len(valid_data),
        "invalid": invalid_count
    }

if __name__ == "__main__":
    result = cleanup_pm_tasks()
    print(f"\n📊 結果:")
    print(f"  総行数: {result['total']}")
    print(f"  有効: {result['valid']}")
    print(f"  無効: {result['invalid']}")


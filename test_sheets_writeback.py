#!/usr/bin/env python3
"""
Google Sheets 結果書き戻しテスト
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from tools.sheets_manager import GoogleSheetsManager

def test_writeback():
    print("\n🧪 Sheets書き戻しテスト")
    print("="*70)
    
    # SheetsManager初期化
    sheets_manager = GoogleSheetsManager(
        service_account_file="configuration/service_account.json",
        spreadsheet_id="YOUR_SPREADSHEET_ID"  # 実際のIDに変更
    )
    
    # テストデータ
    test_task_id = "TEST_001"
    
    print(f"\n📝 テストタスクID: {test_task_id}")
    
    # 1. 実行中に更新
    print("\n[1/3] 実行中ステータス更新...")
    success = sheets_manager.update_task_status(
        task_id=test_task_id,
        status="in_progress"
    )
    print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # 2. 完了に更新
    print("\n[2/3] 完了ステータス更新...")
    success = sheets_manager.update_task_status(
        task_id=test_task_id,
        status="completed",
        result={
            "summary": "テスト実行が完了しました",
            "details": "5,532文字のレスポンスを取得"
        },
        output_file="agent_outputs/test/test_result.md"
    )
    print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # 3. エラー時の更新
    print("\n[3/3] エラーステータス更新...")
    success = sheets_manager.update_task_status(
        task_id=test_task_id,
        status="failed",
        error_message="テスト用のエラーメッセージ"
    )
    print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    print("\n" + "="*70)
    print("✅ テスト完了")
    print("="*70)
    print("\nスプレッドシートを確認してください：")
    print(f"  https://docs.google.com/spreadsheets/d/{sheets_manager.spreadsheet_id}")

if __name__ == "__main__":
    test_writeback()


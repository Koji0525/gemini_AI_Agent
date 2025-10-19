#!/usr/bin/env python3
"""ログシートの構造を確認"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from tools.sheets_manager_with_logging import GoogleSheetsManager
from configuration.config_loader import get_spreadsheet_id, get_service_account_file

def check_log_sheet():
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    try:
        spreadsheet = sheets.gc.open_by_key(get_spreadsheet_id())
        log_sheet = spreadsheet.worksheet('task_execution_log')
        
        # ヘッダー確認
        headers = log_sheet.row_values(1)
        print("📋 task_execution_log ヘッダー:")
        for i, header in enumerate(headers, 1):
            print(f"  {i}. {header}")
        
        # データ確認（最新5件）
        records = log_sheet.get_all_records()
        print(f"\n📊 最新のログ記録 ({len(records)}件):")
        for i, record in enumerate(records[-5:], 1):
            print(f"  {i}. タスク{record.get('task_id', '')} - 品質: {record.get('quality_score', 'N/A')}/10")
            if record.get('quality_evaluation'):
                print(f"     評価: {record.get('quality_evaluation')[:50]}...")
        
        # I列（品質スコア）の確認
        if len(headers) >= 9:
            print(f"\n✅ I列(9列目)は '{headers[8]}' です - 品質スコアが記録されます")
        else:
            print(f"\n⚠️  列数不足: {len(headers)}列 (9列以上必要)")
            
    except Exception as e:
        print(f"❌ ログシート確認エラー: {e}")
        print("💡 task_execution_logシートが存在しない場合は自動的に作成されます")

if __name__ == "__main__":
    check_log_log()


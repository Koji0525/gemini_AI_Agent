#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "📋 Google Sheets 構造確認"
echo "=========================================="

# 設定読み込み
if [ ! -f ".env" ]; then
    echo "❌ .env が見つかりません"
    exit 1
fi

source .env

echo ""
echo "設定:"
echo "  スプレッドシートID: $SPREADSHEET_ID"
echo ""

# Pythonで確認
python3 << 'PYTEST'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from configuration.config_loader import get_spreadsheet_id, get_service_account_file
from tools.sheets_manager import GoogleSheetsManager

def verify_structure():
    print("\n" + "="*70)
    print("📋 構造確認")
    print("="*70)
    
    sheet_id = get_spreadsheet_id()
    sa_file = get_service_account_file()
    
    print(f"\n[1/4] 接続テスト...")
    try:
        sheets = GoogleSheetsManager(
            spreadsheet_id=sheet_id,
            service_account_file=sa_file
        )
        print("✅ 接続成功")
    except Exception as e:
        print(f"❌ 接続失敗: {e}")
        return False
    
    print(f"\n[2/4] スプレッドシート情報取得...")
    try:
        import gspread
        gc = sheets.gc
        spreadsheet = gc.open_by_key(sheet_id)
        
        print(f"✅ スプレッドシート名: {spreadsheet.title}")
        print(f"   URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print("\n考えられる原因:")
        print("  1. スプレッドシートIDが間違っている")
        print("  2. サービスアカウントに共有されていない")
        print("\n対策:")
        print("  1. スプレッドシートのURLを確認")
        print("  2. スプレッドシートを開く")
        print("  3. 右上の「共有」をクリック")
        print("  4. サービスアカウントのメールアドレスを追加")
        print("     （service_account.json の client_email）")
        print("  5. 権限を「編集者」に設定")
        return False
    
    print(f"\n[3/4] シート一覧...")
    try:
        worksheets = spreadsheet.worksheets()
        print(f"✅ 見つかったシート:")
        
        has_tasks = False
        for ws in worksheets:
            print(f"   - {ws.title}")
            if ws.title.lower() == "tasks":
                has_tasks = True
        
        if not has_tasks:
            print("\n⚠️  'tasks' シートが見つかりません")
            print("\n次のステップ:")
            print("  1. スプレッドシートを開く")
            print("  2. 左下のシート名を 'tasks' に変更")
            print("     または新しいシートを追加して 'tasks' と命名")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    print(f"\n[4/4] tasksシートの構造確認...")
    try:
        task_sheet = spreadsheet.worksheet("tasks")
        
        # ヘッダー行を取得
        headers = task_sheet.row_values(1)
        
        print(f"✅ 列数: {len(headers)}")
        print(f"   ヘッダー: {headers}")
        
        # 必要な列
        required = ['id', 'title', 'prompt', 'status']
        missing = []
        
        headers_lower = [h.lower() for h in headers]
        
        for req in required:
            if req not in headers_lower:
                missing.append(req)
        
        if missing:
            print(f"\n⚠️  不足している列: {missing}")
            print("\n推奨される列構成:")
            print("  A列: id")
            print("  B列: title")
            print("  C列: prompt")
            print("  D列: status")
            print("  E列: timestamp")
            print("  F列: result")
            print("  G列: error")
            print("  H列: output_file")
            return False
        
        print(f"\n✅ 必須列が揃っています")
        
        # データ行数
        all_values = task_sheet.get_all_values()
        data_rows = len(all_values) - 1  # ヘッダーを除く
        
        print(f"   データ行数: {data_rows}")
        
        if data_rows == 0:
            print("\n⚠️  データがありません")
            print("\nテストデータを追加してください:")
            print("  A2: TEST001")
            print("  B2: テストタスク")
            print("  C2: Please write a 2-sentence summary about AI.")
            print("  D2: pending")
            return False
        
        print("\n" + "="*70)
        print("🎊 構造確認完了！すべて正常です")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

result = verify_structure()

if result:
    print("\n次のステップ:")
    print("  ./test_sheets_integration_fixed.sh")
else:
    print("\n上記の問題を解決してから再実行してください")

PYTEST

echo ""
echo "=========================================="
echo "✅ 確認完了"
echo "=========================================="


#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🚀 完全統合システム実行"
echo "=========================================="

# ====================================================================
# STEP 1: 前提条件の確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/4] 前提条件確認${NC}"
echo "=========================================="

# Xvfb
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "⚠️  Xvfb起動中..."
    ./setup_xvfb.sh
fi
echo "✅ Xvfb起動中"

# .env
if [ ! -f ".env" ]; then
    echo "❌ .env が見つかりません"
    exit 1
fi
echo "✅ .env 確認"

# service_account.json
if [ ! -f "configuration/service_account.json" ]; then
    echo "❌ service_account.json が見つかりません"
    exit 1
fi
echo "✅ service_account.json 確認"

export DISPLAY=:1

# ====================================================================
# STEP 2: pm_tasks シートの存在確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/4] pm_tasks シート確認${NC}"
echo "=========================================="

python3 << 'CHECK_PM_TASKS'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from configuration.config_loader import get_spreadsheet_id, get_service_account_file
from tools.sheets_manager import GoogleSheetsManager

sheet_id = get_spreadsheet_id()
sheets = GoogleSheetsManager(
    spreadsheet_id=sheet_id,
    service_account_file=get_service_account_file()
)

import gspread
spreadsheet = sheets.gc.open_by_key(sheet_id)
worksheet_names = [ws.title for ws in spreadsheet.worksheets()]

print(f"スプレッドシート内のシート:")
for name in worksheet_names:
    print(f"  - {name}")

if 'pm_tasks' in worksheet_names:
    print("\n✅ pm_tasks シートが存在します")
    
    # データ確認
    pm_sheet = spreadsheet.worksheet('pm_tasks')
    headers = pm_sheet.row_values(1)
    all_data = pm_sheet.get_all_values()
    
    print(f"   列: {headers}")
    print(f"   データ行数: {len(all_data) - 1}")
    
    sys.exit(0)
elif 'tasks' in worksheet_names:
    print("\n✅ tasks シートが存在します")
    sys.exit(0)
else:
    print("\n⚠️  pm_tasks も tasks も見つかりません")
    print("\n次のいずれかを実行してください:")
    print("  1. Google Sheetsで新しいシート 'tasks' を作成")
    print("  2. または 'pm_tasks' を作成")
    sys.exit(1)

CHECK_PM_TASKS

if [ $? -ne 0 ]; then
    echo ""
    echo "シート作成が必要です"
    echo "続行しますか？ (シートを手動で作成してからy) (y/n)"
    read -p "> " continue_setup
    
    if [ "$continue_setup" != "y" ]; then
        echo "中止しました"
        exit 0
    fi
fi

# ====================================================================
# STEP 3: get_tasks メソッドを pm_tasks 対応に修正
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/4] get_tasks を柔軟に修正${NC}"
echo "=========================================="

python3 << 'UPDATE_GET_TASKS'
# get_tasksメソッドを'tasks'と'pm_tasks'の両方に対応させる

with open("tools/sheets_manager.py", "r", encoding="utf-8") as f:
    content = f.read()

# 既存のget_tasksを探す
if "def get_tasks" in content:
    print("📝 get_tasks メソッドを柔軟版に更新中...")
    
    # 柔軟版のメソッド
    new_method = '''
    def get_tasks(self, sheet_name: str = None) -> list:
        """
        Sheetsからタスク一覧を取得（柔軟版）
        
        Args:
            sheet_name: シート名（None の場合は 'pm_tasks' → 'tasks' の順で探す）
        
        Returns:
            list: タスクのリスト（辞書形式）
        """
        try:
            self._ensure_client()
            
            # スプレッドシートを開く
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # シート名が指定されていない場合、自動検索
            if sheet_name is None:
                worksheet_names = [ws.title for ws in sheet.worksheets()]
                
                if 'pm_tasks' in worksheet_names:
                    sheet_name = 'pm_tasks'
                    print(f"✅ 'pm_tasks' シートを使用します")
                elif 'tasks' in worksheet_names:
                    sheet_name = 'tasks'
                    print(f"✅ 'tasks' シートを使用します")
                else:
                    print("⚠️  'pm_tasks' も 'tasks' も見つかりません")
                    return []
            
            # シート取得
            try:
                task_sheet = sheet.worksheet(sheet_name)
            except Exception:
                print(f"⚠️  '{sheet_name}' シートが見つかりません")
                return []
            
            # 全データを取得
            all_values = task_sheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                print("⚠️  データが見つかりません")
                return []
            
            # ヘッダー行（1行目）
            headers = all_values[0]
            
            # データ行（2行目以降）
            tasks = []
            for row in all_values[1:]:
                if not row or not row[0]:  # 空行をスキップ
                    continue
                
                task = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        task[header.lower()] = row[i]
                
                tasks.append(task)
            
            print(f"✅ {len(tasks)}件のタスクを取得しました（シート: {sheet_name}）")
            return tasks
            
        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return []
'''
    
    # 既存のget_tasksを置換
    import re
    pattern = r'    def get_tasks\(self.*?\n(?=    def |class |\Z)'
    content = re.sub(pattern, new_method + '\n', content, flags=re.DOTALL)
    
    with open("tools/sheets_manager.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ get_tasks を柔軟版に更新しました")
else:
    print("⚠️  get_tasks メソッドが見つかりません")

UPDATE_GET_TASKS

# ====================================================================
# STEP 4: 統合テスト実行
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 4/4] 統合テスト実行${NC}"
echo "=========================================="

DISPLAY=:1 python3 << 'INTEGRATION_TEST'
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.cwd()))

from configuration.config_loader import get_spreadsheet_id, get_service_account_file
from browser_control.browser_controller import BrowserController
from tools.sheets_manager import GoogleSheetsManager

async def run_integration():
    print("\n" + "="*70)
    print("🚀 完全統合システム実行")
    print("="*70)
    
    # [1/6] SheetsManager初期化
    print("\n[1/6] SheetsManager初期化...")
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    print("✅ 初期化完了")
    
    # [2/6] タスク取得
    print("\n[2/6] タスク取得...")
    tasks = sheets.get_tasks()  # 自動で pm_tasks または tasks を探す
    
    if not tasks:
        print("❌ タスクが見つかりません")
        return False
    
    print(f"✅ {len(tasks)}件のタスク取得")
    
    # pending タスクを抽出
    pending = [t for t in tasks if t.get('status', '').lower() in ['pending', '']]
    
    if not pending:
        print("⚠️  pending タスクがありません")
        print("\nすべてのタスク:")
        for i, t in enumerate(tasks[:3], 1):
            print(f"  {i}. {t.get('id')}: {t.get('title', 'No title')} (status: {t.get('status')})")
        return False
    
    print(f"   うち pending: {len(pending)}件")
    
    # [3/6] BrowserController初期化
    print("\n[3/6] BrowserController初期化...")
    async with BrowserController(download_folder="./downloads") as browser:
        print("✅ ブラウザ初期化完了")
        
        # Geminiアクセス
        logged_in = await browser.navigate_to_gemini()
        if not logged_in:
            print("❌ Gemini接続失敗")
            return False
        
        print("✅ Gemini準備完了")
        
        # [4/6] 最初のタスク実行
        task = pending[0]
        task_id = task.get('id')
        
        print(f"\n[4/6] タスク実行: {task.get('title', 'No title')}")
        print(f"   ID: {task_id}")
        print(f"   プロンプト: {task.get('prompt', 'No prompt')[:80]}...")
        
        # ステータス更新: in_progress
        sheets.update_task_status(
            task_id=task_id,
            status="in_progress"
        )
        
        # プロンプト送信
        print("\n[5/6] Gemini実行...")
        await browser.send_prompt(task.get('prompt', ''))
        await browser.wait_for_text_generation(max_wait=90)
        response = await browser.extract_latest_text_response()
        
        if response and len(response) > 50:
            print(f"✅ レスポンス: {len(response)} 文字")
            
            # ファイル保存
            output_dir = Path("agent_outputs/integration")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = output_dir / f"{task_id}_{timestamp}.md"
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {task.get('title')}\n\n")
                f.write(f"**ID**: {task_id}\n")
                f.write(f"**文字数**: {len(response)}\n\n")
                f.write("---\n\n")
                f.write(response)
            
            print(f"💾 保存: {filepath}")
            
            # [6/6] ステータス更新: completed
            print("\n[6/6] ステータス更新...")
            sheets.update_task_status(
                task_id=task_id,
                status="completed",
                result={"summary": f"{len(response)}文字取得"},
                output_file=str(filepath)
            )
            
            print("\n" + "="*70)
            print("🎊🎊🎊 完全統合テスト成功！ 🎊🎊🎊")
            print("="*70)
            print(f"\n📋 Google Sheetsを確認:")
            print(f"   https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")
            print(f"\n✅ タスク {task_id} が completed になっているはず")
            print("="*70)
            return True
        else:
            print("❌ レスポンス取得失敗")
            sheets.update_task_status(
                task_id=task_id,
                status="failed",
                error_message="レスポンス取得失敗"
            )
            return False

asyncio.run(run_integration())

INTEGRATION_TEST

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 統合テスト完了${NC}"
echo "=========================================="


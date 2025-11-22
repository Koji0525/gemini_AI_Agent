#!/bin/bash
# pendingタスク実行スクリプト v3
# ステータス更新を確実に実行

cd /workspaces/gemini_AI_Agent

# デフォルト値
LIMIT=1
AUTO_YES=false

# 引数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        -y|--yes)
            AUTO_YES=true
            shift
            ;;
        *)
            echo "不明なオプション: $1"
            exit 1
            ;;
    esac
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 pendingタスク実行 v3（ステータス更新対応）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# F1: タスク可用性チェック
python3 agents/f1_loop_integration.py
F1_RESULT=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 スマートタスク選択"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# スマートタスク選択
python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
from agents.smart_task_selector import SmartTaskSelector

sheets = GoogleSheetsManager()
selector = SmartTaskSelector(sheets)

selected_tasks = selector.select_executable_task(limit=$LIMIT)

if not selected_tasks:
    print("\n⚠️  実行可能なタスクがありません")
    sys.exit(1)

# タスクIDを保存
with open('/tmp/selected_task_ids.txt', 'w') as f:
    for task in selected_tasks:
        f.write(f"{task['task_id']}\n")

print(f"\n✅ {len(selected_tasks)}個のタスクを選択しました")
PYTHON

if [ $? -ne 0 ]; then
    echo "❌ タスク選択に失敗しました"
    exit 1
fi

# 選択されたタスクIDを読み込み
TASK_IDS=$(cat /tmp/selected_task_ids.txt)

if [ -z "$TASK_IDS" ]; then
    echo "❌ 選択されたタスクがありません"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 タスク実行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 確認
if [ "$AUTO_YES" = false ]; then
    echo "【実行するタスク】"
    echo "$TASK_IDS"
    echo ""
    read -p "これらのタスクを実行しますか？ [y/N] " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "キャンセルしました"
        exit 0
    fi
fi

# タスク実行（ステータス更新を確実に実行）
python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.complete_engine_ultimate import CompleteEngineUltimate
from tools.sheets_manager import GoogleSheetsManager
from tools.base_data_accessor import BaseDataAccessor

sheets = GoogleSheetsManager()
accessor = BaseDataAccessor(sheets)
engine = CompleteEngineUltimate()

# タスクIDを読み込み
with open('/tmp/selected_task_ids.txt', 'r') as f:
    task_ids = [line.strip() for line in f if line.strip()]

success_count = 0
for task_id in task_ids:
    print(f"\n{'=' * 80}")
    print(f"🚀 タスク実行: {task_id}")
    print('=' * 80)
    
    # タスクデータを取得
    result = sheets.service.spreadsheets().values().get(
        spreadsheetId=sheets.spreadsheet_id,
        range="pm_tasks!A2:Z1000"
    ).execute()
    
    values = result.get('values', [])
    task_data = None
    row_index = None
    
    for i, row in enumerate(values, 2):  # 2行目から開始
        if len(row) > 0 and row[0] == task_id:
            task_data = {
                'task_id': row[0],
                'parent_goal_id': row[1] if len(row) > 1 else '',
                'description': row[2] if len(row) > 2 else '',
                'required_role': row[3] if len(row) > 3 else '',
                'status': row[4] if len(row) > 4 else '',
                'priority': row[5] if len(row) > 5 else '',
                'execution_type': row[12] if len(row) > 12 else 'implementation'
            }
            row_index = i
            break
    
    if not task_data:
        print(f"❌ タスクデータが見つかりません: {task_id}")
        continue
    
    try:
        # タスク実行
        result = engine.execute_task(task_data)
        
        # ステータス更新を確実に実行
        if result.get('status') == 'completed' or result.get('success'):
            print(f"\n📝 ステータスを更新中: {task_id}")
            
            # Google Sheets のステータスを直接更新
            update_range = f"pm_tasks!E{row_index}"  # E列がstatus列
            sheets.service.spreadsheets().values().update(
                spreadsheetId=sheets.spreadsheet_id,
                range=update_range,
                valueInputOption="RAW",
                body={"values": [["completed"]]}
            ).execute()
            
            print(f"✅ ステータス更新完了: {task_id} → completed")
            print(f"   更新位置: {update_range}")
            success_count += 1
        else:
            print(f"⚠️  タスク実行に問題: {task_id}")
            print(f"   結果: {result}")
    
    except Exception as e:
        print(f"❌ タスク実行エラー: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 80}")
print(f"✅ 実行完了: {success_count}/{len(task_ids)}件成功")
print('=' * 80)

# 更新確認
print("\n【ステータス確認】")
result = sheets.service.spreadsheets().values().get(
    spreadsheetId=sheets.spreadsheet_id,
    range="pm_tasks!A2:Z1000"
).execute()

values = result.get('values', [])
for task_id in task_ids:
    for row in values:
        if len(row) > 0 and row[0] == task_id:
            status = row[4] if len(row) > 4 else 'unknown'
            print(f"  {task_id}: {status}")
            break

PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ タスク実行完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""


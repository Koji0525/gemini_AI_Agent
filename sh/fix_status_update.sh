#!/bin/bash
# ステータス更新が抜けている問題を修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ステータス更新の修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# 原因調査
echo "【原因】"
echo "  start_pending_tasks_v2.sh で engine.execute_task() を直接呼び出し"
echo "  → execute_task() の戻り値を確認するだけ"
echo "  → ステータス更新の処理が抜けている"
echo ""
echo "【元の動作】"
echo "  CompleteEngine.run_full_integration_cycle() を使用"
echo "  → 内部で update_task_status() を呼び出し"
echo "  → Google Sheets のステータスを completed に更新"
echo ""

# 修正版を作成
cat > start_pending_tasks_v3.sh << 'START'
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

START

chmod +x start_pending_tasks_v3.sh
echo "✅ start_pending_tasks_v3作成（ステータス更新対応）"

# 既存のv2を置き換え
cp start_pending_tasks_v2.sh "start_pending_tasks_v2.sh.backup_${NOW_JST}"
cp start_pending_tasks_v3.sh start_pending_tasks_v2.sh

echo "✅ start_pending_tasks_v2.sh を更新版に置き換え"

# 24時間稼働スクリプトも更新（念のため）
echo ""
echo "📝 24時間稼働スクリプトの確認..."

if grep -q "start_pending_tasks_v2.sh" sh/run_autonomous_24h_v4.sh; then
    echo "✅ 既にv2スクリプトを使用（ステータス更新が含まれます）"
else
    echo "⚠️  古いスクリプトを使用している可能性"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【修正内容】"
echo "  1. ✅ ステータス更新を明示的に実行"
echo "  2. ✅ Google Sheets APIで直接更新"
echo "  3. ✅ 更新位置（E列）を正確に指定"
echo "  4. ✅ 更新確認処理を追加"
echo ""
echo "【原因】"
echo "  ❌ v2スクリプトで execute_task() のみ呼び出し"
echo "  ❌ ステータス更新の処理が抜けていた"
echo ""
echo "【解決】"
echo "  ✅ sheets.service.spreadsheets().values().update() で直接更新"
echo "  ✅ 更新後に確認処理を実行"
echo ""
echo "🎯 テスト実行:"
echo "  bash start_pending_tasks_v2.sh --limit 1"
echo ""
echo "📊 ステータス確認:"
echo "  実行後、Google Sheets の pm_tasks シートでステータスを確認"
echo ""


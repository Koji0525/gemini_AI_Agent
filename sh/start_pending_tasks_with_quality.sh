#!/bin/bash
# 品質保証付きタスク実行

cd /workspaces/gemini_AI_Agent

LIMIT=${1:-2}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 品質保証付きタスク実行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "実行タスク数: $LIMIT"
echo ""

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.robust_task_selector import RobustTaskSelector
from core_agents.quality_feedback_loop_v2 import QualityFeedbackLoopV2
from tools.sheets_manager import GoogleSheetsManager

# 初期化
sheets = GoogleSheetsManager()
selector = RobustTaskSelector(sheets)
qfl = QualityFeedbackLoopV2()

# タスク選択
tasks = selector.select_executable_task(limit=$LIMIT)

if not tasks:
    print("⚠️  実行可能なタスクがありません")
    sys.exit(0)

print(f"✅ {len(tasks)}個のタスクを選択しました")
for i, task in enumerate(tasks, 1):
    print(f"  {i}. {task['task_id']}")

print()

# タスク実行（品質保証付き）
success_count = 0
for task in tasks:
    print("\n" + "=" * 80)
    print(f"🚀 タスク実行: {task['task_id']}")
    print("=" * 80)
    
    try:
        # QualityFeedbackLoopで実行
        result = qfl.execute_with_quality_assurance(task)
        
        if result['success']:
            print(f"\n✅ タスク成功: {task['task_id']}")
            print(f"   品質スコア: {result['score']:.1f}/10点")
            print(f"   リトライ回数: {result['retry_count']}")
            print(f"   成果物: {result['output_path']}")
            
            # ステータス更新
            row_index = task['row_index']
            sheets.service.spreadsheets().values().update(
                spreadsheetId=sheets.spreadsheet_id,
                range=f"pm_tasks!E{row_index}",
                valueInputOption="RAW",
                body={"values": [["completed"]]}
            ).execute()
            
            success_count += 1
        else:
            print(f"\n❌ タスク失敗: {task['task_id']}")
            print(f"   理由: {result.get('reason', '不明')}")
            
    except Exception as e:
        print(f"\n❌ タスク実行エラー: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print(f"✅ 実行完了: {success_count}/{len(tasks)}件成功")
print("=" * 80)

PYTHON


#!/bin/bash
# 列構造認識エラーの緊急修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚨 緊急修正：列構造認識エラー"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# 問題の確認
echo "【発見された問題】"
echo "  ❌ 列構造: ['task_id', 'parent_goal_id', 'description', 'required_role', '', 'priority', ...]"
echo "  ❌ インデックス4（status列）が空文字 ''"
echo "  ❌ そのため、status='pending'の判定ができない"
echo "  ❌ 結果：「pendingタスクはありません」と誤判定"
echo ""
echo "【実際の状況】"
echo "  ✅ スプレッドシート上にはpendingタスクが存在"
echo "  ✅ 画像では312行目に「pending」タスクが見える"
echo "  ✅ しかしプログラムが読み取れていない"
echo ""

# 原因調査
python3 << 'PYTHON'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager

print("【原因調査】")
print()

sheets = GoogleSheetsManager()

# ヘッダー行を読み取り
result = sheets.service.spreadsheets().values().get(
    spreadsheetId=sheets.spreadsheet_id,
    range="pm_tasks!A1:M1"
).execute()

header = result.get('values', [[]])[0]
print(f"ヘッダー行: {header}")
print(f"ヘッダー長: {len(header)}")
print()

# 各列を確認
for i, col in enumerate(header):
    print(f"  列{i}: '{col}'")

print()
print("【問題】")
if len(header) > 4:
    if header[4] == '' or header[4] is None:
        print(f"  ❌ 列4（E列）が空: '{header[4]}'")
        print(f"  ❌ 'status'列が認識されていない")
    else:
        print(f"  ✅ 列4（E列）: '{header[4]}'")
else:
    print(f"  ❌ ヘッダーが不完全（列数: {len(header)}）")

# データ行も確認
print()
print("【データ行の確認（最初の3行）】")
result = sheets.service.spreadsheets().values().get(
    spreadsheetId=sheets.spreadsheet_id,
    range="pm_tasks!A2:M4"
).execute()

values = result.get('values', [])
for i, row in enumerate(values, 2):
    print(f"\n行{i}:")
    if len(row) > 4:
        print(f"  task_id: {row[0]}")
        print(f"  status（列4）: '{row[4] if len(row) > 4 else 'なし'}'")
    else:
        print(f"  列数不足: {len(row)}列")

PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 修正方法の決定"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 修正版のタスク選択スクリプトを作成
cat > agents/robust_task_selector.py << 'PYTHON'
"""
ロバストタスク選択エージェント
列名に依存せず、列インデックスで直接アクセス
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from typing import List, Dict, Any

class RobustTaskSelector:
    """ロバストタスク選択エージェント"""
    
    # 列インデックスの定義（固定）
    COL_TASK_ID = 0
    COL_PARENT_GOAL_ID = 1
    COL_DESCRIPTION = 2
    COL_REQUIRED_ROLE = 3
    COL_STATUS = 4  # E列
    COL_PRIORITY = 5
    COL_ESTIMATED_TIME = 6
    COL_DEPENDENCIES = 7
    COL_CREATED_AT = 8
    COL_BATCH_ID = 9
    COL_DETAIL_FILE_PATH = 10
    COL_BLANK = 11
    COL_EXECUTION_TYPE = 12
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """pendingタスクを取得（列インデックスで直接アクセス）"""
        try:
            # データ行を取得（A2:M1000）
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range="pm_tasks!A2:M1000"
            ).execute()
            
            values = result.get('values', [])
            
            pending_tasks = []
            for i, row in enumerate(values, 2):  # 2行目から開始
                # 列数が不足している場合はスキップ
                if len(row) < 5:
                    continue
                
                # status列を取得（列インデックス4）
                status = row[self.COL_STATUS] if len(row) > self.COL_STATUS else ''
                
                # デバッグ出力（最初の3行のみ）
                if i <= 4:
                    task_id = row[self.COL_TASK_ID] if len(row) > self.COL_TASK_ID else ''
                    print(f"  行{i}: task_id='{task_id}', status='{status}'")
                
                # status='pending'のみを追加
                if status == 'pending':
                    task = {
                        'row_index': i,
                        'task_id': row[self.COL_TASK_ID] if len(row) > self.COL_TASK_ID else '',
                        'parent_goal_id': row[self.COL_PARENT_GOAL_ID] if len(row) > self.COL_PARENT_GOAL_ID else '',
                        'description': row[self.COL_DESCRIPTION] if len(row) > self.COL_DESCRIPTION else '',
                        'required_role': row[self.COL_REQUIRED_ROLE] if len(row) > self.COL_REQUIRED_ROLE else '',
                        'status': status,
                        'priority': row[self.COL_PRIORITY] if len(row) > self.COL_PRIORITY else 'medium',
                        'estimated_time': row[self.COL_ESTIMATED_TIME] if len(row) > self.COL_ESTIMATED_TIME else '1h',
                        'dependencies': row[self.COL_DEPENDENCIES] if len(row) > self.COL_DEPENDENCIES else '',
                        'created_at': row[self.COL_CREATED_AT] if len(row) > self.COL_CREATED_AT else '',
                        'batch_id': row[self.COL_BATCH_ID] if len(row) > self.COL_BATCH_ID else '',
                        'execution_type': row[self.COL_EXECUTION_TYPE] if len(row) > self.COL_EXECUTION_TYPE else 'implementation'
                    }
                    pending_tasks.append(task)
            
            print(f"\n📋 pendingタスク: {len(pending_tasks)}個")
            
            # pendingタスクの詳細を表示
            if pending_tasks:
                print("\n【pendingタスク一覧】")
                for i, task in enumerate(pending_tasks[:5], 1):
                    print(f"  {i}. {task['task_id']}")
                    print(f"     行: {task['row_index']}, 優先度: {task['priority']}")
            
            return pending_tasks
            
        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def select_executable_task(self, limit: int = 1) -> List[Dict[str, Any]]:
        """実行可能なタスクを選択"""
        print("━" * 60)
        print("🔍 pendingタスク検索（ロバスト版）")
        print("━" * 60)
        print()
        
        pending_tasks = self.get_pending_tasks()
        
        if not pending_tasks:
            print("\n⚠️  実行可能なpendingタスクがありません")
            return []
        
        # 優先度でソート（高→中→低）
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_tasks = sorted(
            pending_tasks,
            key=lambda t: (
                priority_order.get(t.get('priority', 'medium'), 2),
                1000 if 'auto_quality' in t.get('batch_id', '') else 0
            ),
            reverse=True
        )
        
        selected = sorted_tasks[:limit]
        
        print(f"\n✅ {len(selected)}個のタスクを選択しました")
        for i, task in enumerate(selected, 1):
            print(f"  {i}. {task['task_id']}")
        
        return selected

def main():
    """テスト実行"""
    from tools.sheets_manager import GoogleSheetsManager
    
    sheets = GoogleSheetsManager()
    selector = RobustTaskSelector(sheets)
    
    tasks = selector.get_pending_tasks()
    print(f"\n結果: {len(tasks)}個のpendingタスクを発見")
    
    return 0 if tasks else 1

if __name__ == "__main__":
    sys.exit(main())

PYTHON

echo "✅ ロバストタスク選択エージェント作成"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 動作確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 agents/robust_task_selector.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 start_pending_tasksの修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# start_pending_tasks.shを修正
cat > start_pending_tasks_fixed.sh << 'FIXED'
#!/bin/bash
# pendingタスク実行（修正版）
# 列インデックスで直接アクセス

cd /workspaces/gemini_AI_Agent

LIMIT=${1:-1}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 pendingタスク実行（修正版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
from agents.robust_task_selector import RobustTaskSelector
from agents.complete_engine_ultimate import CompleteEngineUltimate

sheets = GoogleSheetsManager()
selector = RobustTaskSelector(sheets)
engine = CompleteEngineUltimate()

# タスク選択
selected_tasks = selector.select_executable_task(limit=${LIMIT})

if not selected_tasks:
    print("\n⚠️  実行可能なタスクがありません")
    sys.exit(1)

# タスク実行
success_count = 0
for task in selected_tasks:
    print(f"\n{'=' * 80}")
    print(f"�� タスク実行: {task['task_id']}")
    print('=' * 80)
    
    try:
        result = engine.execute_task(task)
        
        if result.get('status') == 'completed':
            # ステータス更新
            row_index = task['row_index']
            update_range = f"pm_tasks!E{row_index}"
            
            sheets.service.spreadsheets().values().update(
                spreadsheetId=sheets.spreadsheet_id,
                range=update_range,
                valueInputOption="RAW",
                body={"values": [["completed"]]}
            ).execute()
            
            print(f"✅ 完了: {task['task_id']}")
            success_count += 1
    
    except Exception as e:
        print(f"❌ エラー: {e}")

print(f"\n✅ 実行完了: {success_count}/{len(selected_tasks)}件成功")

PYTHON

FIXED

chmod +x start_pending_tasks_fixed.sh

echo "✅ 修正版スクリプト作成: start_pending_tasks_fixed.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 緊急修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【問題の原因】"
echo "  ❌ 列名認識に依存していた"
echo "  ❌ status列が空文字として認識"
echo "  ❌ そのためpendingタスクを検出できず"
echo ""
echo "【解決方法】"
echo "  ✅ 列インデックスで直接アクセス"
echo "  ✅ COL_STATUS = 4 を固定使用"
echo "  ✅ 列名に依存しない実装"
echo ""
echo "🎯 テスト実行:"
echo "  bash start_pending_tasks_fixed.sh 1"
echo ""


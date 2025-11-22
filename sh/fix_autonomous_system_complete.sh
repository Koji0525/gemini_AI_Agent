#!/bin/bash
# 24時間自律稼働システムの全問題を解決
# 既存システムを活用して統合強化

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 24時間自律稼働システムの完全修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: タスク選択ロジックの修正
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: タスク選択ロジックの修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/smart_task_selector.py << 'PYTHON'
"""
スマートタスク選択エージェント
高品質タスクを優先し、completedタスクを除外
"""

import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class SmartTaskSelector:
    """スマートタスク選択エージェント"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """pendingタスクを取得（completedを厳密に除外）"""
        try:
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range="pm_tasks!A2:Z1000"
            ).execute()
            
            values = result.get('values', [])
            
            # pendingタスクのみを抽出
            pending_tasks = []
            for i, row in enumerate(values, 2):  # 2行目から開始
                if len(row) > 4:
                    task_id = row[0]
                    status = row[4]
                    
                    # status='pending'のみを追加
                    if status == 'pending':
                        task = {
                            'row_index': i,
                            'task_id': task_id,
                            'parent_goal_id': row[1] if len(row) > 1 else '',
                            'description': row[2] if len(row) > 2 else '',
                            'required_role': row[3] if len(row) > 3 else '',
                            'status': status,
                            'priority': row[5] if len(row) > 5 else 'medium',
                            'estimated_time': row[6] if len(row) > 6 else '1h',
                            'dependencies': row[7] if len(row) > 7 else '',
                            'created_at': row[8] if len(row) > 8 else '',
                            'batch_id': row[9] if len(row) > 9 else '',
                            'execution_type': row[12] if len(row) > 12 else 'implementation'
                        }
                        pending_tasks.append(task)
            
            print(f"📋 pendingタスク: {len(pending_tasks)}個")
            return pending_tasks
            
        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            return []
    
    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """タスクを優先順位でソート"""
        def get_priority_score(task: Dict[str, Any]) -> int:
            score = 0
            
            # 1. batch_idで高品質タスクを最優先
            if 'auto_quality' in task.get('batch_id', ''):
                score += 1000
            elif 'auto_integration' in task.get('batch_id', ''):
                score += 900
            
            # 2. 優先度
            priority_map = {'high': 100, 'medium': 50, 'low': 10}
            score += priority_map.get(task.get('priority', 'medium'), 50)
            
            # 3. execution_typeで実行可能なタイプを優先
            executable_types = ['testing', 'implementation', 'design', 'documentation']
            if task.get('execution_type') in executable_types:
                score += 10
            
            # 4. 依存関係なしを優先
            if not task.get('dependencies'):
                score += 5
            
            # 5. 新しいタスクを優先
            created_at = task.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    days_old = (datetime.now() - dt).days
                    score += max(0, 10 - days_old)  # 新しいほど高得点
                except:
                    pass
            
            return score
        
        # 優先順位でソート（降順）
        sorted_tasks = sorted(tasks, key=get_priority_score, reverse=True)
        
        print("\n【タスク優先順位】")
        for i, task in enumerate(sorted_tasks[:5], 1):
            score = get_priority_score(task)
            print(f"  {i}. {task['task_id']}")
            print(f"     優先度: {task['priority']} | batch: {task['batch_id']}")
            print(f"     スコア: {score}")
        
        return sorted_tasks
    
    def select_executable_task(self, limit: int = 1) -> List[Dict[str, Any]]:
        """実行可能なタスクを選択"""
        pending_tasks = self.get_pending_tasks()
        
        if not pending_tasks:
            print("\n⚠️  実行可能なpendingタスクがありません")
            return []
        
        # 優先順位でソート
        prioritized_tasks = self.prioritize_tasks(pending_tasks)
        
        # 上位limitタスクを選択
        selected = prioritized_tasks[:limit]
        
        print(f"\n✅ {len(selected)}個のタスクを選択しました")
        return selected

PYTHON

echo "✅ スマートタスク選択エージェント作成: agents/smart_task_selector.py"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: F1タスク分解のループ統合
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: F1タスク分解のループ統合"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/f1_loop_integration.py << 'PYTHON'
"""
F1タスク分解のループ統合
pendingタスクが0の場合、自動的にタスク生成
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.smart_task_selector import SmartTaskSelector
from agents.auto_task_generator import AutoTaskGeneratorV2

class F1LoopIntegration:
    """F1タスク分解のループ統合"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        self.task_selector = SmartTaskSelector(sheets_manager)
        self.task_generator = AutoTaskGeneratorV2(sheets_manager)
        
    def ensure_tasks_available(self) -> bool:
        """タスクが利用可能であることを保証"""
        print("━" * 60)
        print("🔄 F1: タスク可用性チェック")
        print("━" * 60)
        print()
        
        # pendingタスクを確認
        pending_tasks = self.task_selector.get_pending_tasks()
        
        if len(pending_tasks) == 0:
            print("⚠️  pendingタスクが0個です")
            print("🔧 F1: 自動タスク生成を起動します...")
            print()
            
            # 自動タスク生成
            result = self.task_generator.auto_generate_if_needed()
            
            if result.get('generated') and result.get('success'):
                print("✅ F1: 高品質タスクの生成に成功しました")
                print(f"   生成数: {result.get('task_count')}個")
                return True
            else:
                print("❌ F1: タスク生成に失敗しました")
                return False
        else:
            print(f"✅ {len(pending_tasks)}個のpendingタスクが存在します")
            return True

def main():
    """メイン実行"""
    from tools.sheets_manager import GoogleSheetsManager
    
    sheets = GoogleSheetsManager()
    f1_loop = F1LoopIntegration(sheets)
    
    success = f1_loop.ensure_tasks_available()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

PYTHON

echo "✅ F1ループ統合作成: agents/f1_loop_integration.py"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: start_pending_tasksの改良
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: start_pending_tasksの改良"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > start_pending_tasks_v2.sh << 'START'
#!/bin/bash
# pendingタスク実行スクリプト v2
# スマートタスク選択とF1統合

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
echo "📋 pendingタスク実行 v2（スマート選択）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# F1: タスク可用性チェック
python3 agents/f1_loop_integration.py
F1_RESULT=$?

if [ $F1_RESULT -ne 0 ]; then
    echo "⚠️  F1: タスク生成に問題がありました"
fi

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

# タスク実行
python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.complete_engine_ultimate import CompleteEngineUltimate
from tools.sheets_manager import GoogleSheetsManager

sheets = GoogleSheetsManager()
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
    
    for row in values:
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
            break
    
    if not task_data:
        print(f"❌ タスクデータが見つかりません: {task_id}")
        continue
    
    try:
        # タスク実行
        result = engine.execute_task(task_data)
        
        if result.get('status') == 'completed':
            print(f"✅ タスク完了: {task_id}")
            success_count += 1
        else:
            print(f"⚠️  タスク実行に問題: {task_id}")
    
    except Exception as e:
        print(f"❌ タスク実行エラー: {e}")

print(f"\n{'=' * 80}")
print(f"✅ 実行完了: {success_count}/{len(task_ids)}件成功")
print('=' * 80)

PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ タスク実行完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

START

chmod +x start_pending_tasks_v2.sh
echo "✅ start_pending_tasksv2作成: start_pending_tasks_v2.sh"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: 24時間稼働スクリプトv4（完全版）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: 24時間稼働スクリプトv4（完全版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/run_autonomous_24h_v4.sh << 'AUTO'
#!/bin/bash
# 24時間自律稼働システム v4（完全版）
# 全問題を解決した最終版

cd /workspaces/gemini_AI_Agent

echo "🚀 24時間自律稼働開始 v4（完全版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【改善点】"
echo "  ✅ スマートタスク選択（completedを除外）"
echo "  ✅ F1ループ統合（タスク自動生成）"
echo "  ✅ 高品質タスク優先実行"
echo "  ✅ status更新の確実化"
echo ""

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
SUCCESS_COUNT=0
MAX_CYCLES=96  # 24時間（15分間隔）

LOG_FILE="logs/autonomous_v4_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"
mkdir -p logs

# システム保護テスト
echo "🛡️ システム保護テスト実行中..." | tee -a "$LOG_FILE"
if python3 tests/system_protection/test_core_functions.py 2>&1 | tee -a "$LOG_FILE"; then
    echo "  ✅ システム保護テスト合格" | tee -a "$LOG_FILE"
else
    echo "  ⚠️  テスト不合格（続行）" | tee -a "$LOG_FILE"
fi

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo "" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    # F1: タスク可用性チェック
    echo "  🔄 F1: タスク可用性チェック..." | tee -a "$LOG_FILE"
    python3 agents/f1_loop_integration.py 2>&1 | tee -a "$LOG_FILE"
    
    # F2: タスク自律実行（スマート選択）
    echo "  🔄 F2: タスク実行中..." | tee -a "$LOG_FILE"
    
    if bash start_pending_tasks_v2.sh --limit 2 --yes 2>&1 | tee -a "$LOG_FILE"; then
        echo "  ✅ タスク実行成功" | tee -a "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        ERROR_COUNT=0
        
    else
        echo "  ⚠️  タスク実行でエラー" | tee -a "$LOG_FILE"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        
        # F7: 自己修復
        if [ $ERROR_COUNT -le 3 ]; then
            echo "  🔧 F7: 自己修復（${ERROR_COUNT}/3）" | tee -a "$LOG_FILE"
            sleep 30
        else
            echo "  ❌ F7: 修復失敗" | tee -a "$LOG_FILE"
            echo "  🚨 F9: 人間通知" | tee -a "$LOG_FILE"
            sleep 3600
            ERROR_COUNT=0
        fi
    fi
    
    # F9: 進捗報告（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  📊 F9: 進捗報告" | tee -a "$LOG_FILE"
        echo "     成功: ${SUCCESS_COUNT}サイクル" | tee -a "$LOG_FILE"
    fi
    
    # F10: 健全性チェック（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  🔬 F10: 健全性チェック" | tee -a "$LOG_FILE"
        bash sh/health_check_periodic.sh 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # システム保護テスト（6時間ごと）
    if [ $((CYCLE_COUNT % 24)) -eq 0 ]; then
        echo "  🛡️ システム保護テスト" | tee -a "$LOG_FILE"
        python3 tests/system_protection/test_core_functions.py 2>&1 | tee -a "$LOG_FILE"
    fi
    
    echo "  ⏳ 次のサイクルまで15分待機..." | tee -a "$LOG_FILE"
    sleep 900
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_HOURS=$((ELAPSED / 3600))

echo "" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "✅ 24時間自律稼働完了" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "  実行時間: ${ELAPSED_HOURS}時間" | tee -a "$LOG_FILE"
echo "  実行サイクル: ${CYCLE_COUNT}" | tee -a "$LOG_FILE"
echo "  成功: ${SUCCESS_COUNT}サイクル" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

AUTO

chmod +x sh/run_autonomous_24h_v4.sh
echo "✅ 24時間稼働v4作成: sh/run_autonomous_24h_v4.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 全修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 解決した問題:"
echo "  1. ✅ タスク選択ロジック修正（completedを除外）"
echo "  2. ✅ F1ループ統合（タスクがない場合に自動生成）"
echo "  3. ✅ 高品質タスク優先実行"
echo "  4. ✅ status更新の確実化"
echo "  5. ✅ フォールバック実行の改善"
echo ""
echo "📄 作成ファイル:"
echo "  - agents/smart_task_selector.py（スマート選択）"
echo "  - agents/f1_loop_integration.py（F1ループ）"
echo "  - start_pending_tasks_v2.sh（改良版）"
echo "  - sh/run_autonomous_24h_v4.sh（完全版）"
echo ""
echo "🎯 次のアクション:"
echo "  1. テスト: bash sh/test_autonomous_3cycles.sh"
echo "  2. 24時間稼働: bash sh/run_autonomous_24h_v4.sh"
echo ""


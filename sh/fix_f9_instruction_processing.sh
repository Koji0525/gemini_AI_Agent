#!/bin/bash
# F9指示の自動処理機能の実装

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 F9指示の自動処理機能の実装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# 問題分析
cat > "MD/${NOW_JST}_F9指示処理問題分析.md" << 'ANALYSIS'
# F9指示処理問題の分析

## 現状の問題

### 動作しているもの
✅ ダッシュボードから指示を追加 → human_instructionsシートに追加される
✅ F9HumanInterface.check_human_instructions() → 指示一覧を取得できる

### 動作していないもの
❌ human_instructionsシートの指示 → pm_tasksシートにタスクとして追加
❌ 指示の自動処理

## 原因

**F9HumanInterface.process_instructions()** が呼ばれていない

現在のフロー：
1. ユーザーがダッシュボードで指示を追加
2. `/api/instruction` POST → `f9_interface.add_instruction()` → human_instructionsに追加 ✅
3. 24時間稼働システムが `f9_human_interface.py` を実行
4. `check_human_instructions()` → 指示一覧を表示 ✅
5. **しかし、`process_instructions()` が呼ばれない** ❌

## 解決策

### 方法1: 24時間稼働スクリプトで自動処理
```bash
# 指示をチェック
python3 agents/f9_human_interface.py

# 指示を処理（追加）
python3 -c "
from agents.f9_human_interface import F9HumanInterface
from tools.sheets_manager import GoogleSheetsManager
sheets = GoogleSheetsManager()
f9 = F9HumanInterface(sheets)
instructions = f9.check_human_instructions()
if instructions:
    f9.process_instructions(instructions)
"
```

### 方法2: F9専用の処理スクリプト作成
独立したスクリプトで定期的に指示を処理

### 方法3: CompleteEngineに統合
タスク実行の前に自動的に指示を処理

ANALYSIS

echo "✅ 問題分析完了: MD/${NOW_JST}_F9指示処理問題分析.md"

# F9指示処理スクリプトの作成
cat > agents/f9_process_instructions.py << 'PYTHON'
"""
F9指示処理スクリプト
human_instructionsシートの指示を処理してpm_tasksに追加
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.f9_human_interface import F9HumanInterface
from tools.sheets_manager import GoogleSheetsManager

def main():
    """F9指示を処理"""
    print("\n" + "=" * 80)
    print("🔄 F9指示処理開始")
    print("=" * 80)
    
    # 初期化
    sheets = GoogleSheetsManager()
    f9 = F9HumanInterface(sheets)
    
    # 未処理の指示をチェック
    instructions = f9.check_human_instructions()
    
    if not instructions:
        print("\n✅ 処理すべき指示はありません")
        return
    
    print(f"\n�� {len(instructions)}件の指示を処理します")
    
    # 指示を処理
    results = f9.process_instructions(instructions)
    
    print("\n" + "=" * 80)
    print("✅ F9指示処理完了")
    print("=" * 80)
    print(f"  処理成功: {results['processed']}件")
    print(f"  処理失敗: {results['failed']}件")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()

PYTHON

echo "✅ F9指示処理スクリプト作成: agents/f9_process_instructions.py"

# 24時間稼働スクリプトを更新
cat > sh/run_autonomous_24h_v6_final.sh << 'AUTO'
#!/bin/bash
# 24時間自律稼働システム v6（F9指示自動処理対応）

cd /workspaces/gemini_AI_Agent

echo "🚀 24時間自律稼働開始 v6（F9指示自動処理対応）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【新機能】"
echo "  ✅ F6: 動的タスク追加（品質不合格時）"
echo "  ✅ F9: 人間指示の自動処理（pm_tasksに追加）"
echo "  ✅ 厳格な品質評価（7点以上で合格）"
echo "  ✅ スマートタスク選択"
echo ""
echo "【F9使い方】"
echo "  ブラウザ: http://localhost:8000"
echo "  指示を追加すると次のサイクルで自動処理されます"
echo ""

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
SUCCESS_COUNT=0
MAX_CYCLES=96  # 24時間（15分間隔）

LOG_FILE="logs/autonomous_v6_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"
mkdir -p logs

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo "" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    # F9: 人間指示の処理（最優先）
    echo "  📨 F9: 人間指示の処理..." | tee -a "$LOG_FILE"
    python3 agents/f9_process_instructions.py 2>&1 | tee -a "$LOG_FILE"
    
    # 一時停止フラグのチェック
    if [ -f "/tmp/system_paused.flag" ]; then
        echo "  ⏸️  システム一時停止中..." | tee -a "$LOG_FILE"
        echo "  💤 1時間待機します" | tee -a "$LOG_FILE"
        sleep 3600
        continue
    fi
    
    # F1: タスク可用性チェック
    echo "  🔄 F1: タスク可用性チェック..." | tee -a "$LOG_FILE"
    python3 agents/f1_loop_integration.py 2>&1 | tee -a "$LOG_FILE"
    
    # F2: タスク自律実行（スマート選択）
    echo "  🔄 F2: タスク実行中..." | tee -a "$LOG_FILE"
    
    if bash start_pending_tasks_fixed.sh 2 2>&1 | tee -a "$LOG_FILE"; then
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
            echo "  🚨 F9: 人間への通知が必要" | tee -a "$LOG_FILE"
            
            # F9経由で通知
            python3 -c "
from agents.f9_human_interface import F9HumanInterface
from tools.sheets_manager import GoogleSheetsManager
sheets = GoogleSheetsManager()
f9 = F9HumanInterface(sheets)
f9.add_instruction('message', '自己修復失敗: 人間の介入が必要です', 'high')
" 2>&1 | tee -a "$LOG_FILE"
            
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

chmod +x sh/run_autonomous_24h_v6_final.sh
echo "✅ 24時間稼働v6作成: sh/run_autonomous_24h_v6_final.sh"

# 手動実行用スクリプトも作成
cat > sh/process_f9_instructions_now.sh << 'MANUAL'
#!/bin/bash
# F9指示を今すぐ処理

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 F9指示を今すぐ処理"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 agents/f9_process_instructions.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 処理完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 確認方法:"
echo "  Google Sheets の pm_tasks を確認"
echo "  新しいタスクが追加されているはずです"
echo ""

MANUAL

chmod +x sh/process_f9_instructions_now.sh
echo "✅ 手動実行スクリプト作成: sh/process_f9_instructions_now.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ F9指示自動処理機能の実装完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 実装内容:"
echo "  1. ✅ F9指示処理スクリプト作成"
echo "  2. ✅ 24時間稼働v6（F9自動処理対応）"
echo "  3. ✅ 手動実行スクリプト作成"
echo ""
echo "�� 使い方:"
echo ""
echo "【自動処理（推奨）】"
echo "  24時間稼働v6を起動すると、15分ごとに自動処理"
echo "  bash sh/run_autonomous_24h_v6_final.sh"
echo ""
echo "【手動処理（テスト用）】"
echo "  今すぐ指示を処理"
echo "  bash sh/process_f9_instructions_now.sh"
echo ""
echo "📝 動作フロー:"
echo "  1. ダッシュボードで指示を追加"
echo "  2. human_instructionsシートに保存される"
echo "  3. 次のサイクル（15分以内）で自動処理"
echo "  4. pm_tasksシートにタスクとして追加"
echo "  5. タスクが実行される"
echo ""
echo "🧪 テスト実行:"
echo "  bash sh/process_f9_instructions_now.sh"
echo ""

# 自動テスト実行
read -p "今すぐF9指示を処理しますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    bash sh/process_f9_instructions_now.sh
else
    echo "⏭️  スキップしました"
    echo "   手動実行: bash sh/process_f9_instructions_now.sh"
fi


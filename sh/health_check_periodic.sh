#!/bin/bash
# F10: 定期健全性チェック
# 1時間ごとに実行されるスクリプト

cd /workspaces/gemini_AI_Agent

NOW_JST=$(TZ=Asia/Tokyo date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/health_check_${NOW_JST}.log"
mkdir -p logs

echo "🔬 システム健全性チェック @ $(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M:%S')" | tee "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"

# 1. ファイル存在確認
echo "" | tee -a "$LOG_FILE"
echo "【1. コアファイル存在確認】" | tee -a "$LOG_FILE"

CRITICAL_FILES=(
    "agents/complete_engine_ultimate.py"
    "tools/sheets_manager.py"
    "tools/base_data_accessor.py"
    "knowledge_system/database/knowledge.db"
)

FILE_OK=true
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file" | tee -a "$LOG_FILE"
    else
        echo "  ❌ $file 消失！" | tee -a "$LOG_FILE"
        FILE_OK=false
    fi
done

# 2. Google Sheets接続確認
echo "" | tee -a "$LOG_FILE"
echo "【2. Google Sheets接続確認】" | tee -a "$LOG_FILE"

if python3 -c "from tools.sheets_manager import GoogleSheetsManager; GoogleSheetsManager()" 2>&1 | grep -q "接続成功"; then
    echo "  ✅ Sheets接続OK" | tee -a "$LOG_FILE"
else
    echo "  ❌ Sheets接続失敗" | tee -a "$LOG_FILE"
fi

# 3. ナレッジシステム確認
echo "" | tee -a "$LOG_FILE"
echo "【3. ナレッジシステム確認】" | tee -a "$LOG_FILE"

if python3 -c "from knowledge_system.core_agents.knowledge_manager import KnowledgeManager; KnowledgeManager()" 2>&1 | grep -q "初期化完了"; then
    echo "  ✅ ナレッジシステムOK" | tee -a "$LOG_FILE"
else
    echo "  ❌ ナレッジシステム失敗" | tee -a "$LOG_FILE"
fi

# 4. F7-F9エージェント確認
echo "" | tee -a "$LOG_FILE"
echo "【4. F7-F9エージェント確認】" | tee -a "$LOG_FILE"

python3 << 'PY' 2>&1 | tee -a "$LOG_FILE"
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
try:
    from agents.complete_engine_ultimate import CompleteEngineUltimate
    engine = CompleteEngineUltimate()
    print("  ✅ F7: self_healing" if hasattr(engine, 'self_healing') else "  ❌ F7")
    print("  ✅ F8: self_evolution" if hasattr(engine, 'self_evolution') else "  ❌ F8")
    print("  ✅ F9: human_collaboration" if hasattr(engine, 'human_collaboration') else "  ❌ F9")
except Exception as e:
    print(f"  ❌ エージェント確認失敗: {e}")
PY

# 5. 総合判定
echo "" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"

if [ "$FILE_OK" = true ]; then
    echo "✅ システム正常" | tee -a "$LOG_FILE"
else
    echo "⚠️  要注意：ファイル消失あり" | tee -a "$LOG_FILE"
    # F9: 人間への通知
    echo "🚨 人間への通知が必要です" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

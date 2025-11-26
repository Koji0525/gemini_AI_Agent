#!/bin/bash
################################################################################
# システムヘルスチェック総合スクリプト
#
# 目的: 既存システムの健全性を監視し、84.3%のテスト成功率を維持
# 実行頻度: 毎日6時（Cron推奨）
# 所要時間: 約30秒
################################################################################

# プロジェクトルート
PROJECT_ROOT="/workspaces/gemini_AI_Agent"
cd "$PROJECT_ROOT"

# ログファイル
LOG_DIR="shared_states/diagnostics"
LOG_FILE="$LOG_DIR/health_check_$(date +%Y%m%d_%H%M%S).log"

# ログ出力関数
log() {
    echo "$1" | tee -a "$LOG_FILE"
}

log "========================================="
log "🏥 システムヘルスチェック"
log "実行日時: $(date '+%Y-%m-%d %H:%M:%S')"
log "========================================="

# 全体の健全性フラグ
OVERALL_HEALTH="good"

# ========================================
# 1. テスト成功率チェック（最重要）
# ========================================
log ""
log "[1/6] テスト成功率チェック..."

# 既存テストのみ実行（新規統合テストは除外）
TEST_OUTPUT=$(pytest tests/ --ignore=tests/integration/ --tb=no -q 2>&1)

# 成功数を抽出
SUCCESS_COUNT=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= passed)' | head -1)
FAILED_COUNT=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= failed)' | head -1)

# デフォルト値設定
SUCCESS_COUNT=${SUCCESS_COUNT:-0}
FAILED_COUNT=${FAILED_COUNT:-0}
TOTAL_COUNT=$((SUCCESS_COUNT + FAILED_COUNT))

if [ $TOTAL_COUNT -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $SUCCESS_COUNT/$TOTAL_COUNT*100" | bc)
else
    SUCCESS_RATE=0
fi

THRESHOLD=84.3

if (( $(echo "$SUCCESS_RATE >= $THRESHOLD" | bc -l) )); then
    log "✅ テスト成功率: $SUCCESS_RATE% (基準: $THRESHOLD%)"
    log "   成功: $SUCCESS_COUNT, 失敗: $FAILED_COUNT, 合計: $TOTAL_COUNT"
else
    log "❌ テスト成功率低下: $SUCCESS_RATE% < $THRESHOLD%"
    log "   成功: $SUCCESS_COUNT, 失敗: $FAILED_COUNT, 合計: $TOTAL_COUNT"
    OVERALL_HEALTH="critical"
fi

# ========================================
# 2. 保護ファイル変更検出
# ========================================
log ""
log "[2/6] 保護ファイル変更検出..."

# 保護ファイルリスト
PROTECTED_FILES=(
    "agents/complete_engine_ultimate.py"
    "tools/sheets_manager.py"
    "tools/safe_sheets_wrapper.py"
    "knowledge_system/core_agents/knowledge_manager.py"
    "tools/base_data_accessor.py"
    "agents/task_execution/high_quality_executor_v8.py"
    "agents/quality_evaluation/quality_evaluator.py"
    "agents/self_healing/self_healing_agent.py"
)

PROTECTED_CHANGED=0
for file in "${PROTECTED_FILES[@]}"; do
    if [ -f "$file" ]; then
        # 最終更新日時を確認（過去24時間以内の変更を検出）
        MODIFIED=$(find "$file" -mtime -1 2>/dev/null)
        if [ -n "$MODIFIED" ]; then
            log "⚠️  保護ファイルが変更されています: $file"
            PROTECTED_CHANGED=1
            OVERALL_HEALTH="warning"
        fi
    fi
done

if [ $PROTECTED_CHANGED -eq 0 ]; then
    log "✅ 保護ファイル変更なし（8ファイル確認）"
fi

# ========================================
# 3. リソース使用状況
# ========================================
log ""
log "[3/6] リソース使用状況..."

# メモリ使用量（MB）
MEMORY_USED=$(free -m | awk '/^Mem:/{print $3}')
MEMORY_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
MEMORY_PERCENT=$(echo "scale=1; $MEMORY_USED/$MEMORY_TOTAL*100" | bc)

log "   メモリ使用: ${MEMORY_USED}MB / ${MEMORY_TOTAL}MB (${MEMORY_PERCENT}%)"

if [ $MEMORY_USED -gt 1800 ]; then
    log "⚠️  メモリ使用量が高い（> 1800MB）"
    OVERALL_HEALTH="warning"
fi

# ディスク使用量
DISK_USED=$(df -h . | awk 'NR==2{print $3}')
DISK_TOTAL=$(df -h . | awk 'NR==2{print $2}')
DISK_PERCENT=$(df -h . | awk 'NR==2{print $5}')

log "   ディスク使用: ${DISK_USED} / ${DISK_TOTAL} (${DISK_PERCENT})"

# ========================================
# 4. エージェント稼働状況
# ========================================
log ""
log "[4/6] エージェント稼働状況..."

AGENT_COUNT=$(find agents/ -name "*.py" -type f ! -path "*/\__pycache__/*" | wc -l)
log "   エージェント数: ${AGENT_COUNT}ファイル"

# エージェント数の履歴確認（減っていないか）
HISTORY_FILE="$LOG_DIR/agent_count_history.txt"
if [ -f "$HISTORY_FILE" ]; then
    LAST_COUNT=$(tail -1 "$HISTORY_FILE" | awk '{print $2}')
    if [ $AGENT_COUNT -lt $LAST_COUNT ]; then
        log "⚠️  エージェント数が減少: $LAST_COUNT → $AGENT_COUNT"
        OVERALL_HEALTH="warning"
    fi
fi

# 現在のカウントを記録
echo "$(date +%Y%m%d) $AGENT_COUNT" >> "$HISTORY_FILE"

# ========================================
# 5. ナレッジDB統計
# ========================================
log ""
log "[5/6] ナレッジDB統計..."

KNOWLEDGE_STATS=$(python3 << 'PYEOF'
import sys
from pathlib import Path
sys.path.insert(0, "/workspaces/gemini_AI_Agent")

try:
    from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
    km = KnowledgeManager()
    stats = km.get_statistics()
    print(f"SUCCESS:{stats.get('total_entries', 0)}")
except Exception as e:
    print(f"ERROR:{e}")
PYEOF
)

if [[ $KNOWLEDGE_STATS == SUCCESS:* ]]; then
    KNOWLEDGE_COUNT=$(echo "$KNOWLEDGE_STATS" | cut -d':' -f2)
    log "   ナレッジ件数: ${KNOWLEDGE_COUNT}件"
    
    if [ $KNOWLEDGE_COUNT -lt 500 ]; then
        log "⚠️  ナレッジ件数が減少している可能性"
        OVERALL_HEALTH="warning"
    fi
else
    log "❌ ナレッジDB接続エラー"
    OVERALL_HEALTH="warning"
fi

# ========================================
# 6. 実行ログ確認
# ========================================
log ""
log "[6/6] 最近の実行ログ確認..."

if [ -d "agent_outputs/auto_log" ]; then
    RECENT_LOGS=$(find agent_outputs/auto_log -name "*.txt" -mtime -1 | wc -l)
    log "   直近24時間の実行ログ: ${RECENT_LOGS}件"
    
    if [ $RECENT_LOGS -eq 0 ]; then
        log "⚠️  最近のタスク実行がありません"
        OVERALL_HEALTH="warning"
    fi
fi

# ========================================
# 総合判定
# ========================================
log ""
log "========================================="
log "📊 総合健全性: $OVERALL_HEALTH"
log "========================================="

case $OVERALL_HEALTH in
    good)
        log "✅ システムは健全です"
        EXIT_CODE=0
        ;;
    warning)
        log "⚠️  警告事項があります（要確認）"
        EXIT_CODE=0
        ;;
    critical)
        log "❌ 重大な問題があります（早急な対応が必要）"
        EXIT_CODE=1
        ;;
esac

log ""
log "📄 詳細ログ: $LOG_FILE"
log ""

# JSONサマリー生成（他のツールで利用可能）
cat > "$LOG_DIR/latest_health.json" << EOFJSON
{
  "timestamp": "$(date -Iseconds)",
  "overall_health": "$OVERALL_HEALTH",
  "test_success_rate": $SUCCESS_RATE,
  "test_threshold": $THRESHOLD,
  "memory_used_mb": $MEMORY_USED,
  "memory_total_mb": $MEMORY_TOTAL,
  "disk_used": "$DISK_USED",
  "agent_count": $AGENT_COUNT,
  "knowledge_count": ${KNOWLEDGE_COUNT:-0},
  "recent_logs": ${RECENT_LOGS:-0},
  "protected_files_changed": $PROTECTED_CHANGED
}
EOFJSON

exit $EXIT_CODE

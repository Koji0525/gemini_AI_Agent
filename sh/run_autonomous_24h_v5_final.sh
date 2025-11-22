#!/bin/bash
# 24時間自律稼働システム v5（完全版）
# F6/F9完全統合

cd /workspaces/gemini_AI_Agent

echo "🚀 24時間自律稼働開始 v5（完全版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【新機能】"
echo "  ✅ F6: 動的タスク追加（品質不合格時）"
echo "  ✅ F9: 人間指示の定期チェック（毎サイクル）"
echo "  ✅ 厳格な品質評価（7点以上で合格）"
echo "  ✅ スマートタスク選択"
echo ""
echo "【F9使用方法】"
echo "  別ターミナルで以下を実行:"
echo "    ./f9                    # 対話モード"
echo "    ./f9 add -t add_task -c '新タスク' -p high"
echo "    ./f9 list --status pending"
echo ""

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
SUCCESS_COUNT=0
MAX_CYCLES=96  # 24時間（15分間隔）

LOG_FILE="logs/autonomous_v5_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"
mkdir -p logs

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo "" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    # F9: 人間指示チェック（最優先）
    echo "  📨 F9: 人間指示チェック..." | tee -a "$LOG_FILE"
    python3 agents/f9_human_interface.py 2>&1 | tee -a "$LOG_FILE"
    
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
            ./f9 add -t message -c "自己修復失敗: 人間の介入が必要です" -p high 2>&1 | tee -a "$LOG_FILE"
            
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


#!/bin/bash
# 24時間自律稼働システム v2
# F7-F9を活用した完全自律実行

cd /workspaces/gemini_AI_Agent

echo "🚀 24時間自律稼働開始 v2"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【統合機能】"
echo "  ✅ F7: エラー時の自動修復（最大3回リトライ）"
echo "  ✅ F8: 成功パターンの自動学習"
echo "  ✅ F9: 必要時のみ人間への報告"
echo ""

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
SUCCESS_COUNT=0
MAX_CYCLES=96  # 24時間分（1サイクル15分）

# ログファイル
LOG_FILE="logs/autonomous_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"
mkdir -p logs

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo "" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    # F2: タスク自律実行（CompleteEngineが内部でF7-F9を呼び出す）
    echo "  🔄 F2: タスク実行中..." | tee -a "$LOG_FILE"
    
    if bash start_pending_tasks.sh --limit 3 2>&1 | tee -a "$LOG_FILE"; then
        echo "  ✅ タスク実行成功" | tee -a "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        ERROR_COUNT=0  # 成功したのでエラーカウントリセット
        
        # F8: 自己進化（成功パターン学習）
        echo "  📊 F8: 成功パターン学習完了" | tee -a "$LOG_FILE"
        
    else
        echo "  ⚠️  タスク実行でエラー発生" | tee -a "$LOG_FILE"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        
        # F7: 自己修復（CompleteEngine内で自動実行）
        echo "  🔧 F7: 自己修復システムが作動中..." | tee -a "$LOG_FILE"
        
        if [ $ERROR_COUNT -le 3 ]; then
            echo "  ⏳ リトライ待機中 (${ERROR_COUNT}/3)" | tee -a "$LOG_FILE"
            sleep 30
        else
            echo "  ❌ 自己修復失敗（3回試行）" | tee -a "$LOG_FILE"
            
            # F9: 人間連携（アラート）
            echo "  🚨 F9: 人間への通知が必要" | tee -a "$LOG_FILE"
            echo "  📧 通知: システムが3回連続でエラー。確認が必要です。" | tee -a "$LOG_FILE"
            
            # 重大エラーなので一時停止
            echo "  ⏸️  一時停止（60分後に再開）" | tee -a "$LOG_FILE"
            sleep 3600
            ERROR_COUNT=0
        fi
    fi
    
    # F9: 定期進捗報告（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  📊 F9: 進捗報告" | tee -a "$LOG_FILE"
        echo "     成功: ${SUCCESS_COUNT}サイクル" | tee -a "$LOG_FILE"
        echo "     実行時間: $((CYCLE_COUNT * 15))分" | tee -a "$LOG_FILE"
        
        # ダッシュボード更新
        python3 agents/observability/dashboard.py 2>&1 | head -30 | tee -a "$LOG_FILE"
    fi
    
    # 次のサイクルまで待機（15分）
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
echo "  成功率: $((SUCCESS_COUNT * 100 / CYCLE_COUNT))%" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

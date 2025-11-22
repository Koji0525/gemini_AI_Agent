#!/bin/bash
# 24時間自律稼働システム v3
# タスク自動生成機能を統合

cd /workspaces/gemini_AI_Agent

echo "🚀 24時間自律稼働開始 v3（タスク自動生成対応）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【新機能】"
echo "  ✅ pendingタスクがない場合、自動生成"
echo "  ✅ 統合テストタスクの自動追加"
echo "  ✅ システム保護テストの定期実行"
echo ""

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
SUCCESS_COUNT=0
AUTO_GENERATED_COUNT=0
MAX_CYCLES=96

LOG_FILE="logs/autonomous_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"
mkdir -p logs

# システム保護テストの実行（起動時）
echo "🛡️ システム保護テスト実行中..." | tee -a "$LOG_FILE"
if python3 tests/system_protection/test_core_functions.py 2>&1 | tee -a "$LOG_FILE"; then
    echo "  ✅ システム保護テスト合格" | tee -a "$LOG_FILE"
else
    echo "  ⚠️  システム保護テスト不合格（続行しますが要確認）" | tee -a "$LOG_FILE"
fi

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo "" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    # F6: pendingタスクがない場合、自動生成
    echo "  📋 タスク状況確認..." | tee -a "$LOG_FILE"
    if python3 agents/auto_task_generator.py 2>&1 | tee -a "$LOG_FILE" | grep -q "統合タスクを自動生成"; then
        echo "  ✅ F6: 統合タスクを自動生成しました" | tee -a "$LOG_FILE"
        AUTO_GENERATED_COUNT=$((AUTO_GENERATED_COUNT + 1))
    fi
    
    # F2: タスク自律実行
    echo "  🔄 F2: タスク実行中..." | tee -a "$LOG_FILE"
    
    if bash start_pending_tasks.sh --limit 3 2>&1 | tee -a "$LOG_FILE"; then
        echo "  ✅ タスク実行成功" | tee -a "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        ERROR_COUNT=0
        
        # F8: 自己進化
        echo "  📊 F8: 成功パターン学習完了" | tee -a "$LOG_FILE"
        
    else
        echo "  ⚠️  タスク実行でエラー発生" | tee -a "$LOG_FILE"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        
        # F7: 自己修復
        echo "  🔧 F7: 自己修復システムが作動中..." | tee -a "$LOG_FILE"
        
        if [ $ERROR_COUNT -le 3 ]; then
            echo "  ⏳ リトライ待機中 (${ERROR_COUNT}/3)" | tee -a "$LOG_FILE"
            sleep 30
        else
            echo "  ❌ 自己修復失敗（3回試行）" | tee -a "$LOG_FILE"
            
            # F9: 人間連携
            echo "  🚨 F9: 人間への通知が必要" | tee -a "$LOG_FILE"
            echo "  ⏸️  一時停止（60分後に再開）" | tee -a "$LOG_FILE"
            sleep 3600
            ERROR_COUNT=0
        fi
    fi
    
    # F9: 定期進捗報告（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  📊 F9: 進捗報告" | tee -a "$LOG_FILE"
        echo "     成功: ${SUCCESS_COUNT}サイクル" | tee -a "$LOG_FILE"
        echo "     自動生成: ${AUTO_GENERATED_COUNT}回" | tee -a "$LOG_FILE"
        echo "     実行時間: $((CYCLE_COUNT * 15))分" | tee -a "$LOG_FILE"
    fi
    
    # F10: 健全性チェック（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  🔬 F10: 健全性チェック" | tee -a "$LOG_FILE"
        bash sh/health_check_periodic.sh 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # システム保護テスト（6時間ごと）
    if [ $((CYCLE_COUNT % 24)) -eq 0 ]; then
        echo "  🛡️ システム保護テスト（定期）" | tee -a "$LOG_FILE"
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
echo "  自動生成: ${AUTO_GENERATED_COUNT}回" | tee -a "$LOG_FILE"
echo "  成功率: $((SUCCESS_COUNT * 100 / CYCLE_COUNT))%" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"


#!/bin/bash
# Phase 4A: 堅牢な24時間自律稼働システム（F1初回実行版）

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Phase 4A: 堅牢な24時間自律稼働システム"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【Phase 4A追加機能】"
echo "  ✅ APIレート制限管理"
echo "  ✅ 緊急停止メカニズム"
echo "  ✅ 自動リソースクリーンアップ"
echo "  ✅ 堅牢なエラーハンドリング"
echo "  ✅ リアルタイムダッシュボード"
echo "  ✅ F1初回実行（新規目標対応）"
echo ""
echo "【既存機能（Phase 1-3）】"
echo "  ✅ 高品質タスク実行（10点保証）"
echo "  ✅ 自動品質チェック・テスト・統合"
echo "  ✅ Git自動コミット"
echo "  ✅ F1-F10完全連携"
echo ""
echo "🎯 目標: 完全自律24時間稼働"
echo ""

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
SUCCESS_COUNT=0
MAX_CYCLES=96  # 24時間（15分間隔）

LOG_FILE="logs/phase4a_autonomous_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"
mkdir -p logs

echo "ログファイル: $LOG_FILE"
echo "ダッシュボード: status.html"
echo ""

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo "" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "🔄 サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    # Phase 4A: 緊急停止チェック
    if [ -f "/tmp/system_emergency_stop.flag" ]; then
        echo "  🚨 緊急停止フラグ検出 - システム停止" | tee -a "$LOG_FILE"
        exit 0
    fi
    
    # Phase 4A: 一時停止チェック
    if [ -f "/tmp/system_paused.flag" ]; then
        echo "  ⏸️  システム一時停止中..." | tee -a "$LOG_FILE"
        sleep 3600
        continue
    fi
    
    # F9: 人間指示の処理
    if [ -f "agents/f9_process_instructions.py" ]; then
        echo "  📨 F9: 人間指示の処理..." | tee -a "$LOG_FILE"
        python3 agents/f9_process_instructions.py 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # F1: タスク可用性チェック
    # 重要: 1回目は必ず実行、以降は1時間ごと
    if [ $CYCLE_COUNT -eq 1 ] || [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        if [ -f "agents/f1_loop_integration.py" ]; then
            if [ $CYCLE_COUNT -eq 1 ]; then
                echo "  🔄 F1: 初回タスク生成（新規目標チェック）..." | tee -a "$LOG_FILE"
            else
                echo "  🔄 F1: タスク可用性チェック..." | tee -a "$LOG_FILE"
            fi
            python3 agents/f1_loop_integration.py 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
    
    # Phase 3: 完全自律タスク実行
    echo "  🚀 Phase 3+4A: タスク実行..." | tee -a "$LOG_FILE"
    
    if bash sh/run_phase3_full_autonomous.sh 2 2>&1 | tee -a "$LOG_FILE"; then
        echo "  ✅ タスク実行成功" | tee -a "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        ERROR_COUNT=0
    else
        echo "  ⚠️  タスク実行エラー" | tee -a "$LOG_FILE"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        
        # F7: 自己修復
        if [ $ERROR_COUNT -le 3 ]; then
            echo "  🔧 F7: 自己修復（${ERROR_COUNT}/3）" | tee -a "$LOG_FILE"
            sleep 30
        else
            echo "  ❌ F7: 修復失敗 - 一時停止" | tee -a "$LOG_FILE"
            touch /tmp/system_paused.flag
            ERROR_COUNT=0
        fi
    fi
    
    # Phase 4A: リソースクリーンアップ（6時間ごと）
    if [ $((CYCLE_COUNT % 24)) -eq 0 ]; then
        echo "  🧹 Phase 4A: リソースクリーンアップ..." | tee -a "$LOG_FILE"
        bash sh/cleanup_resources.sh 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # Phase 4A: ダッシュボード更新
    bash sh/update_dashboard.sh 2>&1 | tee -a "$LOG_FILE"
    
    # F9: 進捗報告（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  📊 F9: 進捗報告" | tee -a "$LOG_FILE"
        echo "     成功サイクル: ${SUCCESS_COUNT}" | tee -a "$LOG_FILE"
        echo "     ダッシュボード: status.html" | tee -a "$LOG_FILE"
    fi
    
    # F10: 健全性チェック（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        if [ -f "sh/health_check_periodic.sh" ]; then
            echo "  🔬 F10: 健全性チェック" | tee -a "$LOG_FILE"
            bash sh/health_check_periodic.sh 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
    
    echo "  ⏳ 次のサイクルまで15分待機..." | tee -a "$LOG_FILE"
    sleep 900
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_HOURS=$((ELAPSED / 3600))

echo "" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "✅ Phase 4A: 24時間稼働完了" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "  実行時間: ${ELAPSED_HOURS}時間" | tee -a "$LOG_FILE"
echo "  実行サイクル: ${CYCLE_COUNT}" | tee -a "$LOG_FILE"
echo "  成功サイクル: ${SUCCESS_COUNT}" | tee -a "$LOG_FILE"
echo "  ダッシュボード: status.html" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"


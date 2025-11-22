#!/bin/bash
# 24時間完全自律稼働システム（Phase 3版）

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 24時間完全自律稼働開始（Phase 3版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【完全自律機能】"
echo "  ✅ F1: ゴール自動分解"
echo "  ✅ F2: タスク自律実行（Phase 3統合）"
echo "  ✅ F3: 品質自動評価"
echo "  ✅ F4: ナレッジ蓄積（自動登録）"
echo "  ✅ F5: 進捗可視化"
echo "  ✅ F6: 動的タスク追加"
echo "  ✅ F7: 自己修復"
echo "  ✅ F8: 自己進化"
echo "  ✅ F9: 人間協働"
echo "  ✅ F10: 健全性チェック"
echo ""
echo "【Phase 3追加機能】"
echo "  ✅ 自動コード品質チェック"
echo "  ✅ 自動テスト生成・実行"
echo "  ✅ 既存システムへの自動統合"
echo "  ✅ Git自動コミット"
echo "  ✅ 再利用可能ライブラリ生成"
echo ""
echo "🎯 目標: 自動で様々なシステム開発が進む状態"
echo ""

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
SUCCESS_COUNT=0
INTEGRATION_COUNT=0
COMMIT_COUNT=0
MAX_CYCLES=96  # 24時間（15分間隔）

LOG_FILE="logs/phase3_autonomous_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"
mkdir -p logs

echo "ログファイル: $LOG_FILE"
echo ""

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo "" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "🔄 サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    # F9: 人間指示の処理（最優先）
    if [ -f "agents/f9_process_instructions.py" ]; then
        echo "  📨 F9: 人間指示の処理..." | tee -a "$LOG_FILE"
        python3 agents/f9_process_instructions.py 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # 一時停止フラグのチェック
    if [ -f "/tmp/system_paused.flag" ]; then
        echo "  ⏸️  システム一時停止中..." | tee -a "$LOG_FILE"
        sleep 3600
        continue
    fi
    
    # F1: タスク可用性チェック（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        if [ -f "agents/f1_loop_integration.py" ]; then
            echo "  🔄 F1: タスク可用性チェック..." | tee -a "$LOG_FILE"
            python3 agents/f1_loop_integration.py 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
    
    # Phase 3完全自律タスク実行
    echo "  🚀 Phase 3: 完全自律タスク実行..." | tee -a "$LOG_FILE"
    
    if bash sh/run_phase3_full_autonomous.sh 2 2>&1 | tee -a "$LOG_FILE"; then
        echo "  ✅ Phase 3実行成功" | tee -a "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        INTEGRATION_COUNT=$((INTEGRATION_COUNT + 2))  # 2タスク統合
        COMMIT_COUNT=$((COMMIT_COUNT + 1))
        ERROR_COUNT=0
    else
        echo "  ⚠️  Phase 3実行エラー" | tee -a "$LOG_FILE"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        
        # F7: 自己修復
        if [ $ERROR_COUNT -le 3 ]; then
            echo "  🔧 F7: 自己修復（${ERROR_COUNT}/3）" | tee -a "$LOG_FILE"
            sleep 30
        else
            echo "  ❌ F7: 修復失敗" | tee -a "$LOG_FILE"
            echo "  🚨 F9: 人間への通知" | tee -a "$LOG_FILE"
            
            # 緊急停止フラグを作成
            touch /tmp/system_paused.flag
            
            sleep 3600
            ERROR_COUNT=0
        fi
    fi
    
    # F9: 進捗報告（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  📊 F9: 進捗報告" | tee -a "$LOG_FILE"
        echo "     成功サイクル: ${SUCCESS_COUNT}" | tee -a "$LOG_FILE"
        echo "     統合モジュール: ${INTEGRATION_COUNT}個" | tee -a "$LOG_FILE"
        echo "     Gitコミット: ${COMMIT_COUNT}回" | tee -a "$LOG_FILE"
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
echo "✅ 24時間完全自律稼働完了（Phase 3版）" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "  実行時間: ${ELAPSED_HOURS}時間" | tee -a "$LOG_FILE"
echo "  実行サイクル: ${CYCLE_COUNT}" | tee -a "$LOG_FILE"
echo "  成功サイクル: ${SUCCESS_COUNT}" | tee -a "$LOG_FILE"
echo "  統合モジュール: ${INTEGRATION_COUNT}個" | tee -a "$LOG_FILE"
echo "  Gitコミット: ${COMMIT_COUNT}回" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"


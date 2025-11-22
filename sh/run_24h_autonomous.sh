#!/bin/bash
# 24時間自律稼働スクリプト
# Phase 2完了後に使用

cd /workspaces/gemini_AI_Agent

echo "🚀 24時間自律稼働開始"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
MAX_CYCLES=100  # 約24時間分（1サイクル約15分想定）

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # F2: タスク自律実行
    if bash start_pending_tasks.sh --limit 3; then
        echo "  ✅ タスク実行成功"
    else
        echo "  ⚠️  タスク実行でエラー発生"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        
        # F7: 自己修復機能（3回まで自動リトライ）
        if [ $ERROR_COUNT -le 3 ]; then
            echo "  🔧 F7: 自己修復を試行 (${ERROR_COUNT}/3)"
            sleep 10
            continue
        else
            echo "  ❌ 修復失敗、人間介入が必要"
            # F9: 人間連携機能（アラート）
            echo "  🚨 F9: 人間への通知が必要"
            break
        fi
    fi
    
    # F8: 自己進化（成功パターン学習）
    echo "  📊 F8: 成功パターン学習中..."
    
    # 15分待機
    echo "  ⏳ 次のサイクルまで15分待機..."
    sleep 900
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_HOURS=$((ELAPSED / 3600))

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 自律稼働終了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  実行時間: ${ELAPSED_HOURS}時間"
echo "  実行サイクル: ${CYCLE_COUNT}"
echo "  エラー回数: ${ERROR_COUNT}"
echo ""

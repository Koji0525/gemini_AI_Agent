#!/bin/bash
# Phase 0 統合診断スクリプト

echo "=========================================================="
echo "Phase 0: 現状確認・診断 統合実行"
echo "=========================================================="
echo ""
echo "【目的】既存システムの健全性を確認し、基準値を記録"
echo "【所要時間】約2時間"
echo ""

cd /workspaces/gemini_AI_Agent

START_TIME=$(date +%s)

# T0.1.1: 既存テスト実行
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "T0.1.1: 既存テスト実行・成功率測定"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash sh/diagnose_phase0_tests.sh
TEST_RESULT=$?
echo ""

# T0.1.2: 既存ファイル一覧
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "T0.1.2: 既存ファイル一覧の記録"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash sh/list_existing_files.sh
FILES_RESULT=$?
echo ""

# T0.1.3: API成功率測定
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "T0.1.3: API成功率の測定"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash sh/measure_api_success_rate.sh
API_RESULT=$?
echo ""

# T0.1.4: ナレッジDB統計
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "T0.1.4: ナレッジDB統計の記録"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash sh/measure_knowledge_stats.sh
KNOWLEDGE_RESULT=$?
echo ""

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "=========================================================="
echo "Phase 0 診断完了"
echo "=========================================================="
echo ""
echo "【実行時間】${ELAPSED}秒"
echo ""
echo "【結果サマリー】"
echo "  T0.1.1 テスト実行: $([ $TEST_RESULT -eq 0 ] && echo '✅' || echo '❌')"
echo "  T0.1.2 ファイル記録: $([ $FILES_RESULT -eq 0 ] && echo '✅' || echo '❌')"
echo "  T0.1.3 API測定: $([ $API_RESULT -eq 0 ] && echo '✅' || echo '❌')"
echo "  T0.1.4 ナレッジ測定: $([ $KNOWLEDGE_RESULT -eq 0 ] && echo '✅' || echo '❌')"
echo ""
echo "【生成ファイル】"
echo "  - MD/PHASE0_TEST_RESULTS.md"
echo "  - MD/EXISTING_FILES_BASELINE.md"
echo ""
echo "【次のステップ】"
echo "  1. MD/PROGRESS_CHECKLIST.md を更新"
echo "  2. Phase 0完了条件を確認"
echo "  3. すべて✅ならPhase 1へ進む"
echo ""

#!/bin/bash
# Phase 0 診断: 既存テスト実行・成功率測定

echo "=================================================="
echo "Phase 0 診断: 既存テスト実行"
echo "=================================================="
echo ""
echo "【目的】既存システムの健全性確認"
echo "【基準値】テスト成功率 84.3%以上"
echo ""

cd /workspaces/gemini_AI_Agent

# テスト実行
echo "🧪 テスト実行中..."
pytest tests/ -v --tb=short > /tmp/test_results.txt 2>&1

# 結果解析
if [ $? -eq 0 ]; then
    echo "✅ すべてのテストが成功しました"
    SUCCESS_RATE="100%"
else
    # 成功率計算
    PASSED=$(grep -o "passed" /tmp/test_results.txt | wc -l)
    FAILED=$(grep -o "failed" /tmp/test_results.txt | wc -l)
    TOTAL=$((PASSED + FAILED))
    
    if [ $TOTAL -gt 0 ]; then
        SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED/$TOTAL)*100}")
        echo "⚠️ テスト成功率: ${SUCCESS_RATE}%"
        echo "   成功: ${PASSED}件"
        echo "   失敗: ${FAILED}件"
    else
        SUCCESS_RATE="0.0"
        echo "❌ テストが実行されませんでした"
    fi
fi

echo ""
echo "【基準値判定】"
if (( $(echo "$SUCCESS_RATE >= 84.3" | bc -l) )); then
    echo "✅ 基準値クリア: ${SUCCESS_RATE}% >= 84.3%"
    STATUS="SUCCESS"
else
    echo "❌ 基準値未達: ${SUCCESS_RATE}% < 84.3%"
    STATUS="FAILED"
fi

# 結果を記録
cat > /workspaces/gemini_AI_Agent/MD/PHASE0_TEST_RESULTS.md << EOF
# Phase 0 テスト結果

**実行日時**: $(date '+%Y-%m-%d %H:%M:%S')
**テスト成功率**: ${SUCCESS_RATE}%
**基準値**: 84.3%以上
**判定**: ${STATUS}

## 詳細

\`\`\`
$(cat /tmp/test_results.txt)
\`\`\`
EOF

echo ""
echo "📊 結果を MD/PHASE0_TEST_RESULTS.md に保存しました"
echo ""
echo "【実測値】${SUCCESS_RATE}%"

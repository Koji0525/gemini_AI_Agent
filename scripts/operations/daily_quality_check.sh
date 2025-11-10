#!/bin/bash

echo "📊 ===== 毎日の品質チェック ====="
echo "実行日時: $(date '+%Y-%m-%d %H:%M:%S')"

# 1. 全テスト実行
echo -e "\n1️⃣ テスト実行..."
pytest tests/ -q --tb=no > /tmp/test_result.txt 2>&1

if [ $? -eq 0 ]; then
    passed=$(grep -o "[0-9]* passed" /tmp/test_result.txt | grep -o "[0-9]*" || echo "0")
    echo "   ✅ 成功: ${passed}件"
else
    echo "   ❌ テスト失敗"
    cat /tmp/test_result.txt
fi

# 2. スコア確認
echo -e "\n2️⃣ スコア確認..."
python3 tools/mock_quality_checker.py > /tmp/score_check.txt 2>&1
current_score=$(grep "総合スコア:" /tmp/score_check.txt | grep -o "[0-9]*\.[0-9]*" | head -1)

if [ -z "$current_score" ]; then
    current_score="0.0"
fi

echo "   現在のスコア: ${current_score}/100"

# 3. 劣化チェック
python3 << PYTHON
score = float("${current_score}")
if score < 82.0:
    print("🚨 緊急: スコアが82点を下回りました")
    print(f"   現在: {score}点")
    print("   → 全作業を停止して調査")
    exit(1)
elif score < 84.0:
    print("⚠️  警告: スコアが84点を下回りました")
    print(f"   現在: {score}点")
    print("   → 即座に調査が必要")
    exit(1)
else:
    print(f"✅ スコア正常: {score}点")
PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "チェック完了"

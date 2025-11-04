#!/bin/bash
# プロジェクトヘルスチェック（改善版）

echo "🏥 プロジェクトヘルスチェック"
echo ""

score=0
total=5

# 1. 構文チェック（_WIP除外）
echo "1. 構文チェック..."
python3 -m compileall -q \
    --exclude="(_WIP|_BACKUP|_ARCHIVE|__pycache__|node_modules)" \
    . 2>&1 | grep -v "Can't list" | grep -q "Error" && echo "❌" || { echo "✅"; ((score++)); }

# 2. 重複チェック
echo "2. 重複チェック..."
python3 tools/file_version_manager.py --check-duplicates 2>/dev/null | grep -q "検出されませんでした" && { echo "✅"; ((score++)); } || echo "⚠️"

# 3. インポートテスト
echo "3. インポートテスト..."
python3 tests/unit/test_imports.py &>/dev/null && { echo "✅"; ((score++)); } || echo "❌"

# 4. 環境変数チェック
echo "4. 環境変数チェック..."
[ -f ".env" ] && grep -q "GEMINI_API_KEY" .env && { echo "✅"; ((score++)); } || echo "❌"

# 5. 依存パッケージチェック
echo "5. 依存パッケージチェック..."
pip check &>/dev/null && { echo "✅"; ((score++)); } || echo "❌"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 スコア: $score / $total"

if [ $score -eq $total ]; then
    echo "🎉 すべて正常"
    exit 0
elif [ $score -ge 3 ]; then
    echo "⚠️ 一部問題あり"
    exit 1
else
    echo "❌ 重大な問題あり"
    exit 2
fi

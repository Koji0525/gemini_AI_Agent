#!/bin/bash
# 段階1: 絶対に安全な削除

echo "🧹 段階1: 100%安全な削除"
echo "========================================"

# 削除前の状態を記録
echo "📊 削除前のファイル数:"
find . -type f | wc -l

echo ""
echo "🗑️ 削除対象:"
echo "  1. __pycache__/ フォルダ（全て）"
echo "  2. *.pyc ファイル（全て）"
echo "  3. browser_data/ フォルダ（全て）"
echo ""

read -p "削除を実行しますか？ (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "キャンセルしました"
    exit 0
fi

# 1. __pycache__削除
echo ""
echo "🗑️ __pycache__/ 削除中..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "✅ __pycache__/ 削除完了"

# 2. .pycファイル削除
echo ""
echo "🗑️ *.pyc ファイル削除中..."
find . -name "*.pyc" -delete
echo "✅ *.pyc ファイル削除完了"

# 3. browser_data削除
echo ""
echo "🗑️ browser_data/ 削除中..."
if [ -d "browser_data" ]; then
    rm -rf browser_data
    echo "✅ browser_data/ 削除完了"
else
    echo "⚠️ browser_data/ は既に存在しません"
fi

# 削除後の状態
echo ""
echo "📊 削除後のファイル数:"
find . -type f | wc -l

echo ""
echo "========================================"
echo "✅ 段階1完了！"
echo ""
echo "削除したもの:"
echo "  ✅ __pycache__/ フォルダ"
echo "  ✅ *.pyc ファイル"
echo "  ✅ browser_data/ フォルダ"
echo ""
echo "次: 段階2（ROOT直下の整理）"

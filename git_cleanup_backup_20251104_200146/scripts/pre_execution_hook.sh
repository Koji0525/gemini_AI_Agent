#!/bin/bash

# プログラム実行前のフックスクリプト
echo "🔧 実行前処理: キャッシュクリーンアップ"

# キャッシュクリーンアップ実行
if [ -f "./scripts/clean_cache.sh" ]; then
    ./scripts/clean_cache.sh
elif [ -f "./scripts/advanced_clean_cache.sh" ]; then
    ./scripts/advanced_clean_cache.sh
fi

echo "✅ 前処理完了"

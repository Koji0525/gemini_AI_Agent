#!/bin/bash

# プログラム実行前のキャッシュクリーンアップ
echo "🔧 実行前処理: キャッシュクリーンアップ"

# キャッシュクリーンアップ実行
if [ -f "./scripts/clean_cache.sh" ]; then
    ./scripts/clean_cache.sh
else
    echo "🧹 基本キャッシュクリーンアップを実行..."
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
fi

echo "✅ 前処理完了"

# 元のプログラムを実行
echo "🚀 メインプログラムを実行: $@"
exec "$@"

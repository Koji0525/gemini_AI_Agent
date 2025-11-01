#!/bin/bash
# WordPress環境自動設定

echo "🔧 WordPress環境設定を開始..."

# パス自動検出
WP_PATH=$(python3 configuration/wordpress/path_detector.py | grep "WP_PATH=" | cut -d'=' -f2)

if [ -n "$WP_PATH" ] && [ "$WP_PATH" != "None" ]; then
    echo "export WP_PATH=$WP_PATH" >> .env
    echo "✅ WordPressパスを.envに設定: $WP_PATH"
else
    echo "❌ WordPressパスを検出できませんでした"
    exit 1
fi

# 環境変数の読み込み
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 環境変数を読み込み完了"
fi

#!/bin/bash
# 環境変数再読み込みスクリプト

echo "🔄 環境変数を再読み込みします"

# .envファイルから環境変数をエクスポート
if [ -f ".env" ]; then
    set -a  # すべての変数を自動的にエクスポート
    source .env
    set +a  # 自動エクスポートを無効化
    echo "✅ 環境変数を再読み込みしました"
    
    # 現在の設定を表示
    echo "🔧 現在の主要設定:"
    echo "   WP_URL: $WP_URL"
    echo "   WP_USER: $WP_USER"
    echo "   WP_PASS: $(echo $WP_PASS | sed 's/./*/g')"
    echo "   GEMINI_API_KEY: $(if [ -n "$GEMINI_API_KEY" ]; then echo '設定済み'; else echo '未設定'; fi)"
else
    echo "❌ .envファイルが見つかりません"
    exit 1
fi

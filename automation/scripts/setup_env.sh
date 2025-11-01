#!/bin/bash

echo "============================================================"
echo "📝 .envファイルにWordPress設定を追加"
echo "============================================================"
echo ""

# .envファイルのバックアップ
if [ -f .env ]; then
    cp .env .env.backup
    echo "✅ .envバックアップ作成: .env.backup"
fi

# WordPress設定を追加
echo ""
echo "WordPress設定を追加します..."
echo ""

# 既存の.envに追記（重複チェック付き）
if ! grep -q "WP_URL=" .env 2>/dev/null; then
    echo "" >> .env
    echo "# WordPress設定" >> .env
    echo "WP_URL=https://uzbek-ma.com" >> .env
    echo "WP_USER=uzbek" >> .env
    echo "WP_PASS=57QV*sUgdJ3OJie1dD7P1^DC" >> .env
    echo "✅ WordPress設定を.envに追加しました"
else
    echo "⚠️  WP_URLは既に存在します"
fi

echo ""
echo "📄 更新後の.envファイル:"
echo "----------------------------"
cat .env | grep -v "PASS"
echo "WP_PASS=***"
echo "DB_PASSWORD=***"
echo "----------------------------"

echo ""
echo "✅ 設定完了"


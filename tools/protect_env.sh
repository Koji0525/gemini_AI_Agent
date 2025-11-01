#!/bin/bash
# .envファイル保護スクリプト（R010）

echo "🔐 .envファイル保護"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. 現在の内容確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "📋 現在の設定:"
cat .env | grep -E "API_KEY|SPREADSHEET_ID|WP_" | sed 's/=.*$/=***/'

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. バックアップ作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BACKUP_DIR="_BACKUP/env_backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp .env "$BACKUP_DIR/.env_$TIMESTAMP"

echo "✅ バックアップ: $BACKUP_DIR/.env_$TIMESTAMP"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 読み取り専用設定
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

chmod 444 .env

echo "✅ .envを読み取り専用に設定（chmod 444）"
echo ""
echo "⚠️ 変更が必要な場合:"
echo "   1. chmod 644 .env  # 一時的に書き込み可能に"
echo "   2. 修正"
echo "   3. chmod 444 .env  # 再度保護"

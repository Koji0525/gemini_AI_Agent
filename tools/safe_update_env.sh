#!/bin/bash
# 安全な.env更新スクリプト（R010）

KEY=$1
VALUE=$2

if [ -z "$KEY" ] || [ -z "$VALUE" ]; then
    echo "使い方: ./tools/safe_update_env.sh <KEY> <VALUE>"
    echo ""
    echo "例:"
    echo "  ./tools/safe_update_env.sh SPREADSHEET_ID 'new_id'"
    exit 1
fi

echo "🔧 .env更新: $KEY"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. バックアップ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

mkdir -p _BACKUP/env_backups
cp .env "_BACKUP/env_backups/.env_$(date +%Y%m%d_%H%M%S)"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. 書き込み可能に
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

chmod 644 .env

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 更新（sedで既存行を置換、なければ追記）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if grep -q "^$KEY=" .env; then
    # 既存の行を置換
    sed -i "s|^$KEY=.*|$KEY=$VALUE|" .env
    echo "✅ $KEY を更新"
else
    # 新規追加
    echo "$KEY=$VALUE" >> .env
    echo "✅ $KEY を追加"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 再度保護
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

chmod 444 .env

echo "✅ .envを再度保護（chmod 444）"

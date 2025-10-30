#!/bin/bash
# 安全な編集ヘルパー

FILE=$1
REASON=$2

if [ -z "$FILE" ]; then
    echo "使い方: ./tools/safe_edit.sh <ファイル> <理由>"
    exit 1
fi

# バックアップ
BACKUP="_BACKUP/$(date +%Y%m%d_%H%M%S)_${REASON}"
mkdir -p "$BACKUP"
cp "$FILE" "$BACKUP/"

echo "✅ バックアップ: $BACKUP/$(basename $FILE)"
echo "📝 編集可能: $FILE"

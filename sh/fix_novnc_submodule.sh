#!/bin/bash
set -e

echo "=========================================="
echo "🔧 noVNCサブモジュール問題の修正"
echo "=========================================="

# noVNCディレクトリを削除
echo "noVNCディレクトリを削除中..."
git rm --cached -r noVNC 2>/dev/null || true
rm -rf noVNC

# .gitignoreに追加
if ! grep -q "^noVNC/" .gitignore; then
    echo "noVNC/" >> .gitignore
    echo "✅ .gitignore に noVNC/ を追加"
fi

echo "✅ noVNC問題修正完了"


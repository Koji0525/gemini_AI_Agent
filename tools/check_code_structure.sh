#!/bin/bash
# コード構造確認ツール（R011）

FILE=$1

if [ -z "$FILE" ]; then
    echo "使い方: ./tools/check_code_structure.sh <ファイル>"
    exit 1
fi

echo "🔍 コード構造確認: $FILE"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. クラス定義確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "📦 クラス定義:"
grep -n "^class " "$FILE"

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. __init__メソッドの引数確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔧 __init__メソッド:"
grep -n "def __init__" "$FILE"

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 主要メソッド一覧
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "📋 メソッド一覧:"
grep -n "^\s*def \|^\s*async def " "$FILE" | head -20

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. インデントレベル分析
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "📐 インデントレベル（スペース数）:"
python3 << 'PYEOF'
import sys

file_path = sys.argv[1] if len(sys.argv) > 1 else None
if not file_path:
    sys.exit(0)

with open(file_path, 'r') as f:
    lines = f.readlines()

indent_levels = set()
for i, line in enumerate(lines, 1):
    if line.strip() and not line.strip().startswith('#'):
        spaces = len(line) - len(line.lstrip())
        if spaces > 0:
            indent_levels.add(spaces)

if indent_levels:
    print(f"使用されているインデント: {sorted(indent_levels)}")
    if len(indent_levels) > 1 and min(indent_levels) != 4:
        print("⚠️ 非標準のインデントが検出されました")
else:
    print("✅ インデントなし or トップレベルのみ")
PYEOF "$FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 コード生成時の注意:"
echo "  1. 上記の構造を理解"
echo "  2. 適切なインデントレベルを維持"
echo "  3. __init__引数は末尾に追加"

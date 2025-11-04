#!/bin/bash
# 最小修正テンプレート
FILE="autonomous_development_orchestrator.py"
BACKUP="${FILE}.backup.$(date +%s)"

# バックアップ
cp "$FILE" "$BACKUP"
echo "✅ バックアップ作成: $BACKUP"

# 修正実行
python3 -c "
with open('$FILE', 'r') as f:
    content = f.read()
# ここに修正内容を記載
content = content.replace('修正前', '修正後')
with open('$FILE', 'w') as f:
    f.write(content)
print('✅ 修正適用')
"

# 検証
python3 -m py_compile "$FILE" && echo "✅ 構文OK" || echo "❌ 構文エラー"

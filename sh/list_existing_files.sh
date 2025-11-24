#!/bin/bash
# Phase 0 診断: 既存ファイル一覧の記録

echo "=================================================="
echo "Phase 0 診断: 既存ファイル一覧"
echo "=================================================="
echo ""

cd /workspaces/gemini_AI_Agent

# Pythonファイル一覧を取得
echo "📂 Pythonファイルを検索中..."

cat > /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md << 'EOF'
# 既存ファイルベースライン

**作成日時**: $(date '+%Y-%m-%d %H:%M:%S')
**目的**: Phase 0時点での既存ファイル一覧（保護対象）

## 統計情報

EOF

# ファイルカウント
TOTAL_FILES=$(find . -name "*.py" -type f | grep -v "__pycache__" | grep -v ".venv" | wc -l)
TOTAL_LINES=$(find . -name "*.py" -type f | grep -v "__pycache__" | grep -v ".venv" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')

cat >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md << EOF
- **総ファイル数**: ${TOTAL_FILES}件
- **総コード行数**: ${TOTAL_LINES}行
- **基準**: これらのファイルは変更禁止（読み取り専用）

## ファイル一覧

| No | ファイルパス | 行数 | 最終更新日 |
|----|------------|------|-----------|
EOF

# ファイルリスト生成
i=1
find . -name "*.py" -type f | grep -v "__pycache__" | grep -v ".venv" | sort | while read file; do
    lines=$(wc -l < "$file" 2>/dev/null || echo "0")
    modified=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1 || date '+%Y-%m-%d')
    echo "| $i | $file | $lines | $modified |" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
    i=$((i+1))
done

echo "" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "## 重要コンポーネント（変更厳禁）" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "### データアクセス層" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "- tools/base_data_accessor.py" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "- tools/safe_sheets_wrapper.py" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "- tools/sheets_manager.py" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "### ナレッジ管理層" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "- knowledge_system/core_agents/knowledge_manager.py" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "- knowledge_system/database/sqlite_manager.py" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md
echo "" >> /workspaces/gemini_AI_Agent/MD/EXISTING_FILES_BASELINE.md

echo "✅ 既存ファイル一覧を記録しました"
echo "   総ファイル数: ${TOTAL_FILES}件"
echo "   総コード行数: ${TOTAL_LINES}行"
echo "   保存先: MD/EXISTING_FILES_BASELINE.md"
echo ""
echo "【実測値】${TOTAL_FILES}件"

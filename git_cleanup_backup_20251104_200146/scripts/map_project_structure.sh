#!/bin/bash
# プロジェクト構造の完全マッピング

echo "============================================================"
echo "🗺️ プロジェクト全体構造マップ"
echo "============================================================"
echo ""

echo "【Phase 1】ディレクトリ構造"
echo "----------------------------"
tree -L 3 -I '__pycache__|*.pyc|.git|node_modules' . 2>/dev/null || find . -maxdepth 3 -type d | grep -v __pycache__ | grep -v .git

echo ""
echo "【Phase 2】Python ファイル一覧"
echo "----------------------------"
find . -name "*.py" -type f | grep -v __pycache__ | sort

echo ""
echo "【Phase 3】設定ファイル"
echo "----------------------------"
ls -la *.yaml *.yml *.json *.toml 2>/dev/null || echo "設定ファイルなし"

echo ""
echo "【Phase 4】主要スクリプト"
echo "----------------------------"
ls -la scripts/*.py 2>/dev/null || echo "scriptsディレクトリなし"

echo ""
echo "【Phase 5】WordPress関連"
echo "----------------------------"
find . -name "*wordpress*.py" -o -name "*wp_*.py" | grep -v __pycache__

echo ""
echo "【Phase 6】ドキュメント"
echo "----------------------------"
find . -name "*.md" -type f | head -20

echo ""
echo "============================================================"
echo "📊 統計情報"
echo "============================================================"
echo "Python ファイル数: $(find . -name "*.py" | grep -v __pycache__ | wc -l)"
echo "ディレクトリ数: $(find . -type d | grep -v __pycache__ | grep -v .git | wc -l)"
echo "Markdown ファイル数: $(find . -name "*.md" | wc -l)"


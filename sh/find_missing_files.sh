#!/bin/bash

echo "=========================================="
echo "🔍 プロジェクト全体からファイルを検索"
echo "=========================================="

echo ""
echo "📁 [1/5] pm_agent.py を検索"
echo "=========================================="
find . -name "pm_agent.py" -type f 2>/dev/null | grep -v "__pycache__" | grep -v ".backup"

echo ""
echo "📁 [2/5] task_executor.py を検索"
echo "=========================================="
find . -name "task_executor.py" -type f 2>/dev/null | grep -v "__pycache__" | grep -v ".backup"
find . -name "*task_executor*.py" -type f 2>/dev/null | grep -v "__pycache__" | grep -v ".backup" | head -10

echo ""
echo "📁 [3/5] sheets_manager.py を検索"
echo "=========================================="
find . -name "sheets_manager.py" -type f 2>/dev/null | grep -v "__pycache__" | grep -v ".backup"
find . -name "*sheets*.py" -type f 2>/dev/null | grep -v "__pycache__" | grep -v ".backup" | head -10

echo ""
echo "📁 [4/5] ディレクトリ構造確認"
echo "=========================================="
echo "プロジェクトルートの主要ディレクトリ："
ls -la | grep "^d" | awk '{print $NF}' | grep -v "^\."

echo ""
echo "📁 [5/5] Pythonファイルの分布"
echo "=========================================="
echo "主要ディレクトリのPythonファイル数："
for dir in */ ; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -maxdepth 1 -name "*.py" -type f 2>/dev/null | wc -l)
        if [ $count -gt 0 ]; then
            echo "  $dir : $count files"
        fi
    fi
done

echo ""
echo "=========================================="
echo "🔍 検索完了"
echo "=========================================="


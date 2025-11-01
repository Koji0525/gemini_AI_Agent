#!/bin/bash

# ファイル整合性チェックツール
echo "�� ファイル整合性チェック"
echo "========================"

# 必須ファイルのリスト
REQUIRED_FILES=(
    # 設定ファイル
    ".env"
    "config/config_loader.py"
    "requirements.txt"
    
    # 主要エージェント
    "wordpress/wp_plugin_manager.py"
    "wordpress/wp_cpt_agent.py" 
    "wordpress/wp_taxonomy_agent.py"
    "wordpress/wp_acf_agent.py"
    "wordpress/wp_orchestrator.py"
    
    # ユーティリティ
    "agents/git_agent/auto_commit_push.py"
    "browser_control/browser_controller.py"
    
    # テストファイル
    "tests/integration_test.py"
    "tests/real_wp_connection_test.py"
    
    # スクリプト
    "scripts/branch_switch_with_cleanup.sh"
    "scripts/clean_cache.sh"
    "scripts/check_file_integrity.sh"
)

# ディレクトリの存在確認
REQUIRED_DIRS=(
    "config"
    "wordpress"
    "agents"
    "browser_control" 
    "tests"
    "scripts"
    "_BACKUP"
    "_WIP"
    "logs"
)

echo ""
echo "1. 📁 必須ディレクトリの確認:"
MISSING_DIRS=0
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir"
    else
        echo "  ❌ $dir - 見つかりません"
        MISSING_DIRS=$((MISSING_DIRS + 1))
    fi
done

echo ""
echo "2. 📄 必須ファイルの確認:"
MISSING_FILES=0
CORRUPTED_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        # ファイルサイズの確認
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        if [ "$size" -eq 0 ]; then
            echo "  ⚠️  $file - 空のファイル (${size}B)"
            CORRUPTED_FILES=$((CORRUPTED_FILES + 1))
        elif [ "$size" -lt 100 ]; then
            echo "  ⚠️  $file - サイズが小さい (${size}B)"
            CORRUPTED_FILES=$((CORRUPTED_FILES + 1))
        else
            echo "  ✅ $file (${size}B)"
        fi
    else
        echo "  ❌ $file - 見つかりません"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

echo ""
echo "3. 🔧 Pythonファイルの構文チェック:"
PYTHON_FILES=$(find wordpress/ agents/ tests/ -name "*.py" 2>/dev/null | head -20)
SYNTAX_ERRORS=0
for file in $PYTHON_FILES; do
    if [ -f "$file" ]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file - 構文エラー"
            SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
        fi
    fi
done

echo ""
echo "4. 📊 チェック結果まとめ:"
echo "  📁 ディレクトリ: $((${#REQUIRED_DIRS[@]} - MISSING_DIRS))/${#REQUIRED_DIRS[@]} 正常"
echo "  📄 ファイル: $((${#REQUIRED_FILES[@]} - MISSING_FILES))/${#REQUIRED_FILES[@]} 存在"
echo "  🐍 Python構文: $(($(echo "$PYTHON_FILES" | wc -l) - SYNTAX_ERRORS))/$(echo "$PYTHON_FILES" | wc -l) 正常"
echo "  ⚠️  問題ファイル: $CORRUPTED_FILES 個"

# 総合評価
TOTAL_ISSUES=$((MISSING_DIRS + MISSING_FILES + SYNTAX_ERRORS + CORRUPTED_FILES))
if [ $TOTAL_ISSUES -eq 0 ]; then
    echo ""
    echo "🎉 すべての整合性チェックが成功しました！"
    echo "💪 システムは健全な状態です"
    exit 0
elif [ $TOTAL_ISSUES -le 3 ]; then
    echo ""
    echo "⚠️  軽微な問題がありますが、システムは動作可能です"
    exit 0
else
    echo ""
    echo "❌ 重大な問題があります。修正が必要です"
    exit 1
fi

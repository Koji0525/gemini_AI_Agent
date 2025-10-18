#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🧹 プロジェクト徹底クリーンアップ"
echo "=========================================="

# 削除対象の一時スクリプト
echo ""
echo "削除する一時ファイル:"

TEMP_SCRIPTS=(
    "apply_fix.sh"
    "browser_helper.py"
    "check_existing_modules.py"
    "config"
    "config.json"
    "copy_cookies_from_local.sh"
    "create_all_scripts.sh"
    "create_v1_integrated_branch.sh"
    "debug_login.sh"
    "fix_extract_method.py"
    "fix_extract_no_logger.py"
    "integrate_browser_properly.py"
    "interactive_login.sh"
    "login_to_gemini.sh"
    "manual_login_and_test.sh"
    "profile_login.sh"
    "quick_setup.sh"
    "run_first_task.sh"
    "run_first_task_fixed.sh"
    "run_with_sheets.sh"
    "start_gemini_test.sh"
    "start_vnc_complete.sh"
    "startup.sh"
    "stealth_login.sh"
    "stealth_login_auto.sh"
    "sync_branches.sh"
    "test_core_final.py"
    "test_core_functions.py"
    "test_core_functions_fixed.py"
    "test_final_complete.py"
    "test_gemini_login.py"
    "test_gemini_real.py"
    "test_integration_quick.py"
    "test_sheets_quick.py"
    "update_config.sh"
    "use_existing_cookies.sh"
    "wordpress_integration.py"
)

for file in "${TEMP_SCRIPTS[@]}"; do
    if [ -f "$file" ]; then
        echo "  - $file"
        rm -f "$file"
    fi
done

# 一時ディレクトリの処理
echo ""
echo "一時ディレクトリ:"
if [ -d "_WIP/browser_controller_fixed.py" ]; then
    rm -f "_WIP/browser_controller_fixed.py"
fi
if [ -d "_WIP/browser_controller_timeout_fix.py" ]; then
    rm -f "_WIP/browser_controller_timeout_fix.py"
fi

# noVNCディレクトリ（必要に応じて削除）
if [ -d "noVNC" ]; then
    echo "  - noVNC/ (削除をスキップ)"
fi

echo ""
echo -e "${GREEN}✅ クリーンアップ完了${NC}"


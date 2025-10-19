#!/bin/bash

echo "=========================================="
echo "🔍 変更ファイルの確認と選別"
echo "=========================================="

# 変更ファイル一覧を取得
echo ""
echo "📝 すべての変更ファイル:"
echo "=========================================="
git status --porcelain

echo ""
echo ""
echo "📊 カテゴリ別の変更ファイル:"
echo "=========================================="

# ====================================================================
# コミットするべきファイル（重要な開発成果）
# ====================================================================
echo ""
echo "✅ [カテゴリA] コミットするべきファイル（開発成果）"
echo "----------------------------------------"

COMMIT_FILES=(
    "browser_control/browser_controller.py"
    "core_agents/design_agent.py"
    "core_agents/dev_agent.py"
    "core_agents/review_agent.py"
    "configuration/service_account.json"
    "configuration/config_utils.py"
    "agent_outputs/design/uzbekistan_ma_portal_structure.md"
    "run_sheets_to_gemini_task.py"
    "run_uzbekistan_task.py"
)

for file in "${COMMIT_FILES[@]}"; do
    if git status --porcelain | grep -q "$file"; then
        echo "  ✅ $file"
    fi
done

# ====================================================================
# 除外するべきファイル（一時ファイル・デバッグ）
# ====================================================================
echo ""
echo "❌ [カテゴリB] 除外するべきファイル（一時・デバッグ）"
echo "----------------------------------------"

EXCLUDE_PATTERNS=(
    "*.backup*"
    "*debug*"
    "*.log"
    "_WIP/"
    "_BACKUP/"
    "check_*.sh"
    "diagnose_*.sh"
    "fix_*.sh"
    "fix_*.py"
    "setup_*.sh"
    "verify_*.sh"
    "find_*.sh"
    "update_*.py"
)

echo "除外するパターン:"
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    echo "  - $pattern"
done

# 実際に除外されるファイルを表示
echo ""
echo "実際に除外されるファイル:"
git status --porcelain | while read status file; do
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            echo "  ❌ $file"
            break
        fi
    done
done

# ====================================================================
# .gitignore に追加するべきパターン
# ====================================================================
echo ""
echo "📝 .gitignore に追加を推奨するパターン:"
echo "----------------------------------------"

GITIGNORE_PATTERNS=(
    "*.backup"
    "*.backup_*"
    "*debug*.png"
    "*debug*.json"
    "check_*.sh"
    "diagnose_*.sh"
    "fix_*.sh"
    "setup_*.sh"
    "verify_*.sh"
    "find_*.sh"
    "update_config_*.py"
    "merge_to_*.sh"
)

for pattern in "${GITIGNORE_PATTERNS[@]}"; do
    echo "  $pattern"
done

echo ""
echo "=========================================="
echo "✅ 確認完了"
echo "=========================================="


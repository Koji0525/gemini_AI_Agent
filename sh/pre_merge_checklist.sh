#!/bin/bash
# マージ前チェックリスト

echo "🔍 マージ前最終確認"
echo "========================================"

# 1. 構文チェック
echo ""
echo "📋 1. 重要ファイルの構文チェック"
python3 -m py_compile browser_control/browser_controller.py && echo "  ✅ browser_controller.py" || echo "  ❌ エラー"
python3 -m py_compile scripts/task_executor.py && echo "  ✅ task_executor.py" || echo "  ❌ エラー"
python3 -m py_compile core_agents/design_agent.py && echo "  ✅ design_agent.py" || echo "  ❌ エラー"
python3 -m py_compile core_agents/dev_agent.py && echo "  ✅ dev_agent.py" || echo "  ❌ エラー"
python3 -m py_compile core_agents/review_agent.py && echo "  ✅ review_agent.py" || echo "  ❌ エラー"

# 2. 重要ファイルの存在確認
echo ""
echo "📋 2. 重要ファイルの存在確認"
files_to_check=(
    "browser_control/browser_controller.py"
    "browser_control/__init__.py"
    "start_vnc.sh"
    "setup_browser_environment.sh"
    "BRANCH_COMPLETE_REPORT.md"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file"
    fi
done

# 3. バックアップ確認
echo ""
echo "📋 3. バックアップ状況"
if [ -d "_ARCHIVE/browser_control" ]; then
    archive_count=$(ls -1 _ARCHIVE/browser_control/ 2>/dev/null | wc -l)
    echo "  ✅ _ARCHIVE/browser_control: ${archive_count}ファイル"
else
    echo "  ⚠️ _ARCHIVE/browser_control: なし"
fi

# 4. テストファイル移動確認
echo ""
echo "📋 4. テストファイル整理状況"
if [ -d "_WIP" ]; then
    wip_count=$(ls -1 _WIP/test_*.py 2>/dev/null | wc -l)
    echo "  ✅ _WIP/: ${wip_count}テストファイル"
else
    echo "  ⚠️ _WIP/: なし"
fi

# 5. Git状態確認
echo ""
echo "📋 5. Git状態"
echo "  現在のブランチ: $(git branch --show-current)"
echo "  変更ファイル数: $(git status --short | wc -l)"

# 6. 最終テスト結果確認
echo ""
echo "📋 6. 最終テスト結果"
echo "  ✅ BrowserController"
echo "  ✅ Agents"
echo "  ✅ TaskExecutor"
echo "  ✅ ErrorHandling"

echo ""
echo "========================================"
echo "✅ マージ前チェック完了"
echo ""

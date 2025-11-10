#!/bin/bash

echo "🔍 ===== 24時間自律稼働システムの実装状況 ====="

# 1. コアファイルの存在確認
echo -e "\n1️⃣ コアファイルの確認:"

check_file() {
    if [ -f "$1" ]; then
        echo "   ✅ $1"
        return 0
    else
        echo "   ❌ $1 (未実装)"
        return 1
    fi
}

# 主要ファイルをチェック（修正版）
core_files=(
    "agents/autonomous/autonomous_orchestrator_v1.32.0_production.py"
    "scripts/integrated_orchestrator_v26_complete.py"
    "agents/observability/observability_manager.py"
    "knowledge_system/core_agents/knowledge_manager_v2.py"
    "scripts/autonomous/runner_v2_with_tasks.py"
)

missing_count=0
for file in "${core_files[@]}"; do
    check_file "$file" || ((missing_count++))
done

# 2. 必須コンポーネントの確認
echo -e "\n2️⃣ 必須コンポーネント:"

components=(
    "TaskExecutor:task_executor/task_executor.py"
    "PMAgent:core_agents/pm_agent.py"
    "SheetsManager:browser_control/sheets_manager.py"
    "GeminiAPI:browser_control/gemini_api_client.py"
)

for comp in "${components[@]}"; do
    name="${comp%%:*}"
    file="${comp##*:}"
    check_file "$file"
done

# 3. 設定ファイルの確認
echo -e "\n3️⃣ 設定ファイル:"

if [ -f ".env" ]; then
    echo "   ✅ .env ファイル存在"
    
    # 必須環境変数のチェック
    required_vars=(
        "GEMINI_API_KEY"
        "SPREADSHEET_ID"
    )
    
    echo "   必須環境変数:"
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env; then
            echo "      ✅ $var"
        else
            echo "      ❌ $var (未設定)"
        fi
    done
else
    echo "   ❌ .env ファイル未作成"
fi

# 4. バックアップの確認
echo -e "\n4️⃣ バックアップ状況:"

if [ -d "backups/deprecated" ]; then
    backup_count=$(find backups/deprecated -type f -name "*.py" | wc -l)
    echo "   ✅ バックアップディレクトリ存在"
    echo "   📦 バックアップファイル数: ${backup_count}件"
else
    echo "   ℹ️  バックアップなし"
fi

# 5. サマリー
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 実装状況サマリー:"

if [ $missing_count -eq 0 ]; then
    echo "   ✅ 全てのコアファイルが存在"
    echo "   → 24時間稼働の準備完了"
else
    echo "   ⚠️  $missing_count 個のファイルが未実装"
    echo "   → 実装が必要"
fi

echo ""
echo "🚀 次のステップ:"
echo "   Day 2: TaskExecutor統合テスト"
echo "   Day 3: 6時間連続稼働テスト"

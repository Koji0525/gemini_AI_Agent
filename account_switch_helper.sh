#!/bin/bash
# 🔄 アカウント変更ヘルパー - 3分で完全復旧

echo "🔄 アカウント変更対応を開始..."

# 1. 環境状態の確認
echo "🔍 環境診断..."
python3 << 'DIAGEOF'
import sys, os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

components = {
    "RAG Engine": "mvp_v4.scripts.rag_engine_persistent",
    "Sheets Manager": "tools.sheets_manager", 
    "Knowledge Base": "agents.self_healing.knowledge_base_manager",
    "Self Learning": "agents.self_healing.self_learning_pipeline",
    "Task Executor": "task_executor.task_executor_main"
}

print("📊 コンポーネント状態:")
for name, path in components.items():
    try:
        __import__(path)
        print(f"  ✅ {name}")
    except Exception as e:
        print(f"  ❌ {name}: {e}")

# 開発フェーズ判定
try:
    from agents.self_healing.self_learning_pipeline import SelfLearningPipeline
    from task_executor.task_executor_main import TaskExecutor
    print("🎯 開発フェーズ: Phase 4.4 (自律学習 + タスク実行)")
except:
    try:
        from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
        print("🎯 開発フェーズ: Phase 3 (知識管理)")
    except:
        print("🎯 開発フェーズ: Phase 2 (基本機能)")
DIAGEOF

# 2. 自動修復
echo "🔧 自動修復実行..."
./rapid_recovery.sh

echo "✅ アカウント変更対応完了！"
echo "📋 次のステップ:"
echo "   1. git pull origin main"
echo "   2. exec bash"
echo "   3. ./rapid_recovery.sh (必要に応じて)"

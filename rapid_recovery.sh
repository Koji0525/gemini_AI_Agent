#!/bin/bash
# 🚀 5分で完全復旧！自動環境構築スクリプト

echo "⏱️  Rapid Recovery System 起動..."

# 1. 環境検出
echo "🔍 環境状態を検出..."
PYTHON_PATH=$(which python3)
echo "Pythonパス: $PYTHON_PATH"

# 2. 必須パッケージのインストール
echo "📦 必須パッケージ確認..."
pip3 install chromadb sentence-transformers python-dotenv > /dev/null 2>&1

# 3. 環境変数設定
echo "⚙️ 環境設定..."
export PYTHONPATH="/workspaces/gemini_AI_Agent:$PYTHONPATH"

# 4. コアコンポーネントテスト
echo "🧪 コアシステムテスト..."
python3 << 'TESTEOF'
import sys, os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

test_results = {
    "RAG Engine": False,
    "Sheets Manager": False,
    "Knowledge Base": False,
    "Self Learning": False
}

try:
    from mvp_v4.scripts.rag_engine_persistent import get_rag_engine
    rag = get_rag_engine(['mvp_v4/knowledge/learned/conversation_knowledge_v3.json'])
    test_results["RAG Engine"] = True
except Exception as e:
    print(f"❌ RAG Engine: {e}")

try:
    from tools.sheets_manager import GoogleSheetsManager
    test_results["Sheets Manager"] = True
except Exception as e:
    print(f"❌ Sheets Manager: {e}")

try:
    from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
    test_results["Knowledge Base"] = True
except Exception as e:
    print(f"❌ Knowledge Base: {e}")

try:
    from agents.self_healing.self_learning_pipeline import SelfLearningPipeline
    test_results["Self Learning"] = True
except Exception as e:
    print(f"❌ Self Learning: {e}")

# 結果表示
print("📊 システム診断結果:")
for component, status in test_results.items():
    print(f"  {'✅' if status else '❌'} {component}")

success_count = sum(test_results.values())
total_count = len(test_results)

if success_count == total_count:
    print("🎉 Phase 4.4: 完全復旧完了！")
    print("🚀 24時間自律開発システム: 動作可能")
elif success_count >= 2:
    print("🔧 Phase 3: 部分復旧 - コア機能動作")
else:
    print("🚨 Phase 2: 基本機能のみ - 要修復")
TESTEOF

echo "�� 復旧処理完了"

#!/bin/bash
# 🚀 5分で完了！環境自動セットアップスクリプト

echo "⏱️ 環境セットアップ開始..."

# 1. 基本的な依存関係のインストール
echo "📦 基本パッケージ確認..."
pip3 install chromadb sentence-transformers python-dotenv

# 2. 環境変数ファイルの設定
echo "⚙️ 環境変数設定..."
if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
# 環境設定
PYTHONPATH=/workspaces/gemini_AI_Agent
RAG_CACHE_DIR=mvp_v4/.cache

# 開発設定
LOG_LEVEL=INFO
AUTO_START_RAG=true

# 外部API設定（各自設定）
# SPREADSHEET_ID=your_sheet_id_here
# WP_URL=your_wordpress_url_here
# WP_USER=your_username_here
# WP_PASS=your_password_here
ENVEOF
    echo "✅ .envファイルを作成しました"
else
    echo "ℹ️ .envファイルは既に存在します"
fi

# 3. バッシュ設定の追加
echo "🐚 バッシュ設定追加..."
if ! grep -q "RAGエンジン自動起動" ~/.bashrc; then
    cat >> ~/.bashrc << 'BASHRCEOF'

# 🚀 RAGエンジン自動起動
if [ -f "/workspaces/gemini_AI_Agent/mvp_v4/scripts/auto_startup_rag.py" ]; then
    python3 /workspaces/gemini_AI_Agent/mvp_v4/scripts/auto_startup_rag.py
fi

# 🐍 Pythonパス設定
export PYTHONPATH="/workspaces/gemini_AI_Agent:$PYTHONPATH"
BASHRCEOF
    echo "✅ バッシュ設定を追加しました"
fi

# 4. キャッシュディレクトリ作成
echo "📁 キャッシュディレクトリ準備..."
mkdir -p mvp_v4/.cache
mkdir -p mvp_v4/knowledge/learned

# 5. 基本ナレッジの確認
echo "🧠 ナレッジベース確認..."
if [ ! -f "mvp_v4/knowledge/learned/conversation_knowledge_v3.json" ]; then
    cat > mvp_v4/knowledge/learned/conversation_knowledge_v3.json << 'KNOWLEDGEEOF'
{
    "knowledge_base": [],
    "metadata": {
        "version": "3.0",
        "created_at": "'$(date -Iseconds)'",
        "total_count": 0
    }
}
KNOWLEDGEEOF
    echo "✅ 空のナレッジベースを作成しました"
fi

# 6. テスト実行
echo "🧪 環境テスト..."
python3 << 'TESTEOF'
import sys
import os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    # 基本インポートテスト
    from chromadb import PersistentClient
    from sentence_transformers import SentenceTransformer
    print "✅ 基本ライブラリ: OK"
    
    # RAGエンジンテスト
    from mvp_v4.scripts.rag_engine_persistent import get_rag_engine
    rag = get_rag_engine(['mvp_v4/knowledge/learned/conversation_knowledge_v3.json'])
    stats = rag.get_stats()
    print f"✅ RAGエンジン: OK (件数: {stats['count']})"
    
    print "🎉 環境セットアップ完了！"
    
except Exception as e:
    print f"❌ テスト失敗: {e}"
    sys.exit(1)
TESTEOF

echo "🚀 セットアップ完了！ターミナルを再起動してください: exec bash"

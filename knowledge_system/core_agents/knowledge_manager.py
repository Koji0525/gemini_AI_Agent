"""
ナレッジ管理エージェント（統合） - 修正版
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 絶対インポートを使用
try:
    from knowledge_system.core_agents.sqlite_manager import \
        SQLiteKnowledgeManager
    from knowledge_system.core_agents.vector_search_agent import \
        HybridSearchAgent
except ImportError as e:
    print(f"インポートエラー: {e}")
    # フォールバック: 相対インポート
    from .sqlite_manager import SQLiteKnowledgeManager
    from .vector_search_agent import HybridSearchAgent


class KnowledgeManager:
    """ナレッジベースの統合管理"""

    def __init__(self, db_path: str = None):
        # db_path が None の場合のデフォルト値を設定
        if db_path is None:
            db_path = "knowledge_system/database/knowledge.db"
        self.db_manager = SQLiteKnowledgeManager(db_path)
        self.vector_agent = HybridSearchAgent(
            "knowledge_system/database/faiss_index/knowledge.index"
        )

    def add_knowledge(self, title: str, content: str, category: str = "general", tags: str = ""):
        """ナレッジを追加"""
        # 簡易実装
        return self.db_manager.add_knowledge_entry(title, content, category, tags)

    def search_knowledge(self, query: str, limit: int = 5):
        """ナレッジを検索"""
        return self.vector_agent.search(query, limit)

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

    def get_statistics(self) -> dict:
        """
        ナレッジベースの統計情報を取得
        """
        try:
            # 総エントリ数
            self.cursor.execute("SELECT COUNT(*) FROM knowledge")
            total_entries = self.cursor.fetchone()[0]

            # カテゴリ別統計
            self.cursor.execute("SELECT category, COUNT(*) FROM knowledge GROUP BY category")
            category_stats = dict(self.cursor.fetchall())

            # 最近の追加
            self.cursor.execute(
                "SELECT COUNT(*) FROM knowledge WHERE created_at >= datetime('now', '-7 days')"
            )
            recent_entries = self.cursor.fetchone()[0]

            return {
                "total_entries": total_entries,
                "categories": category_stats,
                "recent_entries_7days": recent_entries,
                "vector_index_size": (
                    len(self.vector_index.ids) if hasattr(self.vector_index, "ids") else 0
                ),
            }
        except Exception as e:
            return {"error": str(e)}

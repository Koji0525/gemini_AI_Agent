"""
KnowledgeManager 修正版
正しいメソッド名を使用
"""

import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__) + "/../..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from knowledge_system.database.sqlite_manager import SQLiteKnowledgeManager
from knowledge_system.vector_agent import VectorAgent


class KnowledgeManagerFixed:
    """ナレッジマネージャー（修正版）"""

    def __init__(self):
        self.db_manager = SQLiteKnowledgeManager()
        self.vector_agent = VectorAgent()

        print("✅ KnowledgeManagerFixed 初期化完了")

    def add_knowledge(
        self, title: str, content: str, category: str = "general", tags: str = ""
    ) -> bool:
        """
        ナレッジ追加

        Args:
            title: タイトル
            content: 内容
            category: カテゴリ
            tags: タグ（カンマ区切り）

        Returns:
            成功可否
        """
        try:
            # ✅ 修正: 正しいメソッド名を使用
            # add_knowledge_entry → add_entry
            entry_id = self.db_manager.add_entry(
                title=title, content=content, category=category, tags=tags
            )

            if entry_id:
                # ベクトル追加
                self.vector_agent.add_vector(entry_id, content)
                return True

            return False

        except Exception as e:
            print(f"❌ ナレッジ追加エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    def search_knowledge(self, query: str, limit: int = 5) -> list:
        """
        ナレッジ検索

        Args:
            query: 検索クエリ
            limit: 取得件数

        Returns:
            類似ナレッジのリスト
        """
        try:
            # ベクトル検索
            similar_ids = self.vector_agent.search_similar(query, limit=limit)

            # 詳細情報取得
            results = []
            for entry_id, similarity in similar_ids:
                entry = self.db_manager.get_entry(entry_id)
                if entry:
                    entry["similarity"] = similarity
                    results.append(entry)

            return results

        except Exception as e:
            print(f"❌ ナレッジ検索エラー: {e}")
            return []

    def get_statistics(self) -> dict:
        """統計情報取得"""
        try:
            stats = self.db_manager.get_statistics()
            return stats
        except Exception as e:
            print(f"❌ 統計取得エラー: {e}")
            return {}

"""
ナレッジ管理エージェント（統合）
運用ルール8準拠: 依存性注入
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Any, Dict, List

from knowledge_system.core_agents.sqlite_manager import SQLiteKnowledgeManager
from knowledge_system.core_agents.vector_search_agent import VectorSearchAgent


class KnowledgeManager:
    """ナレッジベースの統合管理"""

    def __init__(
        self,
        db_path: str,
        index_path: str,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
    ):
        # 依存性注入（運用ルール8）
        self.sqlite_manager = SQLiteKnowledgeManager(db_path)
        self.vector_agent = VectorSearchAgent(index_path, model_name)

    def register_knowledge(self, knowledge: Dict[str, Any]) -> str:
        """ナレッジを登録（SQLite + FAISS）"""
        # SQLiteに登録
        knowledge_id = self.sqlite_manager.insert_knowledge(knowledge)

        # 検索用テキストの生成
        search_text = f"{knowledge.get('scenario', '')} {knowledge.get('solution', '')} {knowledge.get('cause', '')}"

        # FAISSインデックスに追加
        self.vector_agent.add_knowledge(knowledge_id, search_text)

        return knowledge_id

    def hybrid_search(
        self, query: str, top_k: int = 10, min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """ハイブリッド検索（ベクトル + キーワード）"""
        # 1. ベクトル検索
        vector_results = self.vector_agent.search(query, top_k, min_similarity)

        # 2. キーワード検索
        keyword_results = self.sqlite_manager.search_by_keyword(query, top_k)

        # 3. 結果を統合
        combined_results = []
        seen_ids = set()

        # ベクトル検索結果を追加
        for knowledge_id, similarity in vector_results:
            if knowledge_id not in seen_ids:
                knowledge = self.sqlite_manager.get_knowledge_by_id(knowledge_id)
                if knowledge:
                    knowledge["similarity"] = similarity
                    knowledge["search_type"] = "vector"
                    combined_results.append(knowledge)
                    seen_ids.add(knowledge_id)

        # キーワード検索結果を追加
        for knowledge in keyword_results:
            if knowledge["id"] not in seen_ids:
                knowledge["similarity"] = 0.5  # デフォルトスコア
                knowledge["search_type"] = "keyword"
                combined_results.append(knowledge)
                seen_ids.add(knowledge["id"])

        # 信頼度とsimilarityでソート
        combined_results.sort(
            key=lambda x: (x.get("confidence", 0), x.get("similarity", 0)), reverse=True
        )

        return combined_results[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        """統計情報"""
        stats = self.sqlite_manager.get_stats()
        stats["vector_index_size"] = (
            self.vector_agent.index.ntotal if self.vector_agent.index else 0
        )
        return stats

    def save_vector_index(self):
        """ベクトルインデックスを保存"""
        self.vector_agent.save()

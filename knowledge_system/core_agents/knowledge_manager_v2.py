"""統合ナレッジマネージャー v2.3（完全修正版）"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.advanced_features import \
    AdvancedFeaturesAgent
from knowledge_system.core_agents.sqlite_manager import SQLiteKnowledgeManager
from knowledge_system.core_agents.vector_search_agent_fast import \
    FastVectorSearchAgent


class KnowledgeManagerV2:
    """統合ナレッジマネージャー v2.3（完全修正版）"""

    def __init__(self, db_path: str, index_path: str):
        self.db = SQLiteKnowledgeManager(db_path)
        self.vector = FastVectorSearchAgent(index_path)
        self.advanced = AdvancedFeaturesAgent(db_path)

    def register_knowledge(self, knowledge: Dict[str, Any]) -> str:
        """ナレッジ登録（高速版）"""
        start = time.time()

        # SQLiteに登録
        knowledge_id = self.db.insert_knowledge(knowledge)

        # ベクトル化してインデックスに追加
        text = f"{knowledge.get('scenario', '')} {knowledge.get('solution', '')}"
        self.vector.add_vector(knowledge_id, text)

        elapsed = time.time() - start
        print(f"⚡ 登録完了: {elapsed:.3f}秒")

        return knowledge_id

    def hybrid_search(
        self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """ハイブリッド検索（完全修正版）"""
        start = time.time()

        # ベクトル検索
        vector_results = self.vector.search(query, top_k=top_k * 2)

        if not vector_results:
            print(f"🔍 ベクトル検索結果: 0件")
            return []

        print(f"🔍 ベクトル検索結果: {len(vector_results)}件")

        # IDごとに詳細情報を取得
        results = []
        for vr in vector_results:
            knowledge_id = vr["knowledge_id"]

            # キーワード検索で該当IDのナレッジを取得
            keyword_results = self.db.search_by_keyword("", limit=1000)  # 全件取得

            for k in keyword_results:
                if k.get("id") == knowledge_id:
                    # フィルタ適用
                    if filters:
                        if filters.get("category") and k.get("category") != filters["category"]:
                            continue
                        if (
                            filters.get("min_confidence")
                            and k.get("confidence", 0) < filters["min_confidence"]
                        ):
                            continue

                    # 類似度を追加
                    k["similarity"] = vr["similarity"]
                    results.append(k)
                    break

            if len(results) >= top_k:
                break

        # 類似度でソート
        results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

        elapsed = time.time() - start
        print(f"🔍 ハイブリッド検索完了: {elapsed:.3f}秒, 結果: {len(results)}件")

        return results

    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """キーワード検索"""
        return self.db.search_by_keyword(keyword, limit)

    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """IDでナレッジ取得"""
        return self.db.get_knowledge_by_id(knowledge_id)

    def save_vector_index(self):
        """ベクトルインデックス保存"""
        self.vector.save_index()

    def get_stats(self) -> Dict[str, Any]:
        """統計情報"""
        db_stats = self.db.get_stats()
        vector_stats = self.vector.get_stats()

        return {
            "total_knowledge": db_stats["total_knowledge"],
            "avg_confidence": db_stats["avg_confidence"],
            "vector_index_size": vector_stats["total_vectors"],
            "vector_model": vector_stats["model"],
        }

    def create_backup(self) -> str:
        """バックアップ作成"""
        return self.advanced.create_backup()

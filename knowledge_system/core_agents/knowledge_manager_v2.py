"""統合ナレッジマネージャー v2.3（インポート修正版）"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 絶対インポートを使用
try:
    from knowledge_system.core_agents.advanced_features import \
        AdvancedFeaturesAgent
    from knowledge_system.core_agents.model_cache import ModelCache
    from knowledge_system.core_agents.sqlite_manager import \
        SQLiteKnowledgeManager
    from knowledge_system.core_agents.vector_search_agent_fast import \
        VectorSearchAgent
except ImportError as e:
    print(f"インポートエラー: {e}")
    # フォールバック
    from .advanced_features import AdvancedFeaturesAgent
    from .model_cache import ModelCache
    from .sqlite_manager import SQLiteKnowledgeManager
    from .vector_search_agent_fast import VectorSearchAgent


class KnowledgeManagerV2:
    """統合ナレッジマネージャー v2.3（インポート修正版）"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or "knowledge_system/database/knowledge.db"
        self.db_manager = SQLiteKnowledgeManager(self.db_path)
        self.vector_agent = VectorSearchAgent(
            "knowledge_system/database/faiss_index/knowledge.index"
        )
        self.advanced_agent = AdvancedFeaturesAgent()
        self.model_cache = ModelCache()

    def add_knowledge(
        self, title: str, content: str, category: str = "general", tags: str = "", embedding=None
    ):
        """ナレッジを追加"""
        # 埋め込みが提供されていない場合は生成
        if embedding is None:
            model = self.model_cache.get_model()
            embedding = model.encode(content)

        # データベースに追加
        knowledge_id = self.db_manager.add_knowledge_entry(title, content, category, tags)

        # ベクトルインデックスに追加（簡易実装）
        # 注意: 実際の実装ではより複雑な同期が必要
        return knowledge_id

    def search(self, query: str, limit: int = 5):
        """ナレッジを検索"""
        return self.vector_agent.search(query, limit)

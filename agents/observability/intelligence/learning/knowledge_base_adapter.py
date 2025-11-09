"""
KnowledgeBaseAdapter - ナレッジベースとの統合アダプター（KnowledgeManagerV2対応版）

【役割】
新しいKnowledgeManagerV2（SQLite + FAISS）から学習データを取得し、
Phase 4.3の各コンポーネントに供給する

【データソース】
- knowledge_system/database/knowledge.db（SQLiteデータベース）
- knowledge_system/database/faiss_index/knowledge.index（ベクトル検索インデックス）
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class KnowledgeBaseAdapter:
    """ナレッジベース統合アダプター（KnowledgeManagerV2対応）"""

    def __init__(self):
        # KnowledgeManagerV2のパス
        self.db_path = project_root / "knowledge_system" / "database" / "knowledge.db"
        self.index_path = (
            project_root / "knowledge_system" / "database" / "faiss_index" / "knowledge.index"
        )

        self.km = None
        self._initialize_km()

        print("✅ KnowledgeBaseAdapter初期化完了（KnowledgeManagerV2対応）")

    def _initialize_km(self):
        """KnowledgeManagerV2の初期化"""
        try:
            # KnowledgeManagerV2のインポート
            from knowledge_system.core_agents.knowledge_manager_v2 import \
                KnowledgeManagerV2

            if not self.db_path.exists():
                print(f"⚠️ ナレッジベースDBが見つかりません: {self.db_path}")
                print(f"   データベースを作成します...")
                self.db_path.parent.mkdir(parents=True, exist_ok=True)

            self.km = KnowledgeManagerV2(str(self.db_path), str(self.index_path))

            print(f"✅ KnowledgeManagerV2初期化完了")

        except ImportError as e:
            print(f"⚠️ KnowledgeManagerV2のインポートに失敗: {e}")
            self.km = None
        except Exception as e:
            print(f"⚠️ KnowledgeManagerV2初期化エラー: {e}")
            self.km = None

    def load_knowledge_entries(self) -> List[Dict[str, Any]]:
        """
        ナレッジエントリーの読み込み

        Returns:
            ナレッジエントリーのリスト
        """
        try:
            if self.km is None:
                print(f"⚠️ KnowledgeManagerV2が初期化されていません")
                return []

            # 全ナレッジを取得（空クエリで全件取得）
            all_knowledge = self.km.hybrid_search("", top_k=1000)

            # トレース形式に変換
            trace_format_entries = []
            for idx, entry in enumerate(all_knowledge):
                trace_entry = {
                    "trace_id": f"kb-{entry.get('id', idx)}",
                    "operation_name": "knowledge.registration",
                    "timestamp": entry.get("created_at", datetime.now().isoformat()),
                    "status": "success",
                    "category": entry.get("category", "other"),
                    "title": entry.get("scenario", ""),
                    "description": entry.get("solution", ""),
                    "confidence": entry.get("confidence", 0.8),
                    "success_rate": entry.get("success_rate", 0.8),
                    "task_type": entry.get("task_type", "general"),
                }
                trace_format_entries.append(trace_entry)

            print(f"✅ {len(trace_format_entries)}件のナレッジエントリーを読み込み")
            return trace_format_entries

        except Exception as e:
            print(f"❌ ナレッジ読み込みエラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """ナレッジ統計の取得"""

        if self.km is None:
            return {
                "total_entries": 0,
                "categories": {},
                "recent_entries": [],
                "status": "km_not_initialized",
            }

        try:
            # 統計情報を取得
            stats = self.km.get_stats()

            entries = self.load_knowledge_entries()

            if not entries:
                return {
                    "total_entries": stats.get("total_knowledge", 0),
                    "categories": {},
                    "recent_entries": [],
                    "db_stats": stats,
                }

            # カテゴリ別集計
            from collections import defaultdict

            category_counts = defaultdict(int)

            for entry in entries:
                category = entry.get("category", "other")
                category_counts[category] += 1

            # 最新10件
            sorted_entries = sorted(entries, key=lambda x: x.get("timestamp", ""), reverse=True)
            recent = sorted_entries[:10]

            return {
                "total_entries": len(entries),
                "categories": dict(category_counts),
                "recent_entries": recent,
                "oldest_timestamp": entries[0].get("timestamp") if entries else None,
                "newest_timestamp": entries[-1].get("timestamp") if entries else None,
                "db_stats": stats,
                "system_version": "KnowledgeManagerV2",
            }

        except Exception as e:
            print(f"❌ 統計取得エラー: {e}")
            return {"total_entries": 0, "categories": {}, "recent_entries": [], "error": str(e)}

    def search_knowledge(
        self, query: str, top_k: int = 10, filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        ナレッジ検索

        Args:
            query: 検索クエリ
            top_k: 取得件数
            filters: フィルタ条件

        Returns:
            検索結果のリスト
        """
        try:
            if self.km is None:
                print(f"⚠️ KnowledgeManagerV2が初期化されていません")
                return []

            # ハイブリッド検索を実行
            results = self.km.hybrid_search(query, top_k=top_k, filters=filters)

            return results

        except Exception as e:
            print(f"❌ 検索エラー: {e}")
            return []

    def simulate_healing_traces(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        修復トレースのシミュレーション
        （実際の修復アクションがまだ少ない場合の代替）
        """

        healing_traces = []

        # ナレッジエントリーから修復関連を抽出
        entries = self.load_knowledge_entries()

        if not entries:
            return []

        healing_entries = [
            e
            for e in entries
            if any(
                keyword in e.get("title", "").lower()
                for keyword in ["修正", "解決", "fix", "resolve", "エラー", "error", "問題"]
            )
        ]

        # 修復トレースに変換
        for entry in healing_entries[:count]:
            healing_trace = {
                "trace_id": f"heal-{entry.get('trace_id', 'unknown')}",
                "operation_name": "self_healing.auto_fix",
                "timestamp": entry.get("timestamp"),
                "status": "success",  # ナレッジ化されたものは成功扱い
                "duration_ms": 2500,  # 仮の値
                "healing_action": "auto_retry",
                "description": entry.get("title", ""),
                "confidence": entry.get("confidence", 0.8),
            }
            healing_traces.append(healing_trace)

        return healing_traces


if __name__ == "__main__":
    print("🧪 KnowledgeBaseAdapter テスト（KnowledgeManagerV2対応）")

    adapter = KnowledgeBaseAdapter()

    # テスト1: ナレッジ統計
    print("\n【ナレッジ統計】")
    stats = adapter.get_knowledge_statistics()
    print(f"  総エントリー数: {stats.get('total_entries', 0)}件")
    print(f"  カテゴリ数: {len(stats.get('categories', {}))}種類")
    print(f"  システムバージョン: {stats.get('system_version', 'unknown')}")

    if stats.get("db_stats"):
        db_stats = stats["db_stats"]
        print(f"\n【データベース統計】")
        print(f"  DB総ナレッジ数: {db_stats.get('total_knowledge', 0)}件")
        print(f"  平均信頼度: {db_stats.get('avg_confidence', 0):.2f}")
        print(f"  平均成功率: {db_stats.get('avg_success_rate', 0):.2f}")

    # テスト2: ナレッジエントリー読み込み
    print("\n【ナレッジエントリー読み込み】")
    entries = adapter.load_knowledge_entries()
    print(f"  読み込み成功: {len(entries)}件")

    if entries:
        print(f"  最新エントリー: {entries[0].get('title', 'unknown')}")
        print(f"  カテゴリ: {entries[0].get('category', 'unknown')}")

    # テスト3: ナレッジ検索
    print("\n【ナレッジ検索テスト】")
    search_results = adapter.search_knowledge("API エラー", top_k=3)
    print(f"  検索結果: {len(search_results)}件")

    for idx, result in enumerate(search_results[:3], 1):
        print(f"  {idx}. {result.get('scenario', 'unknown')[:50]}...")
        print(f"     信頼度: {result.get('confidence', 0):.2f}")

    # テスト4: 修復トレース生成
    print("\n【修復トレース生成】")
    healing = adapter.simulate_healing_traces(5)
    print(f"  生成された修復トレース: {len(healing)}件")

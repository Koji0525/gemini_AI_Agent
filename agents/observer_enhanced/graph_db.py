"""
システムグラフデータベース

このモジュールは、システム全体の依存関係をグラフとして管理します。
NetworkXを使用してノード(コンポーネント)とエッジ(依存関係)を保存し、
高速な検索とクエリ機能を提供します。

主要機能:
    - コンポーネント(ノード)の追加/更新/削除
    - 依存関係(エッジ)の追加/更新/削除
    - 影響範囲の計算 (BFS探索)
    - グラフの永続化 (JSON形式)
    - TTLキャッシュによる高速化

パフォーマンス目標:
    - グラフ操作: <10ms/operation
    - 影響範囲計算: <100ms (200ノード時)
    - メモリ使用量: <200MB
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    import networkx as nx
except ImportError:
    print("Error: networkx is required. Install with: pip install networkx --break-system-packages")
    import sys

    sys.exit(1)

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ComponentMetadata:
    """コンポーネントメタデータ"""

    component_id: str
    file: str
    lines: int
    type: str  # 'agent', 'tool', 'script'
    status: str  # 'alive', 'deprecated', 'broken'
    last_check: str
    health_score: float = 100.0
    error_count: int = 0


@dataclass
class DependencyMetadata:
    """依存関係メタデータ"""

    source: str
    target: str
    dep_type: str  # 'import', 'runtime', 'data'
    weight: float = 1.0
    last_used: Optional[str] = None


class SystemGraphDB:
    """
    システムグラフデータベース

    Attributes:
        graph (nx.DiGraph): 依存関係グラフ (有向グラフ)
        db_path (Path): グラフDB永続化パス
        cache (Dict): クエリキャッシュ (TTL: 5分)
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        初期化

        Args:
            db_path: グラフDBファイルパス (Noneの場合はデフォルトパス)
        """
        if db_path is None:
            db_path = Path("logs/system_graph.json")

        self.db_path = Path(db_path)
        self.graph = nx.DiGraph()
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5分
        self.cache_timestamps: Dict[str, float] = {}

        # 既存グラフをロード
        if self.db_path.exists():
            self.load()

        logger.info(f"Initialized SystemGraphDB with path: {self.db_path}")

    def add_component(self, component_id: str, metadata: Dict[str, Any]) -> None:
        """
        コンポーネントをノードとして追加

        Args:
            component_id: コンポーネント識別子 (例: 'pm_agent', 'sheets_manager')
            metadata: メタデータ辞書
                - file: ファイルパス
                - lines: 行数
                - type: タイプ ('agent', 'tool', 'script')
                - status: ステータス ('alive', 'deprecated', 'broken')
                - last_check: 最終チェック時刻 (ISO形式)
                - health_score: ヘルススコア (0-100)
                - error_count: エラー回数

        処理時間: <10ms
        """
        start_time = time.time()

        # デフォルト値を設定
        default_metadata = {
            "type": "unknown",
            "status": "alive",
            "last_check": datetime.now().isoformat(),
            "health_score": 100.0,
            "error_count": 0,
        }
        default_metadata.update(metadata)

        # ノードを追加
        self.graph.add_node(component_id, **default_metadata)

        # キャッシュをクリア
        self._clear_cache()

        elapsed = (time.time() - start_time) * 1000
        logger.debug(f"Added component '{component_id}' in {elapsed:.2f}ms")

    def update_component(self, component_id: str, metadata: Dict[str, Any]) -> None:
        """
        コンポーネント情報を更新

        Args:
            component_id: コンポーネント識別子
            metadata: 更新するメタデータ
        """
        if component_id not in self.graph:
            logger.warning(f"Component '{component_id}' not found")
            return

        # 既存データを取得して更新
        current_data = self.graph.nodes[component_id]
        current_data.update(metadata)
        current_data["last_check"] = datetime.now().isoformat()

        # キャッシュをクリア
        self._clear_cache()

        logger.debug(f"Updated component '{component_id}'")

    def remove_component(self, component_id: str) -> None:
        """
        コンポーネントを削除

        Args:
            component_id: コンポーネント識別子
        """
        if component_id in self.graph:
            self.graph.remove_node(component_id)
            self._clear_cache()
            logger.info(f"Removed component '{component_id}'")
        else:
            logger.warning(f"Component '{component_id}' not found")

    def add_dependency(self, source: str, target: str, dep_type: str, weight: float = 1.0) -> None:
        """
        依存関係をエッジとして追加

        Args:
            source: 呼び出し元コンポーネント
            target: 呼び出し先コンポーネント
            dep_type: 依存タイプ ('import', 'runtime', 'data')
            weight: エッジの重み (デフォルト: 1.0)

        処理時間: <10ms
        """
        start_time = time.time()

        # ノードが存在しない場合は警告
        if source not in self.graph:
            logger.warning(f"Source component '{source}' not found")
            return
        if target not in self.graph:
            logger.warning(f"Target component '{target}' not found")
            return

        # エッジを追加
        self.graph.add_edge(
            source, target, type=dep_type, weight=weight, last_used=datetime.now().isoformat()
        )

        # キャッシュをクリア
        self._clear_cache()

        elapsed = (time.time() - start_time) * 1000
        logger.debug(f"Added dependency {source} -> {target} in {elapsed:.2f}ms")

    def update_dependency(self, source: str, target: str, metadata: Dict[str, Any]) -> None:
        """
        依存関係情報を更新

        Args:
            source: 呼び出し元
            target: 呼び出し先
            metadata: 更新するメタデータ
        """
        if not self.graph.has_edge(source, target):
            logger.warning(f"Dependency {source} -> {target} not found")
            return

        # 既存データを更新
        edge_data = self.graph[source][target]
        edge_data.update(metadata)
        edge_data["last_used"] = datetime.now().isoformat()

        # キャッシュをクリア
        self._clear_cache()

        logger.debug(f"Updated dependency {source} -> {target}")

    def remove_dependency(self, source: str, target: str) -> None:
        """
        依存関係を削除

        Args:
            source: 呼び出し元
            target: 呼び出し先
        """
        if self.graph.has_edge(source, target):
            self.graph.remove_edge(source, target)
            self._clear_cache()
            logger.info(f"Removed dependency {source} -> {target}")
        else:
            logger.warning(f"Dependency {source} -> {target} not found")

    def get_impact_range(self, component_id: str, depth: int = 3) -> Set[str]:
        """
        影響範囲を計算 (BFS探索)

        Args:
            component_id: 変更対象コンポーネント
            depth: 探索深さ (デフォルト: 3階層)

        Returns:
            Set[str]: 影響を受けるコンポーネントのセット

        計算量: O(N + E)
        実行時間: <100ms (200ノード時)
        """
        cache_key = f"impact_{component_id}_{depth}"

        # キャッシュをチェック
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            return cached_result

        start_time = time.time()

        if component_id not in self.graph:
            logger.warning(f"Component '{component_id}' not found")
            return set()

        # BFS探索で影響範囲を計算
        impact_set = set()
        visited = set()
        queue = [(component_id, 0)]

        while queue:
            current, current_depth = queue.pop(0)

            if current in visited or current_depth > depth:
                continue

            visited.add(current)
            if current != component_id:
                impact_set.add(current)

            # 次のレベルを追加
            if current_depth < depth:
                for successor in self.graph.successors(current):
                    if successor not in visited:
                        queue.append((successor, current_depth + 1))

        elapsed = (time.time() - start_time) * 1000
        logger.debug(
            f"Calculated impact range for '{component_id}' in {elapsed:.2f}ms: {len(impact_set)} components"
        )

        # キャッシュに保存
        self._set_cache(cache_key, impact_set)

        return impact_set

    def get_reverse_impact_range(self, component_id: str, depth: int = 3) -> Set[str]:
        """
        逆方向の影響範囲を計算 (このコンポーネントに依存しているコンポーネント)

        Args:
            component_id: 対象コンポーネント
            depth: 探索深さ

        Returns:
            Set[str]: このコンポーネントに依存しているコンポーネントのセット
        """
        cache_key = f"reverse_impact_{component_id}_{depth}"

        # キャッシュをチェック
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            return cached_result

        if component_id not in self.graph:
            logger.warning(f"Component '{component_id}' not found")
            return set()

        # BFS探索 (逆方向)
        impact_set = set()
        visited = set()
        queue = [(component_id, 0)]

        while queue:
            current, current_depth = queue.pop(0)

            if current in visited or current_depth > depth:
                continue

            visited.add(current)
            if current != component_id:
                impact_set.add(current)

            # 前のレベルを追加
            if current_depth < depth:
                for predecessor in self.graph.predecessors(current):
                    if predecessor not in visited:
                        queue.append((predecessor, current_depth + 1))

        # キャッシュに保存
        self._set_cache(cache_key, impact_set)

        return impact_set

    def get_all_components(self) -> List[str]:
        """
        全コンポーネントのリストを取得

        Returns:
            List[str]: コンポーネント識別子のリスト
        """
        return list(self.graph.nodes())

    def get_component_metadata(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        コンポーネントのメタデータを取得

        Args:
            component_id: コンポーネント識別子

        Returns:
            Optional[Dict]: メタデータ辞書 (存在しない場合はNone)
        """
        if component_id not in self.graph:
            return None
        return dict(self.graph.nodes[component_id])

    def save(self, path: Optional[Path] = None) -> None:
        """
        グラフをJSON形式で保存

        Args:
            path: 保存先パス (Noneの場合はself.db_pathを使用)
        """
        if path is None:
            path = self.db_path

        # ディレクトリを作成
        path.parent.mkdir(parents=True, exist_ok=True)

        # グラフデータを辞書形式に変換
        data = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "node_count": self.graph.number_of_nodes(),
                "edge_count": self.graph.number_of_edges(),
                "saved_at": datetime.now().isoformat(),
            },
        }

        # ノード情報
        for node, attrs in self.graph.nodes(data=True):
            data["nodes"].append({"id": node, **attrs})

        # エッジ情報
        for source, target, attrs in self.graph.edges(data=True):
            data["edges"].append({"source": source, "target": target, **attrs})

        # JSONファイルに保存
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Graph saved to {path}")

    def load(self, path: Optional[Path] = None) -> None:
        """
        グラフをJSON形式から読み込み

        Args:
            path: 読み込み元パス (Noneの場合はself.db_pathを使用)
        """
        if path is None:
            path = self.db_path

        if not path.exists():
            logger.warning(f"Graph file not found: {path}")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 新しいグラフを作成
            self.graph = nx.DiGraph()

            # ノードを追加
            for node_data in data.get("nodes", []):
                node_id = node_data.pop("id")
                self.graph.add_node(node_id, **node_data)

            # エッジを追加
            for edge_data in data.get("edges", []):
                source = edge_data.pop("source")
                target = edge_data.pop("target")
                self.graph.add_edge(source, target, **edge_data)

            logger.info(
                f"Graph loaded from {path}: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges"
            )

        except Exception as e:
            logger.error(f"Failed to load graph: {e}")

    def _get_cache(self, key: str) -> Optional[Any]:
        """キャッシュから値を取得 (TTLチェック付き)"""
        if key not in self.cache:
            return None

        # TTLをチェック
        if time.time() - self.cache_timestamps.get(key, 0) > self.cache_ttl:
            del self.cache[key]
            del self.cache_timestamps[key]
            return None

        return self.cache[key]

    def _set_cache(self, key: str, value: Any) -> None:
        """キャッシュに値を保存"""
        self.cache[key] = value
        self.cache_timestamps[key] = time.time()

    def _clear_cache(self) -> None:
        """キャッシュをクリア"""
        self.cache.clear()
        self.cache_timestamps.clear()


def main():
    """メイン関数 (テスト用)"""
    # テスト用のグラフDB
    db = SystemGraphDB(Path("logs/test_system_graph.json"))

    # テストコンポーネントを追加
    db.add_component(
        "test_component_a", {"file": "agents/test_a.py", "lines": 100, "type": "agent"}
    )

    db.add_component("test_component_b", {"file": "agents/test_b.py", "lines": 200, "type": "tool"})

    # 依存関係を追加
    db.add_dependency("test_component_a", "test_component_b", "import")

    # 影響範囲を計算
    impact = db.get_impact_range("test_component_a")
    print(f"Impact range: {impact}")

    # 保存
    db.save()

    print("✅ SystemGraphDB test completed")


if __name__ == "__main__":
    main()

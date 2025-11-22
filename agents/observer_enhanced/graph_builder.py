"""
依存関係グラフ構築エンジン

このモジュールは、StaticAnalyzerの結果とTracerのログを統合して、
システム全体の依存関係グラフを構築します。

主要機能:
    - 静的解析結果からのグラフ構築
    - 動的トレースログとの統合
    - エッジ重み付けロジック (重要度計算)
    - グラフの最適化と整理

パフォーマンス目標:
    - グラフ生成: <3秒 (200ノード、1000エッジ)
    - メモリ使用量: <150MB
"""

import logging
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

try:
    import networkx as nx
except ImportError:
    print("Error: networkx is required. Install with: pip install networkx --break-system-packages")
    sys.exit(1)

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class EdgeWeight:
    """エッジの重み情報"""

    import_count: int = 0  # import回数
    runtime_call_count: int = 0  # 実行時呼び出し回数
    data_transfer_count: int = 0  # データ転送回数
    last_used_timestamp: Optional[float] = None  # 最終使用時刻

    def calculate_weight(self) -> float:
        """
        重みを計算

        計算式: (import_count * 1.0) + (runtime_call_count * 2.0) + (data_transfer_count * 1.5)
        重みが大きいほど重要な依存関係

        Returns:
            float: 計算された重み
        """
        weight = (
            self.import_count * 1.0 + self.runtime_call_count * 2.0 + self.data_transfer_count * 1.5
        )
        return max(weight, 0.1)  # 最小値0.1


class DependencyGraphBuilder:
    """
    依存関係グラフ構築エンジン

    Attributes:
        graph (nx.DiGraph): 構築中のグラフ
        edge_weights (Dict): エッジの重み情報
    """

    def __init__(self):
        """初期化"""
        self.graph = nx.DiGraph()
        self.edge_weights: Dict[Tuple[str, str], EdgeWeight] = {}
        logger.info("Initialized DependencyGraphBuilder")

    def build_from_static_analysis(self, static_graph: nx.DiGraph) -> None:
        """
        静的解析結果からグラフを構築

        Args:
            static_graph: StaticDependencyAnalyzerが生成したグラフ
        """
        logger.info("Building graph from static analysis...")
        start_time = time.time()

        # ノードをコピー
        for node, attrs in static_graph.nodes(data=True):
            self.graph.add_node(node, **attrs)

        # エッジをコピーして重み情報を初期化
        for source, target, attrs in static_graph.edges(data=True):
            # エッジを追加
            self.graph.add_edge(source, target, **attrs)

            # 重み情報を初期化
            edge_key = (source, target)
            if edge_key not in self.edge_weights:
                self.edge_weights[edge_key] = EdgeWeight()

            # import回数をカウント
            self.edge_weights[edge_key].import_count += 1

        elapsed = time.time() - start_time
        logger.info(
            f"Built graph from static analysis in {elapsed:.2f}s: "
            f"{self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges"
        )

    def integrate_runtime_traces(self, traces: List[Dict]) -> None:
        """
        実行時トレースログを統合

        Args:
            traces: トレースログのリスト
                各トレースは以下の形式:
                {
                    'caller': 'PMAgent',
                    'callee': 'SheetsManager',
                    'timestamp': 1234567890.0,
                    'duration_ms': 45.2
                }
        """
        logger.info(f"Integrating {len(traces)} runtime traces...")
        start_time = time.time()

        for trace in traces:
            caller = trace.get("caller")
            callee = trace.get("callee")
            timestamp = trace.get("timestamp")

            if not caller or not callee:
                continue

            # エッジを追加 (存在しない場合)
            if not self.graph.has_edge(caller, callee):
                self.graph.add_edge(caller, callee, type="runtime")

            # 重み情報を更新
            edge_key = (caller, callee)
            if edge_key not in self.edge_weights:
                self.edge_weights[edge_key] = EdgeWeight()

            self.edge_weights[edge_key].runtime_call_count += 1
            if timestamp:
                self.edge_weights[edge_key].last_used_timestamp = timestamp

        elapsed = time.time() - start_time
        logger.info(f"Integrated runtime traces in {elapsed:.2f}s")

    def calculate_and_apply_weights(self) -> None:
        """
        エッジの重みを計算して適用
        """
        logger.info("Calculating and applying edge weights...")

        for edge_key, weight_info in self.edge_weights.items():
            source, target = edge_key

            if self.graph.has_edge(source, target):
                # 重みを計算
                weight = weight_info.calculate_weight()

                # エッジに重みを適用
                self.graph[source][target]["weight"] = weight
                self.graph[source][target]["import_count"] = weight_info.import_count
                self.graph[source][target]["runtime_call_count"] = weight_info.runtime_call_count
                self.graph[source][target]["data_transfer_count"] = weight_info.data_transfer_count

        logger.info("Edge weights applied")

    def prune_weak_edges(self, threshold: float = 0.5) -> int:
        """
        弱いエッジを削除 (重みがthreshold以下)

        Args:
            threshold: 削除する閾値

        Returns:
            int: 削除されたエッジ数
        """
        edges_to_remove = []

        for source, target, attrs in self.graph.edges(data=True):
            weight = attrs.get("weight", 0.0)
            if weight <= threshold:
                edges_to_remove.append((source, target))

        for edge in edges_to_remove:
            self.graph.remove_edge(*edge)

        logger.info(f"Pruned {len(edges_to_remove)} weak edges")
        return len(edges_to_remove)

    def identify_critical_paths(self) -> List[List[str]]:
        """
        クリティカルパス(重要な依存関係経路)を特定

        Returns:
            List[List[str]]: クリティカルパスのリスト
        """
        # 重みの大きいエッジを含むパスを探索
        critical_paths = []

        # 全ノードペアの最短パスを計算
        try:
            for source in self.graph.nodes():
                for target in self.graph.nodes():
                    if source != target and nx.has_path(self.graph, source, target):
                        try:
                            # 重みを考慮した最短パス
                            path = nx.shortest_path(
                                self.graph,
                                source,
                                target,
                                weight=lambda u, v, d: 1.0 / d.get("weight", 0.1),
                            )

                            # パスの総重みを計算
                            total_weight = sum(
                                self.graph[path[i]][path[i + 1]].get("weight", 0.0)
                                for i in range(len(path) - 1)
                            )

                            # 重みが大きいパスを保存
                            if total_weight > 5.0:  # 閾値
                                critical_paths.append(path)
                        except nx.NetworkXNoPath:
                            continue
        except Exception as e:
            logger.warning(f"Error identifying critical paths: {e}")

        return critical_paths

    def get_hub_components(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        ハブコンポーネント(多数の依存関係を持つ)を特定

        Args:
            top_n: 上位何個を返すか

        Returns:
            List[Tuple[str, int]]: (コンポーネント名, 依存数)のリスト
        """
        # 入次数と出次数の合計でランキング
        degree_dict = {}

        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)
            degree_dict[node] = in_degree + out_degree

        # ソートして上位を返す
        sorted_components = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_components[:top_n]

    def detect_bottlenecks(self) -> List[str]:
        """
        ボトルネック(削除すると多くの依存が切れる)を検出

        Returns:
            List[str]: ボトルネックコンポーネントのリスト
        """
        bottlenecks = []

        for node in self.graph.nodes():
            # このノードを一時的に削除
            temp_graph = self.graph.copy()
            temp_graph.remove_node(node)

            # 連結成分の数を計算
            weakly_connected = list(nx.weakly_connected_components(temp_graph))

            # 削除前と比較
            original_components = list(nx.weakly_connected_components(self.graph))

            # 連結成分が増えた場合、ボトルネックの可能性
            if len(weakly_connected) > len(original_components):
                bottlenecks.append(node)

        logger.info(f"Detected {len(bottlenecks)} bottlenecks")
        return bottlenecks

    def get_graph(self) -> nx.DiGraph:
        """
        構築されたグラフを取得

        Returns:
            nx.DiGraph: 依存関係グラフ
        """
        return self.graph

    def export_statistics(self) -> Dict:
        """
        グラフ統計情報をエクスポート

        Returns:
            Dict: 統計情報
        """
        hub_components = self.get_hub_components(top_n=5)
        bottlenecks = self.detect_bottlenecks()

        stats = {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "avg_degree": sum(dict(self.graph.degree()).values())
            / max(self.graph.number_of_nodes(), 1),
            "hub_components": [{"component": comp, "degree": deg} for comp, deg in hub_components],
            "bottlenecks": bottlenecks,
            "weakly_connected_components": len(list(nx.weakly_connected_components(self.graph))),
            "strongly_connected_components": len(
                list(nx.strongly_connected_components(self.graph))
            ),
        }

        return stats


def main():
    """メイン関数 (テスト用)"""
    # テスト用のグラフビルダー
    builder = DependencyGraphBuilder()

    # テスト用の静的グラフを作成
    test_graph = nx.DiGraph()
    test_graph.add_node("ComponentA", type="agent", lines=100)
    test_graph.add_node("ComponentB", type="tool", lines=200)
    test_graph.add_node("ComponentC", type="agent", lines=150)
    test_graph.add_edge("ComponentA", "ComponentB", type="import")
    test_graph.add_edge("ComponentB", "ComponentC", type="import")

    # 静的解析結果から構築
    builder.build_from_static_analysis(test_graph)

    # テスト用のトレースログ
    test_traces = [
        {"caller": "ComponentA", "callee": "ComponentB", "timestamp": time.time()},
        {"caller": "ComponentA", "callee": "ComponentB", "timestamp": time.time()},
        {"caller": "ComponentB", "callee": "ComponentC", "timestamp": time.time()},
    ]

    # トレースログを統合
    builder.integrate_runtime_traces(test_traces)

    # 重みを計算・適用
    builder.calculate_and_apply_weights()

    # 統計情報を表示
    stats = builder.export_statistics()
    print("\n📊 Graph Statistics:")
    print(f"  Nodes: {stats['node_count']}")
    print(f"  Edges: {stats['edge_count']}")
    print(f"  Avg Degree: {stats['avg_degree']:.2f}")
    print(f"  Hub Components: {stats['hub_components']}")
    print(f"  Bottlenecks: {stats['bottlenecks']}")

    print("\n✅ DependencyGraphBuilder test completed")


if __name__ == "__main__":
    main()

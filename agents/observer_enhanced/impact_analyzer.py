"""
影響範囲分析モジュール

目的:
- ファイル変更時の影響範囲をBFS探索で分析
- 3階層までの依存先を追跡
- 変更の危険度を評価

設計方針:
- 既存のdependency_graph.jsonを読み込み
- NetworkXでグラフ処理
- REST APIから呼び出し可能
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import networkx as nx


class ImpactAnalyzer:
    """影響範囲分析器"""

    def __init__(self, graph_data: Dict[str, Any] = None):
        """
        初期化

        Args:
            graph_data: 依存関係グラフデータ（nodes, edgesを含む辞書）
        """
        self.graph = nx.DiGraph()

        if graph_data:
            self._build_graph(graph_data)

    def _build_graph(self, graph_data: Dict[str, Any]):
        """
        依存関係グラフを構築

        Args:
            graph_data: {"nodes": [...], "edges": [...]}
        """
        # ノードを追加
        for node in graph_data.get("nodes", []):
            node_id = node.get("id")
            if node_id:
                self.graph.add_node(node_id, **node)

        # エッジを追加（依存関係）
        for edge in graph_data.get("edges", []):
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                # source が target に依存（source imports target）
                self.graph.add_edge(source, target, **edge)

    def analyze_impact(self, file_path: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        影響範囲を分析（BFS探索）

        Args:
            file_path: 変更対象ファイル
            max_depth: 探索深さ（デフォルト3階層）

        Returns:
            {
                "target": "tools/sheets_manager.py",
                "total_affected": 83,
                "by_depth": {
                    "1": [list of files],
                    "2": [list of files],
                    "3": [list of files]
                },
                "risk_level": "high",
                "recommended_tests": [list]
            }
        """
        if file_path not in self.graph:
            return {
                "target": file_path,
                "error": "File not found in dependency graph",
                "total_affected": 0,
                "by_depth": {},
                "risk_level": "unknown",
            }

        # BFS探索で影響を受けるファイルを収集
        affected_by_depth = self._bfs_reverse_dependencies(file_path, max_depth)

        # 総影響ファイル数
        all_affected = set()
        for depth_files in affected_by_depth.values():
            all_affected.update(depth_files)

        # リスクレベル判定
        risk_level = self._calculate_risk_level(len(all_affected))

        # 推奨テスト
        recommended_tests = self._recommend_tests(file_path, affected_by_depth)

        return {
            "target": file_path,
            "total_affected": len(all_affected),
            "by_depth": affected_by_depth,
            "risk_level": risk_level,
            "recommended_tests": recommended_tests,
            "critical_files": self._identify_critical_files(affected_by_depth),
        }

    def _bfs_reverse_dependencies(self, start_node: str, max_depth: int) -> Dict[str, List[str]]:
        """
        BFS探索で逆依存関係を追跡

        逆依存: start_nodeを変更すると影響を受けるファイル

        Returns:
            {"1": [depth1_files], "2": [depth2_files], "3": [depth3_files]}
        """
        result = {str(i): [] for i in range(1, max_depth + 1)}
        visited = {start_node}
        queue = [(start_node, 0)]  # (node, depth)

        while queue:
            current_node, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            # このノードに依存しているノードを探す
            # graph.predecessors() = current_nodeをimportしているノード
            for dependent in self.graph.predecessors(current_node):
                if dependent not in visited:
                    visited.add(dependent)
                    next_depth = depth + 1
                    result[str(next_depth)].append(dependent)
                    queue.append((dependent, next_depth))

        return result

    def _calculate_risk_level(self, affected_count: int) -> str:
        """
        影響ファイル数からリスクレベルを判定

        Args:
            affected_count: 影響を受けるファイル数

        Returns:
            "low" | "medium" | "high" | "critical"
        """
        if affected_count == 0:
            return "none"
        elif affected_count < 5:
            return "low"
        elif affected_count < 20:
            return "medium"
        elif affected_count < 50:
            return "high"
        else:
            return "critical"

    def _recommend_tests(
        self, target_file: str, affected_by_depth: Dict[str, List[str]]
    ) -> List[str]:
        """
        推奨テストを生成

        Args:
            target_file: 変更対象
            affected_by_depth: 階層別影響ファイル

        Returns:
            推奨テストのリスト
        """
        tests = []

        # 1. 変更対象ファイル自体のテスト
        tests.append(f"Unit test: {target_file}")

        # 2. 直接依存（depth=1）のテスト
        depth1_files = affected_by_depth.get("1", [])
        if depth1_files:
            # 重要度が高いものを優先（agents/配下など）
            critical_depth1 = [f for f in depth1_files if "agents/" in f or "core_agents/" in f]
            for f in critical_depth1[:3]:  # 上位3つ
                tests.append(f"Integration test: {f}")

        # 3. 全体テスト
        total_affected = sum(len(files) for files in affected_by_depth.values())
        if total_affected > 10:
            tests.append("E2E test: Full system test recommended")

        return tests

    def _identify_critical_files(self, affected_by_depth: Dict[str, List[str]]) -> List[str]:
        """
        重要ファイルを特定（agents/配下など）

        Args:
            affected_by_depth: 階層別影響ファイル

        Returns:
            重要ファイルのリスト
        """
        critical_patterns = ["agents/", "core_agents/", "task_executor/", "browser_control/"]

        critical_files = []
        for depth_files in affected_by_depth.values():
            for file in depth_files:
                if any(pattern in file for pattern in critical_patterns):
                    critical_files.append(file)

        return list(set(critical_files))  # 重複除去


def analyze_file_impact(
    file_path: str, graph_data: Dict[str, Any], max_depth: int = 3
) -> Dict[str, Any]:
    """
    影響範囲分析の便利関数

    Args:
        file_path: 変更対象ファイル
        graph_data: 依存関係グラフデータ
        max_depth: 探索深さ

    Returns:
        影響範囲分析結果
    """
    analyzer = ImpactAnalyzer(graph_data)
    return analyzer.analyze_impact(file_path, max_depth)


# テスト実行用
if __name__ == "__main__":
    import sys

    # dependency_graph.jsonを読み込み
    graph_file = Path(__file__).parent / "web" / "dependency_graph.json"

    if not graph_file.exists():
        print(f"❌ {graph_file} が見つかりません")
        sys.exit(1)

    with open(graph_file, "r") as f:
        graph_data = json.load(f)

    # テスト: sheets_manager.py の影響範囲
    test_file = "tools/sheets_manager.py"
    print(f"🔍 影響範囲分析: {test_file}")

    result = analyze_file_impact(test_file, graph_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

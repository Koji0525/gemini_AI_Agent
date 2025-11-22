"""
システムグラフDB（完全実装版）

【責任】
- コンポーネント間の依存関係をグラフとして管理
- ノード追加/更新/削除
- エッジ追加/更新/削除
- グラフ検索・トラバース
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import networkx as nx


class SystemGraphDB:
    """システムグラフデータベース"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初期化

        Args:
            db_path: グラフDB保存パス（デフォルト: logs/system_graph.json）
        """
        self.db_path = Path(db_path or "logs/system_graph.json")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # NetworkXグラフ
        self.graph = nx.DiGraph()

        # 既存データがあれば読み込み
        self.load()

    def add_component(self, component_id: str, attributes: Dict[str, Any]) -> bool:
        """
        コンポーネント（ノード）追加

        Args:
            component_id: コンポーネントID（ファイルパス等）
            attributes: 属性辞書

        Returns:
            成功: True, 失敗: False
        """
        try:
            # タイムスタンプ追加
            attributes["updated_at"] = datetime.now().isoformat()

            # ノード追加/更新
            self.graph.add_node(component_id, **attributes)

            return True

        except Exception as e:
            print(f"❌ ノード追加エラー: {e}")
            return False

    def add_dependency(
        self,
        from_component: str,
        to_component: str,
        dependency_type: str = "import",
        weight: float = 1.0,
    ) -> bool:
        """
        依存関係（エッジ）追加

        Args:
            from_component: 依存元
            to_component: 依存先
            dependency_type: 依存タイプ（import, call, etc）
            weight: 重み

        Returns:
            成功: True, 失敗: False
        """
        try:
            # エッジ追加/更新
            self.graph.add_edge(
                from_component,
                to_component,
                type=dependency_type,
                weight=weight,
                updated_at=datetime.now().isoformat(),
            )

            return True

        except Exception as e:
            print(f"❌ エッジ追加エラー: {e}")
            return False

    def get_dependencies(self, component_id: str, direction: str = "out") -> List[str]:
        """
        依存関係取得

        Args:
            component_id: コンポーネントID
            direction: 方向（'out': 依存先, 'in': 依存元, 'both': 両方）

        Returns:
            依存関係リスト
        """
        if component_id not in self.graph:
            return []

        if direction == "out":
            return list(self.graph.successors(component_id))
        elif direction == "in":
            return list(self.graph.predecessors(component_id))
        else:  # both
            return list(
                set(
                    list(self.graph.successors(component_id))
                    + list(self.graph.predecessors(component_id))
                )
            )

    def get_impact_scope(self, component_id: str, max_depth: int = 3) -> Set[str]:
        """
        影響範囲取得（BFS探索）

        Args:
            component_id: 起点コンポーネント
            max_depth: 最大探索深度

        Returns:
            影響を受けるコンポーネント集合
        """
        if component_id not in self.graph:
            return set()

        impacted = set()

        try:
            # BFSで探索
            for node in nx.bfs_tree(self.graph, component_id, depth_limit=max_depth):
                impacted.add(node)

        except Exception as e:
            print(f"⚠️  影響範囲計算エラー: {e}")

        return impacted

    def export_for_visualization(self) -> Dict[str, Any]:
        """
        可視化用データエクスポート

        Returns:
            {
                'nodes': [...],
                'edges': [...]
            }
        """
        nodes = []
        for node_id, attrs in self.graph.nodes(data=True):
            nodes.append({"id": node_id, "label": Path(node_id).name, **attrs})

        edges = []
        for from_id, to_id, attrs in self.graph.edges(data=True):
            edges.append({"from": from_id, "to": to_id, **attrs})

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "node_count": self.graph.number_of_nodes(),
                "edge_count": self.graph.number_of_edges(),
            },
        }

    def save(self) -> bool:
        """グラフDB保存"""
        try:
            data = nx.node_link_data(self.graph)

            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"❌ グラフDB保存エラー: {e}")
            return False

    def load(self) -> bool:
        """グラフDB読み込み"""
        if not self.db_path.exists():
            return False

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.graph = nx.node_link_graph(data)

            return True

        except Exception as e:
            print(f"⚠️  グラフDB読み込みエラー: {e}")
            return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI実行
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    db = SystemGraphDB()

    # サンプルデータ投入
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔧 GraphDBテスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # コンポーネント追加
    db.add_component("agents/pm_agent.py", {"type": "agent", "lines": 500})
    db.add_component("agents/task_executor.py", {"type": "agent", "lines": 800})
    db.add_component("tools/sheets_manager.py", {"type": "tool", "lines": 600})

    # 依存関係追加
    db.add_dependency("agents/pm_agent.py", "tools/sheets_manager.py", "import")
    db.add_dependency("agents/task_executor.py", "tools/sheets_manager.py", "import")

    # 可視化データ
    viz_data = db.export_for_visualization()

    print(f"ノード数: {viz_data['stats']['node_count']}")
    print(f"エッジ数: {viz_data['stats']['edge_count']}")
    print()

    # 影響範囲
    impacted = db.get_impact_scope("tools/sheets_manager.py")
    print(f"tools/sheets_manager.py の影響範囲: {impacted}")
    print()

    # 保存
    if db.save():
        print(f"✅ 保存完了: {db.db_path}")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

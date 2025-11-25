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


def get_component(self, component_id):
    """コンポーネント情報取得"""
    if component_id not in self.graph.nodes:
        return None
    return {"id": component_id, **self.graph.nodes[component_id]}


def update_component(self, component_id, metadata):
    """コンポーネント情報更新"""
    if component_id not in self.graph.nodes:
        return False
    self.graph.nodes[component_id].update(metadata)
    self._invalidate_cache()
    return True


def remove_component(self, component_id):
    """コンポーネント削除"""
    if component_id not in self.graph.nodes:
        return False
    self.graph.remove_node(component_id)
    self._invalidate_cache()
    return True


def list_components(self, component_type=None):
    """コンポーネント一覧取得"""
    components = []
    for node_id, data in self.graph.nodes(data=True):
        if component_type is None or data.get("type") == component_type:
            components.append({"id": node_id, **data})
    return components


def get_dependency(self, source, target):
    """依存関係情報取得"""
    if not self.graph.has_edge(source, target):
        return None
    return {"source": source, "target": target, **self.graph.edges[source, target]}


def remove_dependency(self, source, target):
    """依存関係削除"""
    if not self.graph.has_edge(source, target):
        return False
    self.graph.remove_edge(source, target)
    self._invalidate_cache()
    return True


def get_impact_range(self, component_id, depth=3, direction="both"):
    """影響範囲取得（エイリアス）"""
    return self.get_impact_scope(component_id, depth, direction)


def get_shortest_path(self, source, target):
    """最短パス取得"""
    import networkx as nx

    try:
        path = nx.shortest_path(self.graph, source, target)
        return path
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def find_cycles(self):
    """循環依存検出"""
    import networkx as nx

    try:
        cycles = list(nx.simple_cycles(self.graph))
        return cycles
    except:
        return []


def get_statistics(self):
    """グラフ統計情報取得"""
    return {
        "node_count": self.graph.number_of_nodes(),
        "edge_count": self.graph.number_of_edges(),
        "density": len(self.graph.edges)
        / max(len(self.graph.nodes) * (len(self.graph.nodes) - 1), 1),
        "components": len(list(self.graph.nodes)),
    }


def get_most_dependent(self, limit=10):
    """最も依存されているコンポーネント取得"""
    in_degrees = dict(self.graph.in_degree())
    sorted_nodes = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
    return [{"id": node_id, "dependents": degree} for node_id, degree in sorted_nodes[:limit]]


def get_most_depending(self, limit=10):
    """最も依存しているコンポーネント取得"""
    out_degrees = dict(self.graph.out_degree())
    sorted_nodes = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)
    return [{"id": node_id, "dependencies": degree} for node_id, degree in sorted_nodes[:limit]]


def export_to_json(self):
    """グラフをJSON形式でエクスポート"""
    from networkx.readwrite import json_graph

    data = json_graph.node_link_data(self.graph)
    return data


def import_from_json(self, data):
    """JSON形式からグラフをインポート"""
    from networkx.readwrite import json_graph

    self.graph = json_graph.node_link_graph(data)
    self._invalidate_cache()
    return True

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # テスト互換性メソッド（Phase 6 - networkx API使用）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_component(self, component_id: str):
        """コンポーネント情報を取得（networkx API）"""
        if component_id in self.graph.nodes:
            return self.graph.nodes[component_id]
        return None

    def update_component(self, component_id: str, attributes: dict) -> bool:
        """コンポーネント属性を更新（networkx API）"""
        if component_id in self.graph.nodes:
            self.graph.nodes[component_id].update(attributes)
            return True
        return False

    def remove_component(self, component_id: str) -> bool:
        """コンポーネントを削除（networkx API）"""
        if component_id in self.graph.nodes:
            self.graph.remove_node(component_id)
            return True
        return False

    def list_components(self):
        """すべてのコンポーネントをリスト（networkx API）"""
        return [{"id": node_id, **self.graph.nodes[node_id]} for node_id in self.graph.nodes]

    def get_dependency(self, source: str, target: str):
        """依存関係情報を取得（networkx API）"""
        if self.graph.has_edge(source, target):
            return self.graph.edges[source, target]
        return None

    def remove_dependency(self, source: str, target: str) -> bool:
        """依存関係を削除（networkx API）"""
        if self.graph.has_edge(source, target):
            self.graph.remove_edge(source, target)
            return True
        return False

    def get_impact_range(self, component_id: str, depth: int = 1, direction: str = "out"):
        """影響範囲を取得（既存メソッドのエイリアス）"""
        return self.get_impact_scope(component_id, depth, direction)

    def get_shortest_path(self, source: str, target: str):
        """最短パスを取得（networkx API）"""
        import networkx as nx

        try:
            return nx.shortest_path(self.graph, source, target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def find_cycles(self):
        """循環依存を検出（networkx API）"""
        import networkx as nx

        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except Exception:
            return []

    def get_statistics(self):
        """グラフ統計情報を取得（networkx API）"""
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        return {
            "total_nodes": num_nodes,
            "total_edges": num_edges,
            "avg_dependencies": num_edges / max(num_nodes, 1),
        }

    def get_most_dependent(self, limit: int = 5):
        """最も依存されているコンポーネントを取得（networkx API）"""
        # in_degree = 依存されている数
        in_degrees = dict(self.graph.in_degree())
        sorted_nodes = sorted(in_degrees.items(), key=lambda x: -x[1])[:limit]

        return [{"id": node_id, "dependency_count": count} for node_id, count in sorted_nodes]

    def get_most_depending(self, limit: int = 5):
        """最も多く依存しているコンポーネントを取得（networkx API）"""
        # out_degree = 依存している数
        out_degrees = dict(self.graph.out_degree())
        sorted_nodes = sorted(out_degrees.items(), key=lambda x: -x[1])[:limit]

        return [{"id": node_id, "depending_count": count} for node_id, count in sorted_nodes]

    def export_to_json(self, filepath: str = None):
        """JSONにエクスポート（networkx API）"""
        import json

        import networkx as nx

        # networkxグラフをnode_link形式に変換
        data = nx.node_link_data(self.graph)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(json_str)
            except Exception as e:
                print(f"エクスポートエラー: {e}")

        return json_str

    def import_from_json(self, filepath: str = None, json_str: str = None):
        """JSONからインポート（networkx API）"""
        import json

        import networkx as nx

        try:
            if filepath:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif json_str:
                data = json.loads(json_str)
            else:
                return False

            # node_link形式からグラフに変換
            self.graph = nx.node_link_graph(data, directed=True)
            return True
        except Exception as e:
            print(f"インポートエラー: {e}")
            return False

#!/usr/bin/env python3
"""
動的DAG（Directed Acyclic Graph）マネージャー

目的: タスクの依存関係を動的に管理し、実行順序を最適化

主要機能:
1. タスク追加・削除
2. 依存関係管理
3. 実行順序の決定（トポロジカルソート）
4. 循環参照検出
5. 動的なタスク分割・統合

使用例:
    dag = DynamicDAGManager(goal_id="6")
    
    # タスク追加
    dag.add_task("task_001", {"description": "データ収集"})
    dag.add_task("task_002", {"description": "分析", "depends_on": ["task_001"]})
    
    # 実行順序取得
    order = dag.get_execution_order()
    # → ["task_001", "task_002"]
"""

import json
from typing import Dict, List, Set, Optional
from pathlib import Path
from datetime import datetime
import networkx as nx

class DynamicDAGManager:
    """
    動的DAGマネージャー
    
    NetworkXを使用してタスクのDAGを管理
    
    データ構造:
    {
        "nodes": {
            "task_001": {
                "type": "original",
                "description": "...",
                "status": "pending",
                "estimated_duration": 3600,
                "metadata": {...}
            }
        },
        "edges": [
            ["task_001", "task_002"],  # task_001 → task_002
        ]
    }
    """
    
    def __init__(self, goal_id: str, storage_dir: str = "shared_states/dags"):
        """
        初期化
        
        Args:
            goal_id: ゴールID
            storage_dir: DAG保存ディレクトリ
        """
        self.goal_id = goal_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.dag_file = self.storage_dir / f"goal_{goal_id}_dag.json"
        
        # NetworkX DiGraph
        self.graph = nx.DiGraph()
        
        # 既存DAGを読み込み
        if self.dag_file.exists():
            self._load()
        
        print(f"✅ DynamicDAGManager初期化: goal_{goal_id}")
    
    def add_task(
        self,
        task_id: str,
        task_data: Dict,
        depends_on: List[str] = None
    ) -> bool:
        """
        タスクをDAGに追加
        
        Args:
            task_id: タスクID
            task_data: タスクデータ
            depends_on: 依存タスクIDのリスト
        
        Returns:
            成功フラグ
        """
        # ノード追加
        self.graph.add_node(task_id, **task_data)
        
        # 依存関係追加
        if depends_on:
            for parent_id in depends_on:
                if parent_id not in self.graph:
                    print(f"⚠️  依存タスクが存在しません: {parent_id}")
                    return False
                
                self.graph.add_edge(parent_id, task_id)
        
        # 循環参照チェック
        if not nx.is_directed_acyclic_graph(self.graph):
            print(f"❌ 循環参照が検出されました")
            # ロールバック
            self.graph.remove_node(task_id)
            return False
        
        # 保存
        self._save()
        
        print(f"✅ タスク追加: {task_id}")
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        タスクをDAGから削除
        
        Args:
            task_id: タスクID
        
        Returns:
            成功フラグ
        """
        if task_id not in self.graph:
            print(f"⚠️  タスクが存在しません: {task_id}")
            return False
        
        self.graph.remove_node(task_id)
        self._save()
        
        print(f"✅ タスク削除: {task_id}")
        return True
    
    def get_execution_order(self) -> List[str]:
        """
        実行順序を取得（トポロジカルソート）
        
        Returns:
            タスクIDのリスト（実行順）
        """
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXError as e:
            print(f"❌ 実行順序の取得に失敗: {e}")
            return []
    
    def get_parallel_groups(self) -> List[List[str]]:
        """
        並列実行可能なタスクグループを取得
        
        Returns:
            タスクIDのリスト（各グループは並列実行可能）
        """
        order = self.get_execution_order()
        
        groups = []
        visited = set()
        
        for task_id in order:
            if task_id in visited:
                continue
            
            # 同じレベル（同じ依存深度）のタスクを収集
            level = self._get_dependency_level(task_id)
            group = [t for t in order 
                    if t not in visited 
                    and self._get_dependency_level(t) == level]
            
            groups.append(group)
            visited.update(group)
        
        return groups
    
    def _get_dependency_level(self, task_id: str) -> int:
        """タスクの依存深度を取得"""
        try:
            # 最長パスの長さ = 依存深度
            paths = nx.single_source_shortest_path_length(
                self.graph.reverse(),
                task_id
            )
            return max(paths.values()) if paths else 0
        except:
            return 0
    
    def split_task(
        self,
        task_id: str,
        subtasks: List[Dict]
    ) -> bool:
        """
        タスクを複数のサブタスクに分割
        
        Args:
            task_id: 分割元タスクID
            subtasks: サブタスクリスト [{"id": "...", "data": {...}}, ...]
        
        Returns:
            成功フラグ
        """
        if task_id not in self.graph:
            print(f"⚠️  タスクが存在しません: {task_id}")
            return False
        
        # 元タスクの依存関係を取得
        predecessors = list(self.graph.predecessors(task_id))
        successors = list(self.graph.successors(task_id))
        
        # サブタスクを追加
        for i, subtask in enumerate(subtasks):
            subtask_id = subtask['id']
            subtask_data = subtask['data']
            
            # 最初のサブタスクは元タスクの依存を継承
            if i == 0:
                self.add_task(subtask_id, subtask_data, depends_on=predecessors)
            else:
                # 次のサブタスクは前のサブタスクに依存
                prev_subtask_id = subtasks[i-1]['id']
                self.add_task(subtask_id, subtask_data, depends_on=[prev_subtask_id])
        
        # 最後のサブタスクから元タスクの後続に接続
        last_subtask_id = subtasks[-1]['id']
        for successor in successors:
            self.graph.add_edge(last_subtask_id, successor)
        
        # 元タスクを削除
        self.graph.remove_node(task_id)
        
        self._save()
        
        print(f"✅ タスク分割: {task_id} → {len(subtasks)}個")
        return True
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        return {
            'total_tasks': self.graph.number_of_nodes(),
            'total_dependencies': self.graph.number_of_edges(),
            'is_dag': nx.is_directed_acyclic_graph(self.graph),
            'max_dependency_depth': self._get_max_depth(),
            'parallel_groups': len(self.get_parallel_groups())
        }
    
    def _get_max_depth(self) -> int:
        """最大依存深度を取得"""
        if self.graph.number_of_nodes() == 0:
            return 0
        
        depths = [self._get_dependency_level(node) for node in self.graph.nodes()]
        return max(depths) if depths else 0
    
    def _save(self):
        """DAGを保存"""
        data = {
            'goal_id': self.goal_id,
            'nodes': dict(self.graph.nodes(data=True)),
            'edges': list(self.graph.edges()),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.dag_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load(self):
        """DAGを読み込み"""
        with open(self.dag_file, 'r') as f:
            data = json.load(f)
        
        # ノード追加
        for node_id, node_data in data['nodes'].items():
            self.graph.add_node(node_id, **node_data)
        
        # エッジ追加
        for edge in data['edges']:
            self.graph.add_edge(edge[0], edge[1])
        
        print(f"✅ DAG読み込み: {self.graph.number_of_nodes()}ノード")

# ========================================
# テスト
# ========================================
if __name__ == "__main__":
    print("="*60)
    print("📋 DynamicDAGManager テスト")
    print("="*60)
    
    # DAG作成
    dag = DynamicDAGManager(goal_id="test_dag")
    
    # タスク追加
    print("\n[1/6] タスク追加...")
    dag.add_task("task_001", {"description": "データ収集", "status": "pending"})
    dag.add_task("task_002", {"description": "データ前処理", "status": "pending"}, depends_on=["task_001"])
    dag.add_task("task_003", {"description": "分析", "status": "pending"}, depends_on=["task_002"])
    dag.add_task("task_004", {"description": "可視化", "status": "pending"}, depends_on=["task_002"])
    
    # 実行順序
    print("\n[2/6] 実行順序取得...")
    order = dag.get_execution_order()
    print(f"   実行順序: {' → '.join(order)}")
    
    # 並列グループ
    print("\n[3/6] 並列グループ取得...")
    groups = dag.get_parallel_groups()
    for i, group in enumerate(groups, 1):
        print(f"   グループ{i}: {', '.join(group)}")
    
    # タスク分割
    print("\n[4/6] タスク分割...")
    dag.split_task("task_003", [
        {"id": "task_003_a", "data": {"description": "分析A"}},
        {"id": "task_003_b", "data": {"description": "分析B"}},
    ])
    
    # 統計情報
    print("\n[5/6] 統計情報...")
    stats = dag.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 実行順序再確認
    print("\n[6/6] 実行順序再確認...")
    order = dag.get_execution_order()
    print(f"   実行順序: {' → '.join(order)}")
    
    print("\n" + "="*60)
    print("✅ テスト完了")
    print("="*60)

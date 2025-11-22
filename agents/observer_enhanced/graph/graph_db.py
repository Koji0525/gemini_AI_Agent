"""
SystemGraphDB - システムグラフデータベース

【設計方針】
- NetworkXを使用した有向グラフ管理
- ノード: コンポーネント（エージェント、ツール、etc）
- エッジ: 依存関係（import、runtime call）
- キャッシュによる高速化

【使用例】
```python
from agents.observer_enhanced.graph.graph_db import SystemGraphDB

db = SystemGraphDB()

# ノード追加
db.add_component('PMAgent', {
    'type': 'agent',
    'file': 'agents/pm_agent.py',
    'lines': 850
})

# エッジ追加
db.add_dependency('PMAgent', 'SheetsManager', 'import')

# 影響範囲取得
affected = db.get_impact_range('SheetsManager', depth=3)
```

【パフォーマンス目標】
- ノード追加: <1ms
- エッジ追加: <1ms
- 影響範囲分析（3階層）: <100ms
"""

import networkx as nx
from typing import Dict, List, Set, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
from cachetools import TTLCache
from collections import defaultdict


class SystemGraphDB:
    """システムグラフデータベース"""
    
    def __init__(self):
        """初期化"""
        # 有向グラフ（依存関係は方向性がある）
        self.graph = nx.DiGraph()
        
        # キャッシュ（5分間有効、最大1000エントリ）
        self.cache = TTLCache(maxsize=1000, ttl=300)
        
        # メタデータ
        self.metadata = {
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        # 統計情報
        self.stats = {
            'total_nodes': 0,
            'total_edges': 0,
            'total_queries': 0
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ノード操作（CRUD）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def add_component(self, component_id: str, metadata: Dict[str, Any]) -> bool:
        """
        コンポーネントをノードとして追加
        
        Args:
            component_id: コンポーネントID（例: 'PMAgent'）
            metadata: メタデータ
                - type: 'agent' | 'tool' | 'service' | 'utility'
                - file: ファイルパス
                - lines: コード行数
                - status: 'active' | 'inactive'
                - last_check: 最終確認日時
                
        Returns:
            成功したらTrue
            
        Performance:
            - 実行時間: <1ms
        """
        try:
            # 既存ノードの更新チェック
            if self.graph.has_node(component_id):
                # 既存メタデータをマージ
                existing = self.graph.nodes[component_id]
                merged = {**existing, **metadata}
                self.graph.nodes[component_id].update(merged)
            else:
                # 新規ノード追加
                self.graph.add_node(component_id, **metadata)
                self.stats['total_nodes'] += 1
            
            # メタデータ更新
            self.graph.nodes[component_id]['updated_at'] = datetime.now().isoformat()
            self.metadata['last_updated'] = datetime.now().isoformat()
            
            # キャッシュクリア
            self._clear_cache()
            
            return True
            
        except Exception as e:
            print(f"❌ ノード追加エラー: {component_id} - {e}")
            return False
    
    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        コンポーネント情報取得
        
        Args:
            component_id: コンポーネントID
            
        Returns:
            メタデータ辞書（存在しない場合はNone）
        """
        if not self.graph.has_node(component_id):
            return None
        
        return dict(self.graph.nodes[component_id])
    
    def update_component(self, component_id: str, metadata: Dict[str, Any]) -> bool:
        """
        コンポーネント情報更新
        
        Args:
            component_id: コンポーネントID
            metadata: 更新するメタデータ
            
        Returns:
            成功したらTrue
        """
        if not self.graph.has_node(component_id):
            return False
        
        self.graph.nodes[component_id].update(metadata)
        self.graph.nodes[component_id]['updated_at'] = datetime.now().isoformat()
        self._clear_cache()
        
        return True
    
    def remove_component(self, component_id: str) -> bool:
        """
        コンポーネント削除
        
        Args:
            component_id: コンポーネントID
            
        Returns:
            成功したらTrue
        """
        if not self.graph.has_node(component_id):
            return False
        
        # エッジ数を減算
        self.stats['total_edges'] -= (
            self.graph.in_degree(component_id) + 
            self.graph.out_degree(component_id)
        )
        
        # ノード削除
        self.graph.remove_node(component_id)
        self.stats['total_nodes'] -= 1
        self._clear_cache()
        
        return True
    
    def list_components(self, component_type: Optional[str] = None) -> List[str]:
        """
        コンポーネント一覧取得
        
        Args:
            component_type: タイプでフィルタ（省略時は全件）
            
        Returns:
            コンポーネントIDのリスト
        """
        if component_type is None:
            return list(self.graph.nodes())
        
        return [
            node for node in self.graph.nodes()
            if self.graph.nodes[node].get('type') == component_type
        ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # エッジ操作（CRUD）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def add_dependency(self, source: str, target: str, dep_type: str = 'import', 
                      weight: float = 1.0, metadata: Dict[str, Any] = None) -> bool:
        """
        依存関係をエッジとして追加
        
        Args:
            source: 呼び出し元（依存する側）
            target: 呼び出し先（依存される側）
            dep_type: 依存タイプ（'import', 'runtime', 'data'）
            weight: 重要度（1.0-10.0）
            metadata: 追加メタデータ
            
        Returns:
            成功したらTrue
            
        Performance:
            - 実行時間: <1ms
        """
        try:
            # ノード存在確認
            if not self.graph.has_node(source):
                self.add_component(source, {'type': 'unknown'})
            
            if not self.graph.has_node(target):
                self.add_component(target, {'type': 'unknown'})
            
            # エッジ追加
            edge_data = {
                'type': dep_type,
                'weight': weight,
                'created_at': datetime.now().isoformat()
            }
            
            if metadata:
                edge_data.update(metadata)
            
            self.graph.add_edge(source, target, **edge_data)
            self.stats['total_edges'] += 1
            
            # キャッシュクリア
            self._clear_cache()
            
            return True
            
        except Exception as e:
            print(f"❌ エッジ追加エラー: {source} -> {target} - {e}")
            return False
    
    def get_dependency(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """
        依存関係情報取得
        
        Args:
            source: 呼び出し元
            target: 呼び出し先
            
        Returns:
            エッジデータ（存在しない場合はNone）
        """
        if not self.graph.has_edge(source, target):
            return None
        
        return dict(self.graph.edges[source, target])
    
    def remove_dependency(self, source: str, target: str) -> bool:
        """
        依存関係削除
        
        Args:
            source: 呼び出し元
            target: 呼び出し先
            
        Returns:
            成功したらTrue
        """
        if not self.graph.has_edge(source, target):
            return False
        
        self.graph.remove_edge(source, target)
        self.stats['total_edges'] -= 1
        self._clear_cache()
        
        return True
    
    def get_dependencies(self, component_id: str, direction: str = 'out') -> List[Dict[str, Any]]:
        """
        コンポーネントの依存関係一覧取得
        
        Args:
            component_id: コンポーネントID
            direction: 'out'（依存先）、'in'（依存元）、'both'（両方）
            
        Returns:
            依存関係のリスト
        """
        if not self.graph.has_node(component_id):
            return []
        
        dependencies = []
        
        if direction in ['out', 'both']:
            # 依存先（このコンポーネントが依存している先）
            for target in self.graph.successors(component_id):
                edge_data = self.graph.edges[component_id, target]
                dependencies.append({
                    'direction': 'out',
                    'source': component_id,
                    'target': target,
                    **edge_data
                })
        
        if direction in ['in', 'both']:
            # 依存元（このコンポーネントに依存している元）
            for source in self.graph.predecessors(component_id):
                edge_data = self.graph.edges[source, component_id]
                dependencies.append({
                    'direction': 'in',
                    'source': source,
                    'target': component_id,
                    **edge_data
                })
        
        return dependencies
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 影響範囲分析（BFS探索）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_impact_range(self, component_id: str, depth: int = 3, 
                        direction: str = 'in') -> Set[str]:
        """
        影響範囲を計算（BFS探索）
        
        Args:
            component_id: 変更対象コンポーネント
            depth: 探索深さ（3階層まで）
            direction: 'in'（依存元を探索）、'out'（依存先を探索）
            
        Returns:
            影響を受けるコンポーネントのセット
            
        Performance:
            - 目標実行時間: <100ms
            - アルゴリズム: BFS（Breadth-First Search）
            
        Example:
            SheetsManagerが変更された場合:
            
            depth=1: [PMAgent, TaskExecutor, ReviewAgent]
            depth=2: [PMAgent, TaskExecutor, ReviewAgent, CompleteEngine, Dashboard]
            depth=3: 上記 + さらに間接的に依存するコンポーネント
        """
        if not self.graph.has_node(component_id):
            return set()
        
        # キャッシュ確認
        cache_key = f"impact_{component_id}_{depth}_{direction}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # BFS探索
        affected = set()
        visited = set()
        queue = [(component_id, 0)]  # (ノード, 現在の深さ)
        
        while queue:
            current, current_depth = queue.pop(0)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # 最初のノード自身は除外
            if current != component_id:
                affected.add(current)
            
            # 深さ制限チェック
            if current_depth >= depth:
                continue
            
            # 次のレベルを探索
            if direction == 'in':
                # 依存元（このコンポーネントに依存している側）
                neighbors = self.graph.predecessors(current)
            else:
                # 依存先（このコンポーネントが依存している側）
                neighbors = self.graph.successors(current)
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, current_depth + 1))
        
        # キャッシュに保存
        self.cache[cache_key] = affected
        self.stats['total_queries'] += 1
        
        return affected
    
    def get_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        最短経路を取得
        
        Args:
            source: 開始ノード
            target: 終了ノード
            
        Returns:
            最短経路のノードリスト（経路がない場合はNone）
        """
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return None
    
    def find_cycles(self) -> List[List[str]]:
        """
        循環依存を検出
        
        Returns:
            循環依存のリスト
        """
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 統計・分析
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        グラフ統計情報取得
        
        Returns:
            統計情報の辞書
        """
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'total_queries': self.stats['total_queries'],
            'average_degree': sum(dict(self.graph.degree()).values()) / max(self.graph.number_of_nodes(), 1),
            'is_directed': self.graph.is_directed(),
            'has_cycles': len(self.find_cycles()) > 0,
            'metadata': self.metadata
        }
    
    def get_most_dependent(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        最も依存されているコンポーネント（トップN）
        
        Args:
            limit: 取得件数
            
        Returns:
            (コンポーネントID, 依存数) のリスト
        """
        in_degrees = dict(self.graph.in_degree())
        sorted_components = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
        return sorted_components[:limit]
    
    def get_most_depending(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        最も多くに依存しているコンポーネント（トップN）
        
        Args:
            limit: 取得件数
            
        Returns:
            (コンポーネントID, 依存数) のリスト
        """
        out_degrees = dict(self.graph.out_degree())
        sorted_components = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)
        return sorted_components[:limit]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # エクスポート・インポート
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def export_to_json(self, filepath: Optional[Path] = None) -> str:
        """
        JSON形式でエクスポート
        
        Args:
            filepath: 保存先（省略時は文字列で返す）
            
        Returns:
            JSON文字列
        """
        data = {
            'metadata': self.metadata,
            'stats': self.get_statistics(),
            'nodes': [
                {
                    'id': node,
                    **self.graph.nodes[node]
                }
                for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': source,
                    'target': target,
                    **self.graph.edges[source, target]
                }
                for source, target in self.graph.edges()
            ]
        }
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    def import_from_json(self, json_str: str = None, filepath: Path = None) -> bool:
        """
        JSON形式からインポート
        
        Args:
            json_str: JSON文字列
            filepath: 読み込み元ファイル
            
        Returns:
            成功したらTrue
        """
        try:
            if filepath:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = json.loads(json_str)
            
            # グラフクリア
            self.graph.clear()
            
            # ノード追加
            for node_data in data.get('nodes', []):
                node_id = node_data.pop('id')
                self.add_component(node_id, node_data)
            
            # エッジ追加
            for edge_data in data.get('edges', []):
                source = edge_data.pop('source')
                target = edge_data.pop('target')
                self.add_dependency(source, target, metadata=edge_data)
            
            # メタデータ復元
            if 'metadata' in data:
                self.metadata.update(data['metadata'])
            
            return True
            
        except Exception as e:
            print(f"❌ インポートエラー: {e}")
            return False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 内部ヘルパー
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _clear_cache(self):
        """キャッシュクリア"""
        self.cache.clear()


def main():
    """テスト実行"""
    print("🔧 SystemGraphDB テスト実行")
    print("=" * 80)
    
    db = SystemGraphDB()
    
    # 1. ノード追加
    print("\n1. ノード追加")
    db.add_component('PMAgent', {
        'type': 'agent',
        'file': 'agents/pm_agent.py',
        'lines': 850,
        'status': 'active'
    })
    db.add_component('TaskExecutor', {
        'type': 'agent',
        'file': 'agents/task_executor.py',
        'lines': 1200,
        'status': 'active'
    })
    db.add_component('SheetsManager', {
        'type': 'tool',
        'file': 'tools/sheets_manager.py',
        'lines': 1150,
        'status': 'active'
    })
    print(f"  ノード数: {db.graph.number_of_nodes()}")
    
    # 2. エッジ追加
    print("\n2. エッジ追加")
    db.add_dependency('PMAgent', 'SheetsManager', 'import', weight=3.0)
    db.add_dependency('TaskExecutor', 'SheetsManager', 'import', weight=5.0)
    print(f"  エッジ数: {db.graph.number_of_edges()}")
    
    # 3. 影響範囲分析
    print("\n3. 影響範囲分析")
    affected = db.get_impact_range('SheetsManager', depth=3, direction='in')
    print(f"  SheetsManagerの変更で影響を受けるコンポーネント: {affected}")
    
    # 4. 統計情報
    print("\n4. 統計情報")
    stats = db.get_statistics()
    print(f"  総ノード数: {stats['total_nodes']}")
    print(f"  総エッジ数: {stats['total_edges']}")
    print(f"  平均次数: {stats['average_degree']:.2f}")
    
    # 5. JSON エクスポート
    print("\n5. JSONエクスポート")
    json_str = db.export_to_json()
    print(f"  JSON長: {len(json_str)} bytes")
    
    print("\n✅ SystemGraphDB テスト完了")


if __name__ == '__main__':
    main()

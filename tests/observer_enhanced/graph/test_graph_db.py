"""
SystemGraphDBのテストケース

【テスト項目】
1. ノードCRUD操作
2. エッジCRUD操作
3. 影響範囲分析（BFS）
4. 統計情報取得
5. JSON エクスポート/インポート
6. パフォーマンステスト
"""

import pytest
from pathlib import Path
import time
import json

# プロジェクトルートをパスに追加
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agents.observer_enhanced.graph.graph_db import SystemGraphDB


class TestSystemGraphDB:
    """SystemGraphDBのテストクラス"""
    
    @pytest.fixture
    def db(self):
        """テスト用DB"""
        return SystemGraphDB()
    
    @pytest.fixture
    def populated_db(self):
        """データが入ったテスト用DB"""
        db = SystemGraphDB()
        
        # ノード追加
        db.add_component('PMAgent', {'type': 'agent', 'lines': 850})
        db.add_component('TaskExecutor', {'type': 'agent', 'lines': 1200})
        db.add_component('SheetsManager', {'type': 'tool', 'lines': 1150})
        db.add_component('KnowledgeManager', {'type': 'tool', 'lines': 980})
        db.add_component('Dashboard', {'type': 'service', 'lines': 450})
        
        # エッジ追加
        db.add_dependency('PMAgent', 'SheetsManager', 'import', weight=3.0)
        db.add_dependency('TaskExecutor', 'SheetsManager', 'import', weight=5.0)
        db.add_dependency('PMAgent', 'KnowledgeManager', 'import', weight=2.0)
        db.add_dependency('Dashboard', 'PMAgent', 'runtime', weight=1.0)
        db.add_dependency('Dashboard', 'TaskExecutor', 'runtime', weight=1.0)
        
        return db
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ノードCRUD操作
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_add_component(self, db):
        """ノード追加のテスト"""
        success = db.add_component('TestComponent', {
            'type': 'agent',
            'file': 'test.py',
            'lines': 100
        })
        
        assert success
        assert db.graph.number_of_nodes() == 1
        assert db.graph.has_node('TestComponent')
    
    def test_get_component(self, populated_db):
        """ノード取得のテスト"""
        comp = populated_db.get_component('PMAgent')
        
        assert comp is not None
        assert comp['type'] == 'agent'
        assert comp['lines'] == 850
    
    def test_update_component(self, populated_db):
        """ノード更新のテスト"""
        success = populated_db.update_component('PMAgent', {'lines': 900})
        
        assert success
        
        comp = populated_db.get_component('PMAgent')
        assert comp['lines'] == 900
    
    def test_remove_component(self, populated_db):
        """ノード削除のテスト"""
        initial_count = populated_db.graph.number_of_nodes()
        
        success = populated_db.remove_component('Dashboard')
        
        assert success
        assert populated_db.graph.number_of_nodes() == initial_count - 1
        assert not populated_db.graph.has_node('Dashboard')
    
    def test_list_components(self, populated_db):
        """ノード一覧取得のテスト"""
        # 全件
        all_comps = populated_db.list_components()
        assert len(all_comps) == 5
        
        # タイプフィルタ
        agents = populated_db.list_components(component_type='agent')
        assert len(agents) == 2
        assert 'PMAgent' in agents
        assert 'TaskExecutor' in agents
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # エッジCRUD操作
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_add_dependency(self, db):
        """エッジ追加のテスト"""
        db.add_component('A', {'type': 'agent'})
        db.add_component('B', {'type': 'tool'})
        
        success = db.add_dependency('A', 'B', 'import', weight=2.0)
        
        assert success
        assert db.graph.number_of_edges() == 1
        assert db.graph.has_edge('A', 'B')
    
    def test_get_dependency(self, populated_db):
        """エッジ取得のテスト"""
        dep = populated_db.get_dependency('PMAgent', 'SheetsManager')
        
        assert dep is not None
        assert dep['type'] == 'import'
        assert dep['weight'] == 3.0
    
    def test_remove_dependency(self, populated_db):
        """エッジ削除のテスト"""
        initial_count = populated_db.graph.number_of_edges()
        
        success = populated_db.remove_dependency('PMAgent', 'SheetsManager')
        
        assert success
        assert populated_db.graph.number_of_edges() == initial_count - 1
    
    def test_get_dependencies(self, populated_db):
        """依存関係一覧取得のテスト"""
        # 依存先（out）
        out_deps = populated_db.get_dependencies('PMAgent', direction='out')
        assert len(out_deps) == 2  # SheetsManager, KnowledgeManager
        
        # 依存元（in）
        in_deps = populated_db.get_dependencies('SheetsManager', direction='in')
        assert len(in_deps) == 2  # PMAgent, TaskExecutor
        
        # 両方
        both_deps = populated_db.get_dependencies('PMAgent', direction='both')
        assert len(both_deps) >= 2
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 影響範囲分析
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_get_impact_range_depth1(self, populated_db):
        """影響範囲分析（深さ1）のテスト"""
        affected = populated_db.get_impact_range('SheetsManager', depth=1, direction='in')
        
        # SheetsManagerに直接依存: PMAgent, TaskExecutor
        assert len(affected) == 2
        assert 'PMAgent' in affected
        assert 'TaskExecutor' in affected
    
    def test_get_impact_range_depth2(self, populated_db):
        """影響範囲分析（深さ2）のテスト"""
        affected = populated_db.get_impact_range('SheetsManager', depth=2, direction='in')
        
        # 深さ2: PMAgent, TaskExecutor + Dashboard
        assert len(affected) >= 2
        assert 'Dashboard' in affected
    
    def test_get_shortest_path(self, populated_db):
        """最短経路取得のテスト"""
        path = populated_db.get_shortest_path('Dashboard', 'SheetsManager')
        
        assert path is not None
        assert path[0] == 'Dashboard'
        assert path[-1] == 'SheetsManager'
        assert len(path) == 3  # Dashboard -> PMAgent -> SheetsManager
    
    def test_find_cycles(self, db):
        """循環依存検出のテスト"""
        # 循環依存を作成
        db.add_component('A', {'type': 'agent'})
        db.add_component('B', {'type': 'tool'})
        db.add_component('C', {'type': 'service'})
        
        db.add_dependency('A', 'B')
        db.add_dependency('B', 'C')
        db.add_dependency('C', 'A')  # 循環
        
        cycles = db.find_cycles()
        
        assert len(cycles) > 0
        assert len(cycles[0]) == 3  # A -> B -> C -> A
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 統計・分析
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_get_statistics(self, populated_db):
        """統計情報取得のテスト"""
        stats = populated_db.get_statistics()
        
        assert stats['total_nodes'] == 5
        assert stats['total_edges'] == 5
        assert stats['is_directed'] is True
        assert 'average_degree' in stats
    
    def test_get_most_dependent(self, populated_db):
        """最も依存されているコンポーネントのテスト"""
        most_dep = populated_db.get_most_dependent(limit=3)
        
        assert len(most_dep) <= 3
        # SheetsManagerが最も依存されている（2個）
        assert most_dep[0][0] == 'SheetsManager'
        assert most_dep[0][1] == 2
    
    def test_get_most_depending(self, populated_db):
        """最も多くに依存しているコンポーネントのテスト"""
        most_dep = populated_db.get_most_depending(limit=3)
        
        assert len(most_dep) <= 3
        # PMAgent, Dashboardが2個に依存
        assert most_dep[0][1] == 2
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # エクスポート/インポート
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_export_to_json(self, populated_db):
        """JSONエクスポートのテスト"""
        json_str = populated_db.export_to_json()
        
        assert len(json_str) > 0
        assert '"nodes":' in json_str or '"nodes": [' in json_str
        assert '"edges":' in json_str or '"edges": [' in json_str
        assert 'PMAgent' in json_str
    
    def test_import_from_json(self, populated_db, tmp_path):
        """JSONインポートのテスト"""
        # エクスポート
        json_file = tmp_path / "test_graph.json"
        populated_db.export_to_json(filepath=json_file)
        
        # 新しいDBにインポート
        new_db = SystemGraphDB()
        success = new_db.import_from_json(filepath=json_file)
        
        assert success
        assert new_db.graph.number_of_nodes() == populated_db.graph.number_of_nodes()
        assert new_db.graph.number_of_edges() == populated_db.graph.number_of_edges()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # パフォーマンステスト
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_performance_add_node(self, db):
        """ノード追加パフォーマンステスト（目標: <1ms）"""
        start_time = time.time()
        
        for i in range(100):
            db.add_component(f'Component{i}', {'type': 'test'})
        
        elapsed_time = (time.time() - start_time) * 1000 / 100  # 平均時間
        
        print(f"\n  ノード追加平均時間: {elapsed_time:.3f}ms")
        assert elapsed_time < 1.0  # 1ms以内
    
    def test_performance_add_edge(self, db):
        """エッジ追加パフォーマンステスト（目標: <1ms）"""
        # ノード準備
        for i in range(50):
            db.add_component(f'Node{i}', {'type': 'test'})
        
        start_time = time.time()
        
        for i in range(49):
            db.add_dependency(f'Node{i}', f'Node{i+1}')
        
        elapsed_time = (time.time() - start_time) * 1000 / 49
        
        print(f"\n  エッジ追加平均時間: {elapsed_time:.3f}ms")
        assert elapsed_time < 1.0
    
    def test_performance_impact_range(self, populated_db):
        """影響範囲分析パフォーマンステスト（目標: <10ms）"""
        start_time = time.time()
        
        affected = populated_db.get_impact_range('SheetsManager', depth=3)
        
        elapsed_time = (time.time() - start_time) * 1000
        
        print(f"\n  影響範囲分析時間: {elapsed_time:.3f}ms")
        assert elapsed_time < 10.0

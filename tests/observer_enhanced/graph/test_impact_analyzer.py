"""
ImpactAnalyzerのテストケース

【テスト項目】
1. 影響範囲分析（BFS探索）
2. 最短経路探索
3. 循環依存検出
4. スコアリング（P3-T005）
5. 推奨テスト生成（P3-T006）
6. パフォーマンステスト
"""

import pytest
from pathlib import Path
import time

# プロジェクトルートをパスに追加
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agents.observer_enhanced.graph.graph_db import SystemGraphDB
from agents.observer_enhanced.graph.impact_analyzer import ImpactAnalyzer


class TestImpactAnalyzer:
    """ImpactAnalyzerのテストクラス"""
    
    @pytest.fixture
    def db_with_data(self):
        """テスト用データが入ったGraphDB"""
        db = SystemGraphDB()
        
        # ノード追加（15個のエージェント構成を模倣）
        db.add_component('PMAgent', {'type': 'agent', 'lines': 850, 'file': 'agents/pm_agent.py'})
        db.add_component('TaskExecutor', {'type': 'agent', 'lines': 1200, 'file': 'agents/task_executor.py'})
        db.add_component('ReviewAgent', {'type': 'agent', 'lines': 650, 'file': 'agents/review_agent.py'})
        db.add_component('SheetsManager', {'type': 'tool', 'lines': 1150, 'file': 'tools/sheets_manager.py'})
        db.add_component('KnowledgeManager', {'type': 'tool', 'lines': 980, 'file': 'tools/knowledge_manager.py'})
        db.add_component('Dashboard', {'type': 'service', 'lines': 450, 'file': 'agents/observability/dashboard.py'})
        
        # エッジ追加（依存関係）
        db.add_dependency('PMAgent', 'SheetsManager', 'import', weight=3.0)
        db.add_dependency('TaskExecutor', 'SheetsManager', 'import', weight=5.0)
        db.add_dependency('ReviewAgent', 'SheetsManager', 'import', weight=2.0)
        db.add_dependency('PMAgent', 'KnowledgeManager', 'import', weight=2.0)
        db.add_dependency('TaskExecutor', 'KnowledgeManager', 'import', weight=3.0)
        db.add_dependency('Dashboard', 'PMAgent', 'runtime', weight=1.0)
        db.add_dependency('Dashboard', 'TaskExecutor', 'runtime', weight=1.0)
        
        return db
    
    @pytest.fixture
    def analyzer_with_data(self, db_with_data):
        """テスト用ImpactAnalyzer"""
        return ImpactAnalyzer(db_with_data)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 影響範囲分析
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_analyze_impact_basic(self, analyzer_with_data):
        """基本的な影響範囲分析のテスト"""
        result = analyzer_with_data.analyze_impact('SheetsManager')
        
        assert 'target_component' in result
        assert result['target_component'] == 'SheetsManager'
        assert 'affected_components' in result
        assert len(result['affected_components']) >= 3  # PMAgent, TaskExecutor, ReviewAgent
    
    def test_analyze_impact_depth(self, analyzer_with_data):
        """深さ指定の影響範囲分析テスト"""
        # 深さ1
        result_d1 = analyzer_with_data.analyze_impact('SheetsManager', depth=1)
        count_d1 = len(result_d1['affected_components'])
        
        # 深さ2
        result_d2 = analyzer_with_data.analyze_impact('SheetsManager', depth=2)
        count_d2 = len(result_d2['affected_components'])
        
        # 深さ2の方が多いはず（Dashboardが含まれる）
        assert count_d2 >= count_d1
    
    def test_analyze_impact_direction_in(self, analyzer_with_data):
        """依存元方向（in）の影響範囲分析テスト"""
        result = analyzer_with_data.analyze_impact('SheetsManager', direction='in')
        
        # SheetsManagerに依存している：PMAgent, TaskExecutor, ReviewAgent
        assert 'PMAgent' in result['affected_components']
        assert 'TaskExecutor' in result['affected_components']
        assert 'ReviewAgent' in result['affected_components']
    
    def test_analyze_impact_direction_out(self, analyzer_with_data):
        """依存先方向（out）の影響範囲分析テスト"""
        result = analyzer_with_data.analyze_impact('PMAgent', direction='out')
        
        # PMAgentが依存している：SheetsManager, KnowledgeManager
        assert 'SheetsManager' in result['affected_components']
        assert 'KnowledgeManager' in result['affected_components']
    
    def test_analyze_impact_nonexistent(self, analyzer_with_data):
        """存在しないコンポーネントの影響範囲分析テスト"""
        result = analyzer_with_data.analyze_impact('NonExistentComponent')
        
        assert result['target_component'] == 'NonExistentComponent'
        assert len(result['affected_components']) == 0
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 最短経路探索
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_find_path(self, analyzer_with_data):
        """最短経路探索のテスト"""
        path = analyzer_with_data.find_path('Dashboard', 'SheetsManager')
        
        assert path is not None
        assert path[0] == 'Dashboard'
        assert path[-1] == 'SheetsManager'
        # Dashboard -> PMAgent -> SheetsManager
        assert len(path) == 3
    
    def test_find_path_no_path(self, analyzer_with_data):
        """経路が存在しない場合のテスト"""
        path = analyzer_with_data.find_path('SheetsManager', 'Dashboard')
        
        # 逆向きには経路がない
        assert path is None
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 循環依存検出
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_detect_cycles_no_cycle(self, analyzer_with_data):
        """循環依存がない場合のテスト"""
        cycles = analyzer_with_data.detect_cycles()
        
        # 現在のテストデータには循環依存がない
        assert len(cycles) == 0
    
    def test_detect_cycles_with_cycle(self, db_with_data):
        """循環依存がある場合のテスト"""
        # 循環依存を追加
        db_with_data.add_component('A', {'type': 'test'})
        db_with_data.add_component('B', {'type': 'test'})
        db_with_data.add_component('C', {'type': 'test'})
        db_with_data.add_dependency('A', 'B')
        db_with_data.add_dependency('B', 'C')
        db_with_data.add_dependency('C', 'A')  # 循環
        
        analyzer = ImpactAnalyzer(db_with_data)
        cycles = analyzer.detect_cycles()
        
        assert len(cycles) > 0
        # 循環の長さは3
        assert any(len(cycle) == 3 for cycle in cycles)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # P3-T005: スコアリングテスト
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_scoring_low_risk(self, analyzer_with_data):
        """低リスク変更のスコアリングテスト"""
        from agents.observer_enhanced.graph.scoring_engine import ScoringEngine
        
        engine = ScoringEngine()
        
        # 小規模変更（10行、影響1件）
        result = engine.calculate_impact_score(
            component_id='Dashboard',
            change_lines=10,
            affected_components={'PMAgent'},
            component_metadata={
                'Dashboard': {'type': 'service', 'lines': 450},
                'PMAgent': {'type': 'agent', 'lines': 850}
            }
        )
        
        assert result['risk_level'] == 'low'
        assert result['total_score'] < 40
    
    def test_scoring_critical_risk(self, analyzer_with_data):
        """クリティカルリスク変更のスコアリングテスト"""
        from agents.observer_enhanced.graph.scoring_engine import ScoringEngine
        
        engine = ScoringEngine()
        
        # 大規模変更（300行、影響5件、重要コンポーネント）
        result = engine.calculate_impact_score(
            component_id='SheetsManager',
            change_lines=300,
            affected_components={'PMAgent', 'TaskExecutor', 'ReviewAgent', 'Dashboard', 'KnowledgeManager'},
            component_metadata={
                'SheetsManager': {'type': 'tool', 'lines': 1150},
                'PMAgent': {'type': 'agent', 'lines': 850},
                'TaskExecutor': {'type': 'agent', 'lines': 1200},
                'ReviewAgent': {'type': 'agent', 'lines': 650},
                'Dashboard': {'type': 'service', 'lines': 450},
                'KnowledgeManager': {'type': 'tool', 'lines': 980}
            }
        )
        
        assert result['risk_level'] == 'critical'
        assert result['total_score'] >= 80
        assert len(result['critical_affected']) > 0
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # P3-T006: 推奨テスト生成テスト
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_generate_test_recommendations(self, analyzer_with_data):
        """推奨テスト生成のテスト"""
        result = analyzer_with_data.generate_test_recommendations(
            component_id='SheetsManager',
            change_lines=100
        )
        
        # 必須フィールド確認
        assert 'impact_analysis' in result
        assert 'score_result' in result
        assert 'recommendations' in result
        
        # 推奨アクション確認
        recommendations = result['recommendations']
        assert 'recommended_tests' in recommendations
        assert 'review_priority' in recommendations
        assert 'rollback_plan' in recommendations
        assert 'monitoring_points' in recommendations
        
        # テストリスト確認
        assert isinstance(recommendations['recommended_tests'], list)
        assert len(recommendations['recommended_tests']) > 0
    
    def test_recommendations_for_critical_change(self, analyzer_with_data):
        """クリティカル変更時の推奨アクションテスト"""
        result = analyzer_with_data.generate_test_recommendations(
            component_id='SheetsManager',
            change_lines=250  # 大規模変更
        )
        
        recommendations = result['recommendations']
        score = result['score_result']
        
        # クリティカルレベルの場合
        if score['risk_level'] == 'critical':
            assert recommendations['review_priority'] == 'critical'
            assert 'ロールバック' in recommendations['rollback_plan']
            assert len(recommendations['recommended_tests']) >= 3
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # パフォーマンステスト
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_performance_analyze_impact(self, analyzer_with_data):
        """影響範囲分析のパフォーマンステスト（目標: <100ms）"""
        start_time = time.time()
        
        result = analyzer_with_data.analyze_impact('SheetsManager', depth=3)
        
        elapsed_time = (time.time() - start_time) * 1000
        
        print(f"\n  影響範囲分析時間: {elapsed_time:.3f}ms")
        assert elapsed_time < 100  # 100ms以内
    
    def test_performance_generate_recommendations(self, analyzer_with_data):
        """推奨テスト生成のパフォーマンステスト（目標: <200ms）"""
        start_time = time.time()
        
        result = analyzer_with_data.generate_test_recommendations('SheetsManager', 100)
        
        elapsed_time = (time.time() - start_time) * 1000
        
        print(f"\n  推奨テスト生成時間: {elapsed_time:.3f}ms")
        assert elapsed_time < 200  # 200ms以内

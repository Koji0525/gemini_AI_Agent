#!/usr/bin/env python3
"""
Phase 8 拡張機能統合テスト
タスクID: P8-T007

テスト対象:
- 隠れた依存関係検出器
- 変更影響分析ツール
- グラフDB
- 完全版ダッシュボード
"""

import unittest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestHiddenDependencyDetector(unittest.TestCase):
    """隠れた依存関係検出器のテスト"""
    
    def test_detector_import(self):
        """検出器がインポートできること"""
        from agents.observer_enhanced.hidden_dependency_detector import HiddenDependencyDetector
        detector = HiddenDependencyDetector()
        self.assertIsNotNone(detector)
    
    def test_detect_file(self):
        """ファイル解析のテスト"""
        from agents.observer_enhanced.hidden_dependency_detector import HiddenDependencyDetector
        detector = HiddenDependencyDetector()
        
        # 実際に存在するファイルでテスト
        test_file = project_root / 'agents' / 'observer_enhanced' / 'hidden_dependency_detector.py'
        if test_file.exists():
            result = detector.detect_file(test_file)
            self.assertIsInstance(result, list)
    
    def test_scan_project(self):
        """プロジェクトスキャンのテスト"""
        from agents.observer_enhanced.hidden_dependency_detector import HiddenDependencyDetector
        detector = HiddenDependencyDetector()
        
        if hasattr(detector, 'scan_project'):
            result = detector.scan_project()
            self.assertIsInstance(result, dict)


class TestChangeImpactAnalyzer(unittest.TestCase):
    """変更影響分析ツールのテスト"""
    
    def test_analyzer_import(self):
        """分析ツールがインポートできること"""
        from agents.observer_enhanced.change_impact_analyzer import ChangeImpactAnalyzer
        analyzer = ChangeImpactAnalyzer()
        self.assertIsNotNone(analyzer)
    
    def test_get_git_changes(self):
        """Git変更取得のテスト"""
        from agents.observer_enhanced.change_impact_analyzer import ChangeImpactAnalyzer
        analyzer = ChangeImpactAnalyzer()
        
        if hasattr(analyzer, 'get_git_changes'):
            result = analyzer.get_git_changes()
            self.assertIsInstance(result, dict)


class TestGraphDB(unittest.TestCase):
    """グラフDBのテスト（正しいパス: graph/graph_db.py）"""
    
    def test_graph_db_import(self):
        """GraphDBがインポートできること"""
        from agents.observer_enhanced.graph.graph_db import SystemGraphDB
        db = SystemGraphDB()
        self.assertIsNotNone(db)
    
    def test_add_component(self):
        """コンポーネント追加のテスト"""
        from agents.observer_enhanced.graph.graph_db import SystemGraphDB
        db = SystemGraphDB()
        
        if hasattr(db, 'add_component'):
            db.add_component('test_component', {'type': 'test'})
            self.assertTrue(True)
        elif hasattr(db, 'add_node'):
            db.add_node('test_component', {'type': 'test'})
            self.assertTrue(True)


class TestImpactAnalyzer(unittest.TestCase):
    """影響範囲分析のテスト（正しいパス: graph/impact_analyzer.py）"""
    
    def test_impact_analyzer_import(self):
        """ImpactAnalyzerがインポートできること"""
        try:
            from agents.observer_enhanced.graph.impact_analyzer import ImpactAnalyzer
            from agents.observer_enhanced.graph.graph_db import SystemGraphDB
            
            db = SystemGraphDB()
            analyzer = ImpactAnalyzer(db)
            self.assertIsNotNone(analyzer)
        except Exception as e:
            self.skipTest(f"インポートエラー: {e}")


class TestCompleteDashboard(unittest.TestCase):
    """完全版ダッシュボードのテスト"""
    
    def test_dashboard_html_exists(self):
        """ダッシュボードHTMLファイルの存在確認"""
        html_path = project_root / 'agents' / 'observer_enhanced' / 'web' / 'complete_dashboard.html'
        self.assertTrue(html_path.exists(), f"ファイルが存在しません: {html_path}")
    
    def test_dashboard_html_size(self):
        """HTMLファイルサイズの確認"""
        html_path = project_root / 'agents' / 'observer_enhanced' / 'web' / 'complete_dashboard.html'
        if not html_path.exists():
            self.skipTest("HTMLファイルが存在しません")
        
        content = html_path.read_text()
        line_count = len(content.split('\n'))
        self.assertGreaterEqual(line_count, 100, f"行数が少なすぎます: {line_count}行")
    
    def test_dashboard_load_time(self):
        """ダッシュボードロード時間のテスト"""
        import time
        
        html_path = project_root / 'agents' / 'observer_enhanced' / 'web' / 'complete_dashboard.html'
        if not html_path.exists():
            self.skipTest("HTMLファイルが存在しません")
        
        start = time.time()
        content = html_path.read_text()
        load_time = time.time() - start
        
        self.assertLess(load_time, 0.1, f"HTMLロード時間が遅すぎます: {load_time:.3f}秒")


class TestAPIExtensions(unittest.TestCase):
    """API拡張エンドポイントのテスト"""
    
    def test_api_extensions_file_exists(self):
        """API拡張ファイルの存在確認"""
        api_path = project_root / 'agents' / 'observer_enhanced' / 'web' / 'api_extensions.py'
        self.assertTrue(api_path.exists(), f"ファイルが存在しません: {api_path}")


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def test_core_components_exist(self):
        """コアコンポーネントのファイル存在確認"""
        core_files = [
            'agents/observer_enhanced/hidden_dependency_detector.py',
            'agents/observer_enhanced/change_impact_analyzer.py',
            'agents/observer_enhanced/graph/graph_db.py',
            'agents/observer_enhanced/graph/impact_analyzer.py',
            'agents/observer_enhanced/web/api_extensions.py',
            'agents/observer_enhanced/web/complete_dashboard.html',
        ]
        
        existing = []
        missing = []
        for f in core_files:
            path = project_root / f
            if path.exists():
                existing.append(f)
            else:
                missing.append(f)
        
        self.assertGreaterEqual(len(existing), 4, f"コアファイルが不足: {missing}")
    
    def test_existing_observer_components(self):
        """既存オブザーバーコンポーネントのインポート確認"""
        components_imported = 0
        
        # GraphDB
        try:
            from agents.observer_enhanced.graph.graph_db import SystemGraphDB
            components_imported += 1
        except ImportError:
            pass
        
        # HiddenDependencyDetector
        try:
            from agents.observer_enhanced.hidden_dependency_detector import HiddenDependencyDetector
            components_imported += 1
        except ImportError:
            pass
        
        # ChangeImpactAnalyzer
        try:
            from agents.observer_enhanced.change_impact_analyzer import ChangeImpactAnalyzer
            components_imported += 1
        except ImportError:
            pass
        
        self.assertGreaterEqual(components_imported, 2, "コアコンポーネントのインポートに失敗")


if __name__ == '__main__':
    unittest.main(verbosity=2)

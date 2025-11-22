"""
影響範囲分析エンジン

【責任】
- コンポーネント変更時の影響範囲をBFS探索で分析
- 変更リスクの評価とスコアリング
- 推奨テスト計画の生成

【使用箇所】
- コード変更時の影響範囲確認
- リリース前のリスク評価
- テスト計画の自動生成
"""

from typing import Dict, Any, List, Set, Optional
from pathlib import Path
import time

from agents.observer_enhanced.graph.graph_db import SystemGraphDB


class ImpactAnalyzer:
    """影響範囲分析エンジン"""
    
    def __init__(self, graph_db: SystemGraphDB):
        """
        初期化
        
        Args:
            graph_db: SystemGraphDB インスタンス
        """
        self.graph_db = graph_db
    
    def analyze_impact(
        self,
        component_id: str,
        depth: int = 3,
        direction: str = 'in',
        change_lines: int = 50
    ) -> Dict[str, Any]:
        """
        影響範囲を分析
        
        Args:
            component_id: 変更対象コンポーネントID
            depth: 探索深さ（デフォルト3階層）
            direction: 探索方向 ('in'=依存元, 'out'=依存先, 'both'=両方)
            change_lines: 変更行数（スコアリング用）
        
        Returns:
            {
                'target_component': str,           # 対象コンポーネント
                'affected_components': List[str],  # 影響を受けるコンポーネント
                'affected_count': int,             # 影響コンポーネント数
                'depth': int,                      # 探索深さ
                'direction': str,                  # 探索方向
                'analysis_time_ms': float          # 分析時間（ミリ秒）
            }
        """
        start_time = time.time()
        
        # 存在確認
        if not self.graph_db.graph.has_node(component_id):
            return {
                'target_component': component_id,
                'affected_components': [],
                'affected_count': 0,
                'depth': depth,
                'direction': direction,
                'analysis_time_ms': 0.0,
                'error': 'Component not found'
            }
        
        # BFS探索で影響範囲を取得
        affected = self.graph_db.get_impact_range(
            component_id=component_id,
            depth=depth,
            direction=direction
        )
        
        # 分析時間
        elapsed_time = (time.time() - start_time) * 1000
        
        return {
            'target_component': component_id,
            'affected_components': list(affected),
            'affected_count': len(affected),
            'depth': depth,
            'direction': direction,
            'analysis_time_ms': round(elapsed_time, 3)
        }
    
    def find_path(
        self,
        source: str,
        target: str
    ) -> Optional[List[str]]:
        """
        最短経路を探索
        
        Args:
            source: 開始ノード
            target: 終了ノード
        
        Returns:
            最短経路のノードリスト、経路がなければNone
        """
        return self.graph_db.get_shortest_path(source, target)
    
    def detect_cycles(self) -> List[List[str]]:
        """
        循環依存を検出
        
        Returns:
            循環依存のリスト（各要素は循環を構成するノードリスト）
        """
        return self.graph_db.find_cycles()
    
    def generate_test_recommendations(
        self,
        component_id: str,
        change_lines: int = 50
    ) -> Dict[str, Any]:
        """
        推奨テストを生成
        
        Args:
            component_id: 変更対象コンポーネント
            change_lines: 変更行数（デフォルト50）
        
        Returns:
            {
                'impact_analysis': {...},       # 影響範囲分析結果
                'score_result': {...},          # スコアリング結果
                'recommendations': {...}        # 推奨アクション
            }
        """
        from agents.observer_enhanced.graph.scoring_engine import ScoringEngine
        
        # 1. 影響範囲分析
        impact = self.analyze_impact(component_id, depth=3, direction='in')
        
        # 2. メタデータ収集
        component_metadata = {}
        for comp_id in [component_id] + impact['affected_components']:
            metadata = self.graph_db.get_component(comp_id)
            if metadata:
                component_metadata[comp_id] = metadata
        
        # 3. スコアリング
        engine = ScoringEngine()
        score_result = engine.calculate_impact_score(
            component_id=component_id,
            change_lines=change_lines,
            affected_components=set(impact['affected_components']),
            component_metadata=component_metadata
        )
        
        # 4. 推奨アクション生成
        recommendations = engine.generate_recommendation(score_result)
        
        return {
            'impact_analysis': impact,
            'score_result': score_result,
            'recommendations': recommendations
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 使用例
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    # テスト実行
    db = SystemGraphDB()
    
    # サンプルデータ
    db.add_component('PMAgent', {'type': 'agent', 'lines': 850})
    db.add_component('TaskExecutor', {'type': 'agent', 'lines': 1200})
    db.add_component('SheetsManager', {'type': 'tool', 'lines': 1150})
    
    db.add_dependency('PMAgent', 'SheetsManager', 'import')
    db.add_dependency('TaskExecutor', 'SheetsManager', 'import')
    
    analyzer = ImpactAnalyzer(db)
    
    # 影響範囲分析
    result = analyzer.analyze_impact('SheetsManager')
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 影響範囲分析結果")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"対象: {result['target_component']}")
    print(f"影響コンポーネント数: {result['affected_count']}")
    print(f"影響先: {result['affected_components']}")
    print(f"分析時間: {result['analysis_time_ms']}ms")
    
    # 推奨テスト生成
    recommendations = analyzer.generate_test_recommendations('SheetsManager', 100)
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("💡 推奨テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"リスクレベル: {recommendations['score_result']['risk_level']}")
    print(f"総合スコア: {recommendations['score_result']['total_score']}点")
    print("\n推奨アクション:")
    for test in recommendations['recommendations']['recommended_tests']:
        print(f"  - {test}")

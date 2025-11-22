"""
ImpactAnalyzer - 影響範囲分析エンジン

【設計方針】
- コード変更時の影響範囲を定量的に分析
- 影響度スコアの計算（変更行数 × 依存先数 × 重要度係数）
- 推奨テストケースの自動生成

【使用例】
```python
from agents.observer_enhanced.graph.impact_analyzer import ImpactAnalyzer

analyzer = ImpactAnalyzer()

# 影響範囲分析
impact = analyzer.analyze_impact(
    component='SheetsManager',
    change_type='modify',
    changed_lines=50
)

print(f"影響を受けるコンポーネント: {impact['affected_components']}")
print(f"影響度スコア: {impact['impact_score']}")
print(f"推奨テスト: {impact['recommended_tests']}")
```

【パフォーマンス目標】
- 影響範囲分析: <100ms
- 推奨テスト生成: <50ms
"""

from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from agents.observer_enhanced.graph.graph_db import SystemGraphDB


class ImpactAnalyzer:
    """影響範囲分析エンジン"""
    
    def __init__(self, graph_db: Optional[SystemGraphDB] = None):
        """
        初期化
        
        Args:
            graph_db: システムグラフDB（省略時は新規作成）
        """
        self.graph_db = graph_db or SystemGraphDB()
        
        # 重要度係数（コンポーネントタイプ別）
        self.importance_factors = {
            'agent': 3.0,      # エージェント（高重要度）
            'tool': 2.5,       # ツール（中高重要度）
            'service': 2.0,    # サービス（中重要度）
            'utility': 1.5,    # ユーティリティ（低重要度）
            'unknown': 1.0     # 不明（デフォルト）
        }
        
        # 変更タイプ係数
        self.change_type_factors = {
            'add': 0.5,        # 追加（影響小）
            'modify': 1.0,     # 修正（影響中）
            'delete': 2.0,     # 削除（影響大）
            'refactor': 1.5    # リファクタ（影響中大）
        }
    
    def analyze_impact(self, component: str, change_type: str = 'modify',
                      changed_lines: int = 10, depth: int = 3) -> Dict[str, Any]:
        """
        影響範囲を分析
        
        Args:
            component: 変更対象コンポーネント
            change_type: 変更タイプ（'add', 'modify', 'delete', 'refactor'）
            changed_lines: 変更行数
            depth: 探索深さ
            
        Returns:
            影響分析結果
            
        Performance:
            - 目標実行時間: <100ms
        """
        start_time = datetime.now()
        
        # 1. 基本情報取得
        component_info = self.graph_db.get_component(component)
        if not component_info:
            return {
                'success': False,
                'error': f'Component not found: {component}'
            }
        
        # 2. 影響を受けるコンポーネント取得（依存元）
        affected = self.graph_db.get_impact_range(component, depth=depth, direction='in')
        
        # 3. 影響度スコア計算
        impact_score = self._calculate_impact_score(
            component=component,
            affected_components=affected,
            change_type=change_type,
            changed_lines=changed_lines
        )
        
        # 4. リスクレベル判定
        risk_level = self._determine_risk_level(impact_score)
        
        # 5. 推奨テスト生成
        recommended_tests = self._generate_recommended_tests(
            component=component,
            affected_components=affected,
            risk_level=risk_level
        )
        
        # 6. 影響詳細
        impact_details = self._get_impact_details(component, affected)
        
        elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'success': True,
            'component': component,
            'change_type': change_type,
            'changed_lines': changed_lines,
            'affected_components': list(affected),
            'affected_count': len(affected),
            'impact_score': round(impact_score, 2),
            'risk_level': risk_level,
            'recommended_tests': recommended_tests,
            'impact_details': impact_details,
            'analysis_time_ms': round(elapsed_time, 2)
        }
    
    def _calculate_impact_score(self, component: str, affected_components: Set[str],
                                change_type: str, changed_lines: int) -> float:
        """
        影響度スコアを計算
        
        計算式:
            影響度スコア = 変更行数 × 依存先数 × 変更タイプ係数 × 重要度係数
            
        Args:
            component: 変更対象コンポーネント
            affected_components: 影響を受けるコンポーネント
            change_type: 変更タイプ
            changed_lines: 変更行数
            
        Returns:
            影響度スコア（0-1000+）
        """
        # コンポーネント情報取得
        comp_info = self.graph_db.get_component(component)
        comp_type = comp_info.get('type', 'unknown') if comp_info else 'unknown'
        
        # 各係数取得
        importance_factor = self.importance_factors.get(comp_type, 1.0)
        change_factor = self.change_type_factors.get(change_type, 1.0)
        
        # スコア計算
        score = (
            changed_lines *
            len(affected_components) *
            change_factor *
            importance_factor
        )
        
        return score
    
    def _determine_risk_level(self, impact_score: float) -> str:
        """
        リスクレベルを判定
        
        Args:
            impact_score: 影響度スコア
            
        Returns:
            リスクレベル（'low', 'medium', 'high', 'critical'）
        """
        if impact_score < 50:
            return 'low'
        elif impact_score < 150:
            return 'medium'
        elif impact_score < 300:
            return 'high'
        else:
            return 'critical'
    
    def _generate_recommended_tests(self, component: str, affected_components: Set[str],
                                   risk_level: str) -> List[Dict[str, Any]]:
        """
        推奨テストを生成
        
        Args:
            component: 変更対象コンポーネント
            affected_components: 影響を受けるコンポーネント
            risk_level: リスクレベル
            
        Returns:
            推奨テストのリスト
        """
        tests = []
        
        # 1. 変更対象自体のユニットテスト（必須）
        tests.append({
            'type': 'unit',
            'target': component,
            'priority': 'high',
            'reason': '変更対象コンポーネントの動作検証'
        })
        
        # 2. 直接依存するコンポーネントの統合テスト
        direct_deps = self.graph_db.get_dependencies(component, direction='in')
        for dep in direct_deps[:5]:  # 上位5件
            tests.append({
                'type': 'integration',
                'target': f"{dep['source']} ↔ {component}",
                'priority': 'high',
                'reason': f"{dep['source']}との連携動作検証"
            })
        
        # 3. リスクレベルに応じた追加テスト
        if risk_level in ['high', 'critical']:
            # 影響を受ける全コンポーネントのテスト
            for affected in list(affected_components)[:10]:  # 上位10件
                tests.append({
                    'type': 'regression',
                    'target': affected,
                    'priority': 'medium',
                    'reason': f'{affected}への影響確認（回帰テスト）'
                })
            
            # E2Eテスト
            tests.append({
                'type': 'e2e',
                'target': 'システム全体フロー',
                'priority': 'high',
                'reason': 'システム全体への影響確認'
            })
        
        return tests
    
    def _get_impact_details(self, component: str, affected: Set[str]) -> List[Dict[str, Any]]:
        """
        影響詳細を取得
        
        Args:
            component: 変更対象コンポーネント
            affected: 影響を受けるコンポーネント
            
        Returns:
            影響詳細のリスト
        """
        details = []
        
        for affected_comp in affected:
            # 最短経路取得
            path = self.graph_db.get_shortest_path(affected_comp, component)
            
            # コンポーネント情報
            comp_info = self.graph_db.get_component(affected_comp)
            
            details.append({
                'component': affected_comp,
                'type': comp_info.get('type', 'unknown') if comp_info else 'unknown',
                'distance': len(path) - 1 if path else None,
                'path': path
            })
        
        # 距離でソート（近い順）
        details.sort(key=lambda x: x['distance'] if x['distance'] is not None else 999)
        
        return details
    
    def get_bottlenecks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        ボトルネックとなるコンポーネント検出
        
        ボトルネック = 多くのコンポーネントに依存されている
        
        Args:
            limit: 取得件数
            
        Returns:
            ボトルネックコンポーネントのリスト
        """
        most_dependent = self.graph_db.get_most_dependent(limit=limit)
        
        bottlenecks = []
        for component, dep_count in most_dependent:
            comp_info = self.graph_db.get_component(component)
            
            bottlenecks.append({
                'component': component,
                'dependent_count': dep_count,
                'type': comp_info.get('type', 'unknown') if comp_info else 'unknown',
                'risk': 'critical' if dep_count >= 5 else 'high' if dep_count >= 3 else 'medium'
            })
        
        return bottlenecks
    
    def detect_circular_dependencies(self) -> List[Dict[str, Any]]:
        """
        循環依存を検出
        
        Returns:
            循環依存のリスト
        """
        cycles = self.graph_db.find_cycles()
        
        circular_deps = []
        for cycle in cycles:
            circular_deps.append({
                'components': cycle,
                'length': len(cycle),
                'risk': 'critical' if len(cycle) <= 3 else 'high'
            })
        
        return circular_deps
    
    def export_report(self, component: str, filepath: Optional[Path] = None) -> str:
        """
        影響分析レポートをエクスポート
        
        Args:
            component: 対象コンポーネント
            filepath: 保存先（省略時は文字列で返す）
            
        Returns:
            レポートJSON文字列
        """
        # 影響分析実行
        impact = self.analyze_impact(component)
        
        # ボトルネック検出
        bottlenecks = self.get_bottlenecks(limit=5)
        
        # 循環依存検出
        circular = self.detect_circular_dependencies()
        
        # レポート作成
        report = {
            'generated_at': datetime.now().isoformat(),
            'target_component': component,
            'impact_analysis': impact,
            'system_bottlenecks': bottlenecks,
            'circular_dependencies': circular,
            'recommendations': self._generate_recommendations(impact, bottlenecks, circular)
        }
        
        json_str = json.dumps(report, indent=2, ensure_ascii=False)
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    def _generate_recommendations(self, impact: Dict, bottlenecks: List, circular: List) -> List[str]:
        """推奨事項生成"""
        recommendations = []
        
        # 影響度に応じた推奨
        if impact.get('risk_level') == 'critical':
            recommendations.append('⚠️ 影響度が非常に高いため、変更前に十分なテスト実施を推奨')
            recommendations.append('📝 変更内容をチームに共有し、レビューを受けることを推奨')
        
        # ボトルネックに関する推奨
        if bottlenecks:
            recommendations.append(f'🔧 ボトルネックコンポーネント（{bottlenecks[0]["component"]}）の変更は慎重に')
        
        # 循環依存に関する推奨
        if circular:
            recommendations.append('⚠️ 循環依存が検出されました。リファクタリングを検討してください')
        
        return recommendations


def main():
    """テスト実行"""
    print("🔍 ImpactAnalyzer テスト実行")
    print("=" * 80)
    
    # グラフDB準備
    db = SystemGraphDB()
    db.add_component('PMAgent', {'type': 'agent', 'lines': 850})
    db.add_component('TaskExecutor', {'type': 'agent', 'lines': 1200})
    db.add_component('SheetsManager', {'type': 'tool', 'lines': 1150})
    db.add_component('KnowledgeManager', {'type': 'tool', 'lines': 980})
    
    db.add_dependency('PMAgent', 'SheetsManager', 'import', weight=3.0)
    db.add_dependency('TaskExecutor', 'SheetsManager', 'import', weight=5.0)
    db.add_dependency('PMAgent', 'KnowledgeManager', 'import', weight=2.0)
    
    # ImpactAnalyzer作成
    analyzer = ImpactAnalyzer(graph_db=db)
    
    # 影響分析
    print("\n📊 影響分析: SheetsManager変更時")
    impact = analyzer.analyze_impact(
        component='SheetsManager',
        change_type='modify',
        changed_lines=50
    )
    
    print(f"  影響を受けるコンポーネント: {impact['affected_count']}個")
    print(f"  影響度スコア: {impact['impact_score']}")
    print(f"  リスクレベル: {impact['risk_level']}")
    print(f"  推奨テスト数: {len(impact['recommended_tests'])}")
    print(f"  分析時間: {impact['analysis_time_ms']}ms")
    
    # ボトルネック検出
    print("\n🔧 ボトルネック検出")
    bottlenecks = analyzer.get_bottlenecks(limit=3)
    for bn in bottlenecks:
        print(f"  {bn['component']}: {bn['dependent_count']}個が依存（リスク: {bn['risk']}）")
    
    print("\n✅ ImpactAnalyzer テスト完了")


if __name__ == '__main__':
    main()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # P3-T006: 推奨テスト生成
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
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
        impact = self.analyze_impact(component_id)
        
        # 2. メタデータ収集
        component_metadata = {}
        for comp_id in [component_id] + list(impact['affected_components']):
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

"""
影響度スコアリングエンジン

【責任】
- コンポーネント変更時の影響度を数値化
- 複数の指標を統合したスコアリング
- リスクレベル判定（Low/Medium/High/Critical）

【使用箇所】
- ImpactAnalyzer（影響範囲分析後のスコア計算）
- 変更レビュー時のリスク評価
"""

from typing import Dict, Any, List, Set
from pathlib import Path
import math


class ScoringEngine:
    """影響度スコアリングエンジン"""
    
    # 重要度係数（コンポーネントタイプ別）
    IMPORTANCE_WEIGHTS = {
        'agent': 3.0,      # エージェント（最重要）
        'tool': 2.0,       # ツール（共通利用）
        'service': 1.5,    # サービス
        'test': 1.0,       # テスト
        'script': 0.8,     # スクリプト
        'config': 0.5      # 設定ファイル
    }
    
    # リスクレベル閾値
    RISK_THRESHOLDS = {
        'critical': 80,    # 80点以上
        'high': 60,        # 60-79点
        'medium': 40,      # 40-59点
        'low': 0           # 0-39点
    }
    
    def __init__(self):
        """初期化"""
        pass
    
    def calculate_impact_score(
        self,
        component_id: str,
        change_lines: int,
        affected_components: Set[str],
        component_metadata: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        影響度スコアを計算
        
        Args:
            component_id: 変更対象コンポーネントID
            change_lines: 変更行数
            affected_components: 影響を受けるコンポーネント集合
            component_metadata: 各コンポーネントのメタデータ
        
        Returns:
            {
                'total_score': 85.5,          # 総合スコア（0-100）
                'risk_level': 'critical',     # リスクレベル
                'breakdown': {                # 内訳
                    'change_impact': 30.0,    # 変更規模の影響
                    'dependency_impact': 45.0,# 依存関係の影響
                    'importance_impact': 10.5 # 重要度の影響
                },
                'affected_count': 12,         # 影響コンポーネント数
                'critical_affected': ['PMAgent', 'TaskExecutor']  # クリティカルな影響先
            }
        """
        # 1. 変更規模スコア（0-40点）
        change_score = self._calculate_change_score(change_lines)
        
        # 2. 依存関係スコア（0-50点）
        dependency_score = self._calculate_dependency_score(
            affected_components,
            component_metadata
        )
        
        # 3. 重要度スコア（0-10点）
        importance_score = self._calculate_importance_score(
            component_id,
            component_metadata
        )
        
        # 総合スコア
        total_score = change_score + dependency_score + importance_score
        
        # リスクレベル判定
        risk_level = self._determine_risk_level(total_score)
        
        # クリティカルな影響先を抽出
        critical_affected = self._find_critical_affected(
            affected_components,
            component_metadata
        )
        
        return {
            'total_score': round(total_score, 2),
            'risk_level': risk_level,
            'breakdown': {
                'change_impact': round(change_score, 2),
                'dependency_impact': round(dependency_score, 2),
                'importance_impact': round(importance_score, 2)
            },
            'affected_count': len(affected_components),
            'critical_affected': critical_affected
        }
    
    def _calculate_change_score(self, change_lines: int) -> float:
        """
        変更規模スコアを計算
        
        スコアリング:
        - 1-10行: 5点
        - 11-50行: 15点
        - 51-100行: 25点
        - 101-200行: 35点
        - 201行以上: 40点
        """
        if change_lines <= 10:
            return 5.0
        elif change_lines <= 50:
            return 15.0
        elif change_lines <= 100:
            return 25.0
        elif change_lines <= 200:
            return 35.0
        else:
            return 40.0
    
    def _calculate_dependency_score(
        self,
        affected_components: Set[str],
        component_metadata: Dict[str, Dict[str, Any]]
    ) -> float:
        """
        依存関係スコアを計算
        
        計算式:
        score = min(50, affected_count * avg_importance * 2)
        
        - 影響コンポーネント数が多いほど高スコア
        - 影響先の重要度が高いほど高スコア
        """
        if not affected_components:
            return 0.0
        
        # 影響先の平均重要度を計算
        total_importance = 0.0
        for comp_id in affected_components:
            metadata = component_metadata.get(comp_id, {})
            comp_type = metadata.get('type', 'script')
            importance = self.IMPORTANCE_WEIGHTS.get(comp_type, 1.0)
            total_importance += importance
        
        avg_importance = total_importance / len(affected_components)
        
        # スコア計算（最大50点）
        score = min(50.0, len(affected_components) * avg_importance * 2)
        
        return score
    
    def _calculate_importance_score(
        self,
        component_id: str,
        component_metadata: Dict[str, Dict[str, Any]]
    ) -> float:
        """
        重要度スコアを計算
        
        変更対象コンポーネントの重要度に応じて加点
        """
        metadata = component_metadata.get(component_id, {})
        comp_type = metadata.get('type', 'script')
        importance = self.IMPORTANCE_WEIGHTS.get(comp_type, 1.0)
        
        # 重要度を0-10点にスケール
        score = (importance / 3.0) * 10.0
        
        return score
    
    def _determine_risk_level(self, total_score: float) -> str:
        """
        リスクレベルを判定
        
        Args:
            total_score: 総合スコア（0-100）
        
        Returns:
            'low' | 'medium' | 'high' | 'critical'
        """
        if total_score >= self.RISK_THRESHOLDS['critical']:
            return 'critical'
        elif total_score >= self.RISK_THRESHOLDS['high']:
            return 'high'
        elif total_score >= self.RISK_THRESHOLDS['medium']:
            return 'medium'
        else:
            return 'low'
    
    def _find_critical_affected(
        self,
        affected_components: Set[str],
        component_metadata: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        クリティカルな影響先を抽出
        
        条件:
        - type='agent' のコンポーネント
        - 上位3件
        """
        critical_comps = []
        
        for comp_id in affected_components:
            metadata = component_metadata.get(comp_id, {})
            if metadata.get('type') == 'agent':
                critical_comps.append(comp_id)
        
        # 上位3件
        return critical_comps[:3]
    
    def generate_recommendation(
        self,
        score_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        推奨アクションを生成
        
        Args:
            score_result: calculate_impact_score()の結果
        
        Returns:
            {
                'recommended_tests': [...],      # 推奨テスト
                'review_priority': 'high',       # レビュー優先度
                'rollback_plan': '...',          # ロールバック計画
                'monitoring_points': [...]       # 監視ポイント
            }
        """
        risk_level = score_result['risk_level']
        affected_count = score_result['affected_count']
        critical_affected = score_result['critical_affected']
        
        # リスクレベル別の推奨
        if risk_level == 'critical':
            return {
                'recommended_tests': [
                    '全既存テスト実行（84.3%以上維持必須）',
                    '影響先コンポーネントの統合テスト',
                    'エンドツーエンドテスト',
                    'ロールバックテスト'
                ],
                'review_priority': 'critical',
                'rollback_plan': 'Git revert準備、バックアップ確認必須',
                'monitoring_points': [
                    '変更直後30分は常時監視',
                    'エラーログのリアルタイムチェック',
                    f'影響先{len(critical_affected)}コンポーネントの動作確認'
                ]
            }
        
        elif risk_level == 'high':
            return {
                'recommended_tests': [
                    '影響先コンポーネントの単体テスト',
                    '既存テスト実行（成功率確認）',
                    '統合テスト（主要フロー）'
                ],
                'review_priority': 'high',
                'rollback_plan': 'Git revert準備',
                'monitoring_points': [
                    '変更後1時間は監視',
                    'エラー発生時は即座に対応'
                ]
            }
        
        elif risk_level == 'medium':
            return {
                'recommended_tests': [
                    '変更箇所の単体テスト',
                    '主要な依存先のテスト'
                ],
                'review_priority': 'medium',
                'rollback_plan': '必要時にGit revert',
                'monitoring_points': [
                    '定期的なログ確認（1時間ごと）'
                ]
            }
        
        else:  # low
            return {
                'recommended_tests': [
                    '変更箇所の単体テスト'
                ],
                'review_priority': 'low',
                'rollback_plan': '通常のGit運用',
                'monitoring_points': [
                    '日次ヘルスチェックで確認'
                ]
            }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 使用例
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    # テスト実行
    engine = ScoringEngine()
    
    # サンプルデータ
    component_metadata = {
        'PMAgent': {'type': 'agent', 'lines': 850},
        'TaskExecutor': {'type': 'agent', 'lines': 1200},
        'SheetsManager': {'type': 'tool', 'lines': 1150},
        'Dashboard': {'type': 'service', 'lines': 450}
    }
    
    affected = {'PMAgent', 'TaskExecutor', 'Dashboard'}
    
    # スコア計算
    result = engine.calculate_impact_score(
        component_id='SheetsManager',
        change_lines=150,
        affected_components=affected,
        component_metadata=component_metadata
    )
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 影響度スコア計算結果")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"総合スコア: {result['total_score']}点")
    print(f"リスクレベル: {result['risk_level']}")
    print(f"影響コンポーネント数: {result['affected_count']}")
    print(f"クリティカル影響先: {result['critical_affected']}")
    print("\n内訳:")
    for key, value in result['breakdown'].items():
        print(f"  {key}: {value}点")
    
    # 推奨アクション
    recommendation = engine.generate_recommendation(result)
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("💡 推奨アクション")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"レビュー優先度: {recommendation['review_priority']}")
    print(f"ロールバック計画: {recommendation['rollback_plan']}")
    print("\n推奨テスト:")
    for test in recommendation['recommended_tests']:
        print(f"  - {test}")
    print("\n監視ポイント:")
    for point in recommendation['monitoring_points']:
        print(f"  - {point}")

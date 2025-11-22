"""
変更影響分析ツール

要件定義書 FR-004 実装:
- Git変更検出
- 影響範囲自動計算
- リスク判定
- 推奨テスト生成

目標: 影響範囲分析 <5秒
"""

import subprocess
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import logging
import sys
import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class ChangeImpact:
    """変更影響を表すデータクラス"""
    changed_file: str
    changed_lines: int
    affected_components: List[str]
    impact_score: float
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    recommended_tests: List[str]


class ChangeImpactAnalyzer:
    """
    Git変更を検出し、影響範囲を自動計算
    
    影響度計算式（要件定義書より）:
    影響度 = 変更行数 × 依存先数 × 重要度係数
    
    重要度係数:
    - agents/ 配下: 3.0
    - tools/ 配下: 2.0
    - tests/ 配下: 1.0
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path('/workspaces/gemini_AI_Agent')
        self.dependency_graph = self._build_simple_graph()
        
        # 重要度係数
        self.importance_weights = {
            'agents/': 3.0,
            'core_agents/': 3.0,
            'tools/': 2.0,
            'tests/': 1.0,
            'default': 1.5
        }
    
    def _build_simple_graph(self) -> nx.DiGraph:
        """
        簡易的な依存グラフを構築
        （graph_db.pyに依存しない独立実装）
        """
        graph = nx.DiGraph()
        
        # 主要コンポーネントを登録
        core_components = [
            'pm_agent',
            'task_executor',
            'review_agent',
            'knowledge_manager',
            'sheets_manager',
            'system_observer',
            'code_generator',
            'quality_evaluator'
        ]
        
        for comp in core_components:
            graph.add_node(comp)
        
        # 既知の依存関係を登録（簡易版）
        dependencies = [
            ('pm_agent', 'sheets_manager'),
            ('pm_agent', 'knowledge_manager'),
            ('task_executor', 'sheets_manager'),
            ('task_executor', 'code_generator'),
            ('review_agent', 'quality_evaluator'),
            ('code_generator', 'knowledge_manager'),
        ]
        
        for source, target in dependencies:
            graph.add_edge(source, target)
        
        return graph
    
    def get_git_changes(self, since: str = 'HEAD~1') -> Dict[str, int]:
        """
        Git変更を取得
        
        Args:
            since: 比較基準（デフォルト: 直前のコミット）
            
        Returns:
            {file_path: changed_lines} の辞書
        """
        try:
            # git diff で変更ファイルと行数を取得
            cmd = f"git diff --numstat {since} HEAD"
            result = subprocess.run(
                cmd.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            changes = {}
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 3:
                    added = parts[0]
                    deleted = parts[1]
                    file_path = parts[2]
                    
                    # Pythonファイルのみ対象
                    if file_path.endswith('.py'):
                        try:
                            changed_lines = int(added) + int(deleted)
                            changes[file_path] = changed_lines
                        except ValueError:
                            continue
            
            return changes
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git diff failed: {e}")
            return {}
    
    def analyze_change_impact(
        self,
        changed_file: str,
        changed_lines: int
    ) -> ChangeImpact:
        """
        1ファイルの変更影響を分析
        
        Args:
            changed_file: 変更されたファイルパス
            changed_lines: 変更行数
            
        Returns:
            変更影響の分析結果
        """
        # 1. 重要度係数を取得
        importance = self._get_importance(changed_file)
        
        # 2. 影響範囲を計算
        component_id = self._file_to_component(changed_file)
        affected = self._get_impact_range(component_id, depth=3)
        
        # 3. 影響度スコア計算
        impact_score = changed_lines * len(affected) * importance
        
        # 4. リスクレベル判定
        risk_level = self._calculate_risk_level(impact_score, changed_lines, len(affected))
        
        # 5. 推奨テスト生成
        recommended_tests = self._generate_test_recommendations(
            changed_file,
            list(affected),
            risk_level
        )
        
        return ChangeImpact(
            changed_file=changed_file,
            changed_lines=changed_lines,
            affected_components=list(affected),
            impact_score=impact_score,
            risk_level=risk_level,
            recommended_tests=recommended_tests
        )
    
    def _get_impact_range(self, component_id: str, depth: int = 3) -> Set[str]:
        """
        影響範囲を計算（BFS探索）
        
        Args:
            component_id: 変更対象
            depth: 探索深さ
            
        Returns:
            影響を受けるコンポーネントのセット
        """
        if component_id not in self.dependency_graph.nodes:
            return set()
        
        affected = set()
        
        # BFS探索で依存先を取得
        try:
            # NetworkXのdescendants関数を使用（深さ制限なし版）
            descendants = nx.descendants(self.dependency_graph, component_id)
            affected.update(descendants)
        except nx.NetworkXError:
            pass
        
        return affected
    
    def _get_importance(self, file_path: str) -> float:
        """ファイルの重要度係数を取得"""
        for prefix, weight in self.importance_weights.items():
            if file_path.startswith(prefix):
                return weight
        return self.importance_weights['default']
    
    def _file_to_component(self, file_path: str) -> str:
        """
        ファイルパスからコンポーネントIDに変換
        
        例: agents/pm_agent.py → pm_agent
        """
        path = Path(file_path)
        return path.stem
    
    def _calculate_risk_level(
        self,
        impact_score: float,
        changed_lines: int,
        affected_count: int
    ) -> str:
        """
        リスクレベルを判定
        
        判定ロジック:
        - critical: スコア > 200 または 影響先 > 10
        - high: スコア > 100 または 影響先 > 5
        - medium: スコア > 50 または 影響先 > 3
        - low: それ以外
        """
        if impact_score > 200 or affected_count > 10:
            return 'critical'
        elif impact_score > 100 or affected_count > 5:
            return 'high'
        elif impact_score > 50 or affected_count > 3:
            return 'medium'
        else:
            return 'low'
    
    def _generate_test_recommendations(
        self,
        changed_file: str,
        affected_components: List[str],
        risk_level: str
    ) -> List[str]:
        """
        推奨テストケースを生成
        
        Args:
            changed_file: 変更ファイル
            affected_components: 影響を受けるコンポーネント
            risk_level: リスクレベル
            
        Returns:
            推奨テストのリスト
        """
        recommendations = []
        
        # 1. 変更ファイル自体のテスト
        test_file = self._get_test_file(changed_file)
        if test_file:
            recommendations.append(f"pytest {test_file}")
        
        # 2. リスクレベルに応じて影響先のテストを追加
        if risk_level in ['high', 'critical']:
            for component in affected_components[:5]:  # 上位5件
                test_file = self._get_test_file(f"{component}.py")
                if test_file:
                    recommendations.append(f"pytest {test_file}")
        
        # 3. criticalの場合は統合テストも推奨
        if risk_level == 'critical':
            recommendations.append("pytest tests/integration/ -v")
        
        return recommendations
    
    def _get_test_file(self, source_file: str) -> Optional[str]:
        """
        ソースファイルに対応するテストファイルを取得
        
        例: agents/pm_agent.py → tests/test_pm_agent.py
        """
        path = Path(source_file)
        
        # agents/xxx.py → tests/test_xxx.py
        if 'agents/' in str(path) or 'core_agents/' in str(path):
            test_path = self.project_root / 'tests' / f"test_{path.name}"
            if test_path.exists():
                return str(test_path)
        
        # tools/xxx.py → tests/test_xxx.py
        if 'tools/' in str(path):
            test_path = self.project_root / 'tests' / f"test_{path.name}"
            if test_path.exists():
                return str(test_path)
        
        return None
    
    def analyze_all_changes(self, since: str = 'HEAD~1') -> List[ChangeImpact]:
        """
        すべての変更を分析
        
        Args:
            since: 比較基準
            
        Returns:
            影響分析結果のリスト
        """
        changes = self.get_git_changes(since)
        
        results = []
        for file_path, changed_lines in changes.items():
            impact = self.analyze_change_impact(file_path, changed_lines)
            results.append(impact)
        
        # 影響度スコアの高い順にソート
        results.sort(key=lambda x: x.impact_score, reverse=True)
        
        return results
    
    def generate_report(self, impacts: List[ChangeImpact]) -> Dict:
        """影響分析レポートを生成"""
        return {
            'total_changes': len(impacts),
            'risk_summary': {
                'critical': len([i for i in impacts if i.risk_level == 'critical']),
                'high': len([i for i in impacts if i.risk_level == 'high']),
                'medium': len([i for i in impacts if i.risk_level == 'medium']),
                'low': len([i for i in impacts if i.risk_level == 'low'])
            },
            'total_affected_components': len(set(
                comp
                for impact in impacts
                for comp in impact.affected_components
            )),
            'recommended_tests': list(set(
                test
                for impact in impacts
                for test in impact.recommended_tests
            )),
            'details': [
                {
                    'file': impact.changed_file,
                    'lines': impact.changed_lines,
                    'score': impact.impact_score,
                    'risk': impact.risk_level,
                    'affected': impact.affected_components,
                    'tests': impact.recommended_tests
                }
                for impact in impacts
            ]
        }


def main():
    """テスト実行"""
    import time
    
    analyzer = ChangeImpactAnalyzer()
    
    print("🔍 変更影響分析開始...")
    
    start = time.time()
    
    # 最新の変更を分析
    impacts = analyzer.analyze_all_changes(since='HEAD~1')
    
    duration = time.time() - start
    
    if not impacts:
        print("✅ 変更がないか、Pythonファイルの変更がありません")
        return
    
    # レポート生成
    report = analyzer.generate_report(impacts)
    
    print("\n" + "=" * 60)
    print("📊 変更影響分析結果")
    print("=" * 60)
    print(f"分析時間: {duration:.2f}秒")
    print(f"変更ファイル数: {report['total_changes']}")
    print(f"影響コンポーネント数: {report['total_affected_components']}")
    
    print("\n【リスク別集計】")
    for level, count in report['risk_summary'].items():
        if count > 0:
            print(f"  {level.upper()}: {count}件")
    
    print("\n【推奨テスト】")
    for test in report['recommended_tests'][:10]:
        print(f"  {test}")
    
    # 詳細表示（上位5件）
    print("\n" + "=" * 60)
    print("📋 影響度上位5件の詳細")
    print("=" * 60)
    for i, detail in enumerate(report['details'][:5], 1):
        print(f"\n{i}. {detail['file']}")
        print(f"   変更行数: {detail['lines']}")
        print(f"   影響スコア: {detail['score']:.1f}")
        print(f"   リスク: {detail['risk'].upper()}")
        print(f"   影響先: {len(detail['affected'])}コンポーネント")


if __name__ == '__main__':
    main()

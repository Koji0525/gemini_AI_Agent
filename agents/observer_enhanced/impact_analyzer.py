"""
影響範囲分析器

このモジュールは、コード変更の影響範囲を分析します。

主要機能:
    - 変更ファイルの影響範囲計算
    - テスト推奨の生成
    - リスク評価
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from .graph_db import SystemGraphDB
except ImportError:
    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    from graph_db import SystemGraphDB

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """
    影響範囲分析器

    Attributes:
        graph_db: システムグラフDB
    """

    def __init__(self, graph_db: Optional[SystemGraphDB] = None):
        """
        初期化

        Args:
            graph_db: システムグラフDB (Noneの場合は新規作成)
        """
        self.graph_db = graph_db if graph_db else SystemGraphDB()
        logger.info("Initialized ImpactAnalyzer")

    def analyze_component_change(self, component_id: str, depth: int = 3) -> Dict[str, Any]:
        """
        コンポーネント変更の影響を分析

        Args:
            component_id: 変更対象コンポーネント
            depth: 探索深さ

        Returns:
            Dict: 影響分析レポート
        """
        logger.info(f"Analyzing impact of changes to '{component_id}'")

        # 影響範囲を計算
        direct_impact = self.graph_db.get_impact_range(component_id, depth=1)
        full_impact = self.graph_db.get_impact_range(component_id, depth=depth)
        reverse_impact = self.graph_db.get_reverse_impact_range(component_id, depth=depth)

        # リスクレベルを計算
        risk_level = self._calculate_risk_level(
            len(direct_impact), len(full_impact), len(reverse_impact)
        )

        # テスト推奨を生成
        recommended_tests = self._generate_test_recommendations(
            component_id, direct_impact, full_impact
        )

        report = {
            "component_id": component_id,
            "risk_level": risk_level,
            "impact_summary": {
                "direct_dependencies": len(direct_impact),
                "total_affected_components": len(full_impact),
                "reverse_dependencies": len(reverse_impact),
            },
            "affected_components": {
                "direct": list(direct_impact),
                "full": list(full_impact),
                "reverse": list(reverse_impact),
            },
            "recommended_tests": recommended_tests,
        }

        logger.info(
            f"Impact analysis completed: {len(full_impact)} components affected (risk: {risk_level})"
        )

        return report

    def _calculate_risk_level(self, direct_count: int, full_count: int, reverse_count: int) -> str:
        """
        リスクレベルを計算

        Args:
            direct_count: 直接依存数
            full_count: 全影響範囲
            reverse_count: 逆依存数

        Returns:
            str: リスクレベル ('low', 'medium', 'high', 'critical')
        """
        # スコア計算
        score = (direct_count * 2) + full_count + (reverse_count * 1.5)

        if score >= 50:
            return "critical"
        elif score >= 30:
            return "high"
        elif score >= 15:
            return "medium"
        else:
            return "low"

    def _generate_test_recommendations(
        self, component_id: str, direct_impact: Set[str], full_impact: Set[str]
    ) -> List[str]:
        """
        テスト推奨を生成

        Args:
            component_id: 変更対象
            direct_impact: 直接影響
            full_impact: 全影響

        Returns:
            List[str]: テスト推奨のリスト
        """
        recommendations = []

        # 変更対象自体のテスト
        recommendations.append(f"Unit test for {component_id}")

        # 直接依存のテスト
        for component in list(direct_impact)[:5]:  # 最大5個
            recommendations.append(f"Integration test: {component_id} -> {component}")

        # 影響範囲が大きい場合
        if len(full_impact) > 10:
            recommendations.append("E2E test covering main workflows")

        return recommendations


def main():
    """メイン関数 (テスト用)"""
    print("🔍 ImpactAnalyzer Test")

    analyzer = ImpactAnalyzer()

    # テスト用のコンポーネントを追加
    analyzer.graph_db.add_component(
        "test_component_a", {"file": "test_a.py", "lines": 100, "type": "agent"}
    )
    analyzer.graph_db.add_component(
        "test_component_b", {"file": "test_b.py", "lines": 200, "type": "tool"}
    )
    analyzer.graph_db.add_dependency("test_component_a", "test_component_b", "import")

    # 影響分析を実行
    report = analyzer.analyze_component_change("test_component_a")

    print(f"\n📊 Impact Analysis Report:")
    print(f"  Component: {report['component_id']}")
    print(f"  Risk Level: {report['risk_level']}")
    print(f"  Affected Components: {report['impact_summary']['total_affected_components']}")
    print(f"\n  Recommended Tests:")
    for test in report["recommended_tests"]:
        print(f"    - {test}")

    print("\n✅ ImpactAnalyzer test completed")


if __name__ == "__main__":
    main()

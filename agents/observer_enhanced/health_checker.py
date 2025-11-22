"""
システムヘルスチェッカー

このモジュールは、システム全体の健全性を評価し、スコアを算出します。

評価項目:
    1. コード品質 (30点)
    2. 依存関係の健全性 (25点)
    3. パフォーマンス (20点)
    4. エラー率 (15点)
    5. テストカバレッジ (10点)

スコア計算:
    - 100点満点
    - グレード: A(90-100), B(80-89), C(70-79), D(60-69), F(0-59)
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .graph_db import SystemGraphDB
    from .tracer import ExecutionTracer
except ImportError:
    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    from graph_db import SystemGraphDB
    from tracer import ExecutionTracer

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HealthChecker:
    """
    システムヘルスチェッカー

    Attributes:
        graph_db: システムグラフDB
        tracer: 実行トレーサー
    """

    def __init__(
        self, graph_db: Optional[SystemGraphDB] = None, tracer: Optional[ExecutionTracer] = None
    ):
        """
        初期化

        Args:
            graph_db: システムグラフDB (Noneの場合は新規作成)
            tracer: 実行トレーサー (Noneの場合は新規作成)
        """
        self.graph_db = graph_db if graph_db else SystemGraphDB()
        self.tracer = tracer if tracer else ExecutionTracer()

        logger.info("Initialized HealthChecker")

    def calculate_health_score(self) -> Dict[str, Any]:
        """
        ヘルススコアを計算

        Returns:
            Dict: ヘルスレポート
                - overall_score: 総合スコア (0-100)
                - grade: グレード (A-F)
                - component_scores: 各項目のスコア
                - recommendations: 改善推奨事項
        """
        logger.info("Calculating health score...")
        start_time = time.time()

        component_scores = {
            "code_quality": self._check_code_quality(),
            "dependency_health": self._check_dependency_health(),
            "performance": self._check_performance(),
            "error_rate": self._check_error_rate(),
            "test_coverage": self._check_test_coverage(),
        }

        # 総合スコアを計算 (加重平均)
        weights = {
            "code_quality": 0.30,
            "dependency_health": 0.25,
            "performance": 0.20,
            "error_rate": 0.15,
            "test_coverage": 0.10,
        }

        overall_score = sum(component_scores[key] * weights[key] for key in weights)

        # グレードを判定
        grade = self._calculate_grade(overall_score)

        # 改善推奨事項を生成
        recommendations = self._generate_recommendations(component_scores)

        elapsed = time.time() - start_time
        logger.info(
            f"Health score calculated in {elapsed:.2f}s: {overall_score:.1f}/100 (Grade: {grade})"
        )

        return {
            "overall_score": overall_score,
            "grade": grade,
            "component_scores": component_scores,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat(),
            "calculation_time_seconds": elapsed,
        }

    def _check_code_quality(self) -> float:
        """
        コード品質をチェック (30点満点)

        評価基準:
            - 循環依存の有無
            - ファイルサイズの適切性
            - 関数/クラス数のバランス

        Returns:
            float: スコア (0-30)
        """
        score = 30.0

        try:
            # 循環依存をチェック
            import networkx as nx

            cycles = list(nx.simple_cycles(self.graph_db.graph))
            if cycles:
                # 循環依存1つにつき-2点
                penalty = min(len(cycles) * 2, 10)
                score -= penalty
                logger.debug(f"Circular dependencies found: {len(cycles)} (-{penalty} points)")

            # ファイルサイズをチェック
            large_files = 0
            for node, attrs in self.graph_db.graph.nodes(data=True):
                lines = attrs.get("lines", 0)
                if lines > 1500:  # 1500行以上は大きすぎる
                    large_files += 1

            if large_files > 0:
                penalty = min(large_files * 1, 5)
                score -= penalty
                logger.debug(f"Large files found: {large_files} (-{penalty} points)")

        except Exception as e:
            logger.warning(f"Error checking code quality: {e}")
            score = 20.0  # エラー時は低めのスコア

        return max(score, 0)

    def _check_dependency_health(self) -> float:
        """
        依存関係の健全性をチェック (25点満点)

        評価基準:
            - 依存の深さ
            - ハブコンポーネントの有無
            - 孤立ノードの有無

        Returns:
            float: スコア (0-25)
        """
        score = 25.0

        try:
            # ハブコンポーネント(依存が集中)をチェック
            hub_threshold = 10  # 10個以上の依存は多すぎる
            high_degree_nodes = 0

            for node in self.graph_db.graph.nodes():
                degree = self.graph_db.graph.degree(node)
                if degree > hub_threshold:
                    high_degree_nodes += 1

            if high_degree_nodes > 0:
                penalty = min(high_degree_nodes * 2, 8)
                score -= penalty
                logger.debug(f"Hub components found: {high_degree_nodes} (-{penalty} points)")

            # 孤立ノード(依存がない)をチェック
            import networkx as nx

            isolated = list(nx.isolates(self.graph_db.graph))
            if isolated:
                penalty = min(len(isolated) * 0.5, 5)
                score -= penalty
                logger.debug(f"Isolated nodes found: {len(isolated)} (-{penalty} points)")

        except Exception as e:
            logger.warning(f"Error checking dependency health: {e}")
            score = 18.0

        return max(score, 0)

    def _check_performance(self) -> float:
        """
        パフォーマンスをチェック (20点満点)

        評価基準:
            - 平均実行時間
            - 遅い処理の有無

        Returns:
            float: スコア (0-20)
        """
        score = 20.0

        try:
            stats = self.tracer.get_statistics()
            avg_duration = stats.get("avg_duration_ms", 0)

            # 平均実行時間でペナルティ
            if avg_duration > 100:  # 100ms以上は遅い
                penalty = min((avg_duration - 100) / 50, 8)
                score -= penalty
                logger.debug(f"Slow average duration: {avg_duration:.2f}ms (-{penalty:.1f} points)")

            # 遅い処理をチェック
            slow_traces = self.tracer.get_slow_traces(threshold_ms=1000, limit=100)
            if slow_traces:
                penalty = min(len(slow_traces) * 0.1, 5)
                score -= penalty
                logger.debug(f"Slow traces found: {len(slow_traces)} (-{penalty:.1f} points)")

        except Exception as e:
            logger.warning(f"Error checking performance: {e}")
            score = 15.0

        return max(score, 0)

    def _check_error_rate(self) -> float:
        """
        エラー率をチェック (15点満点)

        評価基準:
            - エラー発生率
            - エラーの種類

        Returns:
            float: スコア (0-15)
        """
        score = 15.0

        try:
            stats = self.tracer.get_statistics()
            error_rate = stats.get("error_rate", 0)

            # エラー率でペナルティ
            if error_rate > 1.0:  # 1%以上は問題
                penalty = min(error_rate * 2, 10)
                score -= penalty
                logger.debug(f"High error rate: {error_rate:.2f}% (-{penalty:.1f} points)")

        except Exception as e:
            logger.warning(f"Error checking error rate: {e}")
            score = 10.0

        return max(score, 0)

    def _check_test_coverage(self) -> float:
        """
        テストカバレッジをチェック (10点満点)

        注意: 現時点では簡易実装

        Returns:
            float: スコア (0-10)
        """
        # TODO: 実際のテストカバレッジを取得する実装
        # 現時点では固定値
        return 8.0

    def _calculate_grade(self, score: float) -> str:
        """
        スコアからグレードを算出

        Args:
            score: スコア (0-100)

        Returns:
            str: グレード (A-F)
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _generate_recommendations(self, component_scores: Dict[str, float]) -> List[str]:
        """
        改善推奨事項を生成

        Args:
            component_scores: 各項目のスコア

        Returns:
            List[str]: 推奨事項のリスト
        """
        recommendations = []

        if component_scores["code_quality"] < 20:
            recommendations.append(
                "Code quality is low. Consider refactoring large files and resolving circular dependencies."
            )

        if component_scores["dependency_health"] < 18:
            recommendations.append(
                "Dependency health needs improvement. Review hub components and isolated nodes."
            )

        if component_scores["performance"] < 15:
            recommendations.append(
                "Performance issues detected. Investigate slow traces and optimize bottlenecks."
            )

        if component_scores["error_rate"] < 12:
            recommendations.append(
                "High error rate detected. Review error logs and implement error handling improvements."
            )

        if component_scores["test_coverage"] < 7:
            recommendations.append(
                "Test coverage is insufficient. Add more unit and integration tests."
            )

        return recommendations


def main():
    """メイン関数 (テスト用)"""
    print("🏥 HealthChecker Test")

    checker = HealthChecker()
    report = checker.calculate_health_score()

    print("\n📊 Health Report:")
    print(f"  Overall Score: {report['overall_score']:.1f}/100")
    print(f"  Grade: {report['grade']}")
    print("\n  Component Scores:")
    for component, score in report["component_scores"].items():
        print(f"    {component}: {score:.1f}")

    if report["recommendations"]:
        print("\n  💡 Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"    {i}. {rec}")

    print("\n✅ HealthChecker test completed")


if __name__ == "__main__":
    main()

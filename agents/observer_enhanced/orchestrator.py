"""
強化版オブザーバー統括制御

このモジュールは、強化版オブザーバーシステム全体を統括し、
定期的な診断サイクルを実行します。

主要機能:
    - 10分ごとの診断サイクル実行
    - 静的解析・動的トレース・ヘルスチェックの統合
    - グラフDBの更新
    - アラート判定と通知

パフォーマンス目標:
    - 診断サイクル実行: <10分
    - メモリ使用量: <500MB
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# 内部モジュール
try:
    from .alert_manager import AlertManager
    from .graph_builder import DependencyGraphBuilder
    from .graph_db import SystemGraphDB
    from .health_checker import HealthChecker
    from .impact_analyzer import ImpactAnalyzer
    from .static_analyzer import StaticDependencyAnalyzer
    from .tracer import ExecutionTracer
except ImportError:
    # スタンドアロン実行時
    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    from alert_manager import AlertManager
    from graph_builder import DependencyGraphBuilder
    from graph_db import SystemGraphDB
    from health_checker import HealthChecker
    from impact_analyzer import ImpactAnalyzer
    from static_analyzer import StaticDependencyAnalyzer
    from tracer import ExecutionTracer

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedObserverOrchestrator:
    """
    強化版オブザーバー統括制御

    Attributes:
        static_analyzer: 静的依存関係解析器
        tracer: 実行トレーサー
        graph_db: システムグラフDB
        graph_builder: グラフ構築エンジン
        health_checker: ヘルスチェッカー
        alert_manager: アラートマネージャー
        impact_analyzer: 影響範囲分析器
        cycle_interval: 診断サイクル間隔(秒)
        running: 実行中フラグ
    """

    def __init__(
        self, cycle_interval: int = 600, project_root: Optional[Path] = None  # 10分 = 600秒
    ):
        """
        初期化

        Args:
            cycle_interval: 診断サイクル間隔(秒) デフォルト10分
            project_root: プロジェクトルート (Noneの場合は自動検出)
        """
        self.cycle_interval = cycle_interval
        self.running = False

        # 各コンポーネントを初期化
        logger.info("Initializing EnhancedObserverOrchestrator...")

        self.static_analyzer = StaticDependencyAnalyzer(project_root)
        self.tracer = ExecutionTracer()
        self.graph_db = SystemGraphDB()
        self.graph_builder = DependencyGraphBuilder()
        self.health_checker = HealthChecker(self.graph_db)
        self.alert_manager = AlertManager()
        self.impact_analyzer = ImpactAnalyzer(self.graph_db)

        # 統計情報
        self.stats = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "last_cycle_time": None,
            "last_health_score": 0,
        }

        logger.info(f"EnhancedObserverOrchestrator initialized (cycle_interval={cycle_interval}s)")

    async def run_diagnostic_cycle(self) -> Dict[str, Any]:
        """
        診断サイクルを1回実行

        実行内容:
            1. 静的解析 (目標: 3分)
            2. 動的トレース集計 (目標: 2分)
            3. グラフ構築・更新 (目標: 2分)
            4. ヘルスチェック (目標: 3分)
            5. アラート判定

        Returns:
            Dict: 診断結果
        """
        logger.info("=" * 60)
        logger.info("Starting diagnostic cycle")
        logger.info("=" * 60)

        cycle_start_time = time.time()
        results = {
            "cycle_id": f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "phases": {},
        }

        try:
            # Phase 1: 静的解析
            logger.info("Phase 1/5: Static Analysis")
            phase_start = time.time()

            static_graph = self.static_analyzer.scan_project()

            phase_elapsed = time.time() - phase_start
            results["phases"]["static_analysis"] = {
                "status": "success",
                "elapsed_seconds": phase_elapsed,
                "node_count": static_graph.number_of_nodes(),
                "edge_count": static_graph.number_of_edges(),
            }
            logger.info(f"Phase 1 completed in {phase_elapsed:.2f}s")

            # Phase 2: 動的トレース集計
            logger.info("Phase 2/5: Dynamic Trace Aggregation")
            phase_start = time.time()

            recent_traces = self.tracer.get_recent_traces(minutes=10)
            trace_stats = self.tracer.get_statistics()

            phase_elapsed = time.time() - phase_start
            results["phases"]["trace_aggregation"] = {
                "status": "success",
                "elapsed_seconds": phase_elapsed,
                "trace_count": len(recent_traces),
                "error_rate": trace_stats.get("error_rate", 0),
            }
            logger.info(f"Phase 2 completed in {phase_elapsed:.2f}s")

            # Phase 3: グラフ構築・更新
            logger.info("Phase 3/5: Graph Building and Update")
            phase_start = time.time()

            # 静的解析結果からグラフを構築
            self.graph_builder.build_from_static_analysis(static_graph)

            # 動的トレースを統合
            self.graph_builder.integrate_runtime_traces(recent_traces)

            # エッジの重みを計算
            self.graph_builder.calculate_and_apply_weights()

            # グラフDBを更新
            updated_graph = self.graph_builder.get_graph()
            for node, attrs in updated_graph.nodes(data=True):
                if node not in self.graph_db.graph:
                    self.graph_db.add_component(node, attrs)
                else:
                    self.graph_db.update_component(node, attrs)

            # エッジも更新
            for source, target, attrs in updated_graph.edges(data=True):
                if not self.graph_db.graph.has_edge(source, target):
                    self.graph_db.add_dependency(
                        source, target, attrs.get("type", "unknown"), attrs.get("weight", 1.0)
                    )
                else:
                    self.graph_db.update_dependency(source, target, attrs)

            # グラフを保存
            self.graph_db.save()

            phase_elapsed = time.time() - phase_start
            results["phases"]["graph_update"] = {
                "status": "success",
                "elapsed_seconds": phase_elapsed,
                "final_node_count": self.graph_db.graph.number_of_nodes(),
                "final_edge_count": self.graph_db.graph.number_of_edges(),
            }
            logger.info(f"Phase 3 completed in {phase_elapsed:.2f}s")

            # Phase 4: ヘルスチェック
            logger.info("Phase 4/5: Health Check")
            phase_start = time.time()

            health_report = self.health_checker.calculate_health_score()

            phase_elapsed = time.time() - phase_start
            results["phases"]["health_check"] = {
                "status": "success",
                "elapsed_seconds": phase_elapsed,
                "health_score": health_report["overall_score"],
                "grade": health_report["grade"],
            }
            logger.info(f"Phase 4 completed in {phase_elapsed:.2f}s")
            logger.info(
                f"Health Score: {health_report['overall_score']:.1f}/100 (Grade: {health_report['grade']})"
            )

            # Phase 5: アラート判定
            logger.info("Phase 5/5: Alert Judgment")
            phase_start = time.time()

            alerts = []

            # ヘルススコアが低い場合
            if health_report["overall_score"] < 70:
                alert = self.alert_manager.create_alert(
                    level="warning",
                    title="Low Health Score",
                    message=f"System health score is {health_report['overall_score']:.1f}/100",
                    details=health_report,
                )
                alerts.append(alert)

            # エラー率が高い場合
            if trace_stats.get("error_rate", 0) > 5.0:
                alert = self.alert_manager.create_alert(
                    level="error",
                    title="High Error Rate",
                    message=f"Error rate is {trace_stats['error_rate']:.1f}%",
                    details=trace_stats,
                )
                alerts.append(alert)

            phase_elapsed = time.time() - phase_start
            results["phases"]["alert_judgment"] = {
                "status": "success",
                "elapsed_seconds": phase_elapsed,
                "alert_count": len(alerts),
            }
            logger.info(f"Phase 5 completed in {phase_elapsed:.2f}s")

            # サイクル完了
            cycle_elapsed = time.time() - cycle_start_time
            results["status"] = "success"
            results["total_elapsed_seconds"] = cycle_elapsed
            results["health_score"] = health_report["overall_score"]
            results["alerts"] = alerts

            # 統計を更新
            self.stats["total_cycles"] += 1
            self.stats["successful_cycles"] += 1
            self.stats["last_cycle_time"] = datetime.now().isoformat()
            self.stats["last_health_score"] = health_report["overall_score"]

            logger.info("=" * 60)
            logger.info(f"Diagnostic cycle completed successfully in {cycle_elapsed:.2f}s")
            logger.info("=" * 60)

            return results

        except Exception as e:
            logger.error(f"Error in diagnostic cycle: {e}", exc_info=True)

            cycle_elapsed = time.time() - cycle_start_time
            results["status"] = "error"
            results["error_message"] = str(e)
            results["total_elapsed_seconds"] = cycle_elapsed

            # 統計を更新
            self.stats["total_cycles"] += 1
            self.stats["failed_cycles"] += 1

            return results

    async def start_continuous_monitoring(self) -> None:
        """
        連続監視モードを開始

        cycle_interval秒ごとに診断サイクルを実行し続けます。
        """
        logger.info(f"Starting continuous monitoring (interval={self.cycle_interval}s)")
        self.running = True

        while self.running:
            try:
                # 診断サイクルを実行
                results = await self.run_diagnostic_cycle()

                # 結果をファイルに保存
                self._save_cycle_results(results)

                # 次のサイクルまで待機
                logger.info(f"Waiting {self.cycle_interval}s until next cycle...")
                await asyncio.sleep(self.cycle_interval)

            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping...")
                self.running = False
                break

            except Exception as e:
                logger.error(f"Unexpected error in monitoring loop: {e}", exc_info=True)
                # エラーが発生しても継続
                await asyncio.sleep(60)  # 1分待機してリトライ

        logger.info("Continuous monitoring stopped")

    def stop(self) -> None:
        """連続監視を停止"""
        logger.info("Stopping continuous monitoring...")
        self.running = False

    def _save_cycle_results(self, results: Dict[str, Any]) -> None:
        """
        診断サイクル結果を保存

        Args:
            results: 診断結果
        """
        output_dir = Path("logs/diagnostic_cycles")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{results['cycle_id']}.json"

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.debug(f"Cycle results saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save cycle results: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        統計情報を取得

        Returns:
            Dict: 統計情報
        """
        return self.stats.copy()


async def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Observer Orchestrator")
    parser.add_argument("--test-mode", action="store_true", help="Run single cycle for testing")
    parser.add_argument(
        "--interval", type=int, default=600, help="Cycle interval in seconds (default: 600)"
    )

    args = parser.parse_args()
    # --scan-only オプションの処理
    if args.scan_only:
        logger.info("🔍 プロジェクトスキャンのみ実行します")
        try:
            # 静的解析実行
            from .static_analyzer import StaticDependencyAnalyzer

            analyzer = StaticDependencyAnalyzer()
            dep_graph = analyzer.scan_project()

            # グラフをJSONで保存
            import json

            output_path = Path(__file__).parent / "dependency_graph.json"
            with open(output_path, "w", encoding="utf-8") as f:
                graph_data = {
                    "nodes": [{"id": node, **data} for node, data in dep_graph.nodes(data=True)],
                    "edges": [
                        {"source": u, "target": v, **data}
                        for u, v, data in dep_graph.edges(data=True)
                    ],
                }
                json.dump(graph_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ グラフを保存しました: {output_path}")
            logger.info(f"   ノード数: {len(dep_graph.nodes)}")
            logger.info(f"   エッジ数: {len(dep_graph.edges)}")
            return
        except Exception as e:
            logger.error(f"❌ スキャン実行エラー: {e}")
            import traceback

            traceback.print_exc()
            return

    orchestrator = EnhancedObserverOrchestrator(cycle_interval=args.interval)

    if args.test_mode:
        # テストモード: 1サイクルのみ実行
        logger.info("Running in test mode (single cycle)")
        results = await orchestrator.run_diagnostic_cycle()

        print("\n" + "=" * 60)
        print("TEST MODE RESULTS")
        print("=" * 60)
        print(f"Status: {results['status']}")
        print(f"Total time: {results.get('total_elapsed_seconds', 0):.2f}s")
        print(f"Health score: {results.get('health_score', 0):.1f}/100")
        print("=" * 60)
    else:
        # 連続監視モード
        try:
            await orchestrator.start_continuous_monitoring()
        except KeyboardInterrupt:
            orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())

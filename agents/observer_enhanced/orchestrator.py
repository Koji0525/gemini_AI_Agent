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

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# 内部モジュール
try:
    from .alert_manager import AlertManager
    from .graph_db import SystemGraphDB
    from .health_checker import HealthChecker
    from .static_analyzer import StaticDependencyAnalyzer
    from .tracer import ExecutionTracer
except ImportError:
    from alert_manager import AlertManager
    from graph_db import SystemGraphDB
    from health_checker import HealthChecker
    from static_analyzer import StaticDependencyAnalyzer
    from tracer import ExecutionTracer

# ロギング設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedObserverOrchestrator:
    """
    強化版オブザーバー統括制御クラス

    全てのオブザーバーコンポーネントを統括し、
    定期的な診断サイクルを実行します。
    """

    def __init__(self, cycle_interval: int = 600):
        """
        初期化

        Args:
            cycle_interval: 診断サイクル間隔（秒）デフォルト10分
        """
        self.cycle_interval = cycle_interval
        self.static_analyzer = StaticDependencyAnalyzer()
        self.tracer = ExecutionTracer()
        self.graph_db = SystemGraphDB()
        self.health_checker = HealthChecker()
        self.alert_manager = AlertManager()

        logger.info(f"EnhancedObserverOrchestrator 初期化完了（サイクル: {cycle_interval}秒）")

    async def run_diagnostic_cycle(self) -> Dict[str, Any]:
        """
        診断サイクル実行

        実行内容:
            1. 静的解析（3分）
            2. 動的トレース集計（2分）
            3. ヘルスチェック（3分）
            4. グラフ更新（2分）

        Returns:
            Dict: 診断結果
        """
        cycle_start = datetime.now()
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🔬 診断サイクル開始")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        results = {}

        try:
            # 1. 静的解析
            logger.info("📊 [1/4] 静的解析実行中...")
            dep_graph = self.static_analyzer.scan_project()
            results["static_analysis"] = {
                "nodes": len(dep_graph.nodes),
                "edges": len(dep_graph.edges),
                "status": "success",
            }
            logger.info(f"   ✅ ノード数: {len(dep_graph.nodes)}, エッジ数: {len(dep_graph.edges)}")

            # 2. 動的トレース集計
            logger.info("📈 [2/4] トレース集計中...")
            traces = await self.tracer.get_recent_traces(minutes=10)
            results["traces"] = {"count": len(traces), "status": "success"}
            logger.info(f"   ✅ トレース数: {len(traces)}件")

            # 3. ヘルスチェック
            logger.info("🏥 [3/4] ヘルスチェック実行中...")
            health_score = await self.health_checker.calculate_score()
            results["health"] = {
                "score": health_score,
                "grade": self._get_grade(health_score),
                "status": "success",
            }
            logger.info(
                f"   ✅ ヘルススコア: {health_score:.1f}点 ({self._get_grade(health_score)})"
            )

            # 4. グラフDB更新
            logger.info("💾 [4/4] グラフDB更新中...")
            await self.graph_db.update(dep_graph, traces)
            results["graph_update"] = {"status": "success"}
            logger.info("   ✅ グラフDB更新完了")

            # 5. アラート判定
            if health_score < 70:
                logger.warning(f"⚠️  ヘルススコアが低下: {health_score:.1f}点")
                await self.alert_manager.send_alert(health_score=health_score, details=results)

            # サイクル完了
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            results["cycle_duration"] = cycle_duration

            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"✅ 診断サイクル完了（所要時間: {cycle_duration:.1f}秒）")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            return results

        except Exception as e:
            logger.error(f"❌ 診断サイクルエラー: {e}")
            import traceback

            traceback.print_exc()

            results["error"] = str(e)
            results["status"] = "failed"
            return results

    def _get_grade(self, score: float) -> str:
        """ヘルススコアをグレードに変換"""
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

    async def run_continuous(self):
        """
        連続実行（24時間稼働モード）
        """
        logger.info("🚀 24時間稼働モード開始")

        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                logger.info(f"\n📍 サイクル #{cycle_count}")

                await self.run_diagnostic_cycle()

                logger.info(f"⏱️  次のサイクルまで {self.cycle_interval}秒待機...\n")
                await asyncio.sleep(self.cycle_interval)

            except KeyboardInterrupt:
                logger.info("\n⏹️  ユーザーによる停止")
                break
            except Exception as e:
                logger.error(f"❌ 予期しないエラー: {e}")
                logger.info("⏱️  60秒後にリトライ...")
                await asyncio.sleep(60)


def main():
    """メイン実行"""
    parser = argparse.ArgumentParser(description="Enhanced Observer Orchestrator")
    parser.add_argument("--test-mode", action="store_true", help="Run single cycle for testing")
    parser.add_argument(
        "--interval", type=int, default=600, help="Cycle interval in seconds (default: 600)"
    )
    parser.add_argument("--scan-only", action="store_true", help="プロジェクトスキャンのみ実行")
    args = parser.parse_args()

    # --scan-only オプションの処理
    if args.scan_only:
        logger.info("🔍 プロジェクトスキャンのみ実行します")
        try:
            # 静的解析実行
            analyzer = StaticDependencyAnalyzer()
            dep_graph = analyzer.scan_project()

            # グラフをJSONで保存
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

    # 通常の実行モード
    orchestrator = EnhancedObserverOrchestrator(cycle_interval=args.interval)

    if args.test_mode:
        # テストモード: 1サイクルのみ実行
        logger.info("🧪 テストモード: 1サイクルのみ実行")
        asyncio.run(orchestrator.run_diagnostic_cycle())
    else:
        # 連続実行モード
        asyncio.run(orchestrator.run_continuous())


if __name__ == "__main__":
    main()

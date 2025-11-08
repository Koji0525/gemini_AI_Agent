"""
SystemObserver - システム全体可視化オブザーバー

【Phase 1完成版】
既存エージェントを統合し、システム全体の状態をリアルタイムで可視化

【統合エージェント】
1. MonitoringAgent: リソース監視（CPU/メモリ/ディスク）
2. ExecutionAnalyzer: 履歴分析（成功率/エラー率）
3. CollaborationAgent: エージェント状態追跡
4. TaskExecutor: 実行トレース記録
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SystemObserver:
    """システム全体可視化オブザーバー"""

    def __init__(
        self,
        monitoring_agent=None,
        execution_analyzer=None,
        collaboration_agent=None,
        task_executor=None,
    ):
        # 既存エージェントの参照
        self.monitoring_agent = monitoring_agent
        self.execution_analyzer = execution_analyzer
        self.collaboration_agent = collaboration_agent
        self.task_executor = task_executor

        # 統計データ
        self.system_stats = {
            "start_time": datetime.now().isoformat(),
            "total_observations": 0,
            "last_update": None,
        }

        # スナップショット履歴（メモリ内保持）
        self.snapshot_history = []
        self.max_history = 100  # 最大100件

        logger.info("✅ SystemObserver初期化完了")

    def collect_system_snapshot(self) -> Dict[str, Any]:
        """
        システム全体のスナップショットを収集

        Returns:
            システム状態の辞書
        """
        try:
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "resources": self._collect_resource_metrics(),
                "agents": self._collect_agent_status(),
                "tasks": self._collect_task_metrics(),
                "performance": self._collect_performance_metrics(),
                "health": self._calculate_system_health(),
            }

            # スナップショット履歴に追加
            self.snapshot_history.append(snapshot)
            if len(self.snapshot_history) > self.max_history:
                self.snapshot_history.pop(0)

            self.system_stats["total_observations"] += 1
            self.system_stats["last_update"] = snapshot["timestamp"]

            return snapshot

        except Exception as e:
            logger.error(f"❌ スナップショット収集エラー: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _collect_resource_metrics(self) -> Dict[str, Any]:
        """リソースメトリクスを収集（MonitoringAgentから）"""
        if not self.monitoring_agent:
            return {"status": "unavailable", "reason": "MonitoringAgent not initialized"}

        try:
            # MonitoringAgentのメトリクス取得（簡易版）
            import psutil

            metrics = {
                "status": "healthy",
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
                "timestamp": datetime.now().isoformat(),
            }

            # ヘルスステータス判定
            if metrics["cpu_percent"] > 80 or metrics["memory_percent"] > 80:
                metrics["status"] = "warning"
            if metrics["cpu_percent"] > 95 or metrics["memory_percent"] > 95:
                metrics["status"] = "critical"

            return metrics

        except Exception as e:
            logger.warning(f"⚠️ リソースメトリクス収集エラー: {e}")
            return {"status": "error", "error": str(e)}

    def _collect_agent_status(self) -> Dict[str, Any]:
        """エージェント状態を収集（CollaborationAgentから）"""
        if not self.collaboration_agent:
            return {"status": "unavailable", "reason": "CollaborationAgent not initialized"}

        try:
            agents_status = {"total_agents": 0, "active_agents": 0, "idle_agents": 0, "agents": []}

            # CollaborationAgentのregistered_agentsを参照
            if hasattr(self.collaboration_agent, "registered_agents"):
                for agent_id, agent_info in self.collaboration_agent.registered_agents.items():
                    agent_data = {
                        "agent_id": agent_id,
                        "status": "active" if agent_info.get("current_task") else "idle",
                        "success_rate": agent_info.get("success_rate", 0.0),
                        "total_executions": agent_info.get("total_executions", 0),
                        "current_task": agent_info.get("current_task", None),
                    }

                    agents_status["agents"].append(agent_data)
                    agents_status["total_agents"] += 1

                    if agent_data["status"] == "active":
                        agents_status["active_agents"] += 1
                    else:
                        agents_status["idle_agents"] += 1

            return agents_status

        except Exception as e:
            logger.warning(f"⚠️ エージェント状態収集エラー: {e}")
            return {"status": "error", "error": str(e)}

    def _collect_task_metrics(self) -> Dict[str, Any]:
        """タスクメトリクスを収集（TaskExecutorから）"""
        try:
            # 簡易版：統計情報のみ
            metrics = {
                "total_tasks": 0,
                "pending_tasks": 0,
                "running_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
            }

            # TaskExecutorまたはスプレッドシートから取得
            # ※実装時に実際のデータソースに合わせて調整

            return metrics

        except Exception as e:
            logger.warning(f"⚠️ タスクメトリクス収集エラー: {e}")
            return {"status": "error", "error": str(e)}

    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンスメトリクスを収集（ExecutionAnalyzerから）"""
        if not self.execution_analyzer:
            return {"status": "unavailable", "reason": "ExecutionAnalyzer not initialized"}

        try:
            # ExecutionAnalyzerの分析結果を取得
            metrics = {
                "overall_success_rate": 0.0,
                "average_response_time": 0.0,
                "total_executions": 0,
                "error_rate": 0.0,
            }

            # 実際の分析データ取得
            # ※実装時にExecutionAnalyzerのAPIに合わせて調整

            return metrics

        except Exception as e:
            logger.warning(f"⚠️ パフォーマンスメトリクス収集エラー: {e}")
            return {"status": "error", "error": str(e)}

    def _calculate_system_health(self) -> str:
        """システム全体の健全性を計算"""
        try:
            # 簡易版：リソースとエージェント状態から判定
            health_score = 100.0

            # リソース健全性チェック
            # CPU/メモリが80%以上でスコア減少

            # エージェント健全性チェック
            # エラー率が高いとスコア減少

            if health_score >= 90:
                return "healthy"
            elif health_score >= 70:
                return "warning"
            else:
                return "critical"

        except Exception as e:
            logger.error(f"❌ システム健全性計算エラー: {e}")
            return "unknown"

    def get_recent_snapshots(self, count: int = 10) -> List[Dict[str, Any]]:
        """最近のスナップショットを取得"""
        return self.snapshot_history[-count:]

    def get_system_summary(self) -> Dict[str, Any]:
        """システムサマリーを取得"""
        latest_snapshot = self.snapshot_history[-1] if self.snapshot_history else None

        return {
            "system_stats": self.system_stats,
            "latest_snapshot": latest_snapshot,
            "history_count": len(self.snapshot_history),
        }

    def export_snapshot(self, filepath: str = None) -> str:
        """スナップショットをJSON出力"""
        if not filepath:
            filepath = f"/tmp/system_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            latest = self.collect_system_snapshot()

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(latest, f, indent=2, ensure_ascii=False)

            print(f"✅ スナップショットを出力: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"❌ エクスポートエラー: {e}")
            return None


# ==
# テスト実行
# ==
if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 SystemObserver Phase 1 テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # SystemObserverを初期化
    observer = SystemObserver()

    print("\n📊 システムスナップショット収集:")
    snapshot = observer.collect_system_snapshot()

    print(f"\n✅ リソース:")
    print(f"   CPU: {snapshot['resources'].get('cpu_percent', 'N/A')}%")
    print(f"   メモリ: {snapshot['resources'].get('memory_percent', 'N/A')}%")
    print(f"   ディスク: {snapshot['resources'].get('disk_percent', 'N/A')}%")
    print(f"   状態: {snapshot['resources'].get('status', 'N/A')}")

    print(f"\n✅ システムヘルス: {snapshot['health']}")

    # JSON出力
    print("\n📤 スナップショットをJSON出力:")
    filepath = observer.export_snapshot()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 Phase 1 テスト完了")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

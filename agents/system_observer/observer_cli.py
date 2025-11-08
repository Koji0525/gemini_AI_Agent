"""
ObserverCLI - SystemObserver用CLI可視化ツール

【修正】
- v1.24.0が動いていなくても、デフォルトエージェント一覧を表示
- より分かりやすいメッセージ
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse
import time

from agents.system_observer.system_observer import SystemObserver


class ObserverCLI:
    """SystemObserver用CLIツール"""

    # デフォルトエージェント一覧（v1.24.0の全エージェント）
    DEFAULT_AGENTS = [
        {"agent_id": "PMAgent", "capabilities": ["planning", "task_decomposition"]},
        {"agent_id": "TaskExecutor", "capabilities": ["execution", "task_processing"]},
        {"agent_id": "ReviewAgent", "capabilities": ["review", "quality_check"]},
        {"agent_id": "GoalEvaluator", "capabilities": ["goal_evaluation"]},
        {"agent_id": "CollaborationAgent", "capabilities": ["coordination", "load_balancing"]},
        {"agent_id": "ErrorClassifier", "capabilities": ["error_classification"]},
        {"agent_id": "DecisionSupportSystem", "capabilities": ["decision_making"]},
        {"agent_id": "RollbackAgent", "capabilities": ["rollback", "recovery"]},
        {"agent_id": "QualityFeedbackLoop", "capabilities": ["quality_feedback"]},
        {"agent_id": "LearningOptimizer", "capabilities": ["optimization", "learning"]},
        {"agent_id": "KnowledgeBaseManager", "capabilities": ["knowledge_management"]},
        {"agent_id": "SelfLearningPipeline", "capabilities": ["self_learning"]},
        {"agent_id": "MonitoringAgent", "capabilities": ["monitoring", "resource_tracking"]},
        {"agent_id": "ExecutionAnalyzer", "capabilities": ["analysis", "performance_tracking"]},
        {"agent_id": "SystemObserver", "capabilities": ["observation", "visualization"]},
    ]

    def __init__(self):
        self.observer = SystemObserver()

    def _format_metric(self, value, suffix="%", default="N/A"):
        """メトリクス値を安全にフォーマット"""
        if isinstance(value, (int, float)):
            return f"{value:5.1f}{suffix}"
        return default

    def show_status(self):
        """現在のシステム状態を表示"""
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 システム状態")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        snapshot = self.observer.collect_system_snapshot()

        # リソース
        resources = snapshot.get("resources", {})
        print(f"\n🖥️  リソース:")
        print(f"   CPU:    {self._format_metric(resources.get('cpu_percent'))}")
        print(f"   メモリ: {self._format_metric(resources.get('memory_percent'))}")
        print(f"   ディスク: {self._format_metric(resources.get('disk_percent'))}")
        print(f"   状態:   {resources.get('status', 'N/A')}")

        # エージェント
        agents = snapshot.get("agents", {})
        total_agents = agents.get("total_agents", 0)

        print(f"\n👥 エージェント:")

        # v1.24.0が動いていない場合
        if total_agents == 0:
            print(f"   状態:   ⚠️  v1.24.0が稼働していません")
            print(f"   総数:   {len(self.DEFAULT_AGENTS)}個（登録可能）")
            print(f"\n   📋 登録可能なエージェント一覧:")
            for i, agent in enumerate(self.DEFAULT_AGENTS[:5], 1):
                caps = ", ".join(agent["capabilities"][:2])
                print(f"      {i}. {agent['agent_id']} ({caps})")
            print(f"      ... 他{len(self.DEFAULT_AGENTS) - 5}個")
            print(f"\n   💡 v1.24.0を起動すると全エージェントが監視されます")
        else:
            # v1.24.0が動いている場合
            print(f"   総数:   {total_agents}件")
            print(f"   稼働中: {agents.get('active_agents', 0)}件")
            print(f"   待機中: {agents.get('idle_agents', 0)}件")

            if agents.get("healthy_agents"):
                print(f"   健全:   {agents.get('healthy_agents', 0)}件")

            # エージェント一覧表示
            agent_list = agents.get("agents", [])
            if agent_list:
                print(f"\n   📋 エージェント詳細（上位5件）:")
                for agent in agent_list[:5]:
                    caps = ", ".join(agent.get("capabilities", [])[:2])
                    health = agent.get("health", "unknown")
                    print(f"      - {agent['agent_id']}: {health} ({caps})")

        # タスク
        tasks = snapshot.get("tasks", {})
        print(f"\n📋 タスク:")
        print(f"   総数:     {tasks.get('total_tasks', 0)}件")
        print(f"   実行中:   {tasks.get('running_tasks', 0)}件")
        print(f"   完了:     {tasks.get('completed_tasks', 0)}件")
        print(f"   失敗:     {tasks.get('failed_tasks', 0)}件")

        # パフォーマンス
        performance = snapshot.get("performance", {})
        success_rate = performance.get("overall_success_rate", 0.0)
        response_time = performance.get("average_response_time", 0.0)
        error_rate = performance.get("error_rate", 0.0)

        print(f"\n📈 パフォーマンス:")
        print(
            f"   成功率:     {success_rate * 100:5.1f}%"
            if isinstance(success_rate, (int, float))
            else "   成功率:     N/A"
        )
        print(
            f"   平均応答:   {response_time:5.2f}秒"
            if isinstance(response_time, (int, float))
            else "   平均応答:   N/A"
        )
        print(
            f"   エラー率:   {error_rate * 100:5.1f}%"
            if isinstance(error_rate, (int, float))
            else "   エラー率:   N/A"
        )

        # システムヘルス
        health = snapshot.get("health", "unknown")
        health_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "🚨", "unknown": "❓"}
        print(f"\n🏥 システムヘルス: {health_emoji.get(health, '❓')} {health.upper()}")

        print(f"\n⏰ 最終更新: {snapshot.get('timestamp', 'N/A')}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    def monitor_realtime(self, interval: int = 10):
        """リアルタイム監視モード"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🔴 リアルタイム監視開始（{interval}秒間隔）")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Press Ctrl+C to stop")

        try:
            while True:
                self.show_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n⏸️  監視を停止しました")

    def export_report(self, filepath: str = None):
        """レポートをエクスポート"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📤 レポートエクスポート")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        output_path = self.observer.export_snapshot(filepath)

        if output_path:
            print(f"✅ エクスポート完了: {output_path}")
        else:
            print("❌ エクスポート失敗")


def main():
    parser = argparse.ArgumentParser(description="SystemObserver CLI Tool")
    parser.add_argument("command", choices=["status", "monitor", "export"], help="実行コマンド")
    parser.add_argument("--interval", type=int, default=10, help="監視間隔（秒）")
    parser.add_argument("--output", type=str, help="エクスポート先ファイルパス")

    args = parser.parse_args()

    cli = ObserverCLI()

    if args.command == "status":
        cli.show_status()
    elif args.command == "monitor":
        cli.monitor_realtime(interval=args.interval)
    elif args.command == "export":
        cli.export_report(filepath=args.output)


if __name__ == "__main__":
    main()

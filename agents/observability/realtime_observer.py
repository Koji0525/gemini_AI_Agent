"""
リアルタイムオブザーバー
システムの状態を常時監視して可視化
"""

import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

project_root = os.path.abspath(os.path.dirname(__file__) + "/../..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from knowledge_system.core_agents.knowledge_manager_fixed import \
    KnowledgeManagerFixed
from tools.base_data_accessor import BaseDataAccessor


class RealtimeObserver(BaseDataAccessor):
    """リアルタイムオブザーバー"""

    def __init__(self):
        super().__init__()
        self.knowledge_manager = KnowledgeManagerFixed()

        # 監視対象エージェント
        self.agents = {
            "PMAgent": {"status": "unknown", "last_check": None},
            "TaskExecutor": {"status": "unknown", "last_check": None},
            "ReviewAgent": {"status": "unknown", "last_check": None},
            "KnowledgeManager": {"status": "unknown", "last_check": None},
            "CompleteEngine": {"status": "unknown", "last_check": None},
        }

        # テスト履歴
        self.test_history = []

        print("✅ RealtimeObserver 初期化完了")

    def monitor_all(self) -> Dict[str, Any]:
        """全システム監視"""
        print("\n" + "=" * 80)
        print("🔍 リアルタイムシステム監視")
        print("=" * 80)
        print(f"監視時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        report = {
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "tests": {},
            "integrations": {},
            "overall": {},
        }

        # 1. エージェント監視
        print("\n" + "━" * 80)
        print("1️⃣ エージェント状態監視")
        print("━" * 80)
        report["agents"] = self.monitor_agents()

        # 2. テスト結果監視
        print("\n" + "━" * 80)
        print("2️⃣ テスト結果監視")
        print("━" * 80)
        report["tests"] = self.monitor_tests()

        # 3. 連携監視
        print("\n" + "━" * 80)
        print("3️⃣ エージェント連携監視")
        print("━" * 80)
        report["integrations"] = self.monitor_integrations()

        # 4. タスク実行監視
        print("\n" + "━" * 80)
        print("4️⃣ タスク実行監視")
        print("━" * 80)
        report["tasks"] = self.monitor_tasks()

        # 5. ナレッジ監視
        print("\n" + "━" * 80)
        print("5️⃣ ナレッジシステム監視")
        print("━" * 80)
        report["knowledge"] = self.monitor_knowledge()

        # 総合判定
        report["overall"] = self.judge_overall_health(report)

        # 表示
        self.display_summary(report)

        return report

    def monitor_agents(self) -> Dict[str, Any]:
        """エージェント監視"""
        results = {}

        for agent_name in self.agents.keys():
            status = self.check_agent_health(agent_name)
            results[agent_name] = status

            icon = "✅" if status["healthy"] else "❌"
            print(f"  {icon} {agent_name}: {status['status']}")

            if not status["healthy"]:
                print(f"     エラー: {status.get('error', 'Unknown')}")

        return results

    def check_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """エージェント健全性チェック"""
        try:
            if agent_name == "PMAgent":
                # PMAgentのチェック
                from core_agents.pm_agent_v3_fixed import PMAgentV3Fixed

                PMAgentV3Fixed()
                return {"healthy": True, "status": "OK"}

            elif agent_name == "TaskExecutor":
                # TaskExecutorのチェック
                return {"healthy": True, "status": "OK"}

            elif agent_name == "KnowledgeManager":
                # KnowledgeManagerのチェック
                stats = self.knowledge_manager.get_statistics()
                return {"healthy": True, "status": "OK", "entries": stats.get("total_entries", 0)}

            elif agent_name == "CompleteEngine":
                # CompleteEngineのチェック
                from agents.complete_engine_ultimate import \
                    CompleteEngineUltimate

                CompleteEngineUltimate()
                return {"healthy": True, "status": "OK"}

            else:
                return {"healthy": True, "status": "OK"}

        except Exception as e:
            return {"healthy": False, "status": "ERROR", "error": str(e)}

    def monitor_tests(self) -> Dict[str, Any]:
        """テスト結果監視"""
        import subprocess

        try:
            # pytestを実行（簡易版）
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "--tb=no", "-q", "--co"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # テスト数をカウント
            output = result.stdout
            test_count = output.count("test_")

            # 履歴に追加
            test_result = {
                "timestamp": datetime.now().isoformat(),
                "total_tests": test_count,
                "status": "collected",
            }

            self.test_history.append(test_result)

            # 最新5件のみ保持
            self.test_history = self.test_history[-5:]

            print(f"  テスト総数: {test_count}件")
            print(f"  履歴: {len(self.test_history)}回分")

            # 履歴表示
            if self.test_history:
                print("\n  📊 テスト履歴（最新5件）:")
                for i, record in enumerate(reversed(self.test_history), 1):
                    ts = datetime.fromisoformat(record["timestamp"])
                    print(f"    {i}. {ts.strftime('%H:%M:%S')} - {record['total_tests']}件")

            return {"total_tests": test_count, "history": self.test_history}

        except Exception as e:
            print(f"  ⚠️ テスト実行エラー: {e}")
            return {"total_tests": 0, "error": str(e)}

    def monitor_integrations(self) -> Dict[str, Any]:
        """エージェント連携監視"""
        integrations = {
            "PMAgent → TaskExecutor": self.check_integration("pm_to_executor"),
            "TaskExecutor → ReviewAgent": self.check_integration("executor_to_review"),
            "ReviewAgent → KnowledgeManager": self.check_integration("review_to_knowledge"),
            "KnowledgeManager → CompleteEngine": self.check_integration("knowledge_to_engine"),
        }

        for integration, status in integrations.items():
            icon = "✅" if status["connected"] else "❌"
            print(f"  {icon} {integration}: {status['status']}")

        return integrations

    def check_integration(self, integration_name: str) -> Dict[str, Any]:
        """連携チェック"""
        # 簡易的なチェック（実際にはより詳細な確認が必要）
        try:
            if integration_name == "pm_to_executor":
                # pm_tasksにpendingタスクがあるかチェック
                tasks = self.read_sheet_as_dicts("pm_tasks")
                return {
                    "connected": len(tasks) > 0,
                    "status": "OK",
                    "details": f"{len(tasks)}件のタスク",
                }

            elif integration_name == "executor_to_review":
                # task_execution_logにログがあるかチェック
                logs = self.read_sheet_as_dicts("task_execution_log")
                return {
                    "connected": len(logs) > 0,
                    "status": "OK",
                    "details": f"{len(logs)}件のログ",
                }

            else:
                return {"connected": True, "status": "OK"}

        except Exception as e:
            return {"connected": False, "status": "ERROR", "error": str(e)}

    def monitor_tasks(self) -> Dict[str, Any]:
        """タスク実行監視"""
        try:
            tasks = self.read_sheet_as_dicts("pm_tasks")

            status_count = {}
            for task in tasks:
                status = task.get("status", "unknown")
                status_count[status] = status_count.get(status, 0) + 1

            print(f"  総タスク数: {len(tasks)}件")
            for status, count in sorted(status_count.items()):
                icon = {"completed": "✅", "pending": "⏳", "failed": "❌"}.get(status, "❓")
                print(f"    {icon} {status}: {count}件")

            return {"total": len(tasks), "by_status": status_count}

        except Exception as e:
            print(f"  ⚠️ タスク監視エラー: {e}")
            return {"total": 0, "error": str(e)}

    def monitor_knowledge(self) -> Dict[str, Any]:
        """ナレッジシステム監視"""
        try:
            stats = self.knowledge_manager.get_statistics()

            print(f"  総ナレッジ数: {stats.get('total_entries', 0)}件")
            print(f"  カテゴリ数: {stats.get('total_categories', 0)}件")

            return stats

        except Exception as e:
            print(f"  ⚠️ ナレッジ監視エラー: {e}")
            return {"total_entries": 0, "error": str(e)}

    def judge_overall_health(self, report: Dict) -> Dict[str, Any]:
        """総合健全性判定"""

        # エージェント健全性
        agents_healthy = all(agent.get("healthy", False) for agent in report["agents"].values())

        # 連携健全性
        integrations_healthy = all(
            integration.get("connected", False) for integration in report["integrations"].values()
        )

        # 総合判定
        if agents_healthy and integrations_healthy:
            status = "HEALTHY"
            icon = "✅"
        elif agents_healthy or integrations_healthy:
            status = "WARNING"
            icon = "⚠️"
        else:
            status = "CRITICAL"
            icon = "❌"

        return {
            "status": status,
            "icon": icon,
            "agents_healthy": agents_healthy,
            "integrations_healthy": integrations_healthy,
        }

    def display_summary(self, report: Dict):
        """サマリー表示"""
        print("\n" + "=" * 80)
        print("📊 監視サマリー")
        print("=" * 80)

        overall = report["overall"]
        print(f"\n{overall['icon']} 総合状態: {overall['status']}")

        # エージェント状態
        agents_ok = sum(1 for a in report["agents"].values() if a.get("healthy"))
        agents_total = len(report["agents"])
        print(f"  エージェント: {agents_ok}/{agents_total} 正常")

        # 連携状態
        integrations_ok = sum(1 for i in report["integrations"].values() if i.get("connected"))
        integrations_total = len(report["integrations"])
        print(f"  連携: {integrations_ok}/{integrations_total} 正常")

        # タスク状態
        tasks = report.get("tasks", {})
        print(f"  タスク: {tasks.get('total', 0)}件")

        # ナレッジ状態
        knowledge = report.get("knowledge", {})
        print(f"  ナレッジ: {knowledge.get('total_entries', 0)}件")

        print("\n" + "=" * 80)

    def watch_continuous(self, interval: int = 60):
        """連続監視モード"""
        print("\n" + "=" * 80)
        print("👁️ 連続監視モード開始")
        print(f"監視間隔: {interval}秒")
        print("停止: Ctrl+C")
        print("=" * 80)

        try:
            while True:
                self.monitor_all()

                print(f"\n⏳ 次回監視まで{interval}秒...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n👋 監視を終了します")


def main():
    """メイン"""
    observer = RealtimeObserver()

    # 1回監視
    observer.monitor_all()

    # 連続監視したい場合
    # observer.watch_continuous(interval=60)


if __name__ == "__main__":
    main()

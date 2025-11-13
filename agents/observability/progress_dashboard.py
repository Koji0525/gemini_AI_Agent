"""
進捗可視化ダッシュボード
要件定義の進捗率を可視化
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict

project_root = os.path.abspath(os.path.dirname(__file__) + "/../..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from knowledge_system.simple_knowledge_wrapper import SimpleKnowledgeWrapper
from tools.base_data_accessor import BaseDataAccessor


class ProgressDashboard:
    """進捗ダッシュボード"""

    def __init__(self):
        self.accessor = BaseDataAccessor()
        self.km = SimpleKnowledgeWrapper()

        # 要件定義
        self.requirements = {
            "FR-001": {"name": "ゴール自動分解", "weight": 20},
            "FR-002": {"name": "タスク自律実行", "weight": 25},
            "FR-003": {"name": "品質自動評価", "weight": 15},
            "FR-004": {"name": "ナレッジ自動蓄積", "weight": 20},
            "FR-005": {"name": "進捗自動可視化", "weight": 20},
        }

        # 統合状況
        self.integrations = {
            "knowledge_base": {"name": "ナレッジベース統合", "status": "unknown"},
            "sheets_api": {"name": "Google Sheets統合", "status": "unknown"},
            "quality_review": {"name": "品質評価統合", "status": "unknown"},
            "auto_execution": {"name": "自動実行統合", "status": "unknown"},
        }

    def check_all_progress(self) -> Dict[str, Any]:
        """全進捗チェック"""
        print("\n" + "=" * 80)
        print("📊 システム進捗ダッシュボード")
        print("=" * 80)
        print(f"更新時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 要件別進捗
        requirement_progress = {}
        for req_id, info in self.requirements.items():
            progress = self.check_requirement_progress(req_id)
            requirement_progress[req_id] = progress

        # 統合状況
        integration_status = self.check_integrations()

        # 全体進捗
        overall_progress = self.calculate_overall_progress(requirement_progress)

        # 表示
        self.display_progress(requirement_progress, integration_status, overall_progress)

        return {
            "requirements": requirement_progress,
            "integrations": integration_status,
            "overall": overall_progress,
        }

    def check_requirement_progress(self, req_id: str) -> Dict[str, Any]:
        """要件進捗チェック"""

        if req_id == "FR-001":
            return self.check_fr001()
        elif req_id == "FR-002":
            return self.check_fr002()
        elif req_id == "FR-003":
            return self.check_fr003()
        elif req_id == "FR-004":
            return self.check_fr004()
        elif req_id == "FR-005":
            return self.check_fr005()

        return {"progress": 0, "status": "unknown"}

    def check_fr001(self) -> Dict[str, Any]:
        """FR-001: ゴール自動分解"""
        try:
            # ゴール読み込み
            goals = self.accessor.read_sheet_as_dicts("project_goal")

            # タスク読み込み
            tasks = self.accessor.read_sheet_as_dicts("pm_tasks")

            # 進捗計算
            if len(goals) > 0 and len(tasks) > 0:
                return {"progress": 100.0, "status": "completed"}
            elif len(goals) > 0:
                return {"progress": 50.0, "status": "in_progress"}
            else:
                return {"progress": 0, "status": "not_started"}

        except Exception as e:
            return {"progress": 0, "status": "error", "error": str(e)}

    def check_fr002(self) -> Dict[str, Any]:
        """FR-002: タスク自律実行"""
        try:
            # 実行ログ
            logs = self.accessor.read_sheet_as_dicts("task_execution_log")

            # 出力ファイル
            output_files = (
                len([f for f in os.listdir("agent_outputs") if f.endswith(".txt")])
                if os.path.exists("agent_outputs")
                else 0
            )

            # 進捗計算
            if len(logs) > 0 and output_files > 0:
                return {"progress": 100.0, "status": "completed"}
            elif len(logs) > 0:
                return {"progress": 60.0, "status": "in_progress"}
            else:
                return {"progress": 0, "status": "not_started"}

        except Exception as e:
            return {"progress": 0, "status": "error", "error": str(e)}

    def check_fr003(self) -> Dict[str, Any]:
        """FR-003: 品質自動評価"""
        try:
            logs = self.accessor.read_sheet_as_dicts("task_execution_log")

            # スコア付きログ
            scored = [l for l in logs if l.get("Quality_Score") and l["Quality_Score"] != ""]

            # 進捗計算
            if len(scored) > 0:
                rate = len(scored) / len(logs) * 100
                return {"progress": rate, "status": "completed"}
            else:
                return {"progress": 0, "status": "not_started"}

        except Exception as e:
            return {"progress": 0, "status": "error", "error": str(e)}

    def check_fr004(self) -> Dict[str, Any]:
        """FR-004: ナレッジ自動蓄積"""
        try:
            stats = self.km.get_statistics()
            entries = stats.get("total_entries", 0)

            # 進捗計算
            if entries > 100:
                return {"progress": 100.0, "status": "completed"}
            elif entries > 0:
                progress = min(entries / 100 * 100, 99.9)
                return {"progress": progress, "status": "in_progress"}
            else:
                return {"progress": 0, "status": "not_started"}

        except Exception as e:
            return {"progress": 0, "status": "error", "error": str(e)}

    def check_fr005(self) -> Dict[str, Any]:
        """FR-005: 進捗自動可視化"""
        try:
            # ダッシュボード存在確認
            dashboard_exists = os.path.exists("agents/observability/dashboard.py")

            # タスク進捗計算
            tasks = self.accessor.read_sheet_as_dicts("pm_tasks")
            completed = sum(1 for t in tasks if t.get("status") == "completed")

            # 進捗計算
            if dashboard_exists and completed > 0:
                return {"progress": 100.0, "status": "completed"}
            elif dashboard_exists:
                return {"progress": 50.0, "status": "in_progress"}
            else:
                return {"progress": 0, "status": "not_started"}

        except Exception as e:
            return {"progress": 0, "status": "error", "error": str(e)}

    def check_integrations(self) -> Dict[str, Dict]:
        """統合状況チェック"""

        integrations = {}

        # ナレッジベース統合
        try:
            self.km.get_statistics()
            integrations["knowledge_base"] = {"name": "ナレッジベース統合", "status": "✅ 統合済み"}
        except:
            integrations["knowledge_base"] = {"name": "ナレッジベース統合", "status": "❌ 未統合"}

        # Google Sheets統合
        try:
            self.accessor.read_sheet_as_dicts("project_goal")
            integrations["sheets_api"] = {"name": "Google Sheets統合", "status": "✅ 統合済み"}
        except:
            integrations["sheets_api"] = {"name": "Google Sheets統合", "status": "❌ 未統合"}

        # 品質評価統合
        try:
            logs = self.accessor.read_sheet_as_dicts("task_execution_log")
            has_quality = any(l.get("Quality_Score") and l["Quality_Score"] != "" for l in logs)
            integrations["quality_review"] = {
                "name": "品質評価統合",
                "status": "✅ 統合済み" if has_quality else "⏳ 進行中",
            }
        except:
            integrations["quality_review"] = {"name": "品質評価統合", "status": "❌ 未統合"}

        # 自動実行統合
        try:
            logs = self.accessor.read_sheet_as_dicts("task_execution_log")
            integrations["auto_execution"] = {
                "name": "自動実行統合",
                "status": "✅ 統合済み" if len(logs) > 0 else "⏳ 進行中",
            }
        except:
            integrations["auto_execution"] = {"name": "自動実行統合", "status": "❌ 未統合"}

        return integrations

    def calculate_overall_progress(self, requirement_progress: Dict) -> float:
        """全体進捗計算"""
        total_weight = sum(info["weight"] for info in self.requirements.values())
        weighted_progress = sum(
            requirement_progress[req_id]["progress"] * info["weight"]
            for req_id, info in self.requirements.items()
        )

        return weighted_progress / total_weight

    def display_progress(
        self, requirement_progress: Dict, integration_status: Dict, overall: float
    ):
        """進捗表示"""

        print("\n" + "━" * 80)
        print("�� 要件定義別進捗")
        print("━" * 80)

        for req_id, info in self.requirements.items():
            progress_info = requirement_progress[req_id]
            progress_val = progress_info["progress"]

            # ステータスアイコン
            status_icon = {
                "completed": "✅",
                "in_progress": "⏳",
                "not_started": "❌",
                "error": "⚠️",
                "unknown": "❓",
            }.get(progress_info["status"], "❓")

            # プログレスバー
            bar_length = int(progress_val / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            print(f"{req_id} {status_icon} [{bar}] {progress_val:5.1f}% {info['name']}")

        print("\n" + "━" * 80)
        print("🔗 統合状況")
        print("━" * 80)

        for integration_id, info in integration_status.items():
            print(f"  {info['status']} {info['name']}")

        print("\n" + "━" * 80)
        print(f"📊 全体進捗: {overall:.1f}%")
        print("━" * 80)

        # 全体プログレスバー
        overall_bar_length = int(overall / 5)
        overall_bar = "█" * overall_bar_length + "░" * (20 - overall_bar_length)
        print(f"[{overall_bar}] {overall:.1f}%")

        print("=" * 80)


def main():
    """メイン"""
    dashboard = ProgressDashboard()
    result = dashboard.check_all_progress()

    # JSON保存
    with open("progress_report.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n📄 進捗レポート保存: progress_report.json")


if __name__ == "__main__":
    main()

"""
進捗監視エージェント - 修正版
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader


class ProgressMonitorAgent:
    """進捗監視エージェント(修正版)"""

    def __init__(self):
        """コンストラクタ - sheets_managerを内部で初期化"""
        try:
            self.config = ConfigLoader()
            spreadsheet_id = self.config.get("SPREADSHEET_ID")
            service_account_file = self.config.get("GOOGLE_SERVICE_ACCOUNT_FILE")

            print(f"📊 ProgressMonitorAgent初期化: spreadsheet_id={spreadsheet_id}")
            print(f"🔑 ProgressMonitorAgent初期化: service_account_file={service_account_file}")

            self.sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)
            print("✅ ProgressMonitorAgent: Google Sheets接続成功")

        except Exception as e:
            print(f"❌ ProgressMonitorAgent初期化エラー: {e}")
            self.sheets_manager = None

    async def get_dashboard_data(self) -> List[Dict[str, Any]]:
        """
        ダッシュボードからデータを取得

        Returns:
            ダッシュボードの全データ
        """
        try:
            if not self.sheets_manager:
                print("❌ sheets_managerが初期化されていません")
                return []

            # 新しいAPIを使用
            data = await self.sheets_manager.load_tasks_from_sheet("progress_dashboard")

            if not data or len(data) <= 1:
                print("⚠️ ダッシュボードデータがありません")
                return []

            # ヘッダー行を取得
            headers = data[0]

            # データ行を辞書形式に変換
            dashboard_data = []
            for row in data[1:]:
                if row and len(row) > 0 and row[0]:  # goal_idがある行のみ
                    row_dict = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            row_dict[header] = row[i]
                        else:
                            row_dict[header] = ""
                    dashboard_data.append(row_dict)

            print(f"✅ ダッシュボードデータ取得: {len(dashboard_data)}件")
            return dashboard_data

        except Exception as e:
            print(f"❌ ダッシュボードデータ取得エラー: {e}")
            return []

    async def detect_low_progress_goals(self, threshold: float = 50.0) -> List[Dict[str, Any]]:
        """
        進捗率が低い目標を検出

        Args:
            threshold: 進捗率の閾値(デフォルト50%)

        Returns:
            低進捗の目標リスト
        """
        try:
            dashboard_data = await self.get_dashboard_data()
            low_progress_goals = []

            # project_goalシートから最新のstatusを取得
            goal_statuses = {}
            try:
                goal_data = await self.sheets_manager.load_tasks_from_sheet("project_goal")
                if goal_data and len(goal_data) > 1:
                    for row in goal_data[1:]:  # ヘッダーをスキップ
                        if len(row) >= 3:
                            goal_id = row[0]
                            status = row[2].lower() if len(row) > 2 else ""
                            goal_statuses[goal_id] = status
            except Exception as e:
                print(f"⚠️  project_goalのstatus取得エラー: {e}")

            for goal in dashboard_data:
                # project_goalシートの最新statusでcancelledをスキップ
                goal_id = str(goal.get("goal_id", ""))
                status = goal_statuses.get(goal_id, "").lower()
                if status == "cancelled":
                    print(f"  ⏭️  Goal {goal_id} はcancelledのためスキップ")
                    continue

                try:
                    # 数値変換(英語ヘッダー対応)
                    progress_rate = float(goal.get("progress_rate", 0) or 0)
                    total_tasks = int(goal.get("total_tasks", 0) or 0)
                    completed_tasks = int(goal.get("completed_tasks", 0) or 0)
                    avg_quality = float(goal.get("avg_quality", 0) or 0)

                    status = goal.get("status", "")
                    goal_id = goal.get("goal_id", "N/A")

                    # 進捗率が閾値未満で、未完了の目標
                    if progress_rate < threshold and status != "completed":
                        low_progress_goals.append(
                            {
                                "goal_id": goal_id,
                                "goal_name": goal.get("goal_name", f"Goal_{goal_id}"),
                                "progress_rate": progress_rate,
                                "total_tasks": total_tasks,
                                "completed_tasks": completed_tasks,
                                "avg_quality": avg_quality,
                                "priority": goal.get("priority", "medium"),
                                "assigned_agent": goal.get("assigned_agent", ""),
                            }
                        )
                except (ValueError, TypeError) as e:
                    print(f"⚠️ 目標{goal.get('goal_id', 'N/A')}のデータ変換エラー: {e}")
                    continue

            # 優先度順にソート
            priority_order = {"high": 0, "medium": 1, "low": 2}
            low_progress_goals.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["progress_rate"]))

            # activeなゴールも追加（進捗率に関係なく）
            for goal in dashboard_data:
                goal_id = str(goal.get("goal_id", ""))
                status = goal_statuses.get(goal_id, "").lower()

                if status == "active":
                    # すでにlow_progress_goalsに含まれていない場合のみ追加
                    already_included = any(str(g.get("goal_id", "")) == goal_id for g in low_progress_goals)
                    if not already_included:
                        low_progress_goals.append(goal)
                        print(
                            f"  ➕ Goal {goal_id} (active, 進捗率: {float(goal.get('progress_rate', 0) or 0):.1f}%) を処理対象に追加"
                        )

            return low_progress_goals

        except Exception as e:
            print(f"❌ 低進捗目標検出エラー: {e}")
            return []

    async def get_goals_progress(self) -> List[Dict[str, Any]]:
        """
        目標の進捗状況を取得（automation.py用のインターフェース）

        Returns:
            目標の進捗状況リスト
        """
        return await self.detect_low_progress_goals(threshold=50.0)


# テストコード
async def test_progress_monitor():
    """進捗監視のテスト"""
    print("=" * 70)
    print("🧪 PM Agent - Progress Monitor Test (Fixed Version)")
    print("=" * 70)

    try:
        monitor = ProgressMonitorAgent()
        print("✅ ProgressMonitorAgent初期化成功")

        goals = await monitor.get_goals_progress()
        print(f"✅ 目標進捗取得: {len(goals)} 目標")

        for goal in goals:
            print(f"  - 目標 {goal['goal_id']}: {goal['progress_rate']}%")

    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_progress_monitor())

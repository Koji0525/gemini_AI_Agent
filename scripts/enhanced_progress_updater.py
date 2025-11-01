#!/usr/bin/env python3
"""
拡張版Progress Dashboard Updater - 進捗計算を改善
"""

import os
import sys
import asyncio
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configuration.config_loader import ConfigLoader


class EnhancedProgressUpdater:
    """進捗計算を改善した進捗更新クラス"""

    def __init__(self):
        self.config = ConfigLoader()
        self.spreadsheet_id = self.config.get("spreadsheet_id")
        self.service_account_file = self.config.get("service_account_file")
        self.setup_gspread()

    def setup_gspread(self):
        """gspreadをセットアップ"""
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
        self.gc = gspread.authorize(credentials)
        self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
        print("✅ Google Sheetsに接続")

    async def update_progress_dashboard(self):
        """進捗ダッシュボードを更新"""
        try:
            print("🚀 拡張版Progress Dashboard 更新開始...")

            # 1. 各シートからデータ取得
            goals_data = await self.load_sheet_data("project_goal")
            tasks_data = await self.load_sheet_data("pm_tasks")
            dashboard_data = await self.load_sheet_data("progress_dashboard")

            if not goals_data:
                return

            # 2. 詳細な分析
            analysis = self.analyze_progress(goals_data, tasks_data)

            # 3. ダッシュボード更新
            await self.update_dashboard(analysis, dashboard_data)

            print("✅ 拡張版Progress Dashboard 更新完了")

        except Exception as e:
            print(f"❌ 更新エラー: {e}")
            import traceback

            traceback.print_exc()

    async def load_sheet_data(self, sheet_name: str):
        """シートデータを読み込み"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            all_values = worksheet.get_all_values()

            if all_values and len(all_values) > 1:
                print(f"✅ {sheet_name}: {len(all_values)}行 ({len(all_values)-1}データ行)")
                return all_values
            else:
                print(f"⚠️ {sheet_name}: データが少ないか空です")
                return None

        except Exception as e:
            print(f"❌ {sheet_name}読み込みエラー: {e}")
            return None

    def analyze_progress(self, goals_data, tasks_data):
        """進捗を詳細分析"""
        analysis = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_goals": len(goals_data) - 1 if goals_data else 0,
            "active_goals": [],
            "completed_tasks": 0,
            "total_tasks": 0,
            "progress_breakdown": {},
        }

        # Active Goalの分析
        if goals_data:
            analysis["active_goals"] = self.extract_active_goals(goals_data)
            analysis["active_goal_count"] = len(analysis["active_goals"])

        # タスクの分析
        if tasks_data:
            task_stats = self.analyze_tasks(tasks_data)
            analysis.update(task_stats)

        # 進捗率の計算
        analysis["overall_progress"] = self.calculate_overall_progress(analysis)

        return analysis

    def extract_active_goals(self, data):
        """Activeなゴールを抽出"""
        headers = data[0]
        active_goals = []

        status_idx = self.find_column_index(headers, ["status", "ステータス"])
        title_idx = self.find_column_index(headers, ["goal_description", "title", "説明"])
        id_idx = self.find_column_index(headers, ["goal_id", "id"])

        for row_num, row in enumerate(data[1:], 2):
            if status_idx != -1 and len(row) > status_idx:
                status = str(row[status_idx]).lower().strip()
                if status == "active":
                    goal = {
                        "row": row_num,
                        "id": row[id_idx] if id_idx != -1 and len(row) > id_idx else f"row_{row_num}",
                        "title": row[title_idx] if title_idx != -1 and len(row) > title_idx else "N/A",
                        "status": status,
                    }
                    active_goals.append(goal)

        return active_goals

    def analyze_tasks(self, tasks_data):
        """タスクを分析"""
        headers = tasks_data[0]
        status_idx = self.find_column_index(headers, ["status", "ステータス"])

        completed = 0
        total = len(tasks_data) - 1  # ヘッダー行を除く

        for row in tasks_data[1:]:
            if status_idx != -1 and len(row) > status_idx:
                status = str(row[status_idx]).lower().strip()
                if status in ["completed", "完了", "done"]:
                    completed += 1

        return {
            "completed_tasks": completed,
            "total_tasks": total,
            "task_completion_rate": round((completed / total * 100), 2) if total > 0 else 0,
        }

    def calculate_overall_progress(self, analysis):
        """総合進捗率を計算"""
        # 複数の指標から進捗を計算
        progress_components = []

        # Active Goalがある場合は基本進捗
        if analysis["active_goal_count"] > 0:
            progress_components.append(10.0)  # 基本進捗

        # タスク完了率から進捗
        if analysis["total_tasks"] > 0:
            task_progress = analysis["task_completion_rate"] * 0.7  # 70%の重み
            progress_components.append(task_progress)

        # Active Goalの数から進捗
        goal_progress = min(analysis["active_goal_count"] * 5, 20)  # 最大20%
        progress_components.append(goal_progress)

        # 平均を計算
        overall = sum(progress_components) / len(progress_components) if progress_components else 0
        return round(overall, 2)

    def find_column_index(self, headers, possible_names):
        """列インデックスを検索"""
        headers_lower = [str(h).lower() for h in headers]
        for name in possible_names:
            name_lower = name.lower()
            if name_lower in headers_lower:
                return headers_lower.index(name_lower)
        return -1

    async def update_dashboard(self, analysis, dashboard_data):
        """ダッシュボードを更新"""
        try:
            print(f"\n📊 進捗分析結果:")
            print(f"   更新日時: {analysis['timestamp']}")
            print(f"   総合進捗: {analysis['overall_progress']}%")
            print(f"   Activeゴール: {analysis['active_goal_count']}個")
            print(
                f"   完了タスク: {analysis['completed_tasks']}/{analysis['total_tasks']} ({analysis['task_completion_rate']}%)"
            )

            print(f"\n🎯 Activeゴール詳細:")
            for i, goal in enumerate(analysis["active_goals"], 1):
                title_preview = goal["title"][:80] + "..." if len(goal["title"]) > 80 else goal["title"]
                print(f"   {i}. [{goal['id']}] {title_preview}")

            # ここで実際のスプレッドシート更新を実装
            await self.write_to_dashboard(analysis)

        except Exception as e:
            print(f"❌ ダッシュボード更新エラー: {e}")

    async def write_to_dashboard(self, analysis):
        """ダッシュボードに書き込み"""
        try:
            worksheet = self.spreadsheet.worksheet("progress_dashboard")

            # 新しい行のデータ
            new_row = [
                analysis["timestamp"],
                analysis["overall_progress"],
                analysis["active_goal_count"],
                analysis["completed_tasks"],
                analysis["total_tasks"],
                analysis["task_completion_rate"],
                f"Active: {[goal['id'] for goal in analysis['active_goals']]}",
            ]

            # 既存データを確認
            existing_data = worksheet.get_all_values()
            if len(existing_data) > 0:
                # ヘッダーがある場合は2行目に追加
                worksheet.insert_row(new_row, 2)
                print("✅ ダッシュボードに新しい行を追加しました")
            else:
                # ヘッダーを作成して追加
                headers = [
                    "Timestamp",
                    "Overall Progress %",
                    "Active Goals",
                    "Completed Tasks",
                    "Total Tasks",
                    "Completion Rate %",
                    "Active Goal IDs",
                ]
                worksheet.append_row(headers)
                worksheet.append_row(new_row)
                print("✅ ダッシュボードを新規作成しました")

        except Exception as e:
            print(f"❌ ダッシュボード書き込みエラー: {e}")


async def main():
    """メイン実行"""
    try:
        ConfigLoader.validate_config()
        print("\n" + "=" * 50)

        updater = EnhancedProgressUpdater()
        await updater.update_progress_dashboard()

    except Exception as e:
        print(f"❌ 実行エラー: {e}")


if __name__ == "__main__":
    asyncio.run(main())

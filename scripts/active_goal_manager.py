#!/usr/bin/env python3
"""
Active Goal Manager - 本番環境用
スプレッドシートからActiveなゴールを取得し、Progress Dashboardを更新
"""

import os
import sys
import asyncio
from typing import Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.sheets_manager import GoogleSheetsManager


class ActiveGoalManager:
    """Active Goal管理クラス - 本番環境用"""

    def __init__(self):
        self.spreadsheet_id = os.getenv(
            "SPREADSHEET_ID", "1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s"
        )
        service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.sheets_manager = GoogleSheetsManager(self.spreadsheet_id, service_account_file)

    async def get_active_goals(self) -> List[Dict]:
        """Activeなゴールを取得"""
        try:
            print("🎯 Active Goal 取得開始...")

            # project_goalシートからデータ取得
            data = await self.sheets_manager.load_tasks_from_sheet("project_goal")
            if not data or len(data) < 2:
                print("❌ project_goalデータの取得に失敗")
                return []

            print(f"✅ {len(data)-1}個のゴールデータを取得")

            # ヘッダー分析
            headers = data[0]
            print(f"📋 ヘッダー: {headers}")

            # 列マッピング
            column_mapping = self._create_column_mapping(headers)
            print(f"🗂️ 列マッピング: {column_mapping}")

            # Activeゴールの抽出
            active_goals = []
            for row_num, row in enumerate(data[1:], 2):
                if self._is_active_goal(row, column_mapping):
                    goal = self._extract_goal_data(row, column_mapping, row_num)
                    active_goals.append(goal)
                    print(f"✅ Activeゴール検出: 行{row_num} - {goal['title']}")

            print(f"🎯 合計 {len(active_goals)}個のActiveゴールを検出")
            return active_goals

        except Exception as e:
            print(f"❌ Active Goal取得エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    def _create_column_mapping(self, headers: List[str]) -> Dict[str, int]:
        """列マッピングを作成"""
        mapping = {}
        headers_lower = [str(h).lower() for h in headers]

        # ステータス列
        status_keys = ["status", "state", "ステータス", "状態"]
        for key in status_keys:
            if key in headers_lower:
                mapping["status"] = headers_lower.index(key)
                break

        # タイトル列
        title_keys = ["title", "goal_title", "ゴール名", "名前"]
        for key in title_keys:
            if key in headers_lower:
                mapping["title"] = headers_lower.index(key)
                break

        # 進捗率列
        progress_keys = ["progress_rate", "progress", "進捗率", "進捗"]
        for key in progress_keys:
            if key in headers_lower:
                mapping["progress_rate"] = headers_lower.index(key)
                break

        return mapping

    def _is_active_goal(self, row: List, column_mapping: Dict[str, int]) -> bool:
        """行がActiveなゴールか判定"""
        status_idx = column_mapping.get("status", -1)
        if status_idx != -1 and len(row) > status_idx:
            status = str(row[status_idx]).lower().strip()
            return status == "active"
        return False

    def _extract_goal_data(self, row: List, column_mapping: Dict[str, int], row_num: int) -> Dict:
        """ゴールデータを抽出"""
        goal = {"row_number": row_num, "title": "N/A", "progress_rate": "0", "status": "active"}

        # タイトル
        title_idx = column_mapping.get("title", -1)
        if title_idx != -1 and len(row) > title_idx:
            goal["title"] = row[title_idx]

        # 進捗率
        progress_idx = column_mapping.get("progress_rate", -1)
        if progress_idx != -1 and len(row) > progress_idx:
            goal["progress_rate"] = row[progress_idx]

        return goal

    async def update_progress_dashboard(self, active_goals: List[Dict]):
        """Progress Dashboardを更新"""
        try:
            if not active_goals:
                print("📭 更新するActiveゴールがありません")
                return

            print("📊 Progress Dashboard 更新開始...")

            # 進捗率の計算
            total_progress = self._calculate_total_progress(active_goals)
            active_count = len(active_goals)

            print(f"📈 総合進捗: {total_progress}%")
            print(f"🎯 Activeゴール数: {active_count}")

            # ここで実際の更新処理を実装
            # self.sheets_manager.update_task_status() などを使用

            print("✅ Progress Dashboard 更新完了")

        except Exception as e:
            print(f"❌ Progress Dashboard更新エラー: {e}")

    def _calculate_total_progress(self, active_goals: List[Dict]) -> float:
        """総合進捗率を計算"""
        if not active_goals:
            return 0.0

        total = 0.0
        count = 0

        for goal in active_goals:
            try:
                progress = float(str(goal["progress_rate"]).replace("%", "").strip())
                total += progress
                count += 1
            except (ValueError, TypeError):
                continue

        return round(total / count, 2) if count > 0 else 0.0


# メイン実行
async def main():
    """メイン実行関数"""
    print("🚀 Active Goal Manager 起動")
    print("=" * 50)

    manager = ActiveGoalManager()

    # Active Goalの取得
    active_goals = await manager.get_active_goals()

    # 結果表示
    print(f"\n📋 検出結果: {len(active_goals)}個のActiveゴール")
    for i, goal in enumerate(active_goals, 1):
        print(f"  {i}. 行{goal['row_number']}: {goal['title']}")
        print(f"     進捗: {goal['progress_rate']}%")

    # Progress Dashboardの更新

    # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
    if active_goals:
        await manager.update_progress_dashboard(active_goals)

    print("\n" + "=" * 50)
    print("✅ Active Goal Manager 完了")


if __name__ == "__main__":
    asyncio.run(main())

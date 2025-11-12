"""
PMAgent修正版 - リスト→辞書変換を内部で実施
TaskExecutorの成功パターンを適用
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_manager import GoogleSheetsManager

logger = logging.getLogger(__name__)


class PMAgentFixed:
    """PMAgent修正版 - データ変換処理を内部で実施"""

    # スキーマ定義
    GOAL_SCHEMA = ["goal_id", "status", "description"]

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = GoogleSheetsManager()
        self.safe_sheets = SafeSheetsWrapper(self.sheets)
        logger.info("✅ PMAgentFixed 初期化完了")

    def _convert_row_to_dict(self, row: List[Any], schema: List[str]) -> Dict[str, Any]:
        """
        行データを辞書に変換（TaskExecutorのパターンを適用）

        Args:
            row: データ行
            schema: 列名のリスト

        Returns:
            辞書形式のデータ
        """
        result = {}
        for i, col_name in enumerate(schema):
            if i < len(row):
                result[col_name] = row[i]
            else:
                result[col_name] = ""
        return result

    async def load_project_goal(self) -> Optional[Dict]:
        """
        project_goalから最新のアクティブな目標を読み込み（修正版）

        Returns:
            目標情報（辞書形式）
        """
        try:
            logger.info("📋 project_goal読み込み中...")

            # リスト形式でデータ取得
            all_goals_list = self.safe_sheets.safe_read("project_goal!A2:C100", default=[])

            if not all_goals_list:
                logger.warning("⚠️ project_goalにデータがありません")
                return None

            logger.info(f"📥 取得: {len(all_goals_list)}行")

            # ✅ リスト→辞書変換（TaskExecutorのパターン）
            all_goals = [self._convert_row_to_dict(row, self.GOAL_SCHEMA) for row in all_goals_list]

            # active/pending のゴールをフィルタ
            active_goals = [
                goal
                for goal in all_goals
                if goal.get("status", "").lower() in ["active", "pending"]
            ]

            if not active_goals:
                logger.warning("⚠️ 処理可能な目標がありません")
                return None

            # 最初のゴールを返す
            selected_goal = active_goals[0]
            logger.info(f"✅ ゴール選択: {selected_goal.get('goal_id')}")
            logger.info(f"   内容: {selected_goal.get('description', '')[:80]}...")

            return selected_goal

        except Exception as e:
            logger.error(f"❌ 目標読み込みエラー: {e}")
            import traceback

            traceback.print_exc()
            return None

    async def run_pm_cycle(self):
        """PMサイクル実行（修正版）"""
        try:
            logger.info("🔄 PMサイクル開始")

            # ゴール読み込み
            goal = await self.load_project_goal()

            if goal:
                logger.info("✅ PMサイクル完了")
                logger.info(f"   処理ゴール: {goal.get('goal_id')}")
                logger.info(f"   ステータス: {goal.get('status')}")
            else:
                logger.warning("⚠️ 処理可能なゴールなし")

        except Exception as e:
            logger.error(f"❌ PMサイクルエラー: {e}")


# テスト
async def test_pm_agent():
    print("🧪 PMAgent修正版テスト\n")

    pm = PMAgentFixed(None)

    # テスト1: ゴール読み込み
    print("テスト1: ゴール読み込み")
    goal = await pm.load_project_goal()
    if goal:
        print(f"✅ 成功")
        print(f"   goal_id: {goal.get('goal_id')}")
        print(f"   status: {goal.get('status')}")
        print(f"   description: {goal.get('description', '')[:50]}...")
    else:
        print("❌ ゴールなし")

    # テスト2: PMサイクル
    print("\nテスト2: PMサイクル実行")
    await pm.run_pm_cycle()


if __name__ == "__main__":
    asyncio.run(test_pm_agent())

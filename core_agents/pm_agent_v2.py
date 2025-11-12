"""
PMAgent v2 - TaskExecutorパターン完全適用版
ヘッダー行から列構造を自動検出
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


class PMAgentV2:
    """PMAgent v2 - TaskExecutorの成功パターンを完全適用"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = GoogleSheetsManager()
        self.safe_sheets = SafeSheetsWrapper(self.sheets)

        # ✅ TaskExecutorパターン: ヘッダー行から列構造を検出
        self.column_map = {}
        self._initialize_column_map()

        logger.info("✅ PMAgentV2 初期化完了")

    def _initialize_column_map(self):
        """
        列構造の初期化（TaskExecutorパターン）
        ヘッダー行から列名→インデックスのマッピングを作成
        """
        try:
            # ヘッダー行を読み取り
            headers_data = self.safe_sheets.safe_read("project_goal!A1:Z1", default=[])

            if not headers_data or len(headers_data) == 0:
                logger.error("❌ ヘッダー行が取得できません")
                return

            headers = headers_data[0]

            # 列名→インデックスのマッピング作成
            self.column_map = {header: idx for idx, header in enumerate(headers)}

            logger.info(f"✅ 列構造検出成功: {list(self.column_map.keys())}")

        except Exception as e:
            logger.error(f"❌ 列構造初期化エラー: {e}")

    def _convert_row_to_dict(self, row: List[Any]) -> Dict[str, Any]:
        """
        行データを辞書に変換（TaskExecutorパターン）
        column_mapを使って正しい列にアクセス

        Args:
            row: データ行

        Returns:
            辞書形式のデータ
        """
        result = {}

        for col_name, col_idx in self.column_map.items():
            if col_idx < len(row):
                result[col_name] = row[col_idx]
            else:
                result[col_name] = ""

        return result

    async def load_project_goal(self) -> Optional[Dict]:
        """
        project_goalから最新のアクティブな目標を読み込み（v2）

        Returns:
            目標情報（辞書形式）
        """
        try:
            logger.info("📋 project_goal読み込み中...")

            if not self.column_map:
                logger.error("❌ 列構造が初期化されていません")
                return None

            # status列のインデックス取得
            status_idx = self.column_map.get("status")
            if status_idx is None:
                logger.error("❌ status列が見つかりません")
                logger.info(f"利用可能な列: {list(self.column_map.keys())}")
                return None

            logger.info(f"✅ status列: インデックス{status_idx}（列{chr(65+status_idx)}）")

            # データ行を読み取り
            all_goals_list = self.safe_sheets.safe_read("project_goal!A2:Z100", default=[])

            if not all_goals_list:
                logger.warning("⚠️ project_goalにデータがありません")
                return None

            logger.info(f"📥 取得: {len(all_goals_list)}行")

            # ✅ リスト→辞書変換（TaskExecutorパターン）
            all_goals = [self._convert_row_to_dict(row) for row in all_goals_list]

            # デバッグ: 最初の3件の内容を表示
            logger.info("📊 取得したゴール（最初の3件）:")
            for i, goal in enumerate(all_goals[:3], 1):
                goal_id = goal.get("goal_id", "N/A")
                status = goal.get("status", "N/A")
                desc = goal.get("goal_description", goal.get("description", "N/A"))
                logger.info(f"  {i}. ID={goal_id}, status={status}, desc={desc[:50]}...")

            # active/pending のゴールをフィルタ
            active_goals = [
                goal
                for goal in all_goals
                if goal.get("status", "").strip().lower() in ["active", "pending"]
            ]

            logger.info(f"🎯 active/pending ゴール: {len(active_goals)}件")

            if not active_goals:
                logger.warning("⚠️ 処理可能な目標がありません")
                return None

            # 最初のゴールを返す
            selected_goal = active_goals[0]
            logger.info(f"✅ ゴール選択: {selected_goal.get('goal_id')}")
            desc_col = selected_goal.get("goal_description", selected_goal.get("description", ""))
            logger.info(f"   内容: {desc_col[:80]}...")
            logger.info(f"   ステータス: {selected_goal.get('status')}")

            return selected_goal

        except Exception as e:
            logger.error(f"❌ 目標読み込みエラー: {e}")
            import traceback

            traceback.print_exc()
            return None

    async def run_pm_cycle(self):
        """PMサイクル実行（v2）"""
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
async def test_pm_agent_v2():
    print("🧪 PMAgent v2 テスト\n")

    pm = PMAgentV2(None)

    # テスト1: ゴール読み込み
    print("テスト1: ゴール読み込み")
    goal = await pm.load_project_goal()

    if goal:
        print("✅ 成功！")
        print(f"   goal_id: {goal.get('goal_id')}")
        print(f"   status: {goal.get('status')}")
        desc = goal.get("goal_description", goal.get("description", ""))
        print(f"   description: {desc[:80]}...")
    else:
        print("❌ ゴールが見つかりません")

    # テスト2: PMサイクル
    print("\nテスト2: PMサイクル実行")
    await pm.run_pm_cycle()


if __name__ == "__main__":
    asyncio.run(test_pm_agent_v2())

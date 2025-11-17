"""
PMAgent v31 - Project Management Agent
GeminiTaskBreakdownAgentV2統合版（完全AI自動分解）

【主な機能】
1. project_goalから目標を読み込み
2. GeminiでAIによる詳細タスク分解
   - 目的・成功基準・コンテキスト情報を含む
   - タスク種別（調査/設計/実装/テスト/品質改善/ドキュメント）
   - 依存関係の自動生成
3. pm_tasksに書き込み

【バージョン履歴】
- v31 (2025-11-17): GeminiTaskBreakdownAgentV2統合、完全AI自動分解
- v30: 従来版
"""

import sys
import os
import logging
from typing import Dict, Any, Optional, List
import asyncio

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from configuration.sheets_schema import (
    PROJECT_GOAL_SCHEMA,
    PM_TASKS_SCHEMA,
    get_schema,
    row_to_dict,
    dict_to_row,
)

# GeminiTaskBreakdownAgentV2をインポート
from agents.pm_agent.task_breakdown_gemini_enhanced_v2 import GeminiTaskBreakdownAgentV2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PMAgent:
    """
    Project Management Agent v2（GeminiTaskBreakdown統合版）

    【主な機能】
    1. project_goalから目標を読み込み
    2. GeminiでAIによるタスク分解
    3. pm_tasksに書き込み
    """

    def __init__(self, sheets_manager: GoogleSheetsManager, knowledge_manager=None):
        """
        Args:
            sheets_manager: GoogleSheetsManager（外部から注入）
            knowledge_manager: KnowledgeBaseManager（オプション）
        """
        self.sheets = SafeSheetsWrapper(sheets_manager)
        self.sheets_manager = sheets_manager
        self.current_goal = None

        # GeminiTaskBreakdownAgentの初期化
        try:
            self.task_breakdown_agent = GeminiTaskBreakdownAgentV2(knowledge_manager)
            logger.info("✅ GeminiTaskBreakdownAgentV2 初期化成功")
        except Exception as e:
            logger.error(f"❌ GeminiTaskBreakdownAgentV2 初期化失敗: {e}")
            self.task_breakdown_agent = None

        logger.info("✅ PMAgent を初期化しました（GeminiTaskBreakdown統合版）")

    async def load_project_goal(self) -> Optional[Dict]:
        """
        project_goalから最新のアクティブな目標を読み込み

        Returns:
            目標情報（辞書形式）
        """
        try:
            # schemas定義を参照
            schema = get_schema("project_goal")
            expected_headers = schema["headers"]

            logger.info(f"📋 project_goalを読み込み中（期待ヘッダー: {expected_headers}）")

            # SafeSheetsWrapperで安全に読み取り
            all_goals = self.sheets.safe_read("project_goal", default=[])

            if not all_goals:
                logger.warning("⚠️ project_goalにデータがありません")
                return None

            # データをrow_to_dictで辞書形式に変換
            goals_dict = [row_to_dict("project_goal", row) for row in all_goals]

            # activeまたはpendingステータスの目標を検索
            active_goals = [
                goal
                for goal in goals_dict
                if goal.get("status", "").lower() in ["active", "pending"]
            ]

            if not active_goals:
                logger.warning("⚠️ アクティブな目標が見つかりません")
                return None

            # 最新の目標を取得
            latest_goal = active_goals[0]

            logger.info(f"✅ 目標を読み込みました: {latest_goal.get('goal_id', 'unknown')}")
            logger.info(f"   説明: {latest_goal.get('goal_description', '')[:50]}...")

            self.current_goal = latest_goal
            return latest_goal

        except Exception as e:
            logger.error(f"❌ 目標読み込みエラー: {e}")
            import traceback

            traceback.print_exc()
            return None

    async def break_down_goal_to_tasks(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        目標をタスクに分解（GeminiTaskBreakdownAgentV2使用）

        Args:
            goal: 目標情報

        Returns:
            タスクのリスト（pm_tasksスキーマ形式）
        """
        goal_id = goal.get("goal_id", "unknown")
        goal_desc = goal.get("goal_description", "")

        logger.info(f"🔧 目標をAIでタスクに分解中: {goal_id}")
        logger.info(f"   説明: {goal_desc[:100]}...")

        if not self.task_breakdown_agent:
            logger.error("❌ GeminiTaskBreakdownAgent が初期化されていません")
            return []

        try:
            # Geminiでタスク生成
            tasks_detailed = await self.task_breakdown_agent.generate_tasks_for_goal(
                goal_id=goal_id,
                goal_description=goal_desc,
                use_knowledge=True,  # ナレッジベース参照を有効化
            )

            if not tasks_detailed:
                logger.warning("⚠️ タスクが生成されませんでした")
                return []

            # pm_tasksスキーマ形式に変換
            pm_tasks = self.task_breakdown_agent.convert_to_pm_tasks_format(tasks_detailed)

            logger.info(f"✅ {len(pm_tasks)}個のタスクを生成しました")

            # タスク一覧を表示
            for i, task in enumerate(pm_tasks, 1):
                logger.info(f"   {i}. {task['task_id']}: {task['description'][:60]}...")

            return pm_tasks

        except Exception as e:
            logger.error(f"❌ タスク分解エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    async def write_tasks_to_sheet(self, tasks: List[Dict[str, Any]]):
        """
        タスクをpm_tasksに書き込み

        Args:
            tasks: タスクのリスト（pm_tasksスキーマ形式）
        """
        try:
            logger.info(f"📝 {len(tasks)}個のタスクをpm_tasksに書き込み中...")

            # schemas定義に従って行データに変換
            task_rows = [dict_to_row("pm_tasks", task) for task in tasks]

            # SafeSheetsWrapperで安全に追記
            for i, task_row in enumerate(task_rows, 1):
                success = self.sheets.safe_append("pm_tasks", [task_row])

                if success:
                    logger.info(f"  ✅ タスク {i}/{len(task_rows)} 書き込み完了")
                else:
                    logger.warning(f"  ⚠️ タスク {i}/{len(task_rows)} 書き込み失敗")

            logger.info("✅ すべてのタスク書き込み完了")

        except Exception as e:
            logger.error(f"❌ タスク書き込みエラー: {e}")
            import traceback

            traceback.print_exc()

    async def run_pm_cycle(self):
        """
        PMサイクルを1回実行

        1. 目標読み込み
        2. タスク分解（AI使用）
        3. タスク書き込み
        """
        logger.info("=" * 60)
        logger.info("🔄 PMサイクル開始（GeminiTaskBreakdown統合版）")
        logger.info("=" * 60)

        # 目標読み込み
        goal = await self.load_project_goal()

        if not goal:
            logger.warning("ℹ️ 処理可能な目標がありません")
            return

        # タスク分解（AI使用）
        tasks = await self.break_down_goal_to_tasks(goal)

        if not tasks:
            logger.warning("⚠️ タスクが生成されませんでした")
            return

        # タスク書き込み
        await self.write_tasks_to_sheet(tasks)

        logger.info("=" * 60)
        logger.info("✅ PMサイクル完了")
        logger.info("=" * 60)


# テスト用のメイン関数
async def test_pm_agent_v31():
    """PMAgentV2のテスト実行"""
    print("=" * 60)
    print("PMAgent テスト実行")
    print("=" * 60)

    try:
        # GoogleSheetsManagerの初期化
        sheets_manager = GoogleSheetsManager()
        print("✅ GoogleSheetsManager 初期化成功")

        # PMAgentV2の初期化
        pm_agent = PMAgent(sheets_manager)
        print("✅ PMAgent 初期化成功")

        # PMサイクル実行
        await pm_agent.run_pm_cycle()

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_pm_agent_v31())

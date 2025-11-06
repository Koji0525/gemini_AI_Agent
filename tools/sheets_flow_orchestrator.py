#!/usr/bin/env python3
"""
🎯 SheetsFlowOrchestrator v2.0
目的: project_goal → pm_tasks → task_execution_log の自動フロー
更新: 2025-11-05 - open_spreadsheet() 統合
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.safe_sheets_wrapper import SafeSheetsWrapper

logger = logging.getLogger(__name__)


class SheetsFlowOrchestrator:
    """スプレッドシート自動フローの統括"""

    def __init__(self, sheets_manager):
        """
        Args:
            sheets_manager: GoogleSheetsManager のインスタンス
        """
        # SafeWrapperで保護
        self.sheets = SafeSheetsWrapper(sheets_manager)
        self.raw_sheets = sheets_manager  # open_spreadsheet用

        # 統計情報
        self.stats = {"goals_processed": 0, "tasks_created": 0, "logs_written": 0, "errors": []}

        # スプレッドシートを開く
        self._initialize_spreadsheet()

    def _initialize_spreadsheet(self):
        """スプレッドシートの初期化"""
        try:
            # 環境変数からSPREADSHEET_IDを取得
            from dotenv import load_dotenv

            load_dotenv()

            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError(
                    "❌ SPREADSHEET_ID が設定されていません\n"
                    "   .env ファイルに SPREADSHEET_ID=your_id を追加してください"
                )

            # スプレッドシートを開く
            self.raw_sheets.open_spreadsheet(spreadsheet_id)
            logger.info(f"✅ スプレッドシート接続成功: {spreadsheet_id[:20]}...")

        except Exception as e:
            logger.error(f"❌ スプレッドシート初期化エラー: {e}")
            self.stats["errors"].append(f"初期化エラー: {e}")
            raise

    def run_full_flow(self) -> Dict:
        """完全フロー実行"""
        logger.info("🚀 スプレッドシート自動フロー開始")

        try:
            # 1. project_goal から目標を読み取り
            goals = self._read_goals()
            if not goals:
                logger.warning("⚠️  project_goal にデータがありません")
                return self.stats

            # 2. 各目標をタスクに分解
            for goal in goals:
                tasks = self._decompose_goal_to_tasks(goal)
                self._write_tasks(tasks)

            # 3. pending タスクを集計
            pending_tasks = self._read_pending_tasks()
            logger.info(f"✅ pending タスク: {len(pending_tasks)}件")

            return self.stats

        except Exception as e:
            logger.error(f"❌ フローエラー: {e}")
            self.stats["errors"].append(str(e))
            return self.stats

    def _read_goals(self) -> List[Dict]:
        """project_goal から目標を読み取り"""
        try:
            # ヘッダー行をスキップしてA2から読み取り
            data = self.sheets.safe_read("project_goal!A2:Z100", default=[])

            goals = []
            for row in data:
                if len(row) >= 2 and row[0]:  # ID と description が必須
                    goals.append(
                        {
                            "goal_id": row[0],
                            "description": row[1] if len(row) > 1 else "",
                            "priority": row[2] if len(row) > 2 else "medium",
                            "status": row[3] if len(row) > 3 else "pending",
                        }
                    )

            self.stats["goals_processed"] = len(goals)
            logger.info(f"✅ 目標読み取り: {len(goals)}件")
            return goals

        except Exception as e:
            logger.error(f"❌ 目標読み取りエラー: {e}")
            self.stats["errors"].append(f"目標読み取りエラー: {e}")
            return []

    def _decompose_goal_to_tasks(self, goal: Dict) -> List[Dict]:
        """目標をタスクに分解"""
        # シンプルな分解ロジック（1目標 = 1タスク）
        task = {
            "task_id": f"T_{goal['goal_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "parent_goal_id": goal["goal_id"],
            "description": goal["description"],
            "required_role": "developer",
            "status": "pending",
            "priority": goal.get("priority", "medium"),
            "estimated_time": "1h",
            "dependencies": "",
            "created_at": datetime.now().isoformat(),
            "batch_id": "",
        }
        return [task]

    def _write_tasks(self, tasks: List[Dict]):
        """pm_tasks にタスクを書き込み"""
        try:
            rows = []
            for task in tasks:
                rows.append(
                    [
                        task["task_id"],
                        task["parent_goal_id"],
                        task["description"],
                        task["required_role"],
                        task["status"],
                        task["priority"],
                        task["estimated_time"],
                        task["dependencies"],
                        task["created_at"],
                        task["batch_id"],
                    ]
                )

            # safe_append で安全に追記
            success = self.sheets.safe_append("pm_tasks", rows)
            if success:
                self.stats["tasks_created"] += len(tasks)
                logger.info(f"✅ タスク書き込み: {len(tasks)}件")
            else:
                self.stats["errors"].append("タスク書き込み失敗")

        except Exception as e:
            logger.error(f"❌ タスク書き込みエラー: {e}")
            self.stats["errors"].append(f"タスク書き込みエラー: {e}")

    def _read_pending_tasks(self) -> List[Dict]:
        """pending タスクを取得"""
        try:
            # pm_tasks のA2から全データ取得
            data = self.sheets.safe_read("pm_tasks!A2:Z1000", default=[])

            pending = []
            for row in data:
                # status カラム（インデックス4）が 'pending'
                if len(row) >= 5 and row[4] == "pending":
                    pending.append({"task_id": row[0], "description": row[2], "status": row[4]})

            return pending

        except Exception as e:
            logger.error(f"❌ pending タスク読み取りエラー: {e}")
            return []


def main():
    """メイン実行"""
    from tools.sheets_manager import GoogleSheetsManager

    try:
        # GoogleSheetsManager 初期化
        sheets = GoogleSheetsManager()

        # Orchestrator 実行
        orchestrator = SheetsFlowOrchestrator(sheets)
        stats = orchestrator.run_full_flow()

        # 結果表示
        print("\n" + "=" * 60)
        print("📊 実行結果")
        print("=" * 60)
        print(f"  目標処理: {stats['goals_processed']}件")
        print(f"  タスク作成: {stats['tasks_created']}件")
        print(f"  ログ記録: {stats['logs_written']}件")

        if stats["errors"]:
            print(f"\n⚠️  エラー: {len(stats['errors'])}件")
            for err in stats["errors"]:
                print(f"    - {err}")
        else:
            print("\n✅ エラーなし")

        print("=" * 60)

    except Exception as e:
        print(f"❌ 致命的エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

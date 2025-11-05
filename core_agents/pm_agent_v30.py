"""
PM Agent v30 - タスク管理エージェント
import文構文エラー修正版
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 標準ライブラリ
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# プロジェクト内モジュール
from tools.sheets_manager import GoogleSheetsManager
from tools.sheets_validator import SheetsValidator
from configuration.spreadsheet_schema import get_column_names


# Phase 3: execution_type判定機能
def determine_execution_type(task: dict) -> str:
    """
    改善版：タスクの実行タイプを判定
    優先順位:
    1. ExecutionType列が設定されている → それを使用
    2. プレフィックス判定（【WP】【設計】など）
    3. 動詞パターン認識
    4. キーワードマッチ（従来方式）
    """
    # 1. ExecutionType列（最優先）
    if "execution_type" in task and task["execution_type"]:
        return task["execution_type"]

    description = task.get("description", "")

    # 2. プレフィックス判定
    if description.startswith("【WP】"):
        return "wordpress"
    elif description.startswith("【設計】"):
        return "design"
    elif description.startswith("【調査】"):
        return "research"
    elif description.startswith("【実装】"):
        return "implementation"

    # 3. 動詞パターン認識
    if any(verb in description for verb in ["投稿", "公開", "更新", "アップロード"]):
        return "wordpress"
    elif any(verb in description for verb in ["設計", "構想", "アーキテクチャ"]):
        return "design"
    elif any(verb in description for verb in ["調査", "分析", "検証"]):
        return "research"
    elif any(verb in description for verb in ["実装", "開発", "コーディング"]):
        return "implementation"

    # 4. キーワードマッチ（従来方式）
    if "WordPress" in description or "WP" in description:
        return "wordpress"
    elif "コード" in description or "プログラム" in description:
        return "implementation"
    elif "設計" in description or "アーキテクチャ" in description:
        return "design"

    return "general"


class PMAgent:
    """プロジェクト管理エージェント"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManagerインスタンス（依存性注入）
        """
        self.sheets = sheets_manager
        self.validator = SheetsValidator(sheets_manager)
        self.logger = logging.getLogger(__name__)

        # カラム名の取得
        self.columns = get_column_names()

    async def create_task(self, task_data: dict) -> dict:
        """
        新規タスク作成

        Args:
            task_data: タスクデータ（description必須）

        Returns:
            作成結果（task_id含む）
        """
        try:
            # 必須項目チェック
            if "description" not in task_data:
                return {"success": False, "error": "description is required"}

            # タスクIDの生成
            task_id = f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # デフォルト値設定
            row_data = {
                "task_id": task_id,
                "parent_goal_id": task_data.get("parent_goal_id", ""),
                "description": task_data["description"],
                "required_role": task_data.get("required_role", "general"),
                "status": "pending",
                "priority": task_data.get("priority", "medium"),
                "estimated_time": task_data.get("estimated_time", 30),
                "dependencies": task_data.get("dependencies", ""),
                "created_at": datetime.now().isoformat(),
                "batch_id": task_data.get("batch_id", ""),
            }

            # スプレッドシートに追加
            self.sheets.append_row("pm_tasks", list(row_data.values()))

            self.logger.info(f"✅ タスク作成成功: {task_id}")
            return {"success": True, "task_id": task_id}

        except Exception as e:
            self.logger.error(f"❌ タスク作成エラー: {e}")
            return {"success": False, "error": str(e)}

    async def get_pending_tasks(self, limit: int = 10) -> list:
        """
        pending状態のタスクを取得

        Args:
            limit: 取得件数上限

        Returns:
            タスクリスト
        """
        try:
            all_tasks = self.sheets.read_sheet("pm_tasks")

            pending_tasks = []
            for row in all_tasks:
                if isinstance(row, list) and len(row) > 4:
                    if row[4] == "pending":  # E列: status
                        task = {
                            "task_id": row[0],
                            "parent_goal_id": row[1] if len(row) > 1 else "",
                            "description": row[2] if len(row) > 2 else "",
                            "required_role": row[3] if len(row) > 3 else "",
                            "status": row[4],
                            "priority": row[5] if len(row) > 5 else "",
                            "estimated_time": int(row[6]) if len(row) > 6 and row[6] else 30,
                            "dependencies": row[7] if len(row) > 7 else "",
                            "created_at": row[8] if len(row) > 8 else "",
                            "batch_id": row[9] if len(row) > 9 else "",
                        }
                        pending_tasks.append(task)

                        if len(pending_tasks) >= limit:
                            break

            return pending_tasks

        except Exception as e:
            self.logger.error(f"❌ pending タスク取得エラー: {e}")
            return []

    async def update_task_status(self, task_id: str, status: str) -> dict:
        """
        タスクステータス更新

        Args:
            task_id: タスクID
            status: 新しいステータス

        Returns:
            更新結果
        """
        try:
            all_tasks = self.sheets.read_sheet("pm_tasks")

            for i, row in enumerate(all_tasks, start=2):
                if len(row) > 0 and row[0] == task_id:
                    # E列（status）を更新
                    self.sheets.update_cell("pm_tasks", f"E{i}", status)

                    self.logger.info(f"✅ タスクステータス更新: {task_id} → {status}")
                    return {"success": True, "task_id": task_id, "status": status}

            return {"success": False, "error": "task_id not found"}

        except Exception as e:
            self.logger.error(f"❌ ステータス更新エラー: {e}")
            return {"success": False, "error": str(e)}


# テスト用
async def test_pm_agent():
    """PMAgentの動作テスト"""
    sheets = GoogleSheetsManager()
    pm = PMAgent(sheets)

    # pendingタスク取得
    tasks = await pm.get_pending_tasks(limit=5)
    print(f"✅ pending タスク: {len(tasks)}件")

    for task in tasks:
        print(f"  - {task['task_id']}: {task['description'][:50]}")


if __name__ == "__main__":
    asyncio.run(test_pm_agent())

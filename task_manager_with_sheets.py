#!/usr/bin/env python3
"""
Google Sheets連携タスク管理システム
スプレッドシートID: 1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskManagerWithSheets:
    """Google Sheets連携タスクマネージャー"""

    def __init__(self):
        # 実際のスプレッドシートID
        self.spreadsheet_id = "1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s"
        self.sheets = None
        self.error_log_path = Path("error_logs")
        self.error_log_path.mkdir(exist_ok=True)

    async def initialize(self):
        """初期化"""
        logger.info("=" * 80)
        logger.info("🔧 タスクマネージャー初期化")
        logger.info("=" * 80)
        logger.info(f"📊 スプレッドシートID: {self.spreadsheet_id}")

        try:
            from tools.sheets_manager import GoogleSheetsManager

            self.sheets = GoogleSheetsManager(spreadsheet_id=self.spreadsheet_id)
            logger.info("✅ Google Sheets接続完了")
            return True
        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            return False

    async def get_pending_tasks(self) -> List[Dict]:
        """pending状態のタスクを取得（E列 = pending）"""
        logger.info("\n📋 pending タスクを検索中...")

        try:
            # sheetsオブジェクトの利用可能なメソッドを確認
            available_methods = [m for m in dir(self.sheets) if not m.startswith("_")]
            logger.info(f"📝 利用可能なメソッド: {available_methods[:10]}...")

            # データ読み取りを試行
            data = None

            if hasattr(self.sheets, "read_range"):
                data = self.sheets.read_range("A2:I1000")
            elif hasattr(self.sheets, "get_all_values"):
                data = self.sheets.get_all_values()
            elif hasattr(self.sheets, "get_data"):
                data = self.sheets.get_data()
            else:
                logger.warning("⚠️ データ読み取りメソッドが見つかりません")
                logger.info("📝 利用可能なメソッド一覧:")
                for method in available_methods:
                    logger.info(f"   - {method}")
                return []

            if not data:
                logger.warning("⚠️ データが取得できませんでした")
                return []

            logger.info(f"✅ {len(data)} 行のデータを取得")

            # pending タスクをフィルター（E列 = status）
            pending_tasks = []
            for i, row in enumerate(data):
                if len(row) >= 5:
                    status = row[4].strip().lower() if row[4] else ""
                    if status == "pending":
                        task = {
                            "row": i + 2,  # スプレッドシートの実際の行番号
                            "task_id": row[0] if len(row) > 0 else "",
                            "parent": row[1] if len(row) > 1 else "",
                            "description": row[2] if len(row) > 2 else "",
                            "required_role": row[3] if len(row) > 3 else "",
                            "status": row[4] if len(row) > 4 else "",
                            "priority": row[5] if len(row) > 5 else "",
                            "estimated_time": row[6] if len(row) > 6 else "",
                            "dependencies": row[7] if len(row) > 7 else "",
                            "created_at": row[8] if len(row) > 8 else "",
                        }
                        pending_tasks.append(task)
                        logger.info(f"   ✓ タスク発見: {task['task_id']} - {task['description'][:50]}...")

            logger.info(f"✅ {len(pending_tasks)} 件のpendingタスクを発見")
            return pending_tasks

        except Exception as e:
            logger.error(f"❌ タスク取得エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return []

    async def update_task_status(self, task: Dict, status: str, result: Dict = None):
        """タスクステータスを更新（E列）"""
        row = task["row"]
        task_id = task["task_id"]

        logger.info(f"📝 タスク {task_id} (行{row}) のステータスを更新: {status}")

        try:
            # E列（5列目）を更新
            if hasattr(self.sheets, "update_cell"):
                self.sheets.update_cell(row=row, col=5, value=status)
            elif hasattr(self.sheets, "update_range"):
                self.sheets.update_range(f"E{row}", [[status]])
            else:
                logger.warning("⚠️ セル更新メソッドが見つかりません")
                return

            # 結果をJ列に記録（オプション）
            if result:
                result_text = json.dumps(result, ensure_ascii=False)[:500]  # 500文字まで
                if hasattr(self.sheets, "update_cell"):
                    self.sheets.update_cell(row=row, col=10, value=result_text)

            logger.info(f"✅ ステータス更新完了: {task_id} → {status}")

        except Exception as e:
            logger.error(f"❌ ステータス更新エラー: {e}")

    async def execute_task(self, task: Dict) -> Dict:
        """タスクを実行"""
        task_id = task["task_id"]
        description = task["description"]
        required_role = task["required_role"]

        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 タスク実行: {task_id}")
        logger.info(f"   説明: {description}")
        logger.info(f"   ロール: {required_role}")
        logger.info(f"{'='*80}")

        try:
            # ロールに応じてタスクを実行
            if required_role == "wp_dev":
                return await self._execute_wordpress_task(task)
            elif required_role == "content":
                return await self._execute_content_task(task)
            elif required_role == "test":
                return await self._execute_test_task(task)
            else:
                logger.warning(f"⚠️ 未対応のロール: {required_role}")
                return {"success": True, "message": f"Role {required_role} not implemented yet", "skipped": True}

        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_wordpress_task(self, task: Dict) -> Dict:
        """WordPressタスクを実行"""
        logger.info("🌐 WordPressタスクを実行...")

        try:
            # create_wordpress_draft.py を呼び出し
            import subprocess

            result = subprocess.run(
                ["python", "create_wordpress_draft.py"], capture_output=True, text=True, timeout=300  # 5分タイムアウト
            )

            if result.returncode == 0:
                logger.info("✅ WordPressタスク完了")
                return {"success": True, "message": "WordPress post created"}
            else:
                logger.error(f"❌ WordPressタスク失敗: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"❌ WordPressタスクエラー: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_content_task(self, task: Dict) -> Dict:
        """コンテンツ作成タスク"""
        logger.info("📝 コンテンツタスク（未実装）")
        return {"success": True, "message": "Content task (not implemented)", "skipped": True}

    async def _execute_test_task(self, task: Dict) -> Dict:
        """テストタスク"""
        logger.info("🧪 テストタスク（未実装）")
        return {"success": True, "message": "Test task (not implemented)", "skipped": True}

    async def run_cycle(self):
        """1サイクル実行"""
        logger.info("\n" + "=" * 80)
        logger.info("🔄 タスク管理サイクル開始")
        logger.info("=" * 80)

        # pending タスクを取得
        pending_tasks = await self.get_pending_tasks()

        if not pending_tasks:
            logger.info("ℹ️ 実行可能なタスクがありません")
            return

        # 優先度順にソート（high > medium > low）
        priority_order = {"high": 3, "medium": 2, "low": 1, "": 0}
        pending_tasks.sort(key=lambda t: priority_order.get(t.get("priority", "").lower(), 0), reverse=True)

        # 各タスクを実行（最大5タスク）
        for task in pending_tasks[:5]:
            result = await self.execute_task(task)

            # ステータス更新
            if result.get("success"):
                if result.get("skipped"):
                    status = "skipped"
                else:
                    status = "complete"
                await self.update_task_status(task, status, result)
                logger.info(f"✅ タスク完了: {task['task_id']}")
            else:
                await self.update_task_status(task, "failed", result)
                logger.error(f"❌ タスク失敗: {task['task_id']}")

                # エラーログ保存
                await self._save_error_log(task, result)

        logger.info("\n" + "=" * 80)
        logger.info("🎉 サイクル完了")
        logger.info("=" * 80)

    async def _save_error_log(self, task: Dict, result: Dict):
        """エラーログを保存"""
        error_file = self.error_log_path / f"task_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(error_file, "w", encoding="utf-8") as f:
            json.dump(
                {"task": task, "result": result, "timestamp": datetime.now().isoformat()},
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(f"📄 エラーログ保存: {error_file}")


async def main():
    manager = TaskManagerWithSheets()

    if await manager.initialize():
        await manager.run_cycle()
    else:
        logger.error("❌ 初期化失敗")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
統合タスクマネージャー v2（修正版）
- pm_tasks シートからタスク取得
- 1回実行して終了（待機なし）
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json

from tools.sheets_manager import GoogleSheetsManager
from scripts.wordpress_task_executor import WordPressTaskExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedTaskManagerV2:
    """統合タスクマネージャー v2"""

    def __init__(self):
        self.spreadsheet_id = "1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s"
        self.sheet_name = "pm_tasks"
        self.sheets = None
        self.wp_executor = None
        self.error_log_path = Path("error_logs")
        self.error_log_path.mkdir(exist_ok=True)

    async def initialize(self):
        """初期化"""
        logger.info("=" * 80)
        logger.info("🚀 統合タスクマネージャー v2 起動")
        logger.info("=" * 80)
        logger.info(f"📊 スプレッドシートID: {self.spreadsheet_id}")
        logger.info(f"📄 シート名: {self.sheet_name}")

        try:
            # Google Sheets接続
            logger.info("📊 Google Sheets 接続中...")
            self.sheets = GoogleSheetsManager(spreadsheet_id=self.spreadsheet_id)
            logger.info("✅ Google Sheets 接続完了")

            # WordPress エグゼキューター初期化
            logger.info("🌐 WordPress エグゼキューター 初期化中...")
            self.wp_executor = WordPressTaskExecutor()
            if not await self.wp_executor.initialize():
                return False
            logger.info("✅ WordPress エグゼキューター 初期化完了")

            return True

        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    async def get_pending_tasks(self):
        """pending タスクを取得"""
        logger.info("\n📋 pm_tasks シートから pending タスクを取得中...")

        try:
            # load_tasks_from_sheet メソッドを使用（awaitを追加）
            if not hasattr(self.sheets, "load_tasks_from_sheet"):
                logger.error("❌ load_tasks_from_sheet メソッドが見つかりません")
                return []

            # 🔧 FIX: await を追加
            all_tasks = await self.sheets.load_tasks_from_sheet()

            if not all_tasks:
                logger.warning("⚠️ タスクが取得できませんでした")
                return []

            logger.info(f"✅ {len(all_tasks)} 件のタスクを取得")

            # pending タスクをフィルター
            pending_tasks = []
            for task in all_tasks:
                status = task.get("status", "").strip().lower()

                if status == "pending":
                    pending_tasks.append(task)
                    task_id = task.get("task_id", "unknown")
                    description = task.get("description", "")[:50]
                    priority = task.get("priority", "N/A")
                    logger.info(f"   ✓ [{priority}] {task_id}: {description}...")

            logger.info(f"✅ {len(pending_tasks)} 件の pending タスク")
            return pending_tasks

        except Exception as e:
            logger.error(f"❌ タスク取得エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return []

    async def update_status(self, task: dict, new_status: str):
        """ステータス更新"""
        task_id = task.get("task_id", "unknown")

        logger.info(f"📝 ステータス更新: {task_id} → {new_status}")

        try:
            # update_task_status メソッドを使用
            if hasattr(self.sheets, "update_task_status"):
                # 🔧 FIX: メソッドが async かどうか確認
                result = self.sheets.update_task_status(task_id=task_id, status=new_status)

                # もし coroutine なら await
                if asyncio.iscoroutine(result):
                    await result

                logger.info(f"✅ ステータス更新完了: {task_id} → {new_status}")
            else:
                logger.warning("⚠️ update_task_status メソッドが見つかりません")

        except Exception as e:
            logger.error(f"❌ ステータス更新エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())

    async def execute_task(self, task: dict):
        """タスク実行"""
        task_id = task.get("task_id", "unknown")
        description = task.get("description", "")
        role = task.get("required_role", "")

        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 タスク実行: {task_id}")
        logger.info(f"   説明: {description}")
        logger.info(f"   ロール: {role}")
        logger.info(f"{'='*80}")

        try:
            if role == "wp_dev":
                # WordPress記事作成
                wp_task = {
                    "title": description[:200],
                    "content": f"""
<h2>{description}</h2>

<p>このタスクは自動実行システムによって処理されました。</p>

<h3>タスク情報</h3>
<ul>
    <li><strong>タスクID:</strong> {task_id}</li>
    <li><strong>実行日時:</strong> {datetime.now().strftime("%Y年%m月%d日 %H時%M分")}</li>
    <li><strong>ロール:</strong> {role}</li>
    <li><strong>優先度:</strong> {task.get('priority', 'N/A')}</li>
</ul>

<p>詳細: {description}</p>
                    """,
                    "post_status": "draft",
                    "category": "Auto Generated",
                    "tags": ["自動生成", task_id],
                }
                result = await self.wp_executor.create_draft(wp_task)

            else:
                logger.warning(f"⚠️ 未対応ロール: {role}")
                result = {"success": True, "skipped": True, "message": f"Role {role} not supported"}

            return result

        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    async def run_cycle(self):
        """1サイクル実行（1回で終了）"""
        logger.info("\n" + "=" * 80)
        logger.info("🔄 タスク実行サイクル開始")
        logger.info("=" * 80)

        # pending タスクを取得
        pending_tasks = await self.get_pending_tasks()

        if not pending_tasks:
            logger.info("ℹ️ 実行可能なタスクがありません")
            return

        # 優先度順にソート
        priority_map = {"high": 3, "medium": 2, "low": 1, "": 0}
        pending_tasks.sort(key=lambda t: priority_map.get(t.get("priority", "").lower(), 0), reverse=True)

        # タスク実行（最大5タスク）
        max_tasks = 5
        logger.info(f"📊 最大 {max_tasks} タスクを実行します")

        executed_count = 0
        success_count = 0
        failed_count = 0
        skipped_count = 0

        for task in pending_tasks[:max_tasks]:
            result = await self.execute_task(task)
            executed_count += 1

            # ステータス更新
            if result.get("success"):
                if result.get("skipped"):
                    await self.update_status(task, "skipped")
                    skipped_count += 1
                    logger.info(f"⏭️ タスクスキップ: {task['task_id']}")
                else:
                    await self.update_status(task, "complete")
                    success_count += 1
                    logger.info(f"✅ タスク完了: {task['task_id']}")
            else:
                await self.update_status(task, "failed")
                failed_count += 1
                logger.error(f"❌ タスク失敗: {task['task_id']}")

                # エラーログ保存
                self._save_error_log(task, result)

        logger.info("\n" + "=" * 80)
        logger.info("🎉 サイクル完了")
        logger.info("=" * 80)
        logger.info(f"📊 実行結果:")
        logger.info(f"   ✅ 成功: {success_count}")
        logger.info(f"   ❌ 失敗: {failed_count}")
        logger.info(f"   ⏭️ スキップ: {skipped_count}")
        logger.info(f"   📝 合計: {executed_count}")
        logger.info("=" * 80)

    def _save_error_log(self, task: dict, result: dict):
        """エラーログ保存"""
        task_id = task.get("task_id", "unknown")
        error_file = self.error_log_path / f"task_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(error_file, "w", encoding="utf-8") as f:
            json.dump(
                {"task": task, "result": result, "timestamp": datetime.now().isoformat()},
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(f"📄 エラーログ保存: {error_file}")

    async def cleanup(self):
        """クリーンアップ"""
        if self.wp_executor:
            await self.wp_executor.cleanup()


async def main():
    """メイン実行（1回で終了）"""
    manager = IntegratedTaskManagerV2()

    if await manager.initialize():
        await manager.run_cycle()
    else:
        logger.error("❌ 初期化失敗")

    await manager.cleanup()

    logger.info("\n✅ 実行完了 - プログラム終了")


if __name__ == "__main__":
    asyncio.run(main())

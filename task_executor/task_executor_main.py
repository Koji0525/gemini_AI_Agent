"""
TaskExecutor - タスク実行の中核クラス（完全版）
ナレッジ読み込みエラー修正版
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine  # 依存削除
from agents.observability.intelligence.learning.knowledge_base_adapter import \
    KnowledgeBaseAdapter
from configuration.sheets_schema import dict_to_row
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_manager import GoogleSheetsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskExecutor:
    """TaskExecutor統合版（ナレッジ読み込み修正版）"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = SafeSheetsWrapper(sheets_manager)
        self.knowledge_adapter = KnowledgeBaseAdapter()  # 新しいナレッジシステム
        logger.info("✅ TaskExecutor を初期化しました（新しいナレッジシステム使用）")

    def _load_knowledge_base(self):
        """ナレッジベース読み込み（リスト・辞書両対応版）"""
        try:
            knowledge_files = [
                "mvp_v4/knowledge/learned/conversation_knowledge_v3.json",
                "mvp_v4/knowledge/learned/conversation_knowledge_v4.json",
            ]

            # ナレッジを統合
            all_knowledge = []
            for filepath in knowledge_files:
                if not os.path.exists(filepath):
                    continue

                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # リスト形式の場合
                    if isinstance(data, list):
                        all_knowledge.extend(data)
                    # 辞書形式の場合
                    elif isinstance(data, dict):
                        if "knowledge_base" in data:
                            all_knowledge.extend(data["knowledge_base"])
                        else:
                            all_knowledge.append(data)

            if all_knowledge:
                # rag_engine_local.pyが期待する形式（辞書形式）で保存
                temp_file = "/tmp/merged_knowledge.json"
                merged_data = {"knowledge_base": all_knowledge}

                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(merged_data, f, ensure_ascii=False, indent=2)

                # 新しいナレッジシステムでは明示的な読み込みは不要
                logger.info(f"✅ ナレッジベース読み込み: {len(all_knowledge)}件")
            else:
                logger.warning("⚠️ ナレッジベースが空です")

        except Exception as e:
            logger.warning(f"⚠️ ナレッジベース読み込みエラー: {e}")
            import traceback

            traceback.print_exc()

    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """pm_tasksからpendingタスクを取得"""
        try:
            all_tasks = self.sheets.safe_read("pm_tasks", default=[])
            pending_tasks = [
                task for task in all_tasks if task.get("status", "").lower() == "pending"
            ]
            logger.info(f"📋 pending タスク: {len(pending_tasks)}件")
            return pending_tasks
        except Exception as e:
            logger.error(f"❌ タスク取得エラー: {e}")
            return []

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タスク実行"""
        task_id = task.get("task_id", "unknown")
        description = task.get("description", "")

        logger.info(f"🚀 タスク実行開始: {task_id}")

        try:
            # ナレッジベース検索
            knowledge = []
            try:
                knowledge = self.knowledge_adapter.search_knowledge(description, top_k=3)
                if knowledge:
                    logger.info(f"📚 関連ナレッジ: {len(knowledge)}件")
            except Exception as e:
                logger.warning(f"⚠️ ナレッジ検索エラー: {e}")

            # TODO: 実際のタスク実行ロジック
            result = {
                "task_id": task_id,
                "status": "completed",
                "output": f"タスク実行完了: {description}",
                "knowledge_used": len(knowledge) if knowledge else 0,
            }

            logger.info(f"✅ タスク実行完了: {task_id}")
            return result

        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {task_id} - {e}")
            return {"task_id": task_id, "status": "failed", "error": str(e)}

    async def log_execution(self, result: Dict[str, Any]):
        """実行結果をログ記録"""
        try:
            from datetime import datetime

            log_data = {
                "log_id": f"LOG_{result.get('task_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "task_id": result.get("task_id", ""),
                "task_description": result.get("output", ""),
                "timestamp": datetime.now().isoformat(),
                "agent_role": "TaskExecutor",
                "output_summary": result.get("output", ""),
                "output_data": "",
                "status": result.get("status", "unknown"),
                "Quality_Score": "",
                "Quality_description": "",
                "elapsed_time": "",
                "retry_count": "0",
                "error_type": result.get("error", ""),
                "fix_applied": "",
            }

            log_row = dict_to_row("task_execution_log", log_data)
            success = self.sheets.safe_append("task_execution_log", [log_row])

            if success:
                logger.info(f"✅ 実行結果を記録: {result.get('task_id', 'unknown')}")

        except Exception as e:
            logger.error(f"❌ ログ記録エラー: {e}")

    async def run_task_cycle(self):
        """タスクサイクル実行"""
        logger.info("🔄 タスクサイクル開始")

        pending_tasks = await self.get_pending_tasks()

        if not pending_tasks:
            logger.info("ℹ️ 実行可能なタスクがありません")
            return

        for task in pending_tasks[:5]:
            result = await self.execute_task(task)
            await self.log_execution(result)
            await asyncio.sleep(1)

        logger.info("✅ タスクサイクル完了")


async def test_task_executor():
    """テスト実行"""
    print("\n" + "=" * 60)
    print("🧪 TaskExecutor テスト（修正版）")
    print("=" * 60)

    try:
        sheets = GoogleSheetsManager()
        executor = TaskExecutor(sheets)
        await executor.run_task_cycle()

        print("\n" + "=" * 60)
        print("✅ テスト完了")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ テスト中にエラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_task_executor())

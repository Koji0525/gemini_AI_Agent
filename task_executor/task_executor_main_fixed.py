"""
TaskExecutor v3.1 - pending タスク検出ロジック修正版
実スプレッドシート構造に完全対応
"""

import asyncio
import time
import logging
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

# プロジェクトルートをPYTHONPATHに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_manager import GoogleSheetsManager

# ナレッジシステムは条件付きインポート
try:
    from knowledge_system.core_agents.knowledge_manager import KnowledgeManager

    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False
    print("⚠️ KnowledgeManager 未利用（オプション機能）")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskExecutor:
    """
    タスク実行エンジン v3.1

    修正点:
    - 実スプレッドシート構造に対応
    - 列インデックスを動的に検出
    - デバッグログ強化
    """

    def __init__(self, sheets_manager: GoogleSheetsManager):
        """
        初期化（運用ルール8: 依存性注入）

        Args:
            sheets_manager: GoogleSheetsManager インスタンス（外部から注入）
        """
        self.sheets = SafeSheetsWrapper(sheets_manager)

        # スプレッドシート構造のキャッシュ
        self.column_map = None
        self._init_column_map()

        # KnowledgeManager の初期化（オプション）
        if KNOWLEDGE_AVAILABLE:
            try:
                self.knowledge_manager = KnowledgeManager()
                logger.info("✅ KnowledgeManager 統合成功")
            except Exception as e:
                logger.warning(f"⚠️ KnowledgeManager 初期化失敗: {e}")
                self.knowledge_manager = None
        else:
            self.knowledge_manager = None

        self.execution_log = []
        logger.info("✅ TaskExecutor v3.1 初期化完了")

    def _init_column_map(self):
        """
        スプレッドシートの列構造を動的に検出
        """
        try:
            # ヘッダー行を取得
            headers = self.sheets.safe_read("pm_tasks!A1:Z1", default=[])

            if headers and len(headers) > 0:
                header_row = headers[0]

                # 列名 → インデックスのマッピング
                self.column_map = {}
                for i, header in enumerate(header_row):
                    header_lower = str(header).strip().lower()
                    self.column_map[header_lower] = i

                logger.info(f"✅ 列構造検出成功: {list(self.column_map.keys())}")

                # 必須列の確認
                required_cols = ["task_id", "description", "status"]
                missing = [col for col in required_cols if col not in self.column_map]
                if missing:
                    logger.warning(f"⚠️ 必須列が見つかりません: {missing}")
            else:
                logger.warning("⚠️ ヘッダー行が取得できません。デフォルト構造を使用")
                # デフォルト構造（画像から推測）
                self.column_map = {
                    "task_id": 0,
                    "parent_goal_id": 1,
                    "description": 2,
                    "required_role": 3,
                    "status": 4,  # E列
                    "priority": 5,
                    "estimated_time": 6,
                    "dependencies": 7,
                    "created_at": 8,
                    "batch_id": 9,
                    "detail_file_path": 10,
                }
                logger.info("ℹ️ デフォルト列構造を使用")

        except Exception as e:
            logger.error(f"❌ 列構造検出エラー: {e}")
            # フォールバック
            self.column_map = {"task_id": 0, "description": 2, "status": 4, "priority": 5}

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク実行（メインメソッド）
        """
        task_id = task.get("task_id", f"TASK_{int(time.time())}")
        start_time = time.time()

        logger.info(f"🚀 タスク実行開始: {task.get('title', task.get('description', 'Untitled'))}")

        result = {
            "success": False,
            "task_id": task_id,
            "result": None,
            "elapsed_time": 0,
            "knowledge_used": False,
            "error": None,
        }

        try:
            # STEP 1: ナレッジベース検索（実行前）
            knowledge_results = await self._search_knowledge(task)
            if knowledge_results:
                result["knowledge_used"] = True
                logger.info(f"📚 類似事例発見: {len(knowledge_results)}件")

            # STEP 2: タスク実行（シミュレーション）
            await asyncio.sleep(0.5)

            execution_result = {
                "status": "completed",
                "output": f"タスク '{task.get('description', task.get('title', 'Unknown'))}' を実行しました",
                "knowledge_applied": len(knowledge_results) if knowledge_results else 0,
            }

            result["success"] = True
            result["result"] = execution_result

            logger.info("✅ タスク実行成功")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ タスク実行エラー: {e}")

        finally:
            # STEP 3: 実行時間計測
            result["elapsed_time"] = time.time() - start_time

            # STEP 4: 実行ログに記録
            self.execution_log.append(result)

            # STEP 5: task_execution_log シートに書き込み
            await self._record_to_sheet(task, result)

        return result

    async def _search_knowledge(self, task: Dict[str, Any]) -> List[Dict]:
        """ナレッジベース検索（内部メソッド）"""
        if not self.knowledge_manager:
            return []

        try:
            query = task.get("description", task.get("title", ""))

            if hasattr(self.knowledge_manager, "search_knowledge"):
                results = self.knowledge_manager.search_knowledge(query, limit=5)
            else:
                logger.warning("⚠️ KnowledgeManager に search_knowledge メソッドが見つかりません")
                return []

            return results if results else []

        except Exception as e:
            logger.warning(f"⚠️ ナレッジ検索エラー: {e}")
            return []

    async def _record_to_sheet(self, task: Dict[str, Any], result: Dict[str, Any]):
        """実行結果を task_execution_log シートに記録"""
        try:
            log_entry = [
                result["task_id"],
                task.get("description", task.get("title", "Untitled")),
                "success" if result["success"] else "failed",
                str(result.get("result", {})),
                f"{result['elapsed_time']:.2f}秒",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "✓" if result["knowledge_used"] else "",
                result.get("error", ""),
            ]

            success = self.sheets.safe_append("task_execution_log", [log_entry])

            if success:
                logger.info("📝 実行ログ記録成功")
            else:
                logger.warning("⚠️ 実行ログ記録失敗")

        except Exception as e:
            logger.error(f"❌ 実行ログ記録エラー: {e}")

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        pending タスクの取得（修正版）

        Returns:
            pending 状態のタスクリスト
        """
        try:
            # データ行のみ取得（A2:Z100）
            tasks = self.sheets.safe_read("pm_tasks!A2:Z100", default=[])

            logger.info(f"📊 取得した全行数: {len(tasks)}")

            if not self.column_map:
                logger.error("❌ 列構造が初期化されていません")
                return []

            # status列のインデックス
            status_idx = self.column_map.get("status")
            if status_idx is None:
                logger.error("❌ status列が見つかりません")
                logger.info(f"利用可能な列: {list(self.column_map.keys())}")
                return []

            logger.info(f"�� status列: インデックス{status_idx}（列{chr(65+status_idx)}）")

            # pending タスクのフィルタ
            pending_tasks = []
            for row_idx, row in enumerate(tasks, start=2):
                if len(row) > status_idx:
                    status_value = str(row[status_idx]).strip().lower()

                    # デバッグログ（最初の5行のみ）
                    if row_idx <= 6:
                        logger.info(
                            f"  行{row_idx}: status='{status_value}' (元: '{row[status_idx]}')"
                        )

                    if status_value == "pending":
                        task_dict = {
                            "row_number": row_idx,
                            "task_id": (
                                row[self.column_map.get("task_id", 0)]
                                if len(row) > self.column_map.get("task_id", 0)
                                else ""
                            ),
                            "description": (
                                row[self.column_map.get("description", 2)]
                                if len(row) > self.column_map.get("description", 2)
                                else ""
                            ),
                            "status": row[status_idx],
                            "priority": (
                                row[self.column_map.get("priority", 5)]
                                if len(row) > self.column_map.get("priority", 5)
                                else ""
                            ),
                            "required_role": (
                                row[self.column_map.get("required_role", 3)]
                                if len(row) > self.column_map.get("required_role", 3)
                                else ""
                            ),
                        }
                        pending_tasks.append(task_dict)

                        # 最初の3件のみ詳細ログ
                        if len(pending_tasks) <= 3:
                            logger.info(
                                f"  ✅ pending タスク発見: {task_dict['description'][:50]}..."
                            )

            logger.info(f"📋 pending タスク: {len(pending_tasks)}件")
            return pending_tasks

        except Exception as e:
            logger.error(f"❌ タスク取得エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    def get_execution_stats(self) -> Dict[str, Any]:
        """実行統計の取得"""
        if not self.execution_log:
            return {
                "total_tasks": 0,
                "success_rate": 0,
                "avg_elapsed_time": 0,
                "knowledge_usage_rate": 0,
            }

        total = len(self.execution_log)
        success = sum(1 for log in self.execution_log if log["success"])
        knowledge_used = sum(1 for log in self.execution_log if log["knowledge_used"])
        total_time = sum(log["elapsed_time"] for log in self.execution_log)

        return {
            "total_tasks": total,
            "success_rate": (success / total) * 100,
            "avg_elapsed_time": total_time / total,
            "knowledge_usage_rate": (knowledge_used / total) * 100,
        }


# テスト用メイン関数
async def test_task_executor():
    """TaskExecutor v3.1 の動作確認"""
    print("🧪 TaskExecutor v3.1 テスト開始\n")

    sheets = GoogleSheetsManager()
    executor = TaskExecutor(sheets_manager=sheets)

    # pending タスク取得テスト
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📋 pending タスク取得テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    pending = executor.get_pending_tasks()

    print(f"\n取得結果: {len(pending)}件")

    if pending:
        print("\n最初の3件:")
        for task in pending[:3]:
            print(f"  - {task['description'][:60]}...")
            print(f"    優先度: {task['priority']}")
            print(f"    担当: {task['required_role']}")
    else:
        print("⚠️ pending タスクが見つかりません")


if __name__ == "__main__":
    asyncio.run(test_task_executor())

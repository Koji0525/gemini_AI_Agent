"""
ナレッジベース統合版TaskExecutor v0.1
- タスク実行時間の計測
- リトライ回数の記録
- ナレッジベースからの事前検索
"""

import time
import asyncio
from datetime import datetime
from typing import Dict, Any
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, "/workspaces/gemini_AI_Agent")


class KBIntegratedTaskExecutor:
    """ナレッジベース統合版タスクエグゼキューター"""

    def __init__(self, sheets_manager, browser_controller=None):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            browser_controller: BrowserController インスタンス（オプション）
        """
        self.sheets = sheets_manager
        self.browser = browser_controller

        # ナレッジ検索エンジンの初期化（存在する場合）
        self.kb_engine = None
        try:
            from knowledge_search_engine import KnowledgeSearchEngine

            self.kb_engine = KnowledgeSearchEngine(sheets_manager)
            print("✅ ナレッジ検索エンジンを初期化しました")
        except ImportError:
            print("ℹ️ ナレッジ検索エンジンが見つかりません（スキップ）")

    async def execute_task_with_measurement(
        self, task: Dict[str, Any], retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        タスクを実行し、計測情報を記録

        Args:
            task: タスク情報
            retry_count: 現在のリトライ回数

        Returns:
            実行結果と計測情報
        """
        task_id = task.get("task_id", "unknown")
        task_name = task.get("task_name", "unknown")
        task_type = task.get("task_type", "general")

        print(f"\n{'='*60}")
        print(f"🎯 タスク実行開始: {task_name}")
        print(f"{'='*60}")

        # STEP 1: ナレッジベース検索
        knowledge_result = None
        if self.kb_engine:
            print("🔍 ナレッジベース検索中...")
            try:
                knowledge_result = await self.kb_engine.search(
                    task_description=task.get("task_description", ""), task_type=task_type
                )

                if knowledge_result and knowledge_result.get("found"):
                    print(f"✅ ナレッジ発見: {knowledge_result.get('message', '')}")
                    task["kb_approach"] = knowledge_result.get("primary_approach", {}).get(
                        "best_practice"
                    )
                    task["expected_success_rate"] = knowledge_result.get(
                        "primary_approach", {}
                    ).get("success_rate", 0)
                else:
                    print("ℹ️ 該当するナレッジが見つかりませんでした")
            except Exception as e:
                print(f"⚠️ ナレッジ検索エラー（スキップ）: {e}")

        # STEP 2: タスク実行（時間計測）
        start_time = time.time()
        error_type = None
        fix_applied = False
        result = {"status": "pending"}

        try:
            print(f"⏱️ 実行開始: {datetime.now().strftime('%H:%M:%S')}")

            # 実際のタスク実行ロジック（簡易版）
            # TODO: 実際のエージェント呼び出しに置き換え
            await asyncio.sleep(1)  # シミュレーション

            result = {
                "status": "completed",
                "task_id": task_id,
                "message": f"{task_name}を完了しました",
            }

            print(f"✅ 実行成功")

        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ 実行エラー: {error_type} - {str(e)}")

            result = {
                "status": "failed",
                "task_id": task_id,
                "error": str(e),
                "error_type": error_type,
            }

        # STEP 3: 実行時間の計算
        elapsed_time = round(time.time() - start_time, 2)
        print(f"⏱️ 実行時間: {elapsed_time}秒")

        # STEP 4: 計測情報を結果に追加
        result["measurement"] = {
            "elapsed_time": elapsed_time,
            "retry_count": retry_count,
            "error_type": error_type,
            "fix_applied": fix_applied,
            "knowledge_used": bool(knowledge_result and knowledge_result.get("found")),
        }

        # STEP 5: task_execution_logに記録
        await self._save_execution_log(task, result)

        print(f"{'='*60}")
        print(f"✅ タスク実行完了: {task_name}")
        print(f"{'='*60}\n")

        return result

    async def _save_execution_log(self, task: Dict[str, Any], result: Dict[str, Any]):
        """実行ログをスプレッドシートに保存"""
        try:
            measurement = result.get("measurement", {})

            log_row = [
                task.get("task_id", ""),
                task.get("task_name", ""),
                task.get("task_type", ""),
                task.get("task_description", ""),
                result.get("status", ""),
                datetime.now().isoformat(),
                "",  # assigned_agent
                "",  # execution_result
                0,  # quality_score（後で評価）
                "",  # notes
                measurement.get("elapsed_time", 0),
                measurement.get("retry_count", 0),
                measurement.get("error_type", ""),
                "TRUE" if measurement.get("fix_applied") else "FALSE",
            ]

            self.sheets.append_row("task_execution_log", log_row)
            print("📝 実行ログを保存しました")

        except Exception as e:
            print(f"⚠️ ログ保存エラー: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# デモ実行スクリプト
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def demo_execution():
    """デモ実行"""
    from browser_control.sheets_manager import GoogleSheetsManager

    print("\n" + "=" * 80)
    print("🎬 KB統合版TaskExecutor デモ")
    print("=" * 80 + "\n")

    # 初期化
    sheets = GoogleSheetsManager()
    executor = KBIntegratedTaskExecutor(sheets)

    # テストタスク
    test_tasks = [
        {
            "task_id": "demo_001",
            "task_name": "WordPressに記事を投稿",
            "task_type": "wordpress",
            "task_description": "ブログ記事を作成してWordPressに投稿する",
        },
        {
            "task_id": "demo_002",
            "task_name": "デザイン案を作成",
            "task_type": "design",
            "task_description": "ランディングページのデザイン案を3つ作成",
        },
    ]

    # 実行
    for task in test_tasks:
        result = await executor.execute_task_with_measurement(task)
        print(f"結果: {result['status']}")
        await asyncio.sleep(1)

    print("\n" + "=" * 80)
    print("✅ デモ完了")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(demo_execution())

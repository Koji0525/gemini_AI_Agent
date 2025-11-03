"""
🔄 Quality Feedback Loop
品質スコアに基づく自動再実行管理システム

【機能】
- 品質スコア7点未満のタスクを自動再実行
- Gemini APIで改善案を生成（5秒以内）
- 4段階の品質判定と対応戦略

【判定基準】
- 9-10点: 即採用
- 7-8点: 条件付き採用
- 5-6点: 改善案生成 + 再実行
- 4点以下: 代替アプローチ生成 + 再実行

作成日: 2025-11-03
バージョン: v1.0
"""

import logging
import time
from typing import Dict
from datetime import datetime

# Gemini API（環境変数から設定を読み込む）
import google.generativeai as genai
from configuration.config_loader import load_config

logger = logging.getLogger(__name__)


class QualityFeedbackLoop:
    """品質スコアに基づく自動再実行管理"""

    def __init__(self, sheets_manager, task_executor):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            task_executor: TaskExecutor インスタンス
        """
        self.sheets = sheets_manager
        self.executor = task_executor

        # Gemini API設定
        config = load_config()
        genai.configure(api_key=config["gemini_api_key"])
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # 統計情報
        self.stats = {
            "accepted": 0,  # 即採用
            "accepted_with_notes": 0,  # 条件付き採用
            "retry_improvement": 0,  # 改善案で再実行
            "retry_alternative": 0,  # 代替案で再実行
            "total_processed": 0,
        }

        logger.info("✅ QualityFeedbackLoop初期化完了")

    async def process_task_result(self, task: Dict, result: Dict) -> Dict:
        """
        タスク結果を品質評価して適切に処理

        Args:
            task: タスク情報
            result: 実行結果（quality_score含む）

        Returns:
            処理結果（action, reason, plan等）
        """
        quality_score = result.get("quality_score", 0)
        task_name = task.get("task_name", "Unknown")

        logger.info(f"🔍 品質評価: {task_name} = {quality_score}点")

        self.stats["total_processed"] += 1

        # CASE 1: 高品質（9-10点）→ 即採用
        if quality_score >= 9:
            await self._mark_as_completed(task, result)
            self.stats["accepted"] += 1

            logger.info(f"✅ 即採用: {task_name} ({quality_score}点)")
            return {"action": "accepted", "reason": "high_quality", "score": quality_score}

        # CASE 2: 合格（7-8点）→ 条件付き採用
        elif quality_score >= 7:
            await self._mark_as_completed(task, result)
            await self._record_improvement_note(task, result)
            self.stats["accepted_with_notes"] += 1

            logger.info(f"✅ 条件付き採用: {task_name} ({quality_score}点)")
            return {"action": "accepted_with_notes", "reason": "acceptable", "score": quality_score}

        # CASE 3: 要改善（5-6点）→ 改善案生成 + 再実行
        elif quality_score >= 5:
            improvement_plan = await self._generate_improvement(task, result)
            await self._create_retry_task(task, improvement_plan, "improvement")
            self.stats["retry_improvement"] += 1

            logger.warning(f"⚠️  改善再実行: {task_name} ({quality_score}点)")
            return {
                "action": "retry_with_improvement",
                "plan": improvement_plan,
                "score": quality_score,
            }

        # CASE 4: 不合格（4点以下）→ 代替アプローチ
        else:
            alternative = await self._generate_alternative(task, result)
            await self._create_retry_task(task, alternative, "alternative")
            self.stats["retry_alternative"] += 1

            logger.error(f"❌ 代替案再実行: {task_name} ({quality_score}点)")
            return {
                "action": "retry_with_alternative",
                "approach": alternative,
                "score": quality_score,
            }

    async def _mark_as_completed(self, task: Dict, result: Dict) -> None:
        """タスクを完了状態に更新"""
        try:
            # task_execution_logに完了を記録
            self.sheets.append_rows(
                "task_execution_log",
                [
                    [
                        datetime.now().isoformat(),
                        task.get("task_id"),
                        task.get("task_name"),
                        "completed",
                        result.get("output", ""),
                        result.get("quality_score", 0),
                        result.get("elapsed_time", 0),
                        0,  # retry_count
                        None,  # error_type
                        False,  # fix_applied
                    ]
                ],
            )

            logger.info(f"✅ 完了記録: {task.get('task_name')}")

        except Exception as e:
            logger.error(f"❌ 完了記録エラー: {str(e)}")

    async def _record_improvement_note(self, task: Dict, result: Dict) -> None:
        """改善提案をナレッジベースに記録"""
        try:
            note = f"品質改善の余地あり: {task.get('task_name')} (スコア: {result.get('quality_score')})"
            self.sheets.append_rows(
                "knowledge_base",
                [
                    [
                        datetime.now().isoformat(),
                        "improvement_note",
                        task.get("task_name"),
                        note,
                        result.get("quality_score"),
                        "pending_improvement",
                    ]
                ],
            )
            logger.info(f"📝 改善メモ記録: {task.get('task_name')}")
        except Exception as e:
            logger.error(f"❌ 改善メモエラー: {str(e)}")

    async def _generate_improvement(self, task: Dict, result: Dict) -> str:
        """Gemini APIを使用して改善案を生成（5秒以内）"""
        try:
            start_time = time.time()

            prompt = f"""
タスク: {task.get('task_name')}
結果: {result.get('output', 'N/A')}
品質スコア: {result.get('quality_score')}点

このタスクを改善するための具体的な提案を3つ、簡潔に挙げてください。
各提案は1-2文で記述してください。
"""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 300,
                    "temperature": 0.7,
                },
            )

            elapsed = time.time() - start_time
            improvement_text = response.text.strip()

            logger.info(f"💡 改善案生成完了 ({elapsed:.2f}秒)")
            return improvement_text

        except Exception as e:
            logger.error(f"❌ 改善案生成エラー: {str(e)}")
            return "改善案生成に失敗しました。手動で確認してください。"

    async def _generate_alternative(self, task: Dict, result: Dict) -> str:
        """Gemini APIを使用して代替アプローチを生成"""
        try:
            start_time = time.time()

            prompt = f"""
タスク: {task.get('task_name')}
失敗した結果: {result.get('output', 'N/A')}
品質スコア: {result.get('quality_score')}点（不合格）

このタスクを達成するための**全く異なるアプローチ**を2つ提案してください。
元の方法とは別の手法を提案してください。
"""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 400,
                    "temperature": 0.9,  # 創造性を高める
                },
            )

            elapsed = time.time() - start_time
            alternative_text = response.text.strip()

            logger.info(f"💡 代替案生成完了 ({elapsed:.2f}秒)")
            return alternative_text

        except Exception as e:
            logger.error(f"❌ 代替案生成エラー: {str(e)}")
            return "代替案生成に失敗しました。手動で確認してください。"

    async def _create_retry_task(
        self, original_task: Dict, improvement_plan: str, retry_type: str
    ) -> None:
        """再実行タスクを登録"""
        try:
            retry_task = {
                "task_name": f"[RETRY-{retry_type.upper()}] {original_task.get('task_name')}",
                "description": f"{original_task.get('description', '')}\n\n改善案:\n{improvement_plan}",
                "priority": "high",  # 再実行は高優先度
                "retry_count": original_task.get("retry_count", 0) + 1,
                "original_task_id": original_task.get("task_id"),
                "improvement_plan": improvement_plan,
            }

            # tasks シートに登録
            self.sheets.append_rows(
                "pm_tasks",
                [
                    [
                        datetime.now().isoformat(),
                        retry_task["task_name"],
                        retry_task["description"],
                        "pending",
                        retry_task["priority"],
                        retry_task["retry_count"],
                    ],
                ],
            )

            logger.info(f"🔄 再実行タスク登録: {retry_task['task_name']}")

        except Exception as e:
            logger.error(f"❌ 再実行タスク登録エラー: {str(e)}")

    def get_stats(self) -> Dict:
        """統計情報を取得"""
        return {
            **self.stats,
            "retry_rate": (
                (self.stats["retry_improvement"] + self.stats["retry_alternative"])
                / max(self.stats["total_processed"], 1)
                * 100
            ),
        }

    def print_stats(self) -> None:
        """統計情報を表示"""
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("📊 Quality Feedback Loop 統計")
        print("=" * 60)
        print(f"処理総数: {stats['total_processed']}件")
        print(f"  ✅ 即採用: {stats['accepted']}件")
        print(f"  ✅ 条件付き採用: {stats['accepted_with_notes']}件")
        print(f"  🔄 改善再実行: {stats['retry_improvement']}件")
        print(f"  🔄 代替再実行: {stats['retry_alternative']}件")
        print(f"再実行率: {stats['retry_rate']:.1f}%")
        print("=" * 60 + "\n")


# ==
# テスト用エントリーポイント
# ==
async def test_quality_feedback_loop():
    """QualityFeedbackLoop の動作テスト"""
    from browser_control.sheets_manager import GoogleSheetsManager
    from task_executor.task_executor import TaskExecutor

    sheets = GoogleSheetsManager()
    executor = TaskExecutor(sheets)

    qfl = QualityFeedbackLoop(sheets, executor)

    # テストケース1: 高品質（9点）
    test_task1 = {"task_id": "T001", "task_name": "テストタスク1"}
    test_result1 = {"quality_score": 9, "output": "完璧な実装", "elapsed_time": 3.5}

    result1 = await qfl.process_task_result(test_task1, test_result1)
    print(f"テスト1結果: {result1}")

    # テストケース2: 要改善（6点）
    test_task2 = {"task_id": "T002", "task_name": "テストタスク2"}
    test_result2 = {"quality_score": 6, "output": "改善の余地あり", "elapsed_time": 5.2}

    result2 = await qfl.process_task_result(test_task2, test_result2)
    print(f"テスト2結果: {result2}")

    # 統計表示
    qfl.print_stats()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_quality_feedback_loop())

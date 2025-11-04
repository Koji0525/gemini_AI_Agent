"""
Quality Feedback Loop v02 - 品質評価に基づく自動再実行管理
Phase 4-2で追加: 無限ループ防止、タスク情報保持、評価失敗時のデフォルト処理
"""

from datetime import datetime
from typing import Dict, Any


class QualityFeedbackLoop:
    """品質スコアに基づく自動再実行管理（改良版）"""

    # 定数定義
    MAX_RETRY_COUNT = 3  # 最大再実行回数
    DEFAULT_QUALITY_SCORE = 5  # 評価失敗時のデフォルトスコア
    HIGH_QUALITY_THRESHOLD = 9  # 高品質と判定する閾値
    ACCEPTABLE_THRESHOLD = 7  # 合格と判定する閾値
    IMPROVEMENT_THRESHOLD = 5  # 改善可能と判定する閾値

    def __init__(self, sheets_manager, task_executor, review_agent):
        self.sheets = sheets_manager
        self.executor = task_executor
        self.review_agent = review_agent

    async def process_task_result(
        self, task: Dict[str, Any], result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        タスク実行結果を品質評価し、必要に応じて再実行を指示

        Args:
            task: タスク情報（task_id, task_name, retry_count等）
            result: 実行結果（quality_score, output等）

        Returns:
            処理結果（action, reason等）
        """
        # 品質スコアの取得と検証
        quality_score = self._validate_quality_score(result.get("quality_score", 0))
        retry_count = task.get("retry_count", 0)
        task.get("task_id", "unknown")
        task_name = task.get("task_name", "Unknown Task")

        print(f"📋 qualit 💬 🔍 品質評価: {task_name} = {quality_score}点 (retry: {retry_count})")

        # 無限ループ防止: 最大再実行回数チェック
        if retry_count >= self.MAX_RETRY_COUNT:
            print(f"📋 qualit ⚠️  最大再実行回数到達: {task_name}")
            await self._mark_as_failed(task, "max_retry_exceeded")
            return {"action": "failed", "reason": "max_retry_exceeded", "retry_count": retry_count}

        # CASE 1: 高品質（9-10点）→ 即採用
        if quality_score >= self.HIGH_QUALITY_THRESHOLD:
            await self._mark_as_completed(task, result)
            return {"action": "accepted", "reason": "high_quality", "quality_score": quality_score}

        # CASE 2: 合格（7-8点）→ 条件付き採用
        elif quality_score >= self.ACCEPTABLE_THRESHOLD:
            await self._mark_as_completed(task, result)
            await self._record_improvement_note(task, result)
            return {
                "action": "accepted_with_notes",
                "reason": "acceptable",
                "quality_score": quality_score,
            }

        # CASE 3: 要改善（5-6点）→ 改善案生成 + 再実行
        elif quality_score >= self.IMPROVEMENT_THRESHOLD:
            improvement_plan = await self._generate_improvement(task, result)
            await self._create_retry_task(task, improvement_plan, retry_count + 1)
            return {
                "action": "retry_with_improvement",
                "plan": improvement_plan,
                "quality_score": quality_score,
            }

        # CASE 4: 不合格（4点以下）→ 代替アプローチ
        else:
            alternative = await self._generate_alternative(task, result)
            await self._create_retry_task(task, alternative, retry_count + 1, is_alternative=True)
            return {
                "action": "retry_with_alternative",
                "approach": alternative,
                "quality_score": quality_score,
            }

    def _validate_quality_score(self, score: Any) -> int:
        """
        品質スコアを検証し、異常値の場合はデフォルト値を返す

        Args:
            score: 品質スコア（int, float, str等）

        Returns:
            検証済みの品質スコア（0-10の整数）
        """
        try:
            score_int = int(score)

            # 範囲外チェック
            if score_int < 0 or score_int > 10:
                print(
                    f"📋 qualit ⚠️  異常な品質スコア: {score_int} → デフォルト値 {self.DEFAULT_QUALITY_SCORE} を使用"
                )
                return self.DEFAULT_QUALITY_SCORE

            # 0点は評価失敗とみなす
            if score_int == 0:
                print(
                    f"📋 qualit ⚠️  品質評価失敗（0点） → デフォルト値 {self.DEFAULT_QUALITY_SCORE} を使用"
                )
                return self.DEFAULT_QUALITY_SCORE

            return score_int

        except (ValueError, TypeError):
            print(
                f"📋 qualit ❌ ERROR スコア変換失敗: {score} → デフォルト値 {self.DEFAULT_QUALITY_SCORE} を使用"
            )
            return self.DEFAULT_QUALITY_SCORE

    async def _mark_as_completed(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        """タスクを完了としてマーク"""
        task.get("task_id", "unknown")

        # pm_tasksのステータスを更新
        await self.sheets.update_cell(
            sheet_name="pm_tasks", cell_address=f"E{task.get('row_number', 0)}", value="completed"
        )

        print(f"📋 qualit �� ✅ タスク完了: {task.get('task_name', 'Unknown')}")

    async def _mark_as_failed(self, task: Dict[str, Any], reason: str) -> None:
        """タスクを失敗としてマーク"""
        task.get("task_id", "unknown")

        # pm_tasksのステータスを更新
        await self.sheets.update_cell(
            sheet_name="pm_tasks",
            cell_address=f"E{task.get('row_number', 0)}",
            value=f"failed_{reason}",
        )

        print(f"📋 qualit ❌ ERROR タスク失敗: {task.get('task_name', 'Unknown')} (理由: {reason})")

    async def _record_improvement_note(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        """改善点をログに記録"""
        improvement_note = f"品質スコア {result.get('quality_score')}点で合格。今後の改善余地あり。"

        # task_execution_logに記録
        await self.sheets.append_rows(
            sheet_name="task_execution_log",
            values=[
                [
                    datetime.now().isoformat(),
                    task.get("task_id", "unknown"),
                    "improvement_note",
                    improvement_note,
                ]
            ],
        )

    async def _generate_improvement(self, task: Dict[str, Any], result: Dict[str, Any]) -> str:
        """改善案を生成（5秒以内）"""
        # TODO: Gemini APIを使用して改善案を生成
        # 現在は簡易版
        return f"タスク '{task.get('task_name')}' の品質を向上させるため、より具体的な実装を行う"

    async def _generate_alternative(self, task: Dict[str, Any], result: Dict[str, Any]) -> str:
        """代替アプローチを生成（5秒以内）"""
        # TODO: Gemini APIを使用して代替案を生成
        # 現在は簡易版
        return f"タスク '{task.get('task_name')}' の代替アプローチ: 異なる手法で再実装"

    async def _create_retry_task(
        self,
        task: Dict[str, Any],
        improvement_plan: str,
        retry_count: int,
        is_alternative: bool = False,
    ) -> None:
        """
        再実行タスクを作成（元のタスク情報を保持）

        Args:
            task: 元のタスク情報
            improvement_plan: 改善案または代替案
            retry_count: 再実行回数
            is_alternative: 代替アプローチかどうか
        """
        original_task_name = task.get("task_name", "Unknown Task")
        task.get("task_id", "unknown")

        # タスク名に再実行回数と元のタスク名を含める
        prefix = "[RETRY-ALTERNATIVE]" if is_alternative else "[RETRY-IMPROVEMENT]"
        new_task_name = f"{prefix} {original_task_name} (試行{retry_count})"

        # 新しいタスクをpm_tasksに登録
        new_task_data = [
            datetime.now().isoformat(),
            new_task_name,
            f"{task.get('task_description', '')}\n\n改善案:\n{improvement_plan}",
            "pending",
            "high",  # 再実行タスクは高優先度
            retry_count,
        ]

        await self.sheets.append_rows(sheet_name="pm_tasks", values=[new_task_data])

        print(f"📋 qualit 💬 🔄 再実行タスク登録: {new_task_name}")

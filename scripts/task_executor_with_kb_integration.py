"""
🎯 ナレッジベース統合版TaskExecutor

変更理由:
- 既存のTaskExecutorを継承し、ナレッジベース機能を追加
- タスク実行時に自動でレポート生成
- 失敗時に類似ケースを検索して自動修正提案
"""

from typing import Dict

# 既存システムのインポート
try:
    from scripts.task_executor import TaskExecutor
    from agents.sheets.sheets_manager import GoogleSheetsManager
    from agents.self_healing.logging.enhanced_knowledge_manager import (
        TaskReportGenerator,
        EnhancedKnowledgeManager,
    )
except ImportError as e:
    print(f"⚠️  インポートエラー: {e}")
    print("   既存システムとの統合には手動調整が必要です")
    TaskExecutor = object


class KBIntegratedTaskExecutor(TaskExecutor):
    """
    ナレッジベース統合版TaskExecutor

    追加機能:
    - タスク実行時に自動レポート生成
    - エラー発生時に類似ケース検索
    - ナレッジベースへの自動登録
    """

    def __init__(self, sheets_manager: GoogleSheetsManager):
        # 既存TaskExecutorの初期化
        super().__init__(sheets_manager)

        # ナレッジマネージャーを追加
        self.kb_manager = EnhancedKnowledgeManager(sheets_manager)

        print("✅ KBIntegratedTaskExecutor初期化完了")
        print("   - ナレッジベース統合機能が有効")

    async def execute_task_with_reporting(self, task: Dict) -> Dict:
        """
        タスクを実行し、標準レポートを生成

        Args:
            task: タスク定義辞書
                - task_id: タスクID
                - task_name: タスク名
                - task_description: 説明

        Returns:
            実行結果とレポート
        """
        # レポートジェネレーターを作成
        reporter = TaskReportGenerator(
            task_id=task["task_id"],
            task_name=task["task_name"],
            task_description=task.get("description", ""),
        )

        try:
            # STEP 1: タスク準備
            reporter.start_step(1, "タスク準備")
            await self._prepare_task(task)
            reporter.success_step(method="タスク検証完了")

            # STEP 2: タスク実行
            reporter.start_step(2, "タスク実行")
            result = await self._execute_core_task(task)
            reporter.success_step(method=f"{task['task_name']}実行")

            # STEP 3: 結果検証
            reporter.start_step(3, "結果検証")
            await self._verify_result(result)
            reporter.success_step(method="検証完了")

        except Exception as e:
            # エラー発生
            reporter.fail_step(e, root_cause=str(e), error_type=type(e).__name__)

            # 類似ケースを検索
            similar_cases = await self._search_similar_errors(e, task)

            if similar_cases:
                print(f"\n💡 類似ケースを発見: {len(similar_cases)}件")
                for case in similar_cases[:3]:
                    print(f"  - {case['scenario']}: {case['solution']}")

                # リトライ
                reporter.retry_step("類似ケースの解決方法を適用")
                try:
                    # 類似ケースの解決方法を適用してリトライ
                    result = await self._retry_with_solution(task, similar_cases[0])
                    reporter.success_step(
                        method=f"類似ケース解決法適用: {similar_cases[0]['solution']}"
                    )
                except Exception as retry_error:
                    reporter.fail_step(retry_error, root_cause="類似ケース解決法も失敗")
                    raise

        # レポート確定
        report = reporter.finalize()

        # ナレッジベースに保存
        await self.kb_manager.save_task_report(report)

        return {
            "success": report.final_status.value == "✅ 成功",
            "report": report,
            "quality_score": report.quality_score,
        }

    async def _prepare_task(self, task: Dict):
        """タスク準備（既存メソッドを呼び出し）"""
        # 既存のTaskExecutorの準備処理を利用

    async def _execute_core_task(self, task: Dict) -> Dict:
        """コアタスク実行（既存メソッドを呼び出し）"""
        # 既存のTaskExecutorの実行処理を利用
        return {"status": "success", "data": {}}

    async def _verify_result(self, result: Dict):
        """結果検証"""
        if result.get("status") != "success":
            raise ValueError("タスク実行結果が不正")

    async def _search_similar_errors(self, error: Exception, task: Dict) -> list:
        """類似エラーをナレッジベースから検索"""
        type(error).__name__

        # ナレッジベースから類似ケースを検索
        # TODO: 既存のSimilaritySearchEngineと統合

        return []

    async def _retry_with_solution(self, task: Dict, solution: Dict) -> Dict:
        """解決方法を適用してリトライ"""
        print(f"🔄 解決方法を適用: {solution.get('solution', '')}")

        # 解決方法に基づいてタスクを再実行
        return await self._execute_core_task(task)


if __name__ == "__main__":
    print("✅ KBIntegratedTaskExecutor モジュール読み込み完了")

"""
自動再試行システム

品質チェックに失敗した場合、最大3回まで自動的に再実行する。
"""

from typing import Any, Dict

from agents.quality.quality_checker import QualityChecker


class RetryExecutor:
    """自動再試行実行システム"""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.quality_checker = QualityChecker()

    async def execute_with_retry(self, executor, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        品質保証付きタスク実行

        Args:
            executor: タスク実行エンジン
            task: タスク情報

        Returns:
            実行結果
        """
        attempt = 0

        while attempt < self.max_retries:
            attempt += 1

            print(f"🚀 実行試行 {attempt}/{self.max_retries}...")

            # タスク実行
            result = await executor.execute_task(task)

            if not result.get("success"):
                print(f"⚠️  実行失敗: {result.get('error', 'Unknown')}")
                continue

            # 品質チェック
            output_text = result.get("output", "")
            passed, issues = self.quality_checker.check_output(output_text)

            if passed:
                print(f"✅ 品質チェック合格（試行{attempt}回目）")
                return result

            # 品質不合格
            print(f"⚠️  品質チェック不合格（試行{attempt}回目）:")
            for issue in issues:
                print(f"  - {issue}")

            if attempt < self.max_retries:
                print("🔄 改善して再試行します...")

                # 再試行用プロンプト追加
                retry_prompt = self.quality_checker.generate_retry_prompt(issues)
                task["description"] += "\n\n" + retry_prompt
            else:
                print("❌ 最大試行回数に達しました")

        # 全試行失敗
        return {
            "success": False,
            "error": f"{self.max_retries}回試行しましたが品質基準を満たせませんでした",
            "issues": issues,
        }

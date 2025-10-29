"""
Week 6: SandboxRunner - サンドボックス環境でのエージェント実行

生成されたエージェントを安全に実行・検証
"""

import asyncio
import subprocess
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import tempfile
import shutil


class SandboxRunner:
    """
    サンドボックス環境でエージェントとテストを実行
    """

    def __init__(self):
        """初期化"""
        self.execution_history = []
        self.execution_count = 0

    async def run_agent_test(self, test_file_path: str, timeout: int = 60) -> Dict[str, Any]:
        """
        エージェントのテストを実行

        Args:
            test_file_path: テストファイルのパス
            timeout: タイムアウト（秒）

        Returns:
            実行結果
        """
        start_time = datetime.now()

        try:
            # pytestでテスト実行
            result = await self._run_pytest(test_file_path, timeout)

            execution_time = (datetime.now() - start_time).total_seconds()

            # 実行履歴に記録
            execution_record = {
                "test_file": test_file_path,
                "executed_at": start_time.isoformat(),
                "execution_time": execution_time,
                "success": result["returncode"] == 0,
                "output": result["stdout"],
                "errors": result["stderr"],
            }

            self.execution_history.append(execution_record)
            self.execution_count += 1

            return {
                "success": result["returncode"] == 0,
                "execution_time": execution_time,
                "test_results": self._parse_pytest_output(result["stdout"]),
                "output": result["stdout"],
                "errors": result["stderr"],
            }

        except Exception as e:
            return {"success": False, "error": str(e), "execution_time": (datetime.now() - start_time).total_seconds()}

    async def _run_pytest(self, test_file: str, timeout: int) -> Dict[str, Any]:
        """
        pytestを実行

        Args:
            test_file: テストファイル
            timeout: タイムアウト

        Returns:
            実行結果
        """
        cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

                return {
                    "returncode": process.returncode,
                    "stdout": stdout.decode("utf-8", errors="ignore"),
                    "stderr": stderr.decode("utf-8", errors="ignore"),
                }

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Test execution timed out after {timeout}s")

        except Exception as e:
            raise RuntimeError(f"Failed to run pytest: {e}")

    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """
        pytestの出力を解析

        Args:
            output: pytest出力

        Returns:
            解析結果
        """
        lines = output.split("\n")

        # テスト数を抽出
        passed = 0
        failed = 0

        for line in lines:
            if "passed" in line.lower():
                # "5 passed" のようなパターンを探す
                import re

                match = re.search(r"(\d+)\s+passed", line)
                if match:
                    passed = int(match.group(1))

            if "failed" in line.lower():
                match = re.search(r"(\d+)\s+failed", line)
                if match:
                    failed = int(match.group(1))

        return {
            "total": passed + failed,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "0%",
        }

    async def run_agent_directly(self, agent_file_path: str, timeout: int = 30) -> Dict[str, Any]:
        """
        エージェントを直接実行

        Args:
            agent_file_path: エージェントファイルのパス
            timeout: タイムアウト（秒）

        Returns:
            実行結果
        """
        start_time = datetime.now()

        try:
            cmd = [sys.executable, agent_file_path]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

                execution_time = (datetime.now() - start_time).total_seconds()

                return {
                    "success": process.returncode == 0,
                    "execution_time": execution_time,
                    "output": stdout.decode("utf-8", errors="ignore"),
                    "errors": stderr.decode("utf-8", errors="ignore"),
                }

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {"success": False, "error": f"Execution timed out after {timeout}s", "execution_time": timeout}

        except Exception as e:
            return {"success": False, "error": str(e), "execution_time": (datetime.now() - start_time).total_seconds()}

    def validate_agent_quality(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        エージェントの品質を検証

        Args:
            test_results: テスト結果

        Returns:
            品質評価結果
        """
        if not test_results.get("success"):
            return {"approved": False, "quality_score": 0, "reason": "Tests failed"}

        results = test_results.get("test_results", {})
        passed = results.get("passed", 0)
        total = results.get("total", 0)

        if total == 0:
            return {"approved": False, "quality_score": 0, "reason": "No tests found"}

        # 品質スコア計算
        success_rate = (passed / total) * 100
        execution_time = test_results.get("execution_time", 0)

        # 評価基準
        # - 全テスト合格: 必須
        # - 実行時間が妥当: 30秒以内
        quality_score = 0

        if passed == total:
            quality_score += 70  # 全テスト合格
        else:
            quality_score += int((passed / total) * 70)

        if execution_time < 30:
            quality_score += 30  # パフォーマンス良好
        else:
            quality_score += max(0, 30 - int(execution_time - 30))

        # 承認判定（80点以上）
        approved = quality_score >= 80

        return {
            "approved": approved,
            "quality_score": quality_score,
            "success_rate": f"{success_rate:.1f}%",
            "execution_time": execution_time,
            "passed_tests": passed,
            "total_tests": total,
            "reason": "Quality checks passed" if approved else "Quality checks failed",
        }

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        実行履歴を取得

        Args:
            limit: 取得する履歴数

        Returns:
            実行履歴
        """
        return self.execution_history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """
        実行統計を取得

        Returns:
            統計情報
        """
        successful = sum(1 for record in self.execution_history if record["success"])

        return {
            "total_executions": self.execution_count,
            "successful": successful,
            "failed": self.execution_count - successful,
            "success_rate": f"{(successful / self.execution_count * 100):.1f}%" if self.execution_count > 0 else "0%",
        }


# ================================================
# デモ
# ================================================


async def demo_sandbox_runner():
    """SandboxRunnerのデモンストレーション"""
    print("\n" + "=" * 70)
    print("SandboxRunner デモンストレーション")
    print("=" * 70)

    runner = SandboxRunner()

    print("\n【機能紹介】")
    print("-" * 70)
    print("1. エージェントテストの実行")
    print("2. エージェントの直接実行")
    print("3. 品質検証")
    print("4. 実行履歴管理")

    # ダミーのテスト結果で品質検証デモ
    print("\n【品質検証デモ】")
    print("-" * 70)

    dummy_test_results = {
        "success": True,
        "execution_time": 15.5,
        "test_results": {"total": 10, "passed": 10, "failed": 0},
    }

    quality = runner.validate_agent_quality(dummy_test_results)
    print(f"承認: {'✅ YES' if quality['approved'] else '❌ NO'}")
    print(f"品質スコア: {quality['quality_score']}/100")
    print(f"成功率: {quality['success_rate']}")
    print(f"実行時間: {quality['execution_time']}秒")
    print(f"理由: {quality['reason']}")

    # 統計表示
    print("\n【統計情報】")
    print("-" * 70)
    stats = runner.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_sandbox_runner())

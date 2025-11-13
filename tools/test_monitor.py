"""
テスト監視システム
5回に1回の自動テスト実行でシステム破壊を防止
"""

import subprocess
from datetime import datetime


class TestMonitor:
    """テスト監視システム"""

    def __init__(self):
        self.execution_count = 0
        self.test_results = []

    def check_and_run_tests(self, force_run=False):
        """
        テスト実行のチェックと実行

        Args:
            force_run: 強制実行フラグ
        """
        self.execution_count += 1

        # 5回に1回、または強制実行
        if force_run or self.execution_count % 5 == 0:
            print("🧪 テスト監視: 実行中...")
            result = self._run_comprehensive_tests()
            self.test_results.append(result)

            if result["success"]:
                print("✅ テスト監視: すべて正常")
            else:
                print(f"⚠️ テスト監視: 警告 - {result['failed_tests']}件失敗")

            return result
        else:
            print(f"🔍 テスト監視: スキップ (実行カウント: {self.execution_count})")
            return {"success": True, "skipped": True}

    def _run_comprehensive_tests(self):
        """包括的なテスト実行"""
        test_commands = [
            ["python3", "-m", "pytest", "tests/", "-v", "--tb=short"],
            ["python3", "-m", "pytest", "tests/test_self_healing_agent.py", "-v"],
            ["python3", "-m", "pytest", "tests/test_integration_healing.py", "-v"],
            ["python3", "tools/system_diagnostics.py"],
            ["python3", "agents/health_check/health_check_agent.py", "--quick"],
        ]

        results = []
        failed_tests = 0

        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=600  # 10分タイムアウト
                )

                test_result = {
                    "command": " ".join(cmd),
                    "returncode": result.returncode,
                    "success": result.returncode == 0,
                    "timestamp": datetime.now().isoformat(),
                }

                if not test_result["success"]:
                    failed_tests += 1
                    test_result["error"] = result.stderr[:500]  # 先頭500文字のみ

                results.append(test_result)

            except subprocess.TimeoutExpired:
                results.append(
                    {
                        "command": " ".join(cmd),
                        "success": False,
                        "error": "タイムアウト",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                failed_tests += 1
            except Exception as e:
                results.append(
                    {
                        "command": " ".join(cmd),
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                failed_tests += 1

        return {
            "success": failed_tests == 0,
            "total_tests": len(test_commands),
            "failed_tests": failed_tests,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    def get_summary(self):
        """テスト結果のサマリー"""
        if not self.test_results:
            return "テスト未実行"

        total_runs = len(self.test_results)
        successful_runs = sum(1 for r in self.test_results if r["success"])
        success_rate = (successful_runs / total_runs) * 100

        return {
            "total_monitoring_runs": total_runs,
            "successful_runs": successful_runs,
            "success_rate": f"{success_rate:.1f}%",
            "last_check": self.test_results[-1]["timestamp"] if self.test_results else "N/A",
        }


# グローバルインスタンス
test_monitor = TestMonitor()


def monitor_test_execution():
    """テスト監視の実行（5回に1回）"""
    return test_monitor.check_and_run_tests()


if __name__ == "__main__":
    # テスト実行
    result = monitor_test_execution()
    print(f"テスト結果: {result}")

    summary = test_monitor.get_summary()
    print(f"監視サマリー: {summary}")

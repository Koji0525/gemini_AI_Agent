"""
強化版テスト監視システム
5回に1回の自動テスト実行でシステム破壊を防止
"""

import os
import subprocess
from datetime import datetime


class TestMonitorEnhanced:
    """強化版テスト監視システム"""

    def __init__(self, check_interval: int = 5):
        self.execution_count = 0
        self.test_results = []
        self.check_interval = check_interval
        self.last_check_time = None

        # 監視対象ディレクトリ
        self.monitored_dirs = ["agents", "tools", "core_agents", "knowledge_system"]

    def check_and_run_tests(self, force_run=False):
        """
        テスト実行のチェックと実行

        Args:
            force_run: 強制実行フラグ
        """
        self.execution_count += 1

        # 5回に1回、または強制実行
        if force_run or self.execution_count % self.check_interval == 0:
            print("🧪 テスト監視: 実行中...")
            result = self._run_comprehensive_tests()
            self.test_results.append(result)

            if result["success"]:
                print("✅ テスト監視: すべて正常")
            else:
                print(f"⚠️ テスト監視: 警告 - {result['failed_tests']}件失敗")

            return result
        else:
            print(
                f"🔍 テスト監視: スキップ (実行カウント: {self.execution_count}, 次回: {self.check_interval - (self.execution_count % self.check_interval)}回後)"
            )
            return {"success": True, "skipped": True}

    def _run_comprehensive_tests(self):
        """包括的なテスト実行"""
        test_commands = [
            # 基本システムテスト
            [
                "python3",
                "-c",
                "\"import sys; sys.path.insert(0, '/workspaces/gemini_AI_Agent'); from tools.base_data_accessor import BaseDataAccessor; print('✅ BaseDataAccessor インポート成功')\"",
            ],
            # 品質評価テスト
            [
                "python3",
                "-c",
                "\"import sys; sys.path.insert(0, '/workspaces/gemini_AI_Agent'); from agents.quality_evaluation.quality_evaluator import QualityEvaluator; print('✅ QualityEvaluator インポート成功')\"",
            ],
            # シート接続テスト
            [
                "python3",
                "-c",
                "\"import sys; sys.path.insert(0, '/workspaces/gemini_AI_Agent'); from tools.sheets_manager import GoogleSheetsManager; sheets = GoogleSheetsManager(); print('✅ GoogleSheetsManager 初期化成功')\"",
            ],
            # ファイル整合性チェック
            ["find", "agents", "-name", "*.py", "-exec", "python3", "-m", "py_compile", "{}", ";"],
        ]

        results = []
        failed_tests = 0

        for cmd in test_commands:
            try:
                # コマンドの実行
                if cmd[0] == "python3" and "-c" in cmd:
                    # Pythonコードの直接実行
                    code = cmd[2].strip('"')
                    result = subprocess.run(
                        ["python3", "-c", code], capture_output=True, text=True, timeout=30
                    )
                else:
                    # 通常のコマンド実行
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                test_result = {
                    "command": " ".join(cmd) if isinstance(cmd, list) else cmd,
                    "returncode": result.returncode,
                    "success": result.returncode == 0,
                    "timestamp": datetime.now().isoformat(),
                    "output": result.stdout[:200],  # 先頭200文字のみ
                }

                if not test_result["success"]:
                    failed_tests += 1
                    test_result["error"] = (
                        result.stderr[:500] if result.stderr else "No error output"
                    )

                results.append(test_result)

            except subprocess.TimeoutExpired:
                results.append(
                    {
                        "command": " ".join(cmd) if isinstance(cmd, list) else cmd,
                        "success": False,
                        "error": "タイムアウト (60秒)",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                failed_tests += 1
            except Exception as e:
                results.append(
                    {
                        "command": " ".join(cmd) if isinstance(cmd, list) else cmd,
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                failed_tests += 1

        # ファイルシステムの健全性チェック
        fs_check = self._check_filesystem_integrity()
        results.append(fs_check)
        if not fs_check["success"]:
            failed_tests += 1

        return {
            "success": failed_tests == 0,
            "total_tests": len(test_commands) + 1,  # +1 for filesystem check
            "failed_tests": failed_tests,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    def _check_filesystem_integrity(self):
        """ファイルシステムの整合性チェック"""
        missing_files = []

        # 必須ファイルのチェック
        required_files = [
            "tools/base_data_accessor.py",
            "tools/sheets_manager.py",
            "tools/safe_sheets_wrapper.py",
            "agents/quality_evaluation/quality_evaluator.py",
            "knowledge_system/core_agents/knowledge_manager.py",
        ]

        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)

        return {
            "command": "Filesystem Integrity Check",
            "success": len(missing_files) == 0,
            "missing_files": missing_files,
            "timestamp": datetime.now().isoformat(),
        }

    def get_summary(self):
        """テスト結果のサマリー"""
        if not self.test_results:
            return {
                "total_monitoring_runs": 0,
                "successful_runs": 0,
                "success_rate": "0%",
                "last_check": "N/A",
                "status": "テスト未実行",
            }

        # 実際に実行されたテストのみをカウント
        executed_tests = [r for r in self.test_results if not r.get("skipped", False)]

        if not executed_tests:
            return {
                "total_monitoring_runs": self.execution_count,
                "successful_runs": 0,
                "success_rate": "0%",
                "last_check": "N/A",
                "status": "テスト実行なし",
            }

        total_runs = len(executed_tests)
        successful_runs = sum(1 for r in executed_tests if r["success"])
        success_rate = (successful_runs / total_runs) * 100

        return {
            "total_monitoring_runs": total_runs,
            "successful_runs": successful_runs,
            "success_rate": f"{success_rate:.1f}%",
            "last_check": executed_tests[-1]["timestamp"] if executed_tests else "N/A",
            "status": "正常" if success_rate >= 80 else "要確認",
        }


# グローバルインスタンス
test_monitor = TestMonitorEnhanced()


def monitor_test_execution():
    """テスト監視の実行（5回に1回）"""
    return test_monitor.check_and_run_tests()


if __name__ == "__main__":
    # 強制テスト実行
    print("🔧 強化版テスト監視システム起動")
    result = test_monitor.check_and_run_tests(force_run=True)

    print(f"\nテスト結果: {'✅ 成功' if result['success'] else '❌ 失敗'}")

    summary = test_monitor.get_summary()
    print(f"監視サマリー: {summary}")

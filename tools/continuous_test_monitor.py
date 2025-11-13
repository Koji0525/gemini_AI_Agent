"""
継続的テスト監視システム
既存テストを定期的に実行して品質を維持
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class ContinuousTestMonitor:
    """継続的テスト監視"""

    def __init__(self):
        self.baseline_success_rate = 84.3  # 基準成功率
        self.test_history_file = "test_history.json"
        self.test_history = self.load_history()

        print("✅ ContinuousTestMonitor 初期化完了")
        print(f"📊 基準成功率: {self.baseline_success_rate}%")

    def load_history(self) -> List[Dict]:
        """テスト履歴読み込み"""
        if os.path.exists(self.test_history_file):
            with open(self.test_history_file, "r") as f:
                return json.load(f)
        return []

    def save_history(self):
        """テスト履歴保存"""
        with open(self.test_history_file, "w") as f:
            json.dump(self.test_history, f, indent=2)

    def run_all_tests(self) -> Dict[str, Any]:
        """全テスト実行"""
        print("\n" + "=" * 80)
        print("🧪 全テスト実行")
        print("=" * 80)
        print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        result = {"timestamp": datetime.now().isoformat(), "categories": {}}

        # ユニットテスト
        print("\n" + "━" * 80)
        print("1️⃣ ユニットテスト")
        print("━" * 80)
        result["categories"]["unit"] = self.run_unit_tests()

        # 統合テスト
        print("\n" + "━" * 80)
        print("2️⃣ 統合テスト")
        print("━" * 80)
        result["categories"]["integration"] = self.run_integration_tests()

        # E2Eテスト
        print("\n" + "━" * 80)
        print("3️⃣ E2Eテスト")
        print("━" * 80)
        result["categories"]["e2e"] = self.run_e2e_tests()

        # 総合結果
        result["overall"] = self.calculate_overall(result["categories"])

        # 履歴に追加
        self.test_history.append(result)
        self.test_history = self.test_history[-50:]  # 最新50件
        self.save_history()

        # 表示
        self.display_result(result)

        # 判定
        self.judge_and_alert(result)

        return result

    def run_unit_tests(self) -> Dict[str, Any]:
        """ユニットテスト実行"""
        try:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "pytest",
                    "tests/",
                    "-k",
                    "not integration and not e2e",
                    "--tb=short",
                    "-v",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            return self.parse_pytest_output(result)

        except subprocess.TimeoutExpired:
            print("⚠️ タイムアウト（60秒）")
            return {"status": "TIMEOUT", "passed": 0, "failed": 0, "total": 0}
        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            return {"status": "ERROR", "error": str(e)}

    def run_integration_tests(self) -> Dict[str, Any]:
        """統合テスト実行"""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "-k", "integration", "--tb=short", "-v"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            return self.parse_pytest_output(result)

        except subprocess.TimeoutExpired:
            print("⚠️ タイムアウト（120秒）")
            return {"status": "TIMEOUT", "passed": 0, "failed": 0, "total": 0}
        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            return {"status": "ERROR", "error": str(e)}

    def run_e2e_tests(self) -> Dict[str, Any]:
        """E2Eテスト実行"""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "-k", "e2e", "--tb=short", "-v"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            return self.parse_pytest_output(result)

        except subprocess.TimeoutExpired:
            print("⚠️ タイムアウト（300秒）")
            return {"status": "TIMEOUT", "passed": 0, "failed": 0, "total": 0}
        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            return {"status": "ERROR", "error": str(e)}

    def parse_pytest_output(self, result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """pytest出力を解析"""
        output = result.stdout + result.stderr

        # 成功数・失敗数をカウント
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        skipped = output.count(" SKIPPED")
        errors = output.count(" ERROR")

        total = passed + failed + errors

        success_rate = (passed / total * 100) if total > 0 else 0

        return {
            "status": "OK" if failed == 0 and errors == 0 else "FAILED",
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "total": total,
            "success_rate": success_rate,
            "output": output[:1000],  # 最初の1000文字
        }

    def calculate_overall(self, categories: Dict[str, Dict]) -> Dict[str, Any]:
        """総合結果計算"""
        total_passed = 0
        total_failed = 0
        total_total = 0

        for category, result in categories.items():
            if "passed" in result:
                total_passed += result["passed"]
                total_failed += result["failed"]
                total_total += result["total"]

        success_rate = (total_passed / total_total * 100) if total_total > 0 else 0

        return {
            "passed": total_passed,
            "failed": total_failed,
            "total": total_total,
            "success_rate": success_rate,
            "status": "OK" if success_rate >= self.baseline_success_rate else "WARNING",
        }

    def display_result(self, result: Dict):
        """結果表示"""
        print("\n" + "=" * 80)
        print("📊 テスト結果サマリー")
        print("=" * 80)

        overall = result["overall"]

        print(f"\n総合成功率: {overall['success_rate']:.1f}% ", end="")

        if overall["success_rate"] >= self.baseline_success_rate:
            print("✅ 基準達成")
        else:
            print(f"❌ 基準未達（目標: {self.baseline_success_rate}%）")

        print(f"\n総テスト数: {overall['total']}件")
        print(f"  ✅ 成功: {overall['passed']}件")
        print(f"  ❌ 失敗: {overall['failed']}件")

        # カテゴリ別
        print("\nカテゴリ別:")
        for category, res in result["categories"].items():
            if "success_rate" in res:
                icon = "✅" if res["failed"] == 0 else "❌"
                print(
                    f"  {icon} {category:12s}: {res['success_rate']:5.1f}% ({res['passed']}/{res['total']})"
                )

        # 履歴トレンド
        if len(self.test_history) >= 2:
            prev = self.test_history[-2]["overall"]["success_rate"]
            curr = overall["success_rate"]
            diff = curr - prev

            trend = "↑" if diff > 0 else "↓" if diff < 0 else "→"
            print(f"\nトレンド: {trend} {diff:+.1f}%")

        print("=" * 80)

    def judge_and_alert(self, result: Dict):
        """判定とアラート"""
        overall = result["overall"]

        if overall["success_rate"] < self.baseline_success_rate:
            print("\n" + "!" * 80)
            print("⚠️ アラート: テスト成功率が基準を下回りました")
            print("!" * 80)
            print(f"現在: {overall['success_rate']:.1f}%")
            print(f"基準: {self.baseline_success_rate}%")
            print(f"差分: {overall['success_rate'] - self.baseline_success_rate:+.1f}%")
            print("\n対策:")
            print("  1. 失敗したテストを確認")
            print("  2. 原因を特定")
            print("  3. 修正を実施")
            print("  4. 再テスト")
            print("!" * 80)

    def show_history(self, count: int = 10):
        """履歴表示"""
        print("\n" + "=" * 80)
        print(f"📊 テスト履歴（最新{count}件）")
        print("=" * 80)

        for i, record in enumerate(reversed(self.test_history[-count:]), 1):
            ts = datetime.fromisoformat(record["timestamp"])
            overall = record["overall"]

            icon = "✅" if overall["success_rate"] >= self.baseline_success_rate else "❌"

            print(
                f"{i:2d}. {ts.strftime('%Y-%m-%d %H:%M:%S')} {icon} {overall['success_rate']:5.1f}% ({overall['passed']}/{overall['total']})"
            )

        print("=" * 80)


def main():
    """メイン"""
    monitor = ContinuousTestMonitor()

    # テスト実行
    monitor.run_all_tests()

    # 履歴表示
    monitor.show_history(count=10)


if __name__ == "__main__":
    main()

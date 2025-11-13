#!/usr/bin/env python3
"""
テスト監視システム
5回に1回の頻度でテストを実行し、既存システムの破壊を検出
"""

import subprocess
from datetime import datetime


class TestMonitor:
    def __init__(self):
        self.monitor_count = 0
        self.monitor_interval = 5  # 5回に1回監視
        self.baseline_success_rate = 84.3  # 基準値

    def should_run_test(self):
        """テスト実行判定（5回に1回）"""
        self.monitor_count += 1
        return self.monitor_count % self.monitor_interval == 0

    def run_tests(self):
        """テスト実行と結果分析"""
        print("🧪 テスト監視実行中...")

        try:
            # pytest実行
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300,
            )  # 5分タイムアウト

            # 結果解析
            success_rate = self.analyze_test_results(result)

            # レポート生成
            report = self.generate_report(result, success_rate)

            # 基準値チェック
            if success_rate < self.baseline_success_rate:
                print(
                    f"🚨 警告: テスト成功率が基準値を下回りました ({success_rate:.1f}% < {self.baseline_success_rate}%)"
                )
                return False, report
            else:
                print(f"✅ 正常: テスト成功率 {success_rate:.1f}%")
                return True, report

        except subprocess.TimeoutExpired:
            print("❌ テストがタイムアウトしました")
            return False, {"error": "テストタイムアウト"}
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            return False, {"error": str(e)}

    def analyze_test_results(self, result):
        """テスト結果分析"""
        output = result.stdout

        # パス/失敗数カウント
        passed = output.count("PASSED")
        failed = output.count("FAILED")
        total = passed + failed

        if total == 0:
            return 0.0

        return (passed / total) * 100

    def generate_report(self, result, success_rate):
        """テストレポート生成"""
        return {
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "baseline": self.baseline_success_rate,
            "passed": result.stdout.count("PASSED"),
            "failed": result.stdout.count("FAILED"),
            "return_code": result.returncode,
            "monitor_count": self.monitor_count,
        }

    def monitor_execution(self, func, *args, **kwargs):
        """
        関数実行を監視
        5回に1回テストを実行してシステム健全性を確認
        """
        # メイン関数実行
        result = func(*args, **kwargs)

        # テスト監視判定
        if self.should_run_test():
            print(f"\n🔍 テスト監視 ({self.monitor_count}回目) - システム健全性チェック")
            test_success, report = self.run_tests()

            if not test_success:
                print("⚠️ システム健全性に問題があります。開発を継続しますが注意が必要です。")
            else:
                print("✅ システム健全性確認完了")

        return result


# 使用例
def main():
    monitor = TestMonitor()

    # 監視付きで関数実行
    def sample_development_task():
        print("開発タスク実行中...")
        return "開発完了"

    result = monitor.monitor_execution(sample_development_task)
    print(f"結果: {result}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
テスト連携監視システム
- pytest実行結果を追跡
- カバレッジ変化を監視
- テスト失敗と依存関係の相関分析
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


class TestIntegrationMonitor:
    """テスト統合監視"""

    def __init__(self):
        self.test_results_dir = Path("test_results")
        self.test_results_dir.mkdir(exist_ok=True)

    def run_tests(self):
        """pytest実行"""
        print("🧪 テスト実行中...")

        # pytest with JSON report
        result = subprocess.run(
            [
                "python3",
                "-m",
                "pytest",
                "--json-report",
                "--json-report-file=test_results/latest_report.json",
                "--tb=short",
                "-v",
            ],
            capture_output=True,
            text=True,
        )

        print(result.stdout)

        return result.returncode == 0

    def analyze_test_results(self):
        """テスト結果分析"""
        report_file = self.test_results_dir / "latest_report.json"

        if not report_file.exists():
            print("⚠️  テスト結果なし")
            return None

        with open(report_file, "r") as f:
            data = json.load(f)

        summary = data.get("summary", {})

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total": summary.get("total", 0),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "skipped": summary.get("skipped", 0),
            "pass_rate": 0.0,
            "failed_tests": [],
        }

        if analysis["total"] > 0:
            analysis["pass_rate"] = (analysis["passed"] / analysis["total"]) * 100

        # 失敗テスト詳細
        for test in data.get("tests", []):
            if test.get("outcome") == "failed":
                analysis["failed_tests"].append(
                    {
                        "name": test.get("nodeid"),
                        "message": test.get("call", {}).get("longrepr", ""),
                    }
                )

        return analysis

    def correlate_with_changes(self, test_analysis, change_report):
        """テスト失敗と変更の相関分析"""
        correlations = []

        if not test_analysis or not change_report:
            return correlations

        # 変更ファイルと失敗テストの関連を検出
        changed_files = change_report.get("changes", {}).get(
            "new", []
        ) + change_report.get("changes", {}).get("modified", [])

        for failed_test in test_analysis.get("failed_tests", []):
            test_file = failed_test["name"].split("::")[0]

            # テストファイルが変更されたか
            if test_file in changed_files:
                correlations.append(
                    {
                        "test": failed_test["name"],
                        "reason": "test_file_modified",
                        "file": test_file,
                    }
                )
                continue

            # テスト対象ファイルが変更されたか（推測）
            for changed_file in changed_files:
                if changed_file.replace("tests/", "").replace("test_", "") in test_file:
                    correlations.append(
                        {
                            "test": failed_test["name"],
                            "reason": "tested_file_modified",
                            "file": changed_file,
                        }
                    )

        return correlations

    def generate_report(self, test_analysis, correlations):
        """統合レポート生成"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": test_analysis,
            "correlations": correlations,
            "recommendations": self._generate_recommendations(
                test_analysis, correlations
            ),
        }

        with open("test_integration_report.json", "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📊 テスト統合レポート")
        print(f"  成功率: {test_analysis['pass_rate']:.1f}%")
        print(f"  失敗: {test_analysis['failed']}件")
        print(f"  相関検出: {len(correlations)}件")

        return report

    def _generate_recommendations(self, test_analysis, correlations):
        """推奨アクション生成"""
        recommendations = []

        if test_analysis["pass_rate"] < 80:
            recommendations.append(
                {"priority": "HIGH", "action": "テスト成功率が80%未満です。変更を見直してください。"}
            )

        if len(correlations) > 0:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": f"{len(correlations)}個のテスト失敗が最近の変更に関連しています。",
                }
            )

        return recommendations


if __name__ == "__main__":
    monitor = TestIntegrationMonitor()

    # テスト実行
    success = monitor.run_tests()

    # 結果分析
    test_analysis = monitor.analyze_test_results()

    if test_analysis:
        # 変更レポートロード
        change_report = {}
        if Path("hybrid_change_report.json").exists():
            with open("hybrid_change_report.json", "r") as f:
                change_report = json.load(f)

        # 相関分析
        correlations = monitor.correlate_with_changes(test_analysis, change_report)

        # レポート生成
        monitor.generate_report(test_analysis, correlations)

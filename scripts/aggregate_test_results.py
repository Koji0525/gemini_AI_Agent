"""
テスト結果集計スクリプト
"""

import re
import glob
from pathlib import Path
from datetime import datetime


def parse_pytest_log(log_file):
    """pytest ログファイルを解析"""
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()

    # "X passed" パターンを検索
    passed_match = re.search(r"(\d+) passed", content)
    failed_match = re.search(r"(\d+) failed", content)
    error_match = re.search(r"(\d+) error", content)

    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    errors = int(error_match.group(1)) if error_match else 0

    total = passed + failed + errors
    success_rate = (passed / total * 100) if total > 0 else 0

    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "total": total,
        "success_rate": success_rate,
    }


def aggregate_all_tests():
    """全テスト結果を集計"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 テスト結果集計レポート")
    print(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # test_reports ディレクトリの全ログファイルを取得
    log_files = sorted(glob.glob("test_reports/*_test_*.log"))

    if not log_files:
        print("⚠️ テストログファイルが見つかりません")
        return

    total_passed = 0
    total_failed = 0
    total_errors = 0

    for log_file in log_files:
        test_name = Path(log_file).stem
        try:
            result = parse_pytest_log(log_file)

            print(f"📝 {test_name}")
            print(f"   合格: {result['passed']}")
            print(f"   失敗: {result['failed']}")
            print(f"   エラー: {result['errors']}")
            print(f"   成功率: {result['success_rate']:.1f}%")
            print()

            total_passed += result["passed"]
            total_failed += result["failed"]
            total_errors += result["errors"]

        except Exception as e:
            print(f"⚠️ {test_name}: 解析エラー ({e})")

    # 総合成功率
    total_tests = total_passed + total_failed + total_errors
    overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📈 総合結果")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"総テスト数: {total_tests}")
    print(f"合格: {total_passed}")
    print(f"失敗: {total_failed}")
    print(f"エラー: {total_errors}")
    print(f"総合成功率: {overall_success_rate:.1f}%")
    print()

    # 84.3%との比較
    target_rate = 84.3
    if overall_success_rate >= target_rate:
        print(f"✅ 目標達成: {overall_success_rate:.1f}% ≥ {target_rate}%")
    else:
        diff = target_rate - overall_success_rate
        print(f"⚠️ 目標未達: {overall_success_rate:.1f}% < {target_rate}%")
        print(f"   不足: {diff:.1f}%")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # レポート保存
    report_path = f'docs/test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# テスト結果レポート\n\n")
        f.write(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 総合結果\n\n")
        f.write(f"- **総テスト数**: {total_tests}\n")
        f.write(f"- **合格**: {total_passed}\n")
        f.write(f"- **失敗**: {total_failed}\n")
        f.write(f"- **エラー**: {total_errors}\n")
        f.write(f"- **総合成功率**: {overall_success_rate:.1f}%\n\n")

        if overall_success_rate >= target_rate:
            f.write(f"✅ **目標達成**: {overall_success_rate:.1f}% ≥ {target_rate}%\n")
        else:
            f.write(f"⚠️ **目標未達**: {overall_success_rate:.1f}% < {target_rate}%\n")

    print(f"✅ レポート保存: {report_path}")


if __name__ == "__main__":
    aggregate_all_tests()

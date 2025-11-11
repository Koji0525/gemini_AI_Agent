#!/usr/bin/env python3
"""
正確なテスト成功率計算スクリプト

pytestのJUnit XMLレポートを解析して正確なテスト結果を集計
"""
import xml.etree.ElementTree as ET
import subprocess
import sys
from pathlib import Path


def run_tests_with_junit():
    """JUnit形式でテストを実行"""
    print("🧪 テスト実行中...")

    # JUnit XMLレポートを生成
    result = subprocess.run(
        ["pytest", "tests/", "--junit-xml=reports/test_results.xml", "--tb=short", "-q"],
        capture_output=True,
        text=True,
    )

    return result.returncode


def analyze_test_results():
    """テスト結果を分析"""
    xml_file = Path("reports/test_results.xml")

    if not xml_file.exists():
        print("❌ テストレポートが生成されていません")
        return None

    tree = ET.parse(xml_file)
    root = tree.getroot()

    total = 0
    passed = 0
    failed = 0
    skipped = 0
    errors = 0

    for testcase in root.findall(".//testcase"):
        total += 1

        # テスト結果の判定
        if testcase.find("failure") is not None:
            failed += 1
        elif testcase.find("error") is not None:
            errors += 1
        elif testcase.find("skipped") is not None:
            skipped += 1
        else:
            passed += 1

    success_rate = (passed / total) * 100 if total > 0 else 0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
        "success_rate": success_rate,
    }


def main():
    """メイン処理"""
    print("📊 正確なテスト成功率計算")
    print("=" * 50)

    # テスト実行
    return_code = run_tests_with_junit()

    # 結果分析
    results = analyze_test_results()

    if results is None:
        sys.exit(1)

    # 結果表示
    print(f"📈 テスト結果サマリー:")
    print(f"   総テスト数: {results['total']}")
    print(f"   成功: {results['passed']}")
    print(f"   失敗: {results['failed']}")
    print(f"   スキップ: {results['skipped']}")
    print(f"   エラー: {results['errors']}")
    print(f"   成功率: {results['success_rate']:.2f}%")
    print(f"   目標: 84.3%")

    # 目標達成判定
    if results["success_rate"] >= 84.3:
        print("✅ テスト成功率目標達成!")
        return True
    else:
        print("❌ テスト成功率目標未達")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

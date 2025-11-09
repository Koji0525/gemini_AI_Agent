"""品質ゲートチェッカー"""

import json
import sys


def check_quality_gate():
    """品質基準をチェック"""
    with open("coverage.json") as f:
        data = json.load(f)

    total_coverage = data["totals"]["percent_covered"]

    # 基準
    MIN_COVERAGE = 70.0

    print(f"�� 品質ゲートチェック")
    print(f"現在のカバレッジ: {total_coverage:.2f}%")
    print(f"最低基準: {MIN_COVERAGE}%")

    if total_coverage >= MIN_COVERAGE:
        print("✅ 品質ゲート合格")
        return 0
    else:
        print("❌ 品質ゲート不合格")
        print(f"不足: {MIN_COVERAGE - total_coverage:.2f}%")
        return 1


if __name__ == "__main__":
    sys.exit(check_quality_gate())

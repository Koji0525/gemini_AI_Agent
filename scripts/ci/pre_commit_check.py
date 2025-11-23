#!/usr/bin/env python3
"""
Pre-commit チェックスクリプト

コミット前に変更ファイルの影響範囲を分析し、
高リスクの変更がある場合は警告を表示する。
"""

import json
import subprocess
import sys


def get_staged_files():
    """ステージされたPythonファイルを取得する."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
    )

    python_files = [f for f in result.stdout.strip().split("\n") if f.endswith(".py") and f]

    return python_files


def analyze_impact(file_path):
    """ファイルの影響範囲を分析する."""
    try:
        # APIサーバーが起動していることを確認
        result = subprocess.run(
            ["curl", "-s", f"http://localhost:5001/api/impact/{file_path}"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data
    except:
        pass

    return None


def main():
    """メイン処理."""
    print("=" * 60)
    print("🔍 Pre-commit チェック: 影響範囲分析")
    print("=" * 60)

    # ステージされたファイル取得
    staged_files = get_staged_files()

    if not staged_files:
        print("✅ 変更されたPythonファイルなし")
        return 0

    print(f"📊 分析対象: {len(staged_files)}ファイル")

    high_risk_files = []

    for file_path in staged_files:
        print(f"\n🔍 分析中: {file_path}")

        impact = analyze_impact(file_path)

        if impact and impact.get("exists"):
            count = impact.get("direct_dependents_count", 0)
            level = impact.get("impact_level", "unknown")

            print(f"   依存: {count}個のファイル")
            print(f"   レベル: {level}")

            if count >= 50 or level == "high":
                high_risk_files.append((file_path, count))

    # 高リスクファイルがある場合は警告
    if high_risk_files:
        print("\n" + "=" * 60)
        print("⚠️  高リスク変更を検出")
        print("=" * 60)

        for file_path, count in high_risk_files:
            print(f"\n🔴 {file_path}")
            print(f"   影響: {count}個のファイルに依存されています")

        print("\n⚠️  注意事項:")
        print("   - 影響範囲テストの実施を推奨します")
        print("   - 変更内容を慎重にレビューしてください")
        print("   - 段階的なデプロイを検討してください")

        # 確認プロンプト
        response = input("\nこのままコミットしますか? (y/N): ")

        if response.lower() != "y":
            print("❌ コミット中止")
            return 1

    print("\n✅ Pre-commitチェック完了")
    return 0


if __name__ == "__main__":
    sys.exit(main())

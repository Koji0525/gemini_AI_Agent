"""API互換性チェックツール"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import re
from typing import Dict, List

# 非推奨メソッドのマッピング
DEPRECATED_METHODS = {
    "GoogleSheetsManager": {
        "write_data": {
            "status": "removed",
            "alternative": "update_range or append_rows",
            "reason": "メソッド名が不明確",
            "migration": """
# Before:
self.sheets.update_range('pm_tasks', [[data]])

# After (更新の場合):
self.sheets.update_range('pm_tasks!A2:Z2', [[data]])

# After (追加の場合):
self.sheets.append_rows('pm_tasks', [[data]])
""",
        },
        "append_row": {
            "status": "removed",
            "alternative": "append_rows (複数形)",
            "reason": "メソッド統一",
            "migration": """
# Before:
self.sheets.append_rows('pm_tasks', [data])

# After:
self.sheets.append_rows('pm_tasks', [[data]])
""",
        },
    },
    "BaseDataAccessor": {
        "write_rows": {
            "status": "not_exist",
            "alternative": "sheets.append_rows or sheets.update_range",
            "reason": "BaseDataAccessorは読み取り専用",
            "migration": """
# Before:
accessor.sheets.append_rows('pm_tasks', rows)

# After:
accessor.sheets.append_rows('pm_tasks', rows)
""",
        }
    },
}


def check_file(file_path: Path) -> List[Dict]:
    """ファイル内の非推奨メソッドをチェック"""

    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            # 各クラスの非推奨メソッドをチェック
            for class_name, methods in DEPRECATED_METHODS.items():
                for method_name, info in methods.items():
                    # パターン: .method_name(
                    pattern = rf"\.{method_name}\("

                    if re.search(pattern, line):
                        issues.append(
                            {
                                "file": str(file_path),
                                "line": i,
                                "class": class_name,
                                "method": method_name,
                                "status": info["status"],
                                "alternative": info["alternative"],
                                "code": line.strip(),
                                "migration": info["migration"],
                            }
                        )

    except Exception:
        pass

    return issues


def scan_project(target_dirs: List[str]) -> List[Dict]:
    """プロジェクト全体をスキャン"""

    all_issues = []

    for target_dir in target_dirs:
        target_path = Path(target_dir)

        if not target_path.exists():
            continue

        for py_file in target_path.rglob("*.py"):
            # 除外パターン
            if any(x in str(py_file) for x in ["__pycache__", ".backup", "test_", "venv"]):
                continue

            issues = check_file(py_file)
            all_issues.extend(issues)

    return all_issues


def main():
    parser = argparse.ArgumentParser(description="API互換性チェック")
    parser.add_argument("--fix", action="store_true", help="自動修正を試みる")
    parser.add_argument("--verbose", action="store_true", help="詳細表示")

    args = parser.parse_args()

    print("=" * 80)
    print("🔍 API互換性チェック")
    print("=" * 80)

    # スキャン対象ディレクトリ
    target_dirs = [
        "/workspaces/gemini_AI_Agent/agents",
        "/workspaces/gemini_AI_Agent/core_agents",
        "/workspaces/gemini_AI_Agent/tools",
    ]

    print("\nスキャン中...")
    issues = scan_project(target_dirs)

    if not issues:
        print("\n✅ 非推奨メソッドは見つかりませんでした")
        return 0

    print(f"\n⚠️ {len(issues)}個の問題を発見")
    print("\n" + "=" * 80)
    print("問題一覧")
    print("=" * 80)

    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {Path(issue['file']).name}:{issue['line']}")
        print(f"   クラス: {issue['class']}")
        print(f"   メソッド: {issue['method']} ({issue['status']})")
        print(f"   代替: {issue['alternative']}")
        print(f"   コード: {issue['code']}")

        if args.verbose:
            print(f"\n   【移行方法】")
            print(issue["migration"])

    if args.fix:
        print("\n" + "=" * 80)
        print("自動修正")
        print("=" * 80)
        print("\n⚠️ 自動修正は未実装です")
        print("手動で修正してください")

    print("\n" + "=" * 80)
    print("推奨アクション")
    print("=" * 80)
    print("\n1. 各ファイルを確認")
    print("2. 代替メソッドに置換")
    print("3. 再度チェック実行")
    print("4. テスト実行")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())

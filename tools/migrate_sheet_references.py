#!/usr/bin/env python3
"""
シート参照の一括置換
統合されたシート名に全ファイルを更新
"""
import os
from pathlib import Path

MIGRATIONS = {
    "project_goal": "project_goal",
    "execution_history": "execution_history",
    "retry_log": "retry_log",
    "learning_patterns": "learning_patterns",
}


def migrate_file(filepath: Path) -> int:
    """1ファイル内のシート参照を置換"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        changes = 0

        for old_name, new_name in MIGRATIONS.items():
            # パターン: "old_name" または 'old_name'
            patterns = [
                (f'"{old_name}"', f'"{new_name}"'),
                (f"'{old_name}'", f"'{new_name}'"),
            ]

            for old_pattern, new_pattern in patterns:
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    changes += content.count(new_pattern) - original.count(new_pattern)

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return changes

        return 0

    except Exception as e:
        print(f"⚠️  スキップ: {filepath} ({e})")
        return 0


def main():
    """メイン処理"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔄 シート参照の一括置換開始")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    total_files = 0
    total_changes = 0

    # プロジェクトルートから.pyファイルを検索
    for root, dirs, files in os.walk("."):
        # アーカイブは除外
        if "_ARCHIVE" in root or "__pycache__" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                changes = migrate_file(filepath)

                if changes > 0:
                    total_files += 1
                    total_changes += changes
                    print(f"✅ {filepath}: {changes}箇所置換")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ 完了: {total_files}ファイル、{total_changes}箇所置換")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    main()

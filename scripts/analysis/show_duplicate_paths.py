#!/usr/bin/env python3
"""
重複ファイルの実際のパスを表示する

目的:
    レポートではファイル名のみ表示されているため、
    実際のフルパスを確認して、バックアップディレクトリ内の
    ファイルかどうかを判別する。
"""

import json
from pathlib import Path


def main():
    project_root = Path("/workspaces/gemini_AI_Agent")
    duplicate_file_path = project_root / "docs/duplicate_files.json"

    with open(duplicate_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 80)
    print("📁 重複ファイルの実際のパス")
    print("=" * 80)

    for group in data["groups"]:
        base_name = group["base_name"]
        files = group["files"]

        print(f"\n{'━' * 80}")
        print(f"グループ: {base_name} ({len(files)}個)")
        print(f"{'━' * 80}")

        # バージョンでソート
        sorted_files = sorted(files, key=lambda x: x.get("version", "base"), reverse=True)

        for idx, file_info in enumerate(sorted_files, 1):
            path = file_info["path"]
            filename = file_info["filename"]
            import_count = file_info["import_count"]

            # バックアップディレクトリ内かチェック
            is_backup = "backup" in path.lower() or "git_cleanup" in path.lower()
            backup_mark = "🗑️ [バックアップ内]" if is_backup else "📄 [通常ディレクトリ]"

            # 参照状況
            ref_mark = f"({import_count}個から参照)" if import_count > 0 else "(未参照)"

            print(f"{idx}. {backup_mark} {ref_mark}")
            print(f"   パス: {path}")
            print(f"   ファイル名: {filename}")
            print()


if __name__ == "__main__":
    main()

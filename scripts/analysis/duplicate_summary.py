#!/usr/bin/env python3
"""
重複ファイルのサマリー生成

目的:
    ダッシュボードで表示する簡潔なサマリー情報を生成する。
    統合は行わず、現状の把握のみ。
"""

import json
from collections import defaultdict
from pathlib import Path


def generate_summary(duplicate_data: dict) -> dict:
    """
    重複ファイルのサマリーを生成する.

    Returns:
        Dict containing:
            - total_groups: 重複グループ数
            - total_files: 重複ファイル総数
            - backup_only: バックアップ内のみの重複数
            - needs_attention: 通常ディレクトリ内の重複数
            - by_version: バージョン別の統計
    """
    groups = duplicate_data.get("groups", [])

    total_groups = len(groups)
    total_files = sum(len(g["files"]) for g in groups)

    backup_only = 0
    needs_attention = 0
    version_stats = defaultdict(int)

    for group in groups:
        files = group["files"]

        # バックアップディレクトリ内かチェック
        normal_files = [
            f
            for f in files
            if not any(
                keyword in f["path"] for keyword in ["backup", "git_cleanup", "_BACKUP", "_ARCHIVE"]
            )
        ]

        if len(normal_files) <= 1:
            backup_only += 1
        else:
            needs_attention += 1

            # バージョン情報を集計
            for file in normal_files:
                filename = file["filename"]
                if "_v" in filename:
                    version_stats[group["base_name"]] += 1

    return {
        "total_groups": total_groups,
        "total_files": total_files,
        "backup_only": backup_only,
        "needs_attention": needs_attention,
        "needs_attention_files": sum(version_stats.values()),
        "groups_needing_attention": list(version_stats.keys()),
        "summary": f"{needs_attention}グループ（{sum(version_stats.values())}ファイル）が通常ディレクトリ内で重複しています",
    }


def main():
    """メイン処理."""
    project_root = Path("/workspaces/gemini_AI_Agent")
    duplicate_file_path = project_root / "docs/duplicate_files.json"
    output_path = project_root / "docs/duplicate_summary.json"

    # データ読み込み
    with open(duplicate_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # サマリー生成
    summary = generate_summary(data)

    # 保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print("📊 重複ファイルサマリー")
    print("=" * 60)
    print(f"重複グループ数: {summary['total_groups']}個")
    print(f"重複ファイル総数: {summary['total_files']}個")
    print()
    print(f"🗑️ バックアップ内のみの重複: {summary['backup_only']}グループ")
    print(
        f"⚠️  通常ディレクトリ内の重複: {summary['needs_attention']}グループ（{summary['needs_attention_files']}ファイル）"
    )
    print()
    print("通常ディレクトリ内で重複しているグループ:")
    for group_name in summary["groups_needing_attention"]:
        print(f"  - {group_name}")
    print()
    print(f"💾 サマリー保存: {output_path}")


if __name__ == "__main__":
    main()

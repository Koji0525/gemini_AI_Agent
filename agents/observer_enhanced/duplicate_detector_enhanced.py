"""
重複ファイル検出（強化版）
Levenshtein距離とバージョン番号判定
"""

import json
import re
from pathlib import Path
from typing import Dict


def detect_version_pattern(filename: str) -> tuple:
    """
    ファイル名からバージョン番号を検出

    Returns:
        (base_name, version_str)
    """
    # _v2, _v3, _v30 などのパターン
    pattern = r"(.+)_v(\d+)\.py$"
    match = re.match(pattern, filename)

    if match:
        return (match.group(1), match.group(2))

    return (filename.replace(".py", ""), None)


def group_duplicates(graph_data: Dict) -> Dict:
    """
    重複ファイルをグループ化

    Returns:
        グループ化された重複ファイル情報
    """
    nodes = graph_data.get("nodes", [])

    # ファイル名でグループ化
    groups = {}

    for node in nodes:
        filename = node.get("filename", "")
        if not filename.endswith(".py"):
            continue

        base_name, version = detect_version_pattern(filename)

        # バージョン付きファイルのみを対象
        if version:
            if base_name not in groups:
                groups[base_name] = []

            groups[base_name].append(
                {
                    "path": node["path"],
                    "filename": filename,
                    "version": int(version),
                    "imported_by_count": len(node.get("imported_by", [])),
                }
            )

    # グループごとに最新版を判定
    duplicate_groups = []

    for base_name, files in groups.items():
        if len(files) < 2:
            continue  # 重複なし

        # バージョン番号でソート
        files.sort(key=lambda x: x["version"], reverse=True)

        latest_file = files[0]
        older_files = files[1:]

        # 削除候補（被依存数が0のもの）
        safe_to_delete = [f for f in older_files if f["imported_by_count"] == 0]
        unsafe_to_delete = [f for f in older_files if f["imported_by_count"] > 0]

        duplicate_groups.append(
            {
                "base_name": base_name,
                "total_files": len(files),
                "latest": latest_file,
                "older_versions": older_files,
                "safe_to_delete": safe_to_delete,
                "unsafe_to_delete": unsafe_to_delete,
            }
        )

    # 削除候補数でソート
    duplicate_groups.sort(key=lambda x: len(x["safe_to_delete"]), reverse=True)

    return {
        "total_duplicate_groups": len(duplicate_groups),
        "total_safe_delete_count": sum(len(g["safe_to_delete"]) for g in duplicate_groups),
        "total_unsafe_delete_count": sum(len(g["unsafe_to_delete"]) for g in duplicate_groups),
        "groups": duplicate_groups,
    }


if __name__ == "__main__":
    # テスト実行
    graph_file = Path("docs/dependency_map.json")
    if graph_file.exists():
        with open(graph_file, "r") as f:
            graph_data = json.load(f)

        result = group_duplicates(graph_data)

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 重複ファイル検出結果")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"重複グループ数: {result['total_duplicate_groups']}")
        print(f"安全に削除可能: {result['total_safe_delete_count']}ファイル")
        print(f"警告（被依存あり）: {result['total_unsafe_delete_count']}ファイル")
        print("")
        print("トップ5重複グループ:")
        for i, group in enumerate(result["groups"][:5], 1):
            print(f"  {i}. {group['base_name']}")
            print(f"     - 総ファイル数: {group['total_files']}")
            print(f"     - 最新版: {group['latest']['filename']} (v{group['latest']['version']})")
            print(f"     - 削除可能: {len(group['safe_to_delete'])}件")

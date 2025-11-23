#!/usr/bin/env python3
"""
重複ファイル検出システム（修正版）

改善点:
1. __init__.py等の除外リスト追加
2. フルパス表示で重複の正確な把握
3. バージョン番号の厳密な検出
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 除外するファイル名（重複検出から除外）
EXCLUDE_FILES = {
    "__init__.py",
    "__main__.py",
    "conftest.py",
    "setup.py",
    "test_*.py",  # テストファイル（パターン）
}


def should_exclude(filename: str) -> bool:
    """除外すべきファイルかどうか判定する."""
    # 厳密一致
    if filename in EXCLUDE_FILES:
        return True

    # パターンマッチ（test_*.py等）
    for pattern in EXCLUDE_FILES:
        if "*" in pattern:
            regex_pattern = pattern.replace("*", ".*")
            if re.match(regex_pattern, filename):
                return True

    return False


def detect_version_pattern(filename: str) -> Tuple[str, str]:
    """
    ファイル名からバージョンパターンを検出する（厳格版）.

    例:
        pm_agent_v2.py → (pm_agent, v2)
        task_executor_v30.py → (task_executor, v30)
        main.py → (main, base) ← バージョンなし

    バージョンパターン:
    - _v数字: _v2, _v3, _v30 など
    - _数字のみ: _2, _3 など（2桁以上）
    """
    # パターン1: _vXX形式（_v2, _v3, _v30など）
    match = re.search(r"(.+?)_v(\d+)\.py$", filename)
    if match:
        base_name = match.group(1)
        version = f"v{match.group(2)}"
        return (base_name, version)

    # パターン2: _XX形式（2桁以上の数字のみ）
    # 1桁は除外（main_1.py等の一時ファイルを除外）
    match = re.search(r"(.+?)_(\d{2,})\.py$", filename)
    if match:
        base_name = match.group(1)
        version = match.group(2)
        return (base_name, version)

    # バージョンなし
    return (filename.replace(".py", ""), "base")


def group_similar_files(files: List[str]) -> Dict[str, List[str]]:
    """
    類似したファイルをグループ化する（改善版）.

    戦略:
    1. 除外ファイルをスキップ
    2. バージョンパターンで厳密グルーピング
    3. フルパスを保持
    """
    version_groups = defaultdict(list)

    for file_path in files:
        filename = os.path.basename(file_path)

        # 除外ファイルチェック
        if should_exclude(filename):
            continue

        base_name, version = detect_version_pattern(filename)

        # バージョンがない場合（baseのみ）は、フルパスで区別
        # 同じディレクトリに複数のmain.pyがある場合のみグループ化
        if version == "base":
            # ディレクトリパスを含めた一意キーにする
            dir_path = os.path.dirname(file_path)
            unique_key = f"{base_name}@{dir_path}"

            version_groups[unique_key].append(
                {
                    "path": file_path,
                    "filename": filename,
                    "base_name": base_name,
                    "version": version,
                    "dir": dir_path,
                }
            )
        else:
            # バージョンがある場合は通常通りグループ化
            version_groups[base_name].append(
                {
                    "path": file_path,
                    "filename": filename,
                    "base_name": base_name,
                    "version": version,
                    "dir": os.path.dirname(file_path),
                }
            )

    # 2個以上のバージョンがあるものを重複とみなす
    duplicates = {}

    for key, file_list in version_groups.items():
        if len(file_list) >= 2:
            # baseの場合は元のbase_nameを使用
            if "@" in key:
                base_name = key.split("@")[0]
            else:
                base_name = key

            duplicates[base_name] = file_list

    return duplicates


def analyze_duplicates(project_root: str, dependency_map_path: str) -> Dict:
    """
    重複ファイルを分析する.
    """
    print("🔍 重複ファイル検出開始...")

    # dependency_map.jsonを読み込み
    with open(dependency_map_path, "r", encoding="utf-8") as f:
        dep_data = json.load(f)

    dependency_map = dep_data.get("dependency_map", {})

    # 全Pythonファイルを収集
    python_files = list(dependency_map.keys())
    print(f"📊 分析対象: {len(python_files)}ファイル")

    # 重複グループを検出
    duplicate_groups = group_similar_files(python_files)
    print(f"🔍 検出された重複グループ: {len(duplicate_groups)}個")

    # 各グループの詳細分析
    results = []

    for base_name, file_list in duplicate_groups.items():
        group_info = {"base_name": base_name, "files": [], "recommendation": None}

        for file_info in file_list:
            file_path = file_info["path"]
            dep_info = dependency_map.get(file_path, {})

            # ファイルの詳細情報
            full_path = Path(project_root) / file_path
            file_stat = {
                "path": file_path,
                "filename": file_info["filename"],
                "version": file_info["version"],
                "directory": file_info["dir"],
                "import_count": dep_info.get("import_count", 0),
                "total_imports": dep_info.get("total_imports", 0),
                "file_size": full_path.stat().st_size if full_path.exists() else 0,
                "last_modified": (
                    datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
                    if full_path.exists()
                    else None
                ),
            }

            group_info["files"].append(file_stat)

        # 最新版を判定（被依存数 > 更新日時の優先順位）
        sorted_files = sorted(
            group_info["files"],
            key=lambda x: (x["import_count"], x["last_modified"] or ""),
            reverse=True,
        )

        if sorted_files:
            # 同じimport_countの場合は警告
            keep_file = sorted_files[0]
            delete_candidates = sorted_files[1:]

            # 同率の場合は警告メッセージ
            same_count_files = [
                f for f in sorted_files if f["import_count"] == keep_file["import_count"]
            ]

            group_info["recommendation"] = {
                "keep": keep_file["path"],
                "reason": f"最も依存されている ({keep_file['import_count']}個から参照)",
                "delete_candidates": [f["path"] for f in delete_candidates],
                "warning": (
                    f"注意: {len(same_count_files)}個のファイルが同じ被依存数"
                    if len(same_count_files) > 1
                    else None
                ),
            }

        results.append(group_info)

    # 被依存数でソート（重要度順）
    results.sort(key=lambda x: max(f["import_count"] for f in x["files"]), reverse=True)

    return {
        "total_groups": len(results),
        "total_duplicates": sum(len(g["files"]) for g in results),
        "groups": results,
        "analysis_time": datetime.now().isoformat(),
    }


def main():
    """メイン処理."""
    project_root = "/workspaces/gemini_AI_Agent"
    dependency_map_path = f"{project_root}/docs/dependency_map.json"
    output_path = f"{project_root}/docs/duplicate_files.json"

    print("=" * 60)
    print("🔍 重複ファイル検出システム（改善版）")
    print("=" * 60)
    print(f"除外ファイル: {', '.join(EXCLUDE_FILES)}")
    print("=" * 60)

    # 重複ファイル分析
    results = analyze_duplicates(project_root, dependency_map_path)

    # 結果保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print("✅ 重複ファイル検出完了")
    print("=" * 60)
    print(f"📊 検出された重複グループ: {results['total_groups']}個")
    print(f"📊 重複ファイル総数: {results['total_duplicates']}個")
    print(f"💾 結果保存先: {output_path}")

    # Top 10重複グループを表示
    if results["groups"]:
        print("\n🏆 Top 10 重複グループ（被依存数順）:")
        for i, group in enumerate(results["groups"][:10], 1):
            max_refs = max(f["import_count"] for f in group["files"])
            print(
                f"\n{i}. {group['base_name']} ({len(group['files'])}個のバージョン, 最大{max_refs}個から参照)"
            )

            for file in group["files"]:
                status = (
                    "✅ 保持推奨"
                    if file["path"] == group["recommendation"]["keep"]
                    else "⚠️  削除候補"
                )
                print(f"   {status}: {file['path']}")
                print(
                    f"              被依存: {file['import_count']}個, サイズ: {file['file_size']:,}B"
                )

            if group["recommendation"].get("warning"):
                print(f"   ⚠️  {group['recommendation']['warning']}")


if __name__ == "__main__":
    main()

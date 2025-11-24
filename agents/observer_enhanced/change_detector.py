"""
依存関係の変化を検出
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List


def load_snapshot(snapshot_path: Path) -> dict:
    """スナップショットを読み込み"""
    with open(snapshot_path, "r") as f:
        return json.load(f)


def compare_dependencies(old_data: dict, new_data: dict) -> dict:
    """2つの依存関係データを比較"""

    old_nodes = {node["id"]: node for node in old_data.get("nodes", [])}
    new_nodes = {node["id"]: node for node in new_data.get("nodes", [])}

    old_edges = set()
    for edge in old_data.get("edges", []):
        old_edges.add((edge["source"], edge["target"]))

    new_edges = set()
    for edge in new_data.get("edges", []):
        new_edges.add((edge["source"], edge["target"]))

    # ファイルの変化
    added_files = set(new_nodes.keys()) - set(old_nodes.keys())
    removed_files = set(old_nodes.keys()) - set(new_nodes.keys())

    # 依存関係の変化
    added_edges = new_edges - old_edges
    removed_edges = old_edges - new_edges

    # 変更されたファイル（依存関係が変わった）
    changed_files = set()
    for node_id in set(old_nodes.keys()) & set(new_nodes.keys()):
        old_deps = set(old_nodes[node_id].get("imports", []))
        new_deps = set(new_nodes[node_id].get("imports", []))
        if old_deps != new_deps:
            changed_files.add(node_id)

    return {
        "summary": {
            "added_files_count": len(added_files),
            "removed_files_count": len(removed_files),
            "changed_files_count": len(changed_files),
            "added_edges_count": len(added_edges),
            "removed_edges_count": len(removed_edges),
        },
        "added_files": [new_nodes[fid] for fid in added_files],
        "removed_files": [old_nodes[fid] for fid in removed_files],
        "changed_files": [
            {
                "file": new_nodes[fid],
                "old_imports": old_nodes[fid].get("imports", []),
                "new_imports": new_nodes[fid].get("imports", []),
                "added_imports": list(
                    set(new_nodes[fid].get("imports", [])) - set(old_nodes[fid].get("imports", []))
                ),
                "removed_imports": list(
                    set(old_nodes[fid].get("imports", [])) - set(new_nodes[fid].get("imports", []))
                ),
            }
            for fid in changed_files
        ],
        "added_edges": [{"source": s, "target": t} for s, t in added_edges],
        "removed_edges": [{"source": s, "target": t} for s, t in removed_edges],
    }


def get_latest_snapshots(snapshot_dir: Path, n: int = 10) -> List[dict]:
    """最新のスナップショット一覧を取得"""
    snapshots = []

    for file in snapshot_dir.glob("dependency_map_*.json"):
        timestamp_str = file.stem.replace("dependency_map_", "")
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            snapshots.append(
                {
                    "filename": file.name,
                    "path": str(file),
                    "timestamp": timestamp.isoformat(),
                    "size": file.stat().st_size,
                }
            )
        except ValueError:
            continue

    snapshots.sort(key=lambda x: x["timestamp"], reverse=True)
    return snapshots[:n]


if __name__ == "__main__":
    # テスト実行
    snapshot_dir = Path("docs/dependency_snapshots")
    current_file = Path("docs/dependency_map.json")

    snapshots = get_latest_snapshots(snapshot_dir)
    print(f"スナップショット数: {len(snapshots)}")

    if len(snapshots) >= 1:
        old_data = load_snapshot(Path(snapshots[0]["path"]))
        new_data = load_snapshot(current_file)

        changes = compare_dependencies(old_data, new_data)
        print("\n変化サマリー:")
        print(f"  追加ファイル: {changes['summary']['added_files_count']}")
        print(f"  削除ファイル: {changes['summary']['removed_files_count']}")
        print(f"  変更ファイル: {changes['summary']['changed_files_count']}")

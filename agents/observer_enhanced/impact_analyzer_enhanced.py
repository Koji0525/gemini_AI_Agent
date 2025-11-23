"""
影響範囲分析（強化版）
多階層BFS探索で依存関係を追跡
"""

import json
from collections import deque
from pathlib import Path
from typing import Dict


def bfs_impact_analysis(graph_data: Dict, target_file: str, max_depth: int = 3) -> Dict:
    """
    BFS探索で影響範囲を分析（多階層）

    Args:
        graph_data: dependency_map.json のデータ
        target_file: 分析対象ファイル
        max_depth: 最大探索階層（デフォルト3）

    Returns:
        階層別影響範囲
    """
    nodes = graph_data.get("nodes", [])

    # ノードIDからノードへのマップ
    node_map = {node["id"]: node for node in nodes}

    # ターゲットファイルを探す
    target_node = None
    for node in nodes:
        if target_file in node["path"]:
            target_node = node
            break

    if not target_node:
        return {
            "target_file": target_file,
            "found": False,
            "error": "File not found in dependency graph",
        }

    # BFS探索
    visited = set()
    queue = deque([(target_node["id"], 0)])  # (node_id, depth)
    impact_by_level = {i: [] for i in range(max_depth + 1)}

    while queue:
        current_id, depth = queue.popleft()

        if current_id in visited or depth > max_depth:
            continue

        visited.add(current_id)
        current_node = node_map.get(current_id)

        if not current_node:
            continue

        # 現在の階層に追加
        if depth > 0:  # ターゲット自身は除く
            impact_by_level[depth].append(
                {
                    "path": current_node["path"],
                    "filename": current_node["filename"],
                    "depth": depth,
                    "imported_by_count": len(current_node.get("imported_by", [])),
                }
            )

        # このファイルを参照しているファイルを探す
        for referencing_file in current_node.get("imported_by", []):
            if referencing_file not in visited:
                queue.append((referencing_file, depth + 1))

    # 階層別影響度スコア
    impact_scores = {}
    for depth in range(1, max_depth + 1):
        score = 100 // (2 ** (depth - 1))  # 1階層:100, 2階層:50, 3階層:25
        impact_scores[f"level_{depth}"] = {
            "count": len(impact_by_level[depth]),
            "score": score,
            "files": impact_by_level[depth][:10],  # トップ10のみ
        }

    # 推奨テスト
    recommended_tests = []
    for depth in range(1, max_depth + 1):
        for file_info in impact_by_level[depth][:5]:  # トップ5
            test_path = file_info["path"].replace(".py", "_test.py").replace("agents/", "tests/")
            recommended_tests.append(
                {
                    "file": file_info["path"],
                    "test": test_path,
                    "priority": "high" if depth == 1 else "medium" if depth == 2 else "low",
                }
            )

    total_impact = sum(len(impact_by_level[i]) for i in range(1, max_depth + 1))

    return {
        "target_file": target_node["path"],
        "found": True,
        "total_impact_count": total_impact,
        "direct_impact": impact_by_level[1],
        "impact_by_level": impact_scores,
        "recommended_tests": recommended_tests[:10],
    }


if __name__ == "__main__":
    # テスト実行
    graph_file = Path("docs/dependency_map.json")
    if graph_file.exists():
        with open(graph_file, "r") as f:
            graph_data = json.load(f)

        # sheets_manager.py の影響範囲を分析
        result = bfs_impact_analysis(graph_data, "sheets_manager.py", max_depth=3)

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("�� 影響範囲分析結果")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"ターゲット: {result['target_file']}")
        print(f"総影響数: {result['total_impact_count']}ファイル")
        print("")
        print("階層別影響:")
        for level_key, level_data in result.get("impact_by_level", {}).items():
            print(f"  {level_key}: {level_data['count']}件（スコア: {level_data['score']}）")

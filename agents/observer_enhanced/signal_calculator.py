"""
信号機表示ロジック
ファイルの被依存数に基づいて変更リスクを可視化
"""

import json
from pathlib import Path
from typing import Dict


def calculate_signal(imported_by_count: int) -> str:
    """
    被依存数から信号機を計算

    Args:
        imported_by_count: 被依存数

    Returns:
        信号機アイコン (🔴🟡🟢💤)
    """
    if imported_by_count >= 20:
        return "🔴"  # 高リスク
    elif imported_by_count >= 10:
        return "🟡"  # 中リスク
    elif imported_by_count >= 1:
        return "🟢"  # 低リスク
    else:
        return "💤"  # 未使用


def calculate_risk_level(imported_by_count: int) -> str:
    """
    被依存数からリスクレベルを計算

    Returns:
        'high', 'medium', 'low', 'unused'
    """
    if imported_by_count >= 20:
        return "high"
    elif imported_by_count >= 10:
        return "medium"
    elif imported_by_count >= 1:
        return "low"
    else:
        return "unused"


def analyze_signals(graph_data: Dict) -> Dict:
    """
    全ファイルの信号機を分析

    Args:
        graph_data: dependency_map.json のデータ

    Returns:
        信号機分析結果
    """
    nodes = graph_data.get("nodes", [])

    signal_counts = {
        "🔴": 0,  # 高リスク
        "🟡": 0,  # 中リスク
        "🟢": 0,  # 低リスク
        "💤": 0,  # 未使用
    }

    signals_by_file = []

    for node in nodes:
        imported_by_count = len(node.get("imported_by", []))
        signal = calculate_signal(imported_by_count)
        risk_level = calculate_risk_level(imported_by_count)

        signal_counts[signal] += 1

        signals_by_file.append(
            {
                "path": node.get("path", ""),
                "filename": node.get("filename", ""),
                "imported_by_count": imported_by_count,
                "signal": signal,
                "risk_level": risk_level,
            }
        )

    # リスクレベルでソート
    signals_by_file.sort(key=lambda x: x["imported_by_count"], reverse=True)

    return {
        "total_files": len(nodes),
        "signal_counts": signal_counts,
        "high_risk_files": [f for f in signals_by_file if f["risk_level"] == "high"],
        "medium_risk_files": [f for f in signals_by_file if f["risk_level"] == "medium"],
        "low_risk_files": [f for f in signals_by_file if f["risk_level"] == "low"],
        "unused_files": [f for f in signals_by_file if f["risk_level"] == "unused"],
        "all_files": signals_by_file,
    }


if __name__ == "__main__":
    # テスト実行
    graph_file = Path("docs/dependency_map.json")
    if graph_file.exists():
        with open(graph_file, "r") as f:
            graph_data = json.load(f)

        result = analyze_signals(graph_data)

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚦 信号機分析結果")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"総ファイル数: {result['total_files']}")
        print(f"🔴 高リスク: {result['signal_counts']['🔴']}件")
        print(f"🟡 中リスク: {result['signal_counts']['🟡']}件")
        print(f"🟢 低リスク: {result['signal_counts']['🟢']}件")
        print(f"💤 未使用: {result['signal_counts']['��']}件")
        print("")
        print("🔴 高リスクファイル（トップ10）:")
        for i, f in enumerate(result["high_risk_files"][:10], 1):
            print(f"  {i}. {f['filename']}: {f['imported_by_count']}箇所から参照")
    else:
        print("❌ dependency_map.json が見つかりません")

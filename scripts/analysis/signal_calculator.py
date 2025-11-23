#!/usr/bin/env python3
"""
信号機表示機能

目的:
    ファイルの被依存数に基づいて、変更リスクを信号機で表示する。

基準:
    🔴 高リスク: 20個以上から参照
    🟡 中リスク: 10-19個から参照
    🟢 低リスク: 1-9個から参照
    💤 未使用: 0個から参照

根拠:
    - 20個以上: sheets_manager.pyなど、システムコアファイル
    - 10個以上: pm_agent.pyなど、主要エージェント
    - 1個以上: 通常のモジュール
    - 0個: 未使用または重複候補
"""

import json
from pathlib import Path
from typing import Dict, Tuple


def calculate_signal(import_count: int) -> Tuple[str, str, str]:
    """
    被依存数から信号機を計算する.

    Args:
        import_count: 被依存数（何個のファイルから参照されているか）

    Returns:
        Tuple of (emoji, color, level):
            - emoji: 信号機の絵文字
            - color: CSSカラーコード
            - level: リスクレベル (high/medium/low/unused)
    """
    if import_count >= 20:
        return ("🔴", "#dc3545", "high")  # 赤: 高リスク
    elif import_count >= 10:
        return ("🟡", "#ffc107", "medium")  # 黄: 中リスク
    elif import_count >= 1:
        return ("🟢", "#28a745", "low")  # 緑: 低リスク
    else:
        return ("💤", "#6c757d", "unused")  # グレー: 未使用


def analyze_signals(dependency_map: Dict) -> Dict:
    """
    全ファイルの信号機情報を生成する.

    Returns:
        Dict containing:
            - total_files: 総ファイル数
            - high_risk: 高リスクファイル数
            - medium_risk: 中リスクファイル数
            - low_risk: 低リスクファイル数
            - unused: 未使用ファイル数
            - files: 各ファイルの信号機情報
    """
    high_risk = []
    medium_risk = []
    low_risk = []
    unused = []

    files_with_signals = {}

    for file_path, file_info in dependency_map.items():
        import_count = file_info.get("import_count", 0)
        emoji, color, level = calculate_signal(import_count)

        file_data = {
            "path": file_path,
            "import_count": import_count,
            "signal_emoji": emoji,
            "signal_color": color,
            "signal_level": level,
            "total_imports": file_info.get("total_imports", 0),
            "imported_by": file_info.get("imported_by", []),
        }

        files_with_signals[file_path] = file_data

        # カテゴリ別に分類
        if level == "high":
            high_risk.append(file_data)
        elif level == "medium":
            medium_risk.append(file_data)
        elif level == "low":
            low_risk.append(file_data)
        else:
            unused.append(file_data)

    # 各カテゴリを被依存数でソート
    high_risk.sort(key=lambda x: x["import_count"], reverse=True)
    medium_risk.sort(key=lambda x: x["import_count"], reverse=True)
    low_risk.sort(key=lambda x: x["import_count"], reverse=True)

    return {
        "total_files": len(dependency_map),
        "high_risk_count": len(high_risk),
        "medium_risk_count": len(medium_risk),
        "low_risk_count": len(low_risk),
        "unused_count": len(unused),
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "unused": unused,
        "files": files_with_signals,
    }


def generate_signal_report(signal_data: Dict) -> str:
    """
    信号機レポートを生成する（Markdown形式）.
    """
    lines = [
        "# 🚦 ファイル変更リスク信号機レポート",
        "",
        f"**分析日時**: {signal_data.get('analysis_time', 'N/A')}",
        f"**総ファイル数**: {signal_data['total_files']:,}個",
        "",
        "---",
        "",
        "## 📊 リスク分布",
        "",
        f"- 🔴 **高リスク**: {signal_data['high_risk_count']}個（20個以上から参照）",
        f"- 🟡 **中リスク**: {signal_data['medium_risk_count']}個（10-19個から参照）",
        f"- 🟢 **低リスク**: {signal_data['low_risk_count']}個（1-9個から参照）",
        f"- 💤 **未使用**: {signal_data['unused_count']}個（0個から参照）",
        "",
        "---",
        "",
        "## 🔴 高リスクファイル（変更注意）",
        "",
        "これらのファイルは多くのファイルから参照されており、変更時は影響範囲が大きくなります。",
        "",
    ]

    if signal_data["high_risk"]:
        lines.append("| ファイル | 被依存数 | 総import数 |")
        lines.append("|---------|---------|-----------|")

        for file in signal_data["high_risk"][:20]:  # Top 20のみ
            lines.append(
                f"| `{file['path']}` " f"| {file['import_count']} " f"| {file['total_imports']} |"
            )
    else:
        lines.append("高リスクファイルはありません。")

    lines.extend(["", "---", ""])

    # 中リスク
    lines.extend(
        [
            "## 🟡 中リスクファイル",
            "",
            "これらのファイルは複数のモジュールから参照されています。",
            "",
        ]
    )

    if signal_data["medium_risk"]:
        lines.append("| ファイル | 被依存数 | 総import数 |")
        lines.append("|---------|---------|-----------|")

        for file in signal_data["medium_risk"][:20]:
            lines.append(
                f"| `{file['path']}` " f"| {file['import_count']} " f"| {file['total_imports']} |"
            )
    else:
        lines.append("中リスクファイルはありません。")

    lines.extend(["", "---", ""])

    # 未使用
    lines.extend(
        [
            "## 💤 未使用ファイル（削除候補）",
            "",
            "これらのファイルはどこからも参照されていません。削除または統合を検討してください。",
            "",
        ]
    )

    if signal_data["unused"]:
        # バックアップディレクトリを除外
        normal_unused = [
            f
            for f in signal_data["unused"]
            if not any(
                keyword in f["path"] for keyword in ["backup", "git_cleanup", "_BACKUP", "_ARCHIVE"]
            )
        ]

        if normal_unused:
            lines.append("| ファイル | ディレクトリ |")
            lines.append("|---------|-------------|")

            for file in normal_unused[:30]:  # Top 30のみ
                lines.append(f"| `{file['path']}` | 通常 |")
        else:
            lines.append("通常ディレクトリ内の未使用ファイルはありません。")
    else:
        lines.append("未使用ファイルはありません。")

    return "\n".join(lines)


def main():
    """メイン処理."""
    project_root = Path("/workspaces/gemini_AI_Agent")
    dependency_map_path = project_root / "docs/dependency_map.json"
    output_json_path = project_root / "docs/signal_analysis.json"
    output_md_path = project_root / "docs/signal_analysis.md"

    print("=" * 60)
    print("🚦 信号機分析システム")
    print("=" * 60)

    # データ読み込み
    with open(dependency_map_path, "r", encoding="utf-8") as f:
        dep_data = json.load(f)

    dependency_map = dep_data.get("dependency_map", {})

    # 信号機分析
    signal_data = analyze_signals(dependency_map)

    # 分析時刻を追加
    from datetime import datetime

    signal_data["analysis_time"] = datetime.now().isoformat()

    # JSON保存
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(signal_data, f, indent=2, ensure_ascii=False)

    # Markdownレポート生成
    report = generate_signal_report(signal_data)
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("=" * 60)
    print("✅ 信号機分析完了")
    print("=" * 60)
    print(f"総ファイル数: {signal_data['total_files']:,}個")
    print()
    print(f"🔴 高リスク: {signal_data['high_risk_count']}個")
    print(f"🟡 中リスク: {signal_data['medium_risk_count']}個")
    print(f"🟢 低リスク: {signal_data['low_risk_count']}個")
    print(f"💤 未使用: {signal_data['unused_count']}個")
    print()

    # Top 5 高リスクファイル
    if signal_data["high_risk"]:
        print("🔴 Top 5 高リスクファイル:")
        for idx, file in enumerate(signal_data["high_risk"][:5], 1):
            print(f"  {idx}. {file['path']}")
            print(f"     被依存数: {file['import_count']}個")

    print()
    print(f"💾 JSON保存: {output_json_path}")
    print(f"💾 レポート保存: {output_md_path}")


if __name__ == "__main__":
    main()

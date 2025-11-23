#!/usr/bin/env python3
"""
重複ファイル分析強化システム

目的:
    重複ファイルの統合判断に必要な詳細情報を提供する。
    自動統合は行わず、人間が安全に判断できる材料を提供。

機能:
    1. バージョン番号の解析（v2, v3, v30, v31など）
    2. 各ファイルの依存関係詳細（どこから参照されているか）
    3. コード差分の可視化
    4. 統合推奨度のスコアリング（安全性評価）
    5. 統合シミュレーション（影響範囲の予測）

出力:
    - 詳細レポート（Markdown形式）
    - 推奨アクション（優先度付き）
    - リスク評価（3段階）
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List


def extract_version_info(filename: str) -> Dict[str, any]:
    """
    ファイル名からバージョン情報を抽出する.

    Args:
        filename: ファイル名（例: pm_agent_v31.py）

    Returns:
        Dict containing:
            - base_name: ベース名（例: pm_agent）
            - version: バージョン番号（例: 31）
            - version_str: バージョン文字列（例: v31）
            - is_versioned: バージョン付きファイルか
    """
    # パターン1: _vXX形式（最も一般的）
    match = re.search(r"(.+?)_v(\d+)\.py$", filename)
    if match:
        return {
            "base_name": match.group(1),
            "version": int(match.group(2)),
            "version_str": f"v{match.group(2)}",
            "is_versioned": True,
            "pattern": "v_number",
        }

    # パターン2: _XX形式（数字のみ）
    match = re.search(r"(.+?)_(\d+)\.py$", filename)
    if match:
        return {
            "base_name": match.group(1),
            "version": int(match.group(2)),
            "version_str": match.group(2),
            "is_versioned": True,
            "pattern": "number_only",
        }

    # バージョンなし
    return {
        "base_name": filename.replace(".py", ""),
        "version": 0,
        "version_str": "base",
        "is_versioned": False,
        "pattern": "no_version",
    }


def calculate_merge_safety_score(file_info: Dict, group_info: List[Dict]) -> Dict:
    """
    統合の安全性をスコアリングする.

    評価基準:
        1. 被依存数（低いほど安全）: 40点
        2. バージョン番号（大きいほど新しい）: 30点
        3. 更新日時（新しいほど良い）: 20点
        4. ファイルサイズ（大きいほど機能が豊富）: 10点

    Returns:
        Dict containing:
            - safety_score: 0-100の安全性スコア
            - risk_level: 'low', 'medium', 'high'
            - recommendations: 推奨アクション
    """
    score = 0
    reasons = []

    # 1. 被依存数評価（低いほど安全）
    import_count = file_info.get("import_count", 0)
    if import_count == 0:
        score += 40
        reasons.append("✅ 依存なし（完全に安全）")
    elif import_count <= 2:
        score += 30
        reasons.append("✅ 依存少（比較的安全）")
    elif import_count <= 5:
        score += 15
        reasons.append("⚠️ 依存中（注意が必要）")
    else:
        score += 0
        reasons.append("❌ 依存多（高リスク）")

    # 2. バージョン番号評価
    version_info = extract_version_info(file_info["filename"])
    max_version = max(extract_version_info(f["filename"])["version"] for f in group_info)

    if version_info["version"] == max_version:
        score += 30
        reasons.append(f"✅ 最新バージョン（{version_info['version_str']}）")
    elif version_info["version"] >= max_version * 0.8:
        score += 20
        reasons.append(f"⚠️ 準最新バージョン（{version_info['version_str']}）")
    else:
        score += 0
        reasons.append(f"❌ 古いバージョン（{version_info['version_str']}）")

    # 3. 更新日時評価
    last_modified = file_info.get("last_modified")
    if last_modified:
        file_date = datetime.fromisoformat(last_modified)
        now = datetime.now()
        days_old = (now - file_date).days

        if days_old <= 7:
            score += 20
            reasons.append(f"✅ 最近更新（{days_old}日前）")
        elif days_old <= 30:
            score += 15
            reasons.append(f"⚠️ 1ヶ月以内に更新（{days_old}日前）")
        else:
            score += 5
            reasons.append(f"❌ 長期間更新なし（{days_old}日前）")

    # 4. ファイルサイズ評価
    file_size = file_info.get("file_size", 0)
    avg_size = sum(f.get("file_size", 0) for f in group_info) / len(group_info)

    if file_size >= avg_size * 1.2:
        score += 10
        reasons.append(f"✅ 平均より大きい（{file_size}B）")
    elif file_size >= avg_size * 0.8:
        score += 5
        reasons.append(f"⚠️ 平均的なサイズ（{file_size}B）")
    else:
        score += 0
        reasons.append(f"❌ 平均より小さい（{file_size}B）")

    # リスクレベル判定
    if score >= 80:
        risk_level = "low"
        risk_text = "🟢 低リスク"
    elif score >= 50:
        risk_level = "medium"
        risk_text = "🟡 中リスク"
    else:
        risk_level = "high"
        risk_text = "🔴 高リスク"

    return {
        "safety_score": score,
        "risk_level": risk_level,
        "risk_text": risk_text,
        "reasons": reasons,
    }


def generate_detailed_report(
    duplicate_groups: List[Dict], dependency_map: Dict, project_root: str
) -> str:
    """
    詳細な分析レポートを生成する（Markdown形式）.
    """
    report_lines = [
        "# 🔍 重複ファイル詳細分析レポート",
        "",
        f"**作成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**分析対象**: {len(duplicate_groups)}グループ",
        "",
        "---",
        "",
        "## 📊 サマリー",
        "",
    ]

    # グループごとに分析
    for idx, group in enumerate(duplicate_groups, 1):
        base_name = group["base_name"]
        files = group["files"]

        report_lines.extend(
            [f"### {idx}. `{base_name}` グループ", "", f"**ファイル数**: {len(files)}個", ""]
        )

        # 各ファイルの詳細
        report_lines.append("| ファイル | バージョン | 被依存数 | サイズ | 更新日時 | 安全性 |")
        report_lines.append("|---------|-----------|---------|--------|---------|--------|")

        for file_info in files:
            version_info = extract_version_info(file_info["filename"])
            safety = calculate_merge_safety_score(file_info, files)

            report_lines.append(
                f"| `{file_info['filename']}` "
                f"| {version_info['version_str']} "
                f"| {file_info['import_count']} "
                f"| {file_info['file_size']:,}B "
                f"| {file_info.get('last_modified', 'N/A')[:10]} "
                f"| {safety['risk_text']} ({safety['safety_score']}点) |"
            )

        # 推奨アクション
        if group.get("recommendation"):
            rec = group["recommendation"]
            report_lines.extend(
                [
                    "",
                    "**推奨アクション**:",
                    f"- ✅ **保持**: `{os.path.basename(rec['keep'])}`",
                    f"  - 理由: {rec['reason']}",
                    "",
                ]
            )

            if rec.get("delete_candidates"):
                report_lines.append("- ⚠️ **統合候補**:")
                for candidate in rec["delete_candidates"]:
                    candidate_info = next(f for f in files if f["path"] == candidate)
                    safety = calculate_merge_safety_score(candidate_info, files)
                    report_lines.append(
                        f"  - `{os.path.basename(candidate)}` "
                        f"({safety['risk_text']}, {safety['safety_score']}点)"
                    )
                report_lines.append("")

        # 依存関係の詳細
        report_lines.extend(["**依存関係の詳細**:", ""])

        for file_info in files:
            file_path = file_info["path"]
            dep_info = dependency_map.get(file_path, {})
            imported_by = dep_info.get("imported_by", [])

            if imported_by:
                report_lines.append(f"- `{file_info['filename']}` は以下から参照されています:")
                for ref in imported_by[:5]:  # 最大5件まで表示
                    report_lines.append(f"  - `{os.path.basename(ref)}`")
                if len(imported_by) > 5:
                    report_lines.append(f"  - ...他 {len(imported_by) - 5}件")
            else:
                report_lines.append(
                    f"- `{file_info['filename']}` はどこからも参照されていません（削除候補）"
                )

            report_lines.append("")

        report_lines.extend(["---", ""])

    # 統合優先度の推奨
    report_lines.extend(
        ["## 🎯 統合優先度の推奨", "", "以下の順序で統合を検討することを推奨します:", ""]
    )

    # 安全性スコアでソート
    all_files_with_safety = []
    for group in duplicate_groups:
        for file_info in group["files"]:
            safety = calculate_merge_safety_score(file_info, group["files"])
            all_files_with_safety.append(
                {"group": group["base_name"], "file": file_info, "safety": safety}
            )

    # 高スコア（安全）順にソート
    sorted_files = sorted(
        all_files_with_safety, key=lambda x: x["safety"]["safety_score"], reverse=True
    )

    priority_groups = defaultdict(list)
    for item in sorted_files:
        risk = item["safety"]["risk_level"]
        priority_groups[risk].append(item)

    # 優先度別に表示
    for priority, label, emoji in [
        ("low", "低リスク（すぐに統合可能）", "🟢"),
        ("medium", "中リスク（慎重に統合）", "🟡"),
        ("high", "高リスク（要注意）", "🔴"),
    ]:
        if priority in priority_groups:
            report_lines.append(f"### {emoji} {label}")
            report_lines.append("")

            for item in priority_groups[priority][:10]:  # 最大10件
                report_lines.append(
                    f"- `{item['file']['filename']}` "
                    f"（グループ: {item['group']}, "
                    f"スコア: {item['safety']['safety_score']}点）"
                )

            report_lines.append("")

    return "\n".join(report_lines)


def main():
    """メイン処理."""
    project_root = "/workspaces/gemini_AI_Agent"
    duplicate_file_path = f"{project_root}/docs/duplicate_files.json"
    dependency_map_path = f"{project_root}/docs/dependency_map.json"
    output_path = f"{project_root}/docs/duplicate_analysis_detailed.md"

    print("=" * 60)
    print("🔍 重複ファイル詳細分析システム")
    print("=" * 60)

    # データ読み込み
    with open(duplicate_file_path, "r", encoding="utf-8") as f:
        duplicate_data = json.load(f)

    with open(dependency_map_path, "r", encoding="utf-8") as f:
        dep_data = json.load(f)

    duplicate_groups = duplicate_data.get("groups", [])
    dependency_map = dep_data.get("dependency_map", {})

    # 詳細レポート生成
    report = generate_detailed_report(duplicate_groups, dependency_map, project_root)

    # レポート保存
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("=" * 60)
    print("✅ 詳細分析完了")
    print("=" * 60)
    print(f"📄 レポート保存先: {output_path}")
    print(f"📊 分析グループ数: {len(duplicate_groups)}個")
    print("")
    print("🎯 次のアクション:")
    print("  1. レポートを確認: cat docs/duplicate_analysis_detailed.md")
    print("  2. 低リスクファイルから順に統合を検討")
    print("  3. 各統合前に file_version_manager.py でバックアップ")
    print("")


if __name__ == "__main__":
    main()

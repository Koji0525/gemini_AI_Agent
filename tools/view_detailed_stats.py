#!/usr/bin/env python3
"""
詳細統計表示
"""
import json
from pathlib import Path
from datetime import datetime


def view_stats():
    stats_dir = Path("logs")
    stats_files = sorted(stats_dir.glob("stats_*.json"), reverse=True)

    if not stats_files:
        print("❌ 統計ファイルが見つかりません")
        return

    print("=" * 80)
    print("📊 タスク実行統計（最新5件）")
    print("=" * 80)

    for stats_file in stats_files[:5]:
        with open(stats_file) as f:
            data = json.load(f)

        print(f"\n📅 {stats_file.stem.replace('stats_', '')}")
        print(f"   実行タスク: {data.get('tasks_executed', 0)}")
        print(f"   エラー数: {data.get('errors_detected', 0)}")
        print(f"   自動修正: {data.get('fixes_applied', 0)}")
        print(f"   実行時間: {data.get('total_time', 0):.2f}秒")

        if data.get("errors_detected", 0) > 0:
            print(f"   ⚠️ エラーが検出されました")


if __name__ == "__main__":
    view_stats()

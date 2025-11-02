#!/usr/bin/env python3
"""
24時間自律開発システム 依頼ツール（最終版）

【再発防止機能】
✅ シート構造の自動検証
✅ 実データ範囲の正確な検出
✅ エラーの事前検出
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.smart_sheets_manager import SmartSheetsManager


def request_development(goal_description: str):
    """開発を依頼"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 24時間自律開発システムに依頼")
    print("   （スマート版 - 再発防止機能付き）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    try:
        manager = SmartSheetsManager()

        # 1. シート構造確認
        print("\n📊 STEP 1: シート構造確認")
        structure = manager.get_sheet_structure("project_goal")
        print(f"   ヘッダー: {structure['headers']}")
        print(f"   現在のデータ行数: {structure['data_rows']}")

        # 2. データ準備
        goal_id = f"GOAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        goal_data = [[goal_id, goal_description, "active", datetime.now().strftime("%Y-%m-%d")]]

        # 3. スマートappend（構造検証付き）
        print(f"\n📝 STEP 2: データ追加（検証付き）")
        print(f"   goal_id: {goal_id}")
        print(f"   description: {goal_description}")

        manager.smart_append_rows(
            "project_goal",
            goal_data,
            expected_columns=["goal_id", "goal_description", "status", "created_at"],
            validate=True,
        )

        print(f"\n✅ 依頼完了！")
        print(f"\n📅 次回の自動実行で処理されます")
        print("   （0:00, 6:00, 12:00, 18:00 JST）")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方:")
        print('  python3 tools/request_development.py "開発目標"')
        sys.exit(1)

    request_development(sys.argv[1])

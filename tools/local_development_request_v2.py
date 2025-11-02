#!/usr/bin/env python3
"""
24時間自律開発システム 依頼ツール v2.0

既存のproject_goalシート構造に完全対応:
  A列: goal_id
  B列: goal_description
  C列: status
  D列: created_at
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.sheets_manager import GoogleSheetsManager


def request_development(goal_description: str):
    """
    開発を依頼

    Args:
        goal_description: 開発目標
    """
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 24時間自律開発システムに依頼 v2.0")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    try:
        sheets_manager = GoogleSheetsManager()

        # goal_id生成
        goal_id = f"GOAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 既存シート構造に合わせたデータ（4列のみ）
        goal_data = [
            [
                goal_id,  # A列: goal_id
                goal_description,  # B列: goal_description
                "active",  # C列: status
                datetime.now().strftime("%Y-%m-%d"),  # D列: created_at
            ]
        ]

        print(f"\n📝 登録データ:")
        print(f"   goal_id: {goal_id}")
        print(f"   description: {goal_description}")
        print(f"   status: active")
        print(f"   created_at: {goal_data[0][3]}")

        print(f"\n📊 書き込み先: project_goal シート")
        sheets_manager.append_rows("project_goal", goal_data)

        print(f"\n✅ 依頼完了！")
        print(f"\n📅 次回の自動実行で処理されます")
        print("   （0:00, 6:00, 12:00, 18:00 JST）")

        print(f"\n🔍 確認方法:")
        print(f"   Google Sheets → project_goal シート")
        print(f"   → 最終行に {goal_id} があるはず")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方:")
        print('  python3 tools/local_development_request_v2.py "開発目標"')
        print("\n例:")
        print('  python3 tools/local_development_request_v2.py "M&Aポータル検索機能実装"')
        sys.exit(1)

    goal = sys.argv[1]
    request_development(goal)

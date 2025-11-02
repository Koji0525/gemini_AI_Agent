#!/usr/bin/env python3
"""
24時間自律開発システム 依頼ツール（修正版）

正しいシート: project_goal
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.sheets_manager import GoogleSheetsManager


def request_development(goal_description: str, priority: str = "high"):
    """
    開発を依頼

    Args:
        goal_description: 開発目標
        priority: 優先度 (high/medium/low)
    """
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 24時間自律開発システムに依頼（修正版）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    try:
        sheets_manager = GoogleSheetsManager()

        # goal_id生成
        goal_id = f"GOAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # project_goalシートに追加（正しいシート名）
        goal_data = [
            [goal_id, goal_description, priority, "active", "0%", datetime.now().isoformat()]
        ]

        print(f"\n📝 登録先シート: project_goal")
        sheets_manager.append_rows("project_goal", goal_data)

        print(f"\n✅ 依頼完了！")
        print(f"   目標ID: {goal_id}")
        print(f"   内容: {goal_description}")
        print(f"   優先度: {priority}")
        print(f"\n📅 次回の自動実行で処理されます")
        print("   （0:00, 6:00, 12:00, 18:00 JST）")

        # 確認
        print(f"\n🔍 確認方法:")
        print(f"   Google Sheets → project_goal シートを開く")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方:")
        print('  python3 tools/local_development_request_fixed.py "開発目標" [優先度]')
        print("\n例:")
        print('  python3 tools/local_development_request_fixed.py "M&Aポータル検索機能実装" high')
        sys.exit(1)

    goal = sys.argv[1]
    priority = sys.argv[2] if len(sys.argv) > 2 else "high"

    request_development(goal, priority)

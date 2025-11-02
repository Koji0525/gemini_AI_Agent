#!/usr/bin/env python3
"""
ローカル開発依頼ツール（GitHub Actions不要）
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.sheets_manager import GoogleSheetsManager

def request_development(goal: str, priority: str = "high"):
    """開発を依頼"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 24時間自律開発システムに依頼（ローカル版）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        sheets_manager = GoogleSheetsManager()
        
        goal_id = f"GOAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        goal_data = [[
            goal_id,
            goal,
            priority,
            "active",
            "0%",
            datetime.now().isoformat()
        ]]
        
        sheets_manager.append_rows('pm_goals', goal_data)
        
        print(f"\n✅ 依頼完了！")
        print(f"   目標ID: {goal_id}")
        print(f"   内容: {goal}")
        print(f"\n📅 次回の自動実行で処理されます")
        print("   （0:00, 6:00, 12:00, 18:00 JST）")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        print("\n💡 .envファイルが正しく設定されているか確認してください")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方:")
        print('  python3 tools/local_development_request.py "開発目標" [優先度]')
        sys.exit(1)
    
    request_development(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "high")

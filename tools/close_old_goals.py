#!/usr/bin/env python3
"""
古い目標を完了にする
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.smart_sheets_manager import SmartSheetsManager

manager = SmartSheetsManager()

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🗓️ 古い目標のクローズ")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# 実データ範囲を検出
last_row = manager.detect_actual_data_range("project_goal")
all_data = manager.read_range(f"project_goal!A2:D{last_row}")

# 30日以上前の目標を抽出
cutoff_date = datetime.now() - timedelta(days=30)
old_goals = []

for i, row in enumerate(all_data, start=2):
    if len(row) >= 3 and row[2] == "active":
        try:
            created = datetime.strptime(row[3], "%Y-%m-%d")
            if created < cutoff_date:
                old_goals.append((i, row))
        except:
            pass

if old_goals:
    print(f"\n⚠️ 30日以上前のアクティブな目標: {len(old_goals)}件\n")

    for row_num, row in old_goals:
        print(f"行{row_num}: {row[0]}")
        print(f"  内容: {row[1][:60]}...")
        print(f"  作成日: {row[3]}")

    print("\n📝 これらの目標を'completed'に変更しますか？")
    print("   手動でスプレッドシートを編集してください")
    print(f"   C列（status）を 'active' → 'completed' に変更")
else:
    print("\n✅ 古いアクティブな目標はありません")

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

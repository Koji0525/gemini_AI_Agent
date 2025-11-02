#!/usr/bin/env python3
"""
誤った形式で登録された目標をクリーンアップ

priority列があるデータ（6列）は削除
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.sheets_manager import GoogleSheetsManager

sheets_manager = GoogleSheetsManager()

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🧹 誤ったデータのクリーンアップ")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# 全データ取得
all_data = sheets_manager.read_range("project_goal!A2:F200")

print(f"\n📋 全データ行数: {len(all_data)}")

# 6列あるデータを特定（誤った形式）
wrong_format = []
for i, row in enumerate(all_data, start=2):  # 2行目から
    if len(row) >= 6:
        # 6列目（F列）にデータがある = 誤った形式
        if row[5]:  # created_atがF列にある
            wrong_format.append((i, row))

if wrong_format:
    print(f"\n⚠️ 誤った形式のデータ: {len(wrong_format)}件")
    print("\n削除候補:")
    for row_num, row in wrong_format:
        print(f"  行{row_num}: {row[0]} - {row[1][:50]}")

    print("\n❌ 手動で削除してください:")
    print("   Google Sheets → project_goal")
    print(f"   → 行{wrong_format[0][0]}から行{wrong_format[-1][0]}を削除")
else:
    print("\n✅ クリーンアップ不要（誤ったデータなし）")

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

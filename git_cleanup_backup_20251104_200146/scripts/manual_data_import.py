#!/usr/bin/env python3
"""
手動データ投入スクリプト - 接続問題時の代替手段
"""

import json

# デモデータ
demo_companies = [
    {
        "title": "テックカンパニーA",
        "industry": "IT・ソフトウェア",
        "location": "東京都渋谷区",
        "capital": 5000,
        "employees": 25,
        "revenue": 15000,
        "deal_type": "売却希望",
        "description": "AIスタートアップ。急成長中のテック企業。",
    },
    {
        "title": "製造業B",
        "industry": "製造業",
        "location": "大阪府大阪市",
        "capital": 8000,
        "employees": 45,
        "revenue": 25000,
        "deal_type": "売却希望",
        "description": "精密部品メーカー。安定した収益あり。",
    },
]

print("📋 手動投入用データ（WordPress管理画面で入力してください）:")
print("=" * 60)

for i, company in enumerate(demo_companies, 1):
    print(f"\n🏢 企業 {i}: {company['title']}")
    print(f"   業種: {company['industry']}")
    print(f"   所在地: {company['location']}")
    print(f"   資本金: {company['capital']}万円")
    print(f"   従業員数: {company['employees']}人")
    print(f"   年商: {company['revenue']}万円")
    print(f"   希望条件: {company['deal_type']}")
    print(f"   説明: {company['description']}")
    print("-" * 40)

print(f"\n💡 手順:")
print("1. WordPress管理画面 → M&A企業情報 → 新規追加")
print("2. 上記データを入力")
print("3. 公開する")
print(f"4. {len(demo_companies)}社分繰り返す")

# データをJSONファイルとして保存
with open("wordpress_projects/ma_portal/manual_import_data.json", "w", encoding="utf-8") as f:
    json.dump(demo_companies, f, ensure_ascii=False, indent=2)

print(f"\n✅ 手動入力データを保存しました: wordpress_projects/ma_portal/manual_import_data.json")

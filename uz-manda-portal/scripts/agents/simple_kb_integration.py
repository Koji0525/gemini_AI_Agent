"""
簡易ナレッジベース連携
Google Sheetsが使えない場合の代替機能
"""

import os
import json
from typing import Dict, List


class SimpleKnowledgeBase:
    def __init__(self):
        self.companies_data = self.load_companies_from_env()

    def load_companies_from_env(self) -> List[Dict]:
        """環境変数から企業データを読み込み"""
        kb_json = os.getenv("KB_COMPANIES_JSON")
        if kb_json:
            try:
                companies = json.loads(kb_json)
                print(f"✅ 環境変数から {len(companies)} 企業を読み込み")
                return companies
            except json.JSONDecodeError as e:
                print(f"❌ JSONデコードエラー: {e}")

        # デフォルトの企業データ
        return [
            {
                "title": "ウズベキスタン現地コンサルティング株式会社",
                "content": """<h2>ウズベキスタン市場専門のコンサルティング企業</h2>
                <p>現地での事業設立、規制対応、パートナー紹介を専門としています。</p>""",
                "industry": "コンサルティング",
                "meta": {
                    "founded_year": "2019",
                    "employees": "30",
                    "capital": "2億円",
                    "location": "タシケント",
                    "special_note": "ウズベキスタン政府との強いネットワーク",
                },
            },
            {
                "title": "中央アジア貿易株式会社",
                "content": """<h2>中央アジアとの貿易事業</h2>
                <p>ウズベキスタン、カザフスタン、キルギスとの貿易業務を展開。</p>""",
                "industry": "貿易",
                "meta": {
                    "founded_year": "2017",
                    "employees": "45",
                    "capital": "3.5億円",
                    "location": "大阪",
                    "business_scope": "農産物、繊維製品の輸入",
                },
            },
        ]

    def get_companies(self) -> List[Dict]:
        """企業データを取得"""
        return self.companies_data


def get_companies_from_simple_kb():
    """簡易ナレッジベースから企業データを取得"""
    kb = SimpleKnowledgeBase()
    return kb.get_companies()

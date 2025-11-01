"""
ナレッジベース連携エージェント
既存のナレッジベースから企業データを取得
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, List, Optional


class KnowledgeBaseIntegration:
    def __init__(self):
        self.setup_google_sheets()

    def setup_google_sheets(self):
        """Google Sheets APIの設定"""
        try:
            # サービスアカウントの認証情報を環境変数から取得
            creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            if creds_json:
                creds_dict = json.loads(creds_json)
                creds = Credentials.from_service_account_info(creds_dict)
            else:
                # デフォルトの認証ファイルを使用
                creds = Credentials.from_service_account_file("credentials.json")

            self.client = gspread.authorize(creds)
            print("✅ Google Sheets接続完了")
        except Exception as e:
            print(f"❌ Google Sheets接続エラー: {e}")
            self.client = None

    def get_companies_from_knowledge_base(self, sheet_name: str = "knowledge_base") -> List[Dict]:
        """ナレッジベースから企業データを取得"""
        if not self.client:
            print("❌ Google Sheetsクライアントが初期化されていません")
            return []

        try:
            # スプレッドシートを開く
            spreadsheet = self.client.open(sheet_name)

            # 企業データが含まれるシートを検索
            available_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
            print(f"📊 利用可能なシート: {available_sheets}")

            companies = []

            # knowledge_baseシートから企業データを取得
            if "knowledge_base" in available_sheets:
                worksheet = spreadsheet.worksheet("knowledge_base")
                records = worksheet.get_all_records()

                for record in records:
                    if self._is_company_record(record):
                        company_data = self._convert_to_company_format(record)
                        companies.append(company_data)

            print(f"✅ ナレッジベースから {len(companies)} 企業を取得")
            return companies

        except Exception as e:
            print(f"❌ ナレッジベース取得エラー: {e}")
            return []

    def _is_company_record(self, record: Dict) -> bool:
        """レコードが企業データか判定"""
        required_fields = ["company_name", "industry", "description"]
        return any(field in record for field in required_fields)

    def _convert_to_company_format(self, record: Dict) -> Dict:
        """ナレッジベース形式から投稿形式に変換"""
        company_data = {
            "title": record.get("company_name", "未設定企業"),
            "content": record.get("description", "説明なし"),
            "industry": record.get("industry", "その他"),
            "meta": {},
        }

        # メタデータのマッピング
        field_mapping = {
            "founded_year": "設立年",
            "employees": "従業員数",
            "capital": "資本金",
            "location": "所在地",
            "revenue": "売上高",
        }

        for meta_key, record_key in field_mapping.items():
            if record_key in record and record[record_key]:
                company_data["meta"][meta_key] = str(record[record_key])

        return company_data


# ナレッジベースから企業データを取得する関数
def get_companies_from_kb():
    """ナレッジベースから企業データを取得"""
    kb_integration = KnowledgeBaseIntegration()
    return kb_integration.get_companies_from_knowledge_base()


if __name__ == "__main__":
    companies = get_companies_from_kb()
    for company in companies:
        print(f"📝 {company['title']} - {company['industry']}")

"""
M&A企業情報 自動投稿エージェント - 最終版
環境変数対応 + 複数データソース対応
"""

import requests
import json
import base64
import time
import os
import sys
from typing import Dict, List, Optional


class MAAutoPosterAgent:
    def __init__(self, wp_url: str = None, username: str = None, password: str = None):
        # 環境変数から設定を読み込み
        self.wp_url = wp_url or os.getenv("WP_URL")
        self.username = username or os.getenv("WP_USERNAME")
        self.password = password or os.getenv("WP_PASSWORD")

        if not all([self.wp_url, self.username, self.password]):
            missing = []
            if not self.wp_url:
                missing.append("WP_URL")
            if not self.username:
                missing.append("WP_USERNAME")
            if not self.password:
                missing.append("WP_PASSWORD")
            raise ValueError(f"必要な環境変数が設定されていません: {', '.join(missing)}")

        self.api_url = f"{self.wp_url.rstrip('/')}/wp-json/wp/v2"
        self.auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        self.headers = {"Content-Type": "application/json", "Authorization": f"Basic {self.auth}"}

        print(f"🔧 WordPress設定: {self.wp_url}")
        print(f"🔧 ユーザー名: {self.username}")

    def test_connection(self) -> bool:
        """WordPress REST API接続テスト"""
        try:
            response = requests.get(f"{self.api_url}/types", headers=self.headers, timeout=10)
            if response.status_code == 200:
                print("✅ WordPress REST API接続成功")
                return True
            else:
                print(f"❌ WordPress接続失敗: {response.status_code}")
                print(f"📋 レスポンス: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 接続エラー: {str(e)}")
            return False

    def check_ma_company_cpt(self) -> bool:
        """ma_companyカスタム投稿タイプの存在確認"""
        try:
            response = requests.get(f"{self.api_url}/types/ma_company", headers=self.headers)
            if response.status_code == 200:
                print("✅ ma_companyカスタム投稿タイプ確認")
                return True
            else:
                print(f"❌ ma_company CPT未登録: {response.status_code}")
                print("💡 以下のいずれかを実行してください:")
                print("   1. functions.phpにCPT定義を追加")
                print("   2. パーマリンク設定を更新（設定 → パーマリンク → 保存）")
                return False
        except Exception as e:
            print(f"❌ CPT確認エラー: {str(e)}")
            return False

    def create_ma_company_post(self, company_data: Dict) -> Optional[int]:
        """M&A企業情報投稿を作成"""

        post_data = {
            "title": company_data["title"],
            "content": company_data["content"],
            "status": "publish",
            "type": "ma_company",
        }

        # 業種タクソノミー処理
        if "industry" in company_data and company_data["industry"]:
            industry_id = self.get_or_create_industry(company_data["industry"])
            if industry_id:
                post_data["ma_industry"] = [industry_id]

        try:
            response = requests.post(f"{self.api_url}/ma-companies", headers=self.headers, json=post_data, timeout=30)

            if response.status_code == 201:
                post_id = response.json()["id"]
                print(f"✅ 投稿作成成功: {company_data['title']} (ID: {post_id})")

                # カスタムフィールド追加
                if "meta" in company_data:
                    self.add_custom_fields(post_id, company_data["meta"])

                return post_id
            else:
                print(f"❌ 投稿作成失敗 {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"❌ 投稿作成エラー: {str(e)}")
            return None

    def get_or_create_industry(self, industry_name: str) -> Optional[int]:
        """業種タームを作成または取得"""
        try:
            # 既存ターム検索
            search_response = requests.get(
                f"{self.api_url}/ma_industry", headers=self.headers, params={"search": industry_name, "per_page": 100}
            )

            if search_response.status_code == 200:
                for term in search_response.json():
                    if term["name"].lower() == industry_name.lower():
                        return term["id"]

            # 新規ターム作成
            term_data = {"name": industry_name, "taxonomy": "ma_industry"}
            create_response = requests.post(f"{self.api_url}/ma_industry", headers=self.headers, json=term_data)

            if create_response.status_code == 201:
                return create_response.json()["id"]
            else:
                print(f"⚠️ 業種作成失敗: {create_response.text}")
                return None

        except Exception as e:
            print(f"❌ 業種処理エラー: {str(e)}")
            return None

    def add_custom_fields(self, post_id: int, meta_data: Dict):
        """カスタムフィールドを追加"""
        for key, value in meta_data.items():
            try:
                meta_response = requests.post(
                    f"{self.api_url}/ma-companies/{post_id}/meta",
                    headers=self.headers,
                    json={"key": key, "value": value},
                )

                if meta_response.status_code == 201:
                    print(f"  ✅ フィールド追加: {key} = {value}")
                else:
                    print(f"  ⚠️ フィールド追加失敗 {key}: {meta_response.text}")
            except Exception as e:
                print(f"  ❌ フィールドエラー {key}: {str(e)}")

    def batch_create_companies(self, companies_data: List[Dict]) -> List[Dict]:
        """複数企業を一括作成"""
        results = []

        for company_data in companies_data:
            print(f"📝 作成中: {company_data['title']}")
            post_id = self.create_ma_company_post(company_data)

            results.append(
                {"title": company_data["title"], "status": "success" if post_id else "failed", "post_id": post_id}
            )

            # API負荷軽減のため少し待機
            time.sleep(1)

        return results


# データソース選択関数
def get_companies_data(source: str = "demo"):
    """
    企業データを取得
    source: "demo" = デモデータ, "kb" = ナレッジベース, "simple_kb" = 簡易ナレッジベース
    """
    if source == "kb":
        try:
            from knowledge_base_integration import get_companies_from_kb

            companies = get_companies_from_kb()
            if companies:
                print("✅ ナレッジベースからデータを取得")
                return companies
        except ImportError as e:
            print(f"⚠️ ナレッジベース連携のインポートエラー: {e}")

    if source == "simple_kb":
        try:
            from simple_kb_integration import get_companies_from_simple_kb

            companies = get_companies_from_simple_kb()
            if companies:
                print("✅ 簡易ナレッジベースからデータを取得")
                return companies
        except ImportError as e:
            print(f"⚠️ 簡易ナレッジベース連携のインポートエラー: {e}")

    # デモデータをフォールバックとして使用
    print("✅ デモデータを使用")
    return generate_demo_companies()


# デモデータ生成関数
def generate_demo_companies():
    """テスト用デモデータ生成"""
    return [
        {
            "title": "メディカルケア株式会社",
            "content": """<h2>医療機器開発のパイオニア企業</h2>
            <p>創業以来、革新的な医療機器の開発に注力し、国内外で特許を多数取得。</p>""",
            "industry": "医療・ヘルスケア",
            "meta": {"founded_year": "2015", "employees": "150", "capital": "5億円", "location": "東京"},
        },
        {
            "title": "株式会社テクノロジーソリューションズ",
            "content": """<h2>AI・IoTソリューション専門企業</h2>
            <p>製造業向けのAI品質検査システムとIoTによる生産管理システムを提供。</p>""",
            "industry": "IT・テクノロジー",
            "meta": {"founded_year": "2018", "employees": "85", "capital": "3億円", "location": "大阪"},
        },
    ]


if __name__ == "__main__":
    try:
        poster = MAAutoPosterAgent()

        # 接続テスト
        if poster.test_connection() and poster.check_ma_company_cpt():
            # データソースを選択（環境変数から取得またはデフォルト）
            data_source = os.getenv("DATA_SOURCE", "demo")
            companies = get_companies_data(data_source)

            results = poster.batch_create_companies(companies)

            # 結果表示
            print("\n📊 実行結果:")
            success_count = sum(1 for r in results if r["status"] == "success")
            print(f"🎯 成功: {success_count}/{len(results)}件")

            for result in results:
                status_icon = "✅" if result["status"] == "success" else "❌"
                print(f"{status_icon} {result['title']} - ID: {result['post_id']}")
        else:
            print("❌ 初期チェック失敗。設定を確認してください。")
    except Exception as e:
        print(f"❌ エージェント初期化エラー: {e}")
        print("💡 環境変数設定を確認してください:")
        print("   export WP_URL=https://your-site.com")
        print("   export WP_USERNAME=admin")
        print("   export WP_PASSWORD=your_password")

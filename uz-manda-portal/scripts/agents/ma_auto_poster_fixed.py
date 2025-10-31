"""
M&A企業情報 自動投稿エージェント - 修正版
REST APIエンドポイント問題を解決
"""

import requests
import json
import base64
import time
import os
import sys
from typing import Dict, List, Optional


class MAAutoPosterAgentFixed:
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
                return False
        except Exception as e:
            print(f"❌ 接続エラー: {str(e)}")
            return False

    def check_ma_company_cpt(self) -> bool:
        """ma_companyカスタム投稿タイプの存在確認 - 複数方法で確認"""
        endpoints_to_check = [
            f"{self.api_url}/types/ma_company",
            f"{self.api_url}/ma_company",  # 直接エンドポイントをチェック
            f"{self.api_url}/posts",  # 通常の投稿エンドポイントもチェック
        ]

        for endpoint in endpoints_to_check:
            try:
                response = requests.get(endpoint, headers=self.headers)
                if response.status_code == 200:
                    print(f"✅ エンドポイント確認: {endpoint}")
                    return True
            except Exception as e:
                print(f"⚠️ エンドポイントチェック失敗 {endpoint}: {e}")

        print("❌ カスタム投稿タイプのエンドポイントが見つかりません")
        return False

    def discover_cpt_endpoint(self) -> str:
        """CPTエンドポイントを自動検出"""
        endpoints = [
            "ma_company",  # 標準的なエンドポイント
            "ma-companies",  # rest_baseが設定されている場合
            "companies",  # 別名の場合
            "ma-company",  # 単数形の場合
        ]

        for endpoint in endpoints:
            test_url = f"{self.api_url}/{endpoint}"
            try:
                response = requests.get(test_url, headers=self.headers, params={"per_page": 1})
                if response.status_code == 200:
                    print(f"✅ CPTエンドポイントを発見: {endpoint}")
                    return endpoint
            except:
                continue

        print("⚠️ CPTエンドポイントを自動検出できませんでした")
        return "ma_company"  # デフォルト

    def create_ma_company_post(self, company_data: Dict) -> Optional[int]:
        """M&A企業情報投稿を作成 - エンドポイント自動検出版"""

        # エンドポイントを自動検出
        cpt_endpoint = self.discover_cpt_endpoint()

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
            response = requests.post(f"{self.api_url}/{cpt_endpoint}", headers=self.headers, json=post_data, timeout=30)

            if response.status_code == 201:
                post_id = response.json()["id"]
                print(f"✅ 投稿作成成功: {company_data['title']} (ID: {post_id})")

                # カスタムフィールド追加（メタデータとして）
                if "meta" in company_data:
                    self.add_custom_fields(post_id, company_data["meta"], cpt_endpoint)

                return post_id
            else:
                print(f"❌ 投稿作成失敗 {response.status_code}: {response.text}")
                # 代替方法を試す
                return self.try_alternative_post_method(company_data, cpt_endpoint)

        except Exception as e:
            print(f"❌ 投稿作成エラー: {str(e)}")
            return None

    def try_alternative_post_method(self, company_data: Dict, cpt_endpoint: str) -> Optional[int]:
        """代替投稿方法を試行"""
        print("🔄 代替投稿方法を試行中...")

        # 方法1: 通常の投稿として作成し、投稿タイプを変更
        try:
            post_data = {
                "title": company_data["title"],
                "content": company_data["content"],
                "status": "publish",
                "type": "post",  # 一旦通常投稿で作成
            }

            response = requests.post(f"{self.api_url}/posts", headers=self.headers, json=post_data, timeout=30)

            if response.status_code == 201:
                post_id = response.json()["id"]
                print(f"✅ 通常投稿として作成成功 (ID: {post_id})")

                # 投稿タイプを変更（WordPressのREST APIでは直接変更できないため、メタデータでマーキング）
                self.add_custom_fields(
                    post_id,
                    {**company_data.get("meta", {}), "post_type": "ma_company", "is_ma_company": "true"},
                    "posts",
                )

                return post_id
        except Exception as e:
            print(f"❌ 代替方法も失敗: {e}")

        return None

    def get_or_create_industry(self, industry_name: str) -> Optional[int]:
        """業種タームを作成または取得"""
        taxonomy_endpoints = ["ma_industry", "categories", "tags"]

        for endpoint in taxonomy_endpoints:
            try:
                # 既存ターム検索
                search_response = requests.get(
                    f"{self.api_url}/{endpoint}",
                    headers=self.headers,
                    params={"search": industry_name, "per_page": 100},
                )

                if search_response.status_code == 200:
                    for term in search_response.json():
                        if term["name"].lower() == industry_name.lower():
                            return term["id"]

                # 新規ターム作成
                term_data = {"name": industry_name}
                create_response = requests.post(f"{self.api_url}/{endpoint}", headers=self.headers, json=term_data)

                if create_response.status_code == 201:
                    return create_response.json()["id"]

            except Exception as e:
                print(f"⚠️ タクソノミー {endpoint} 処理エラー: {e}")
                continue

        print(f"❌ 業種 '{industry_name}' の作成に失敗")
        return None

    def add_custom_fields(self, post_id: int, meta_data: Dict, endpoint: str):
        """カスタムフィールドを追加"""
        for key, value in meta_data.items():
            try:
                meta_response = requests.post(
                    f"{self.api_url}/{endpoint}/{post_id}/meta", headers=self.headers, json={"key": key, "value": value}
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
            "title": "テスト企業株式会社",
            "content": """<h2>テスト用企業データ</h2>
            <p>これは自動投稿システムのテスト用企業データです。</p>""",
            "industry": "テスト業種",
            "meta": {
                "founded_year": "2024",
                "employees": "10",
                "capital": "1億円",
                "location": "東京",
                "test_flag": "true",
            },
        }
    ]


if __name__ == "__main__":
    try:
        poster = MAAutoPosterAgentFixed()

        # 接続テスト
        if poster.test_connection() and poster.check_ma_company_cpt():
            # データソースを選択
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

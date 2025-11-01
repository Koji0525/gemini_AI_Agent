"""
M&A企業情報 自動投稿エージェント - セルフヒーリング連携版
既存のRetryManager, ErrorClassifierと連携
"""

import requests
import json
import base64
import time
import os
import sys
from typing import Dict, List, Optional

# 既存エージェントのインポートを試行
try:
    sys.path.append("../agents")
    from self_healing.retry_manager import RetryManager
    from self_healing.error_classifier import ErrorClassifier
    from self_healing.logging.context_logger import ContextLogger
    from self_healing.feedback.intelligent_feedback import IntelligentFeedbackGenerator

    HAS_SELF_HEALING = True
    print("✅ セルフヒーリングエージェントと連携")
except ImportError as e:
    print(f"⚠️ セルフヒーリングエージェント連携不可: {e}")
    HAS_SELF_HEALING = False


class MAAutoPosterWithHealing:
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

        # セルフヒーリングコンポーネントの初期化
        if HAS_SELF_HEALING:
            self.retry_manager = RetryManager(max_retries=3)
            self.error_classifier = ErrorClassifier()
            self.context_logger = ContextLogger()
            self.feedback_generator = IntelligentFeedbackGenerator()

        print(f"🔧 WordPress設定: {self.wp_url}")
        print(f"🔧 ユーザー名: {self.username}")
        print(f"🔧 セルフヒーリング: {'有効' if HAS_SELF_HEALING else '無効'}")

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
        """ma_companyカスタム投稿タイプの存在確認"""
        endpoints_to_check = [
            f"{self.api_url}/types/ma_company",
            f"{self.api_url}/ma_company",
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

    def create_ma_company_post(self, company_data: Dict) -> Optional[int]:
        """M&A企業情報投稿を作成 - セルフヒーリング対応"""

        if HAS_SELF_HEALING:
            # コンテキストログの記録開始
            self.context_logger.start_context(operation="create_ma_company_post", target_data=company_data)

        def post_operation():
            """実際の投稿操作"""
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

            response = requests.post(f"{self.api_url}/ma_company", headers=self.headers, json=post_data, timeout=30)

            if response.status_code == 201:
                post_id = response.json()["id"]
                print(f"✅ 投稿作成成功: {company_data['title']} (ID: {post_id})")

                # カスタムフィールド追加（ACF対応）
                if "meta" in company_data:
                    self.add_custom_fields_acf(post_id, company_data["meta"])

                return post_id
            else:
                raise Exception(f"投稿作成失敗 {response.status_code}: {response.text}")

        # セルフヒーリング対応の実行
        if HAS_SELF_HEALING:
            try:
                result = self.retry_manager.execute_with_retry(post_operation)

                if result:
                    self.context_logger.log_success(result=result, additional_info={"company": company_data["title"]})

                return result

            except Exception as e:
                error_type = "unknown_error"  # TODO: ErrorClassifierが未実装(str(e))
                self.context_logger.log_error(
                    error=str(e), error_type=error_type, recovery_actions=["check_cpt_endpoint", "verify_permissions"]
                )

                # インテリジェントフィードバック生成
                feedback = self.feedback_generator.generate_feedback(
                    error=str(e), context=self.context_logger.get_current_context()
                )
                print(f"💡 改善提案: {feedback}")

                return None
        else:
            # セルフヒーリングなしの通常実行
            try:
                return post_operation()
            except Exception as e:
                print(f"❌ 投稿作成エラー: {str(e)}")
                return None

    def add_custom_fields_acf(self, post_id: int, meta_data: Dict):
        """ACFカスタムフィールドを追加 - メタデータ方式"""
        print(f"🔧 カスタムフィールド追加: {len(meta_data)}項目")

        for key, value in meta_data.items():
            try:
                # メタデータとして追加
                meta_response = requests.post(
                    f"{self.api_url}/ma_company/{post_id}/meta", headers=self.headers, json={"key": key, "value": value}
                )

                if meta_response.status_code == 201:
                    print(f"  ✅ フィールド追加: {key} = {value}")
                else:
                    # 代替方法: コンテンツ内に埋め込み
                    self.add_field_to_content(post_id, key, value)

            except Exception as e:
                print(f"  ⚠️ フィールド追加失敗 {key}: {e}")

    def add_field_to_content(self, post_id: int, key: str, value: str):
        """フィールドをコンテンツ内に埋め込む代替方法"""
        try:
            # 現在の投稿を取得
            response = requests.get(f"{self.api_url}/ma_company/{post_id}", headers=self.headers)
            if response.status_code == 200:
                post_data = response.json()
                current_content = post_data.get("content", {}).get("rendered", "")

                # フィールド情報をコンテンツに追加
                new_content = f"{current_content}<p><strong>{key}:</strong> {value}</p>"

                # 投稿を更新
                update_response = requests.post(
                    f"{self.api_url}/ma_company/{post_id}", headers=self.headers, json={"content": new_content}
                )

                if update_response.status_code == 200:
                    print(f"  🔄 フィールドをコンテンツに追加: {key}")
                else:
                    print(f"  ❌ コンテンツ更新失敗: {key}")

        except Exception as e:
            print(f"  ❌ 代替方法も失敗: {key} - {e}")

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
            term_data = {"name": industry_name}
            create_response = requests.post(f"{self.api_url}/ma_industry", headers=self.headers, json=term_data)

            if create_response.status_code == 201:
                return create_response.json()["id"]
            else:
                print(f"⚠️ 業種作成失敗: {create_response.text}")
                return None

        except Exception as e:
            print(f"❌ 業種処理エラー: {str(e)}")
            return None

    def batch_create_companies(self, companies_data: List[Dict]) -> List[Dict]:
        """複数企業を一括作成 - 進捗表示付き"""
        results = []
        total = len(companies_data)

        for i, company_data in enumerate(companies_data, 1):
            print(f"📝 作成中 ({i}/{total}): {company_data['title']}")
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
            "title": "テスト企業株式会社 - セルフヒーリング版",
            "content": """<h2>セルフヒーリング連携テスト企業</h2>
            <p>この企業データはセルフヒーリング機能と連携した自動投稿システムで作成されました。</p>
            <h3>特徴</h3>
            <ul>
                <li>自動リトライ機能対応</li>
                <li>エラー分類と分析</li>
                <li>インテリジェントフィードバック生成</li>
            </ul>""",
            "industry": "テクノロジー",
            "meta": {
                "founded_year": "2024",
                "employees": "50",
                "capital": "10億円",
                "location": "東京",
                "special_note": "セルフヒーリングテスト企業",
            },
        },
        {
            "title": "中央アジア貿易株式会社 - 連携版",
            "content": """<h2>中央アジア貿易専門企業</h2>
            <p>ウズベキスタン、カザフスタンとの貿易業務を展開。</p>""",
            "industry": "貿易",
            "meta": {"founded_year": "2018", "employees": "35", "capital": "5億円", "location": "大阪"},
        },
    ]


if __name__ == "__main__":
    try:
        poster = MAAutoPosterWithHealing()

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

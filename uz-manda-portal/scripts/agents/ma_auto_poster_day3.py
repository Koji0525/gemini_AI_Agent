"""
Day 3専用: M&A企業情報 自動投稿エージェント
セルフヒーリング連携（正しい初期化）
"""

import requests
import json
import base64
import time
import os
import sys
from typing import Dict, List, Optional

# 親プロジェクトへのパス設定
PARENT_PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, PARENT_PROJECT)

# セルフヒーリングエージェント連携（オプション）
HAS_SELF_HEALING = False
try:
    from agents.self_healing.retry_manager import RetryManager
    from agents.self_healing.utils.error_classifier import ErrorClassifier

    HAS_SELF_HEALING = True
    print("✅ セルフヒーリングエージェント連携成功")
except ImportError as e:
    print(f"⚠️ セルフヒーリング機能なし（基本機能で動作）: {e}")


class MAAutoPosterDay3:
    """Day 3専用: 5社一括投稿エージェント"""

    def __init__(self, wp_url: str = None, username: str = None, password: str = None):
        # WordPress設定
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

        # セルフヒーリング機能（正しい初期化）
        self.retry_manager = None
        self.error_classifier = None

        if HAS_SELF_HEALING:
            try:
                # RetryManagerを引数なしで初期化（実際の実装に合わせる）
                self.retry_manager = RetryManager()
                self.error_classifier = ErrorClassifier()
                print("✅ セルフヒーリング機能: 有効")
            except Exception as e:
                print(f"⚠️ セルフヒーリング初期化失敗: {e}")
                self.retry_manager = None
        else:
            print("⚠️ セルフヒーリング機能: 無効（基本機能のみ）")

        print(f"🔧 WordPress: {self.wp_url}")
        print(f"🔧 ユーザー: {self.username}")

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

    def create_ma_company_post(self, company_data: Dict) -> Optional[int]:
        """M&A企業情報投稿を作成（リトライ機能付き）"""

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 投稿データ作成
                post_data = {"title": company_data["title"], "content": company_data["content"], "status": "publish"}

                # 業種タクソノミー追加
                if "industry" in company_data and company_data["industry"]:
                    industry_id = self.get_or_create_industry(company_data["industry"])
                    if industry_id:
                        post_data["ma_industry"] = [industry_id]

                # 投稿作成
                response = requests.post(f"{self.api_url}/ma_company", headers=self.headers, json=post_data, timeout=30)

                if response.status_code == 201:
                    post_id = response.json()["id"]
                    print(f"✅ 投稿作成成功: {company_data['title']} (ID: {post_id})")

                    # カスタムフィールド追加
                    if "meta" in company_data:
                        self.add_custom_fields(post_id, company_data["meta"])

                    return post_id
                else:
                    error_msg = f"投稿作成失敗 {response.status_code}: {response.text}"

                    # エラー分類（セルフヒーリングがあれば）
                    if self.error_classifier:
                        error_type = self.error_classifier.classify_error(error_msg)
                        print(f"⚠️ エラー分類: {error_type}")

                    raise Exception(error_msg)

            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = retry_count * 2  # 指数バックオフ
                    print(f"⚠️ リトライ {retry_count}/{max_retries} ({wait_time}秒後)")
                    time.sleep(wait_time)
                else:
                    print(f"❌ 投稿作成エラー（最終）: {str(e)}")
                    return None

        return None

    def add_custom_fields(self, post_id: int, meta_data: Dict):
        """DD項目をカスタムフィールドとして追加"""
        print(f"🔧 DD項目追加: {len(meta_data)}項目")

        # DD項目一覧を取得
        response = requests.get(f"{self.api_url}/ma_company/{post_id}", headers=self.headers)
        if response.status_code != 200:
            print("⚠️ 投稿取得失敗")
            return

        post_data = response.json()
        current_content = post_data.get("content", {}).get("rendered", "")

        # DD情報セクションを構築
        dd_html = "\n\n<!-- DD情報セクション -->\n"
        dd_html += '<div class="dd-information" style="margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 8px;">\n'
        dd_html += '<h3 style="color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px;">📊 デューデリジェンス情報</h3>\n'
        dd_html += '<table style="width: 100%; border-collapse: collapse; margin-top: 15px;">\n'

        for key, value in meta_data.items():
            # キーを日本語に変換（見やすく）
            display_key = self._format_key(key)
            dd_html += f'<tr style="border-bottom: 1px solid #ddd;">\n'
            dd_html += f'  <td style="padding: 10px; font-weight: bold; width: 30%;">{display_key}</td>\n'
            dd_html += f'  <td style="padding: 10px;">{value}</td>\n'
            dd_html += f"</tr>\n"

        dd_html += "</table>\n"
        dd_html += "</div>\n"

        # コンテンツを更新
        new_content = current_content + dd_html

        try:
            update_response = requests.post(
                f"{self.api_url}/ma_company/{post_id}", headers=self.headers, json={"content": new_content}
            )

            if update_response.status_code == 200:
                print(f"  ✅ DD情報セクション追加完了")
            else:
                print(f"  ⚠️ 更新失敗: {update_response.status_code}")

        except Exception as e:
            print(f"  ❌ DD情報追加エラー: {e}")

    def _format_key(self, key: str) -> str:
        """キー名を日本語表示に変換"""
        key_map = {
            "founded_year": "設立年",
            "capital": "資本金",
            "employees": "従業員数",
            "location": "所在地",
            "revenue": "売上高",
            "profit": "利益",
            "main_clients": "主要取引先",
            "main_business": "主要事業",
            "main_products": "主要製品",
            "strengths": "強み",
            "aum": "運用資産",
            "deal_count": "年間案件数",
            "dd_completion": "DD完了度",
        }
        return key_map.get(key, key)

    def get_or_create_industry(self, industry_name: str) -> Optional[int]:
        """業種タームを作成または取得"""
        try:
            # 既存ターム検索
            search_response = requests.get(
                f"{self.api_url}/ma_industry", headers=self.headers, params={"search": industry_name, "per_page": 100}
            )

            if search_response.status_code == 200:
                terms = search_response.json()
                for term in terms:
                    if term["name"].lower() == industry_name.lower():
                        print(f"  📂 既存業種使用: {industry_name}")
                        return term["id"]

            # 新規ターム作成
            create_response = requests.post(
                f"{self.api_url}/ma_industry", headers=self.headers, json={"name": industry_name}
            )

            if create_response.status_code == 201:
                print(f"  ✨ 新規業種作成: {industry_name}")
                return create_response.json()["id"]

        except Exception as e:
            print(f"  ⚠️ 業種処理エラー: {str(e)}")

        return None

    def batch_create_companies(self, companies_data: List[Dict]) -> List[Dict]:
        """5社を一括投稿"""
        results = []
        total = len(companies_data)

        print(f"\n{'='*60}")
        print(f"🚀 一括投稿開始: {total}社")
        print(f"{'='*60}\n")

        for i, company_data in enumerate(companies_data, 1):
            print(f"📝 [{i}/{total}] {company_data['title']}")
            print("-" * 60)

            post_id = self.create_ma_company_post(company_data)

            results.append(
                {
                    "title": company_data["title"],
                    "status": "success" if post_id else "failed",
                    "post_id": post_id,
                    "industry": company_data.get("industry", ""),
                    "dd_items": len(company_data.get("meta", {})),
                }
            )

            if i < total:
                print("\n⏱️  API負荷軽減のため2秒待機...\n")
                time.sleep(2)

        return results


# ==
# Day 3用データ: 5社の企業情報（DD項目付き）
# ==
def get_day3_companies():
    """Day 3達成用: 5社の詳細データ"""
    return [
        {
            "title": "株式会社グローバルトレード・ジャパン",
            "content": """
<h2>🌏 企業概要</h2>
<p>中央アジア・東南アジア地域との国際貿易を専門とする総合商社。特にウズベキスタン、カザフスタンとの取引実績が豊富で、現地パートナー企業とのネットワークを活用した貿易仲介業務を展開しています。</p>

<h3>💼 主要事業内容</h3>
<ul>
    <li><strong>貿易仲介業務</strong>: 日本企業とアジア企業のマッチング</li>
    <li><strong>現地パートナー開拓</strong>: 中央アジア地域での新規取引先開拓</li>
    <li><strong>物流コンサルティング</strong>: 国際物流の最適化提案</li>
    <li><strong>市場調査サービス</strong>: 現地市場の詳細分析</li>
</ul>

<h3>🎯 強み</h3>
<p>15年以上にわたって構築した中央アジアネットワーク、現地語対応可能なスタッフ、迅速な物流手配能力が当社の主な強みです。</p>
            """,
            "industry": "貿易・商社",
            "meta": {
                "founded_year": "2015年",
                "capital": "3億円",
                "employees": "45名",
                "location": "東京都港区六本木",
                "revenue": "年商20億円",
                "profit": "営業利益2億円",
                "main_clients": "ウズベキスタン企業5社、カザフスタン企業3社",
                "strengths": "中央アジアネットワーク、現地語対応",
                "dd_completion": "85%",
            },
        },
        {
            "title": "アジア物流ソリューションズ株式会社",
            "content": """
<h2>🚚 総合物流サービス</h2>
<p>アジア全域をカバーする国際物流の専門企業。海上輸送、航空輸送、陸上輸送を組み合わせた最適な物流ソリューションを提供しています。</p>

<h3>📦 サービス内容</h3>
<ul>
    <li><strong>国際輸送</strong>: 海上・航空・陸上の複合輸送</li>
    <li><strong>倉庫管理</strong>: 保税倉庫を含む総合倉庫サービス</li>
    <li><strong>通関業務</strong>: 迅速な通関手続き代行</li>
    <li><strong>ラストワンマイル配送</strong>: 現地での最終配送</li>
</ul>
            """,
            "industry": "物流",
            "meta": {
                "founded_year": "2012年",
                "capital": "5億円",
                "employees": "120名",
                "location": "大阪府大阪市北区",
                "revenue": "年商50億円",
                "profit": "営業利益5億円",
                "main_business": "国際物流、倉庫管理、通関業務",
                "strengths": "アジア全域ネットワーク、保税倉庫保有",
                "dd_completion": "90%",
            },
        },
        {
            "title": "中央アジアビジネスコンサルティング株式会社",
            "content": """
<h2>💡 コンサルティングサービス</h2>
<p>中央アジア進出を目指す日本企業向けの専門コンサルティング。現地法規制、ビジネス慣習、パートナー選定など、進出に必要なあらゆる情報を提供します。</p>

<h3>🎓 サービス領域</h3>
<ul>
    <li><strong>市場調査</strong>: 詳細な現地市場分析</li>
    <li><strong>進出戦略立案</strong>: 最適な進出形態の提案</li>
    <li><strong>パートナー紹介</strong>: 信頼できる現地企業の紹介</li>
    <li><strong>法務サポート</strong>: 現地法規制への対応支援</li>
</ul>
            """,
            "industry": "コンサルティング",
            "meta": {
                "founded_year": "2018年",
                "capital": "1億円",
                "employees": "25名",
                "location": "東京都千代田区丸の内",
                "revenue": "年商8億円",
                "profit": "営業利益1.5億円",
                "main_clients": "日本企業30社以上",
                "strengths": "現地ネットワーク、法務専門家在籍",
                "dd_completion": "75%",
            },
        },
        {
            "title": "株式会社テクノロジー・ブリッジ",
            "content": """
<h2>💻 IT×国際ビジネス</h2>
<p>ITソリューションで国際ビジネスを効率化。貿易管理システム、多言語対応CRM、越境ECプラットフォームなど、グローバルビジネスに特化したシステムを開発・提供しています。</p>

<h3>🛠️ 主要製品・サービス</h3>
<ul>
    <li><strong>貿易管理システム</strong>: 書類作成から輸送追跡まで一元管理</li>
    <li><strong>多言語CRM</strong>: 20言語対応の顧客管理システム</li>
    <li><strong>越境ECプラットフォーム</strong>: アジア市場向けEC構築</li>
    <li><strong>データ分析ツール</strong>: 貿易データの可視化・分析</li>
</ul>
            """,
            "industry": "IT・テクノロジー",
            "meta": {
                "founded_year": "2020年",
                "capital": "2億円",
                "employees": "35名（エンジニア25名）",
                "location": "東京都渋谷区",
                "revenue": "年商12億円",
                "profit": "営業利益2億円",
                "main_products": "貿易管理システム、多言語CRM",
                "strengths": "グローバル対応、アジア言語対応",
                "dd_completion": "80%",
            },
        },
        {
            "title": "日本アジア投資パートナーズ株式会社",
            "content": """
<h2>💰 投資・M&A仲介</h2>
<p>アジア企業とのM&A案件を専門とする投資会社。日本企業のアジア進出支援、アジア企業の日本市場参入支援、クロスボーダーM&Aの仲介を主要業務としています。</p>

<h3>📈 主要サービス</h3>
<ul>
    <li><strong>M&A仲介</strong>: 日本-アジア間のM&A案件仲介</li>
    <li><strong>投資コンサルティング</strong>: 投資先の発掘・評価</li>
    <li><strong>デューデリジェンス</strong>: 財務・法務・ビジネスDD</li>
    <li><strong>PMI支援</strong>: M&A後の統合サポート</li>
</ul>

<h3>🏆 実績</h3>
<p>過去5年間で15件のクロスボーダーM&A案件を成約。総取引額は100億円を超えています。</p>
            """,
            "industry": "投資・金融",
            "meta": {
                "founded_year": "2016年",
                "capital": "10億円",
                "employees": "30名",
                "location": "東京都中央区日本橋",
                "aum": "運用資産100億円",
                "deal_count": "年間案件数15件",
                "revenue": "年商15億円",
                "profit": "営業利益3億円",
                "strengths": "M&A実績、ネットワーク、DD能力",
                "dd_completion": "95%",
            },
        },
    ]


if __name__ == "__main__":
    print("⚠️ このファイルは直接実行できません")
    print("📝 run_day3_mission.py を使用してください")

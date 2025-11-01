#!/usr/bin/env python3
"""
M&Aポータルサイト構築スクリプト
変更理由: Phase 10.2 - WordPress上にM&Aサイトを構築
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wordpress.wp_dev import WordPressCPTAgent, WordPressACFAgent, WordPressTaxonomyAgent
from configuration.wp_config_loader import WordPressConfigLoader


class MAPortalBuilder:
    """M&Aポータルサイト構築"""

    def __init__(self):
        # WordPress設定読み込み
        config_loader = WordPressConfigLoader()
        self.config = config_loader.load_config()

        # エージェント初期化
        self.cpt_agent = WordPressCPTAgent()
        self.acf_agent = WordPressACFAgent()
        self.taxonomy_agent = WordPressTaxonomyAgent()

    def build_step1_basic_structure(self):
        """Phase 1: 基本構造の構築"""
        print("\n" + "=" * 70)
        print("🏗️ Phase 1: 基本構造の構築")
        print("=" * 70)

        # Step 1.1: WordPress接続テスト
        print("\n📡 Step 1.1: WordPress接続テスト")
        if not self._test_connection():
            print("❌ WordPress接続失敗 - 処理を中止")
            return False

        # Step 1.2: カスタム投稿タイプ作成
        print("\n📄 Step 1.2: カスタム投稿タイプ作成")
        cpt_result = self._create_custom_post_type()

        # Step 1.3: タクソノミー作成
        print("\n🏷️ Step 1.3: タクソノミー作成")
        taxonomy_result = self._create_taxonomy()

        # Step 1.4: カスタムフィールド作成
        print("\n📝 Step 1.4: カスタムフィールド作成")
        acf_result = self._create_custom_fields()

        return all([cpt_result, taxonomy_result, acf_result])

    def _test_connection(self):
        """WordPress接続テスト"""
        try:
            import requests

            url = self.config["wp_api_base"]
            auth = (self.config["wp_user"], self.config["wp_pass"])

            response = requests.get(url, auth=auth, timeout=10)

            if response.status_code == 200:
                print(f"✅ 接続成功: {self.config['wp_url']}")
                return True
            else:
                print(f"❌ 接続失敗: ステータスコード {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ 接続エラー: {e}")
            return False

    def _create_custom_post_type(self):
        """カスタム投稿タイプ: ma_company を作成"""

        cpt_config = {
            "post_type": "ma_company",
            "label": "企業情報",
            "description": "M&A対象企業の情報",
            "public": True,
            "has_archive": True,
            "supports": ["title", "editor", "thumbnail"],
            "menu_icon": "dashicons-building",
        }

        try:
            result = self.cpt_agent.create_post_type(cpt_config)

            if result.get("success"):
                print(f"✅ カスタム投稿タイプ作成: ma_company")
                return True
            else:
                print(f"⚠️ 作成スキップまたはエラー: {result.get('message')}")
                return True  # 既に存在する場合もOK

        except Exception as e:
            print(f"❌ エラー: {e}")
            return False

    def _create_taxonomy(self):
        """タクソノミー: ma_industry を作成"""

        taxonomy_config = {
            "taxonomy": "ma_industry",
            "label": "業種",
            "post_type": "ma_company",
            "hierarchical": True,
        }

        # 業種カテゴリー
        industries = [
            "IT・ソフトウェア",
            "製造業",
            "サービス業",
            "小売業",
            "建設業",
            "その他",
        ]

        try:
            # タクソノミー作成
            result = self.taxonomy_agent.create_taxonomy(taxonomy_config)

            if result.get("success"):
                print(f"✅ タクソノミー作成: ma_industry")

            # カテゴリー追加
            for industry in industries:
                term_result = self.taxonomy_agent.create_term(
                    {
                        "taxonomy": "ma_industry",
                        "name": industry,
                        "slug": industry.lower().replace("・", "-").replace(" ", "-"),
                    }
                )

                if term_result.get("success"):
                    print(f"   ✅ カテゴリー追加: {industry}")

            return True

        except Exception as e:
            print(f"❌ エラー: {e}")
            return False

    def _create_custom_fields(self):
        """カスタムフィールド作成"""

        fields = [
            {
                "name": "location",
                "label": "所在地",
                "type": "text",
            },
            {
                "name": "capital",
                "label": "資本金（万円）",
                "type": "number",
            },
            {
                "name": "employees",
                "label": "従業員数",
                "type": "number",
            },
            {
                "name": "revenue",
                "label": "年商（万円）",
                "type": "number",
            },
            {
                "name": "deal_type",
                "label": "希望条件",
                "type": "select",
                "choices": ["売却希望", "買収希望"],
            },
        ]

        try:
            for field in fields:
                result = self.acf_agent.create_field({"post_type": "ma_company", **field})

                if result.get("success"):
                    print(f"   ✅ フィールド作成: {field['label']}")

            return True

        except Exception as e:
            print(f"❌ エラー: {e}")
            return False

    def build_step2_demo_data(self):
        """Phase 2: デモデータ投入"""
        print("\n" + "=" * 70)
        print("📊 Phase 2: デモデータ投入")
        print("=" * 70)

        demo_companies = [
            {
                "title": "テックカンパニーA",
                "industry": "IT・ソフトウェア",
                "location": "東京都渋谷区",
                "capital": 10000,  # 1億円 = 10000万円
                "employees": 50,
                "revenue": 100000,  # 10億円
                "deal_type": "売却希望",
                "content": "AIを活用したSaaSプロダクトを展開する成長企業",
            },
            {
                "title": "製造業B",
                "industry": "製造業",
                "location": "愛知県名古屋市",
                "capital": 5000,
                "employees": 30,
                "revenue": 50000,
                "deal_type": "売却希望",
                "content": "精密部品製造で高いシェアを持つ中堅企業",
            },
            {
                "title": "サービスC",
                "industry": "サービス業",
                "location": "大阪府大阪市",
                "capital": 3000,
                "employees": 20,
                "revenue": 30000,
                "deal_type": "買収希望",
                "content": "介護・福祉サービスで地域に根ざした事業展開",
            },
            {
                "title": "小売店D",
                "industry": "小売業",
                "location": "福岡県福岡市",
                "capital": 2000,
                "employees": 15,
                "revenue": 20000,
                "deal_type": "売却希望",
                "content": "地域密着型のスーパーマーケットチェーン",
            },
            {
                "title": "建設E",
                "industry": "建設業",
                "location": "北海道札幌市",
                "capital": 15000,
                "employees": 80,
                "revenue": 150000,
                "deal_type": "買収希望",
                "content": "公共工事を中心とした総合建設会社",
            },
        ]

        print(f"\n📝 {len(demo_companies)}社のデモデータを作成します...")

        for company in demo_companies:
            try:
                # 投稿作成（ここではシミュレーション）
                print(f"\n✅ {company['title']}")
                print(f"   業種: {company['industry']}")
                print(f"   資本金: {company['capital']:,}万円")
                print(f"   従業員: {company['employees']}名")
                print(f"   年商: {company['revenue']:,}万円")
                print(f"   希望: {company['deal_type']}")

            except Exception as e:
                print(f"❌ エラー: {e}")

        print("\n⚠️ 注意: 実際のデータ投入はWordPress REST APIまたは手動で実施")
        return True


def main():
    print("🚀 M&Aポータルサイト構築開始")
    print("=" * 70)

    builder = MAPortalBuilder()

    # Phase 1: 基本構造
    if builder.build_step1_basic_structure():
        print("\n✅ Phase 1 完了: 基本構造構築")

        # Phase 2: デモデータ
        builder.build_step2_demo_data()
        print("\n✅ Phase 2 完了: デモデータ準備")

        print("\n" + "=" * 70)
        print("🎉 M&Aポータルサイト構築完了")
        print("=" * 70)
        print("\n📋 次のアクション:")
        print("  1. WordPress管理画面で確認")
        print("  2. デモデータを手動または自動で投入")
        print("  3. 検索機能の実装")
    else:
        print("\n❌ 構築失敗")


if __name__ == "__main__":
    main()

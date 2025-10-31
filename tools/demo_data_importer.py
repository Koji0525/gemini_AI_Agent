#!/usr/bin/env python3
"""
デモデータ自動投入ツール（堅牢版）
変更理由: エラーハンドリング強化、事前チェック追加
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wordpress.wp_dev.wp_rest_client import WordPressRESTClient
from configuration.wp_config_loader import WordPressConfigLoader


class DemoDataImporter:
    """デモデータ自動投入（堅牢版）"""

    def __init__(self):
        config_loader = WordPressConfigLoader()
        self.config = config_loader.load_config()
        self.client = WordPressRESTClient(self.config["wp_url"], self.config["wp_user"], self.config["wp_pass"])

    def import_from_json(self, json_path: str) -> bool:
        """JSONからデモデータを投入"""
        print("📊 デモデータ自動投入")
        print("=" * 70)

        # 事前チェック
        if not self._pre_check():
            print("\n❌ 事前チェック失敗")
            print("\n💡 解決策:")
            print("   1. functions.phpにコードを追加")
            print("   2. WordPressで「設定 → パーマリンク設定」を開いて保存")
            print("   3. 再度このスクリプトを実行")
            return False

        # JSON読み込み
        with open(json_path, "r", encoding="utf-8") as f:
            demo_data = json.load(f)

        print(f"\n✅ 事前チェック完了")
        print(f"📋 投入予定: {len(demo_data)}件の企業データ\n")

        results = []
        success_count = 0

        for i, company in enumerate(demo_data, 1):
            print(f"[{i}/{len(demo_data)}] {company['title']} を投入中...")

            try:
                result = self._create_company_post(company)

                if result.get("success"):
                    print(f"   ✅ 成功 (ID: {result.get('post_id')})")
                    success_count += 1
                else:
                    print(f"   ❌ 失敗: {result.get('error')}")

                results.append(result)

            except Exception as e:
                print(f"   ❌ エラー: {e}")
                results.append({"success": False, "error": str(e)})

        print("\n" + "=" * 70)
        print(f"📊 投入結果: {success_count}/{len(demo_data)}件成功")
        print("=" * 70)

        return success_count > 0

    def _pre_check(self) -> bool:
        """事前チェック"""
        import requests

        # カスタム投稿タイプの存在確認
        url = f"{self.config['wp_api_base']}/ma_company"

        try:
            response = requests.get(url, auth=(self.config["wp_user"], self.config["wp_pass"]), timeout=10)

            # 200 or 401 ならエンドポイント存在
            # 404 ならエンドポイント未登録
            if response.status_code in [200, 401]:
                return True
            elif response.status_code == 404:
                print("\n⚠️ カスタム投稿タイプ 'ma_company' が未登録です")
                return False
            else:
                print(f"\n⚠️ 不明なエラー (HTTP {response.status_code})")
                return False

        except Exception as e:
            print(f"\n❌ 接続エラー: {e}")
            return False

    def _create_company_post(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """企業投稿を作成"""
        import requests

        # 投稿作成
        post_data = {
            "title": company["title"],
            "content": company["content"],
            "status": "publish",
        }

        url = f"{self.config['wp_api_base']}/ma_company"

        response = requests.post(url, json=post_data, auth=(self.config["wp_user"], self.config["wp_pass"]), timeout=30)

        if response.status_code != 201:
            return {"success": False, "error": f"HTTP {response.status_code}"}

        post_id = response.json()["id"]

        # 業種設定（エラーは無視）
        try:
            if "industry" in company:
                self._set_taxonomy(post_id, "ma_industry", company["industry"])
        except:
            pass

        # カスタムフィールド設定（エラーは無視）
        try:
            self._set_custom_fields(post_id, company)
        except:
            pass

        return {"success": True, "post_id": post_id, "title": company["title"]}

    def _set_taxonomy(self, post_id: int, taxonomy: str, term_name: str) -> None:
        """タクソノミーを設定"""
        import requests

        # ターム検索
        term_url = f"{self.config['wp_api_base']}/{taxonomy}"
        response = requests.get(
            term_url, params={"search": term_name}, auth=(self.config["wp_user"], self.config["wp_pass"]), timeout=10
        )

        if response.status_code == 200:
            terms = response.json()
            if terms:
                term_id = terms[0]["id"]

                # 投稿にターム設定
                post_url = f"{self.config['wp_api_base']}/ma_company/{post_id}"
                requests.post(
                    post_url,
                    json={"ma_industry": [term_id]},
                    auth=(self.config["wp_user"], self.config["wp_pass"]),
                    timeout=10,
                )

    def _set_custom_fields(self, post_id: int, company: Dict[str, Any]) -> None:
        """カスタムフィールドを設定"""
        import requests

        fields = {
            "location": company.get("location"),
            "capital": company.get("capital"),
            "employees": company.get("employees"),
            "revenue": company.get("revenue"),
            "deal_type": company.get("deal_type"),
        }

        # フィールドごとに設定
        for field_name, value in fields.items():
            if value is not None:
                meta_url = f"{self.config['wp_api_base']}/ma_company/{post_id}"
                requests.post(
                    meta_url,
                    json={"meta": {field_name: value}},
                    auth=(self.config["wp_user"], self.config["wp_pass"]),
                    timeout=10,
                )


def main():
    import sys

    if len(sys.argv) < 2:
        print("使い方: python3 demo_data_importer.py <demo_data.json>")
        sys.exit(1)

    json_path = sys.argv[1]

    if not Path(json_path).exists():
        print(f"❌ エラー: ファイルが見つかりません: {json_path}")
        sys.exit(1)

    importer = DemoDataImporter()
    success = importer.import_from_json(json_path)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

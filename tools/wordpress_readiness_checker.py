#!/usr/bin/env python3
"""
WordPress環境チェッカー
変更理由: 実行前に環境を検証、問題を事前検出
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wordpress.wp_dev.wp_rest_client import WordPressRESTClient
from configuration.wp_config_loader import WordPressConfigLoader


class WordPressReadinessChecker:
    """WordPress環境の準備状態をチェック"""

    def __init__(self):
        config_loader = WordPressConfigLoader()
        self.config = config_loader.load_config()
        self.client = WordPressRESTClient(self.config["wp_url"], self.config["wp_user"], self.config["wp_pass"])

    def check_all(self) -> bool:
        """全チェック実行"""
        print("🔍 WordPress環境チェック")
        print("=" * 70)

        checks = [
            ("WordPress接続", self._check_connection),
            ("カスタム投稿タイプ 'ma_company'", self._check_post_type),
            ("タクソノミー 'ma_industry'", self._check_taxonomy),
            ("ACFプラグイン", self._check_acf_plugin),
        ]

        results = []

        for check_name, check_func in checks:
            print(f"\n📋 {check_name}をチェック中...")
            result = check_func()
            results.append(result)

            if result["status"] == "ok":
                print(f"   ✅ {result['message']}")
            elif result["status"] == "warning":
                print(f"   ⚠️  {result['message']}")
            else:
                print(f"   ❌ {result['message']}")

        # サマリー
        print("\n" + "=" * 70)
        print("📊 チェック結果サマリー")
        print("=" * 70)

        ok_count = sum(1 for r in results if r["status"] == "ok")
        warning_count = sum(1 for r in results if r["status"] == "warning")
        error_count = sum(1 for r in results if r["status"] == "error")

        print(f"\n✅ OK: {ok_count}")
        print(f"⚠️  警告: {warning_count}")
        print(f"❌ エラー: {error_count}")

        # 推奨アクション
        print("\n" + "=" * 70)
        print("💡 推奨アクション")
        print("=" * 70)

        for result in results:
            if result["status"] != "ok" and "action" in result:
                print(f"\n{result['action']}")

        all_ok = error_count == 0

        if all_ok:
            print("\n✅ 環境は準備完了です！")
        else:
            print("\n⚠️ 上記の問題を解決してから実行してください")

        return all_ok

    def _check_connection(self) -> dict:
        """WordPress接続チェック"""
        try:
            import requests

            response = requests.get(self.config["wp_url"], timeout=10)

            if response.status_code == 200:
                return {"status": "ok", "message": f"接続成功 ({self.config['wp_url']})"}
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}",
                    "action": "WordPressサイトが正常に動作しているか確認してください",
                }
        except Exception as e:
            return {"status": "error", "message": str(e), "action": "ネットワーク接続とWordPress URLを確認してください"}

    def _check_post_type(self) -> dict:
        """カスタム投稿タイプの存在チェック"""
        try:
            import requests

            url = f"{self.config['wp_api_base']}/types"
            response = requests.get(url, auth=(self.config["wp_user"], self.config["wp_pass"]), timeout=10)

            if response.status_code == 200:
                post_types = response.json()

                if "ma_company" in post_types:
                    return {"status": "ok", "message": "'ma_company' が登録されています"}
                else:
                    return {
                        "status": "error",
                        "message": "'ma_company' が未登録です",
                        "action": """【必須】functions.phpにコードを追加してください:
   1. cat wordpress_projects/ma_portal/PASTE_TO_WORDPRESS.txt
   2. https://uzbek-ma.com/wp-admin/theme-editor.php
   3. functions.phpの最後に貼り付け
   4. 保存""",
                    }
            else:
                return {"status": "error", "message": f"チェック失敗 (HTTP {response.status_code})"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _check_taxonomy(self) -> dict:
        """タクソノミーの存在チェック"""
        try:
            import requests

            url = f"{self.config['wp_api_base']}/taxonomies"
            response = requests.get(url, auth=(self.config["wp_user"], self.config["wp_pass"]), timeout=10)

            if response.status_code == 200:
                taxonomies = response.json()

                if "ma_industry" in taxonomies:
                    return {"status": "ok", "message": "'ma_industry' が登録されています"}
                else:
                    return {"status": "warning", "message": "'ma_industry' が未登録（functions.php追加で自動作成）"}
            else:
                return {"status": "warning", "message": "チェックできませんでした"}
        except Exception as e:
            return {"status": "warning", "message": str(e)}

    def _check_acf_plugin(self) -> dict:
        """ACFプラグインのチェック"""
        # REST API経由でのプラグインチェックは制限があるため簡易的に
        return {
            "status": "warning",
            "message": "ACFプラグインは手動確認が必要です",
            "action": """ACFプラグインがインストール済みか確認:
   WordPress管理画面 → プラグイン → インストール済みプラグイン
   未インストールの場合: プラグイン → 新規追加 → "Advanced Custom Fields" で検索""",
        }


def main():
    checker = WordPressReadinessChecker()
    is_ready = checker.check_all()

    sys.exit(0 if is_ready else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
WordPress既存コード調査スクリプト
変更理由: functions.php や既存のカスタム投稿タイプを確認し、競合を回避
"""

import sys
from pathlib import Path
import re

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wordpress.wp_dev.wp_rest_client import WordPressRESTClient
from configuration.wp_config_loader import WordPressConfigLoader


class WordPressCodeInvestigator:
    """WordPress既存コード調査"""

    def __init__(self):
        config_loader = WordPressConfigLoader()
        self.config = config_loader.load_config()
        self.client = WordPressRESTClient(self.config["wp_url"], self.config["wp_user"], self.config["wp_pass"])

    def run_full_investigation(self):
        """完全な調査を実行"""
        print("🔍 WordPress既存コード調査開始")
        print("=" * 70)

        # 1. 既存の投稿タイプを調査
        print("\n📋 Step 1: 既存の投稿タイプを調査")
        self._check_post_types()

        # 2. 既存のタクソノミーを調査
        print("\n🏷️ Step 2: 既存のタクソノミーを調査")
        self._check_taxonomies()

        # 3. プラグイン状況を調査
        print("\n🔌 Step 3: インストール済みプラグインを調査")
        self._check_plugins()

        # 4. 安全な実装方針を提案
        print("\n" + "=" * 70)
        print("💡 実装方針の提案")
        print("=" * 70)
        self._suggest_implementation_strategy()

    def _check_post_types(self):
        """既存の投稿タイプを確認"""
        try:
            import requests

            # REST APIで投稿タイプ一覧を取得
            url = f"{self.config['wp_api_base']}/types"
            response = requests.get(url, auth=(self.config["wp_user"], self.config["wp_pass"]), timeout=10)

            if response.status_code == 200:
                post_types = response.json()

                print("\n既存の投稿タイプ:")
                for pt_key, pt_data in post_types.items():
                    name = pt_data.get("name", pt_key)
                    print(f"   • {pt_key}: {name}")

                # ma_company が既に存在するかチェック
                if "ma_company" in post_types:
                    print("\n⚠️ 重要: 'ma_company' は既に存在します！")
                    print("   対策: 既存のものを使用するか、別名で作成（例: ma_company_v2）")
                else:
                    print("\n✅ 'ma_company' は未使用 - 安全に作成可能")
            else:
                print(f"⚠️ 投稿タイプ取得失敗: {response.status_code}")

        except Exception as e:
            print(f"❌ エラー: {e}")

    def _check_taxonomies(self):
        """既存のタクソノミーを確認"""
        try:
            import requests

            url = f"{self.config['wp_api_base']}/taxonomies"
            response = requests.get(url, auth=(self.config["wp_user"], self.config["wp_pass"]), timeout=10)

            if response.status_code == 200:
                taxonomies = response.json()

                print("\n既存のタクソノミー:")
                for tax_key, tax_data in taxonomies.items():
                    name = tax_data.get("name", tax_key)
                    print(f"   • {tax_key}: {name}")

                # ma_industry が既に存在するかチェック
                if "ma_industry" in taxonomies:
                    print("\n⚠️ 重要: 'ma_industry' は既に存在します！")
                else:
                    print("\n✅ 'ma_industry' は未使用 - 安全に作成可能")
            else:
                print(f"⚠️ タクソノミー取得失敗: {response.status_code}")

        except Exception as e:
            print(f"❌ エラー: {e}")

    def _check_plugins(self):
        """インストール済みプラグインを確認"""
        print("\n主要プラグインの確認:")
        print("   ℹ️ REST APIではプラグイン情報取得に制限があります")
        print("   推奨: WordPress管理画面で以下を確認")
        print("     • Advanced Custom Fields (ACF)")
        print("     • Custom Post Type UI")
        print("     • SearchWP または Relevanssi（検索機能強化）")

    def _suggest_implementation_strategy(self):
        """安全な実装方針を提案"""

        suggestions = """
🎯 安全な実装方針

### 方針1: 既存コードを確認してから追加（推奨）
1. WordPress管理画面 → 外観 → テーマファイルエディター
2. functions.php を開いて既存コードを確認
3. 以下をチェック:
   - register_post_type で 'ma_company' が既に登録されていないか
   - register_taxonomy で 'ma_industry' が既に登録されていないか
4. 競合がない場合のみ、新規コードを追加

### 方針2: 関数名にプレフィックスを追加
既存コードと競合しないよう、関数名を工夫:

❌ 競合リスク:
function create_ma_company_post_type() { }

✅ 安全:
function uzbek_ma_create_company_post_type() { }

### 方針3: プラグインで実装（最も安全）
Custom Post Type UI プラグインを使用:
- GUI で簡単に作成
- コード編集不要
- 競合リスク最小

### 方針4: 子テーマで実装
親テーマの functions.php を直接編集せず、子テーマで実装:
- テーマ更新時も安全
- 変更を独立管理

---

🔧 次のステップ（推奨順）

1. 【最優先】WordPress管理画面で functions.php の内容確認
   → https://uzbek-ma.com/wp-admin/theme-editor.php

2. 既存コードをこのスクリプトに貼り付けて解析
   → 競合チェックスクリプトを実行

3. 安全性確認後、実装方針を決定
   → プラグイン使用 or コード追加

4. バックアップ取得
   → functions.php のバックアップを保存
        """

        print(suggestions)


def main():
    print("🚀 WordPress既存コード調査ツール")

    investigator = WordPressCodeInvestigator()
    investigator.run_full_investigation()

    print("\n" + "=" * 70)
    print("📝 次のアクション")
    print("=" * 70)
    print("1. WordPress管理画面で functions.php を確認")
    print("2. 既存コードがあれば、このスクリプトに貼り付けて解析")
    print("3. 安全性を確認してから実装開始")


if __name__ == "__main__":
    main()

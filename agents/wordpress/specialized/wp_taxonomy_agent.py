#!/usr/bin/env python3
"""
WPTaxonomyAgent - WordPressタクソノミー管理エージェント
PHPコード生成アプローチ + スプレッドシート記録

v2.0 - ログ記録機能追加
運用ルール準拠: 1ファイル1000行以下、PEP 8準拠
"""

import sys
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, "/workspaces/gemini_AI_Agent")
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager
from agents.wordpress.specialized.wp_agent_logger import WPAgentLogger


@dataclass
class TaxonomySpecification:
    """タクソノミーの仕様"""

    taxonomy: str
    singular_name: str
    plural_name: str
    post_types: List[str] = field(default_factory=lambda: ["post"])
    description: str = ""
    public: bool = True
    hierarchical: bool = True
    show_admin_column: bool = True
    show_in_rest: bool = True
    rewrite_slug: Optional[str] = None

    def __post_init__(self):
        if self.rewrite_slug is None:
            self.rewrite_slug = self.taxonomy


class WPTaxonomyAgent:
    """WordPressタクソノミー管理エージェント"""

    def __init__(
        self, config_loader: ConfigLoader, sheets_manager: Optional[GoogleSheetsManager] = None
    ):
        """
        初期化（依存性注入）

        Args:
            config_loader: ConfigLoaderインスタンス
            sheets_manager: GoogleSheetsManagerインスタンス（オプション）
        """
        self.config = config_loader
        self.wp_url = self.config._config.get("WP_URL")
        self.wp_user = self.config._config.get("wp_user")
        self.wp_pass = self.config._config.get("wp_pass")
        self.auth = (self.wp_user, self.wp_pass)

        # ロガーの初期化
        self.logger = WPAgentLogger(sheets_manager) if sheets_manager else None

    async def list_taxonomies(self) -> Dict[str, Any]:
        """既存のタクソノミー一覧を取得"""
        print("\n📋 既存のタクソノミーを取得中...")
        try:
            response = requests.get(
                f"{self.wp_url}/wp-json/wp/v2/taxonomies", auth=self.auth, timeout=10
            )

            if response.status_code == 200:
                taxonomies = response.json()
                print(f"✅ タクソノミー数: {len(taxonomies)}個")

                standard_taxonomies = [
                    "category",
                    "post_tag",
                    "nav_menu",
                    "link_category",
                    "post_format",
                ]

                custom_taxonomies = {
                    k: v for k, v in taxonomies.items() if k not in standard_taxonomies
                }

                if custom_taxonomies:
                    print(f"   カスタムタクソノミー: {len(custom_taxonomies)}個")
                    for tax_name, tax_data in custom_taxonomies.items():
                        print(f"   - {tax_name}: {tax_data.get('name', 'N/A')}")

                return taxonomies
            else:
                print(f"❌ 取得失敗: Status {response.status_code}")
                return {}

        except Exception as e:
            print(f"❌ エラー: {e}")
            return {}

    async def verify_taxonomy(self, taxonomy: str) -> bool:
        """タクソノミーの存在を確認"""
        try:
            response = requests.get(
                f"{self.wp_url}/wp-json/wp/v2/taxonomies/{taxonomy}", auth=self.auth, timeout=10
            )

            if response.status_code == 200:
                print(f"✅ タクソノミー '{taxonomy}' が存在します")
                return True
            else:
                print(f"❌ タクソノミー '{taxonomy}' は存在しません")
                return False

        except Exception as e:
            print(f"❌ エラー: {e}")
            return False

    def generate_php_code(self, spec: TaxonomySpecification) -> str:
        """register_taxonomy()のPHPコードを生成"""
        print(f"\n🔧 PHPコード生成中: {spec.taxonomy}")

        post_types_str = "array('" + "', '".join(spec.post_types) + "')"

        if spec.hierarchical:
            labels = {
                "name": spec.plural_name,
                "singular_name": spec.singular_name,
                "search_items": f"{spec.plural_name}を検索",
                "all_items": f"すべての{spec.plural_name}",
                "parent_item": f"親{spec.singular_name}",
                "parent_item_colon": f"親{spec.singular_name}:",
                "edit_item": f"{spec.singular_name}を編集",
                "update_item": f"{spec.singular_name}を更新",
                "add_new_item": f"新しい{spec.singular_name}を追加",
                "new_item_name": f"新しい{spec.singular_name}名",
                "menu_name": spec.plural_name,
            }
        else:
            labels = {
                "name": spec.plural_name,
                "singular_name": spec.singular_name,
                "search_items": f"{spec.plural_name}を検索",
                "popular_items": f"人気の{spec.plural_name}",
                "all_items": f"すべての{spec.plural_name}",
                "edit_item": f"{spec.singular_name}を編集",
                "update_item": f"{spec.singular_name}を更新",
                "add_new_item": f"新しい{spec.singular_name}を追加",
                "new_item_name": f"新しい{spec.singular_name}名",
                "menu_name": spec.plural_name,
            }

        labels_str = "array(\n"
        for key, value in labels.items():
            labels_str += f"        '{key}' => '{value}',\n"
        labels_str += "    )"

        php_code = f"""<?php
/**
 * カスタムタクソノミー: {spec.plural_name}
 * タイプ: {'階層型（カテゴリー）' if spec.hierarchical else '非階層型（タグ）'}
 * 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

function register_taxonomy_{spec.taxonomy}() {{
    $labels = {labels_str};
    
    $args = array(
        'labels' => $labels,
        'description' => '{spec.description}',
        'public' => {str(spec.public).lower()},
        'hierarchical' => {str(spec.hierarchical).lower()},
        'show_ui' => true,
        'show_in_menu' => true,
        'show_in_nav_menus' => true,
        'show_admin_column' => {str(spec.show_admin_column).lower()},
        'show_in_rest' => {str(spec.show_in_rest).lower()},
        'rewrite' => array('slug' => '{spec.rewrite_slug}'),
    );
    
    register_taxonomy('{spec.taxonomy}', {post_types_str}, $args);
}}

add_action('init', 'register_taxonomy_{spec.taxonomy}');
?>"""

        print("✅ PHPコード生成完了")
        return php_code

    def save_php_code(self, php_code: str, filename: str) -> str:
        """生成したPHPコードをファイルに保存"""
        import os

        output_dir = "/workspaces/gemini_AI_Agent/agent_outputs/wordpress_taxonomy"
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(php_code)

        print(f"✅ PHPコード保存: {filepath}")
        return filepath

    async def create_taxonomy(self, spec: TaxonomySpecification) -> Dict[str, Any]:
        """カスタムタクソノミーを作成（PHPコード生成）"""
        print("=" * 80)
        print(f"🚀 カスタムタクソノミー作成: {spec.plural_name}")
        print("=" * 80)

        result = {
            "success": False,
            "taxonomy": spec.taxonomy,
            "php_code": "",
            "filepath": "",
            "instructions": [],
        }

        # 1. 既存の確認
        existing = await self.verify_taxonomy(spec.taxonomy)
        if existing:
            print(f"⚠️  タクソノミー '{spec.taxonomy}' は既に存在します")
            result["success"] = False
            result["message"] = "既に存在します"
            return result

        # 2. PHPコード生成
        php_code = self.generate_php_code(spec)
        result["php_code"] = php_code

        # 3. ファイルに保存
        filename = f"taxonomy_{spec.taxonomy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.php"
        filepath = self.save_php_code(php_code, filename)
        result["filepath"] = filepath

        # 4. 配置方法の指示
        taxonomy_type = "階層型（カテゴリー風）" if spec.hierarchical else "非階層型（タグ風）"
        instructions = [
            f"📋 カスタムタクソノミー（{taxonomy_type}）の有効化手順:",
            "",
            "【方法1: functions.phpに追加】",
            f"1. 生成されたコード ({filepath}) を開く",
            "2. <?php と ?> を除いたコードをコピー",
            "3. テーマの functions.php に貼り付け",
            "4. WordPressダッシュボードでパーマリンク設定を更新",
        ]

        result["instructions"] = instructions
        result["success"] = True

        # 5. スプレッドシートに記録
        if self.logger:
            await self.logger.log_taxonomy_creation(result, spec)

        print("\n" + "=" * 80)
        print("✅ タクソノミー作成処理完了")
        print("=" * 80)

        for instruction in instructions:
            print(instruction)

        return result


# テスト用のメイン関数
async def test_taxonomy_agent_with_logging():
    """WPTaxonomyAgent（ログ記録付き）のテスト"""
    print("=" * 80)
    print("🧪 WPTaxonomyAgent（ログ記録付き）テスト")
    print("=" * 80)

    from dotenv import load_dotenv

    load_dotenv("/workspaces/gemini_AI_Agent/.env")

    config = ConfigLoader()

    # SheetsManager初期化
    sheets_manager = GoogleSheetsManager(
        spreadsheet_id=config._config.get("SPREADSHEET_ID"),
        service_account_file=config._config.get("GOOGLE_SERVICE_ACCOUNT_FILE"),
    )

    # TaxonomyAgent初期化
    agent = WPTaxonomyAgent(config, sheets_manager)

    # テスト用タクソノミー仕様（階層型）
    test_spec = TaxonomySpecification(
        taxonomy="skill",
        singular_name="スキル",
        plural_name="スキル一覧",
        post_types=["portfolio"],
        description="プロジェクトで使用したスキルを分類",
        hierarchical=True,
        show_admin_column=True,
    )

    # タクソノミー作成
    result = await agent.create_taxonomy(test_spec)

    print("\n" + "=" * 80)
    print("📊 テスト結果:")
    print(f"   成功: {result['success']}")
    print(f"   タクソノミー: {result['taxonomy']}")
    print(f"   保存先: {result['filepath']}")
    print("=" * 80)


if __name__ == "__main__":
    import asyncio

    # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)

    asyncio.run(test_taxonomy_agent_with_logging())

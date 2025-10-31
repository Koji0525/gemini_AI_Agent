#!/usr/bin/env python3
"""
WordPress簡易エージェント（REST API版）
変更理由: playwright依存を排除、M&Aポータル構築に特化
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from wordpress.wp_dev.wp_rest_client import WordPressRESTClient
from configuration.wp_config_loader import WordPressConfigLoader


class SimpleWordPressAgent:
    """WordPress簡易エージェント基底クラス"""

    def __init__(self):
        config_loader = WordPressConfigLoader()
        config = config_loader.load_config()

        self.client = WordPressRESTClient(config["wp_url"], config["wp_user"], config["wp_pass"])

    def test_connection(self):
        return self.client.test_connection()


class SimpleCPTAgent(SimpleWordPressAgent):
    """カスタム投稿タイプ作成エージェント（簡易版）"""

    def create_ma_company_cpt(self):
        """M&A企業情報のカスタム投稿タイプを作成"""
        print("📄 カスタム投稿タイプ: ma_company を作成")
        print("⚠️ 注意: REST APIでのCPT作成にはプラグインが必要")
        print("   推奨: functions.php に直接記述するか、CPT UIプラグインを使用")

        php_code = """
// M&A企業情報カスタム投稿タイプ
function create_ma_company_post_type() {
    register_post_type('ma_company', array(
        'labels' => array(
            'name' => 'M&A企業情報',
            'singular_name' => '企業情報'
        ),
        'public' => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail'),
        'menu_icon' => 'dashicons-building',
        'show_in_rest' => true,
    ));
}
add_action('init', 'create_ma_company_post_type');
"""

        return {"success": True, "message": "PHP コードを生成しました", "php_code": php_code}


class SimpleACFAgent(SimpleWordPressAgent):
    """カスタムフィールド作成エージェント（簡易版）"""

    def create_ma_fields(self):
        """M&A企業情報のカスタムフィールドを作成"""
        print("📝 カスタムフィールドを作成")
        print("⚠️ 注意: ACFプラグインが必要です")

        fields_config = {
            "location": {"label": "所在地", "type": "text"},
            "capital": {"label": "資本金（万円）", "type": "number"},
            "employees": {"label": "従業員数", "type": "number"},
            "revenue": {"label": "年商（万円）", "type": "number"},
            "deal_type": {"label": "希望条件", "type": "select", "choices": ["売却希望", "買収希望"]},
        }

        return {"success": True, "message": "フィールド設定を生成しました", "fields": fields_config}


class SimplePostCreator(SimpleWordPressAgent):
    """投稿作成エージェント"""

    def create_demo_company(self, company_data: dict):
        """デモ企業情報を投稿"""

        # 注意: カスタム投稿タイプへの投稿にはREST APIのエンドポイントが必要
        # 通常の投稿として作成する例

        post_data = {
            "title": company_data.get("title"),
            "content": company_data.get("content"),
            "status": "publish",
        }

        result = self.client.create_post(post_data)

        if result["success"]:
            print(f"✅ {company_data.get('title')} を作成")
        else:
            print(f"❌ 作成失敗: {result.get('error')}")

        return result

#!/usr/bin/env python3
"""
WordPress 完全自動デプロイマスターシステム
"""

import os
import json
import base64
import requests
from datetime import datetime
import re


class WordPressAutoDeployer:
    """WordPress完全自動デプロイヤー"""

    def __init__(self):
        self.config_file = "deploy_system/config.json"
        self.log_file = f"deploy_system/logs/deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        os.makedirs("deploy_system/logs", exist_ok=True)

        self.config = self.load_config()

    def load_config(self):
        """設定を読み込み"""
        if not os.path.exists(self.config_file):
            print("❌ エラー: 設定ファイルが見つかりません")
            print("   先に ./wp-setup を実行してください")
            return None

        with open(self.config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def log(self, message, level="INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")

    def generate_clean_functions_php(self):
        """クリーンなfunctions.phpを生成"""
        self.log("functions.php生成開始")

        addon_path = "wordpress_projects/ma_portal_complete_20251031_024504/FIXED_FUNCTIONS_ADDON.php"

        if not os.path.exists(addon_path):
            self.log("エラー: 検索機能コードが見つかりません", "ERROR")
            return None

        with open(addon_path, "r", encoding="utf-8") as f:
            search_code = f.read()
            search_code = re.sub(r"<\?php\s*", "", search_code)
            search_code = search_code.replace("?>", "")
            search_code = re.sub(r"/\*\*\s*━+.*?━+\s*\*/", "", search_code, flags=re.DOTALL)

        clean_functions = f"""<?php
/**
 * Cocoon Child Theme - functions.php
 * 自動デプロイ: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
 */

// M&Aポータルサイト - バックエンド
function ma_company_register_post_type() {{
    if (post_type_exists('ma_company')) return;
    register_post_type('ma_company', array(
        'labels' => array(
            'name' => 'M&A企業情報',
            'singular_name' => '企業情報',
            'add_new' => '新規追加',
            'add_new_item' => '新しい企業情報を追加',
            'edit_item' => '企業情報を編集',
            'view_item' => '企業情報を表示',
            'all_items' => '全ての企業情報',
            'search_items' => '企業情報を検索',
            'not_found' => '企業情報が見つかりませんでした',
        ),
        'public' => true,
        'has_archive' => true,
        'menu_position' => 6,
        'menu_icon' => 'dashicons-building',
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'show_in_rest' => true,
        'rewrite' => array('slug' => 'companies'),
    ));
}}
add_action('init', 'ma_company_register_post_type');

function ma_industry_register_taxonomy() {{
    if (taxonomy_exists('ma_industry')) return;
    register_taxonomy('ma_industry', 'ma_company', array(
        'labels' => array('name' => '業種'),
        'hierarchical' => true,
        'show_in_rest' => true,
        'show_admin_column' => true,
        'rewrite' => array('slug' => 'industry'),
    ));
}}
add_action('init', 'ma_industry_register_taxonomy');

function ma_industry_create_default_terms() {{
    if (get_option('ma_industry_default_terms_created')) return;
    $industries = array('IT・ソフトウェア', '製造業', 'サービス業', '小売業', '建設業', 'その他');
    foreach ($industries as $name) {{
        if (!term_exists($name, 'ma_industry')) {{
            wp_insert_term($name, 'ma_industry', array('slug' => sanitize_title($name)));
        }}
    }}
    update_option('ma_industry_default_terms_created', true);
}}
add_action('init', 'ma_industry_create_default_terms', 100);

function ma_company_custom_columns($columns) {{
    return array(
        'cb' => $columns['cb'],
        'title' => '企業名',
        'industry' => '業種',
        'location' => '所在地',
        'capital' => '資本金',
        'deal_type' => '希望条件',
        'date' => $columns['date'],
    );
}}
add_filter('manage_ma_company_posts_columns', 'ma_company_custom_columns');

function ma_company_custom_column_content($column, $post_id) {{
    switch ($column) {{
        case 'industry':
            $terms = get_the_terms($post_id, 'ma_industry');
            echo $terms && !is_wp_error($terms) ? implode(', ', wp_list_pluck($terms, 'name')) : '—';
            break;
        case 'location':
            echo get_field('location', $post_id) ?: '—';
            break;
        case 'capital':
            $cap = get_field('capital', $post_id);
            echo $cap ? number_format($cap) . '万円' : '—';
            break;
        case 'deal_type':
            $type = get_field('deal_type', $post_id);
            if ($type) {{
                $class = ($type == '売却希望') ? 'sell' : 'buy';
                echo '<span class="ma-deal-type-' . $class . '">' . esc_html($type) . '</span>';
            }} else {{
                echo '—';
            }}
            break;
    }}
}}
add_action('manage_ma_company_posts_custom_column', 'ma_company_custom_column_content', 10, 2);

function ma_company_admin_styles() {{
    global $post_type;
    if ($post_type == 'ma_company') {{
        echo '<style>
            .ma-deal-type-sell {{ background: #ffebee; color: #c62828; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
            .ma-deal-type-buy {{ background: #e8f5e9; color: #2e7d32; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
        </style>';
    }}
}}
add_action('admin_head', 'ma_company_admin_styles');

// M&Aポータルサイト - 検索機能
{search_code.strip()}
"""

        temp_file = f"deploy_system/temp/functions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.php"
        os.makedirs("deploy_system/temp", exist_ok=True)

        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(clean_functions)

        self.log(f"functions.php生成完了: {temp_file}")
        return temp_file

    def deploy_via_rest_api(self, file_path):
        """WordPress REST API経由でデプロイ"""
        self.log("REST API経由でデプロイ開始")

        wp_url = self.config["wp_url"].rstrip("/")
        wp_user = self.config["wp_user"]
        wp_pass = self.config["wp_password"]

        credentials = f"{wp_user}:{wp_pass}"
        token = base64.b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        endpoint = f"{wp_url}/wp-json/custom/v1/deploy-functions"

        payload = {"file_content": file_content, "timestamp": datetime.now().isoformat()}

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                self.log("✅ デプロイ成功！", "SUCCESS")
                return True
            else:
                self.log(f"❌ デプロイ失敗: {response.status_code} - {response.text}", "ERROR")
                return False

        except Exception as e:
            self.log(f"❌ デプロイエラー: {str(e)}", "ERROR")
            return False

    def flush_wordpress_rewrite_rules(self):
        """WordPressのパーマリンク設定を自動更新"""
        self.log("パーマリンク設定を自動更新")

        wp_url = self.config["wp_url"].rstrip("/")
        wp_user = self.config["wp_user"]
        wp_pass = self.config["wp_password"]

        credentials = f"{wp_user}:{wp_pass}"
        token = base64.b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {token}"}

        endpoint = f"{wp_url}/wp-json/custom/v1/flush-rewrite"

        try:
            response = requests.post(endpoint, headers=headers, timeout=30)
            if response.status_code == 200:
                self.log("✅ パーマリンク更新成功")
                return True
        except:
            pass

        self.log("⚠️ パーマリンク更新は手動で行ってください", "WARNING")
        return False

    def deploy(self):
        """完全自動デプロイを実行"""
        if not self.config:
            return False

        print()
        print("=" * 70)
        print("🚀 WordPress 完全自動デプロイ開始")
        print("=" * 70)
        print()

        print("【STEP 1】クリーンなfunctions.php生成")
        file_path = self.generate_clean_functions_php()
        if not file_path:
            print("❌ ファイル生成失敗")
            return False
        print(f"✅ 生成完了: {file_path}")
        print()

        print("【STEP 2】WordPressにデプロイ")
        success = self.deploy_via_rest_api(file_path)

        if not success:
            print("❌ デプロイ失敗")
            return False

        print("✅ デプロイ成功！")
        print()

        print("【STEP 3】パーマリンク設定更新")
        self.flush_wordpress_rewrite_rules()
        print()

        print("=" * 70)
        print("🎉 自動デプロイ完了！")
        print("=" * 70)
        print()
        print(f"📁 ログファイル: {self.log_file}")
        print(f"🌐 WordPressサイト: {self.config['wp_url']}")
        print()

        return True


if __name__ == "__main__":
    deployer = WordPressAutoDeployer()
    deployer.deploy()

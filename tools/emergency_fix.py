#!/usr/bin/env python3
"""
緊急修正：functions.phpのParse Errorを解消
"""

import json
import base64
import requests
from datetime import datetime
import re


def fix_functions_php():
    """エラーを修正したfunctions.phpを生成・デプロイ"""

    print("=" * 70)
    print("🚨 緊急修正：functions.phpエラー解消")
    print("=" * 70)
    print()

    # 設定読み込み
    with open("deploy_system/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    # 検索機能コードを読み込み
    addon_path = "wordpress_projects/ma_portal_complete_20251031_024504/FIXED_FUNCTIONS_ADDON.php"

    with open(addon_path, "r", encoding="utf-8") as f:
        search_code = f.read()

    # 徹底的にクリーンアップ
    # 1. すべてのPHPタグを削除
    search_code = re.sub(r"<\?php\s*", "", search_code)
    search_code = re.sub(r"\?>", "", search_code)

    # 2. HTMLコメントを削除
    search_code = re.sub(r"<!--.*?-->", "", search_code, flags=re.DOTALL)

    # 3. 大量のコメント記号を削除
    search_code = re.sub(r"/\*\*\s*━+.*?━+\s*\*/", "", search_code, flags=re.DOTALL)
    search_code = re.sub(r"//\s*━+.*?\n", "\n", search_code)

    # 4. 余計な空白行を削除
    search_code = re.sub(r"\n\s*\n\s*\n", "\n\n", search_code)

    # 完全にクリーンなfunctions.phpを生成
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
            $value = get_post_meta($post_id, 'location', true);
            echo $value ? esc_html($value) : '—';
            break;
        case 'capital':
            $cap = get_post_meta($post_id, 'capital', true);
            echo $cap ? number_format($cap) . '万円' : '—';
            break;
        case 'deal_type':
            $type = get_post_meta($post_id, 'deal_type', true);
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

{search_code.strip()}
"""

    # 最後の検証：不正な文字を除去
    clean_functions = clean_functions.replace("<?", "").replace("?>", "")

    # 先頭に正しいPHPタグを追加
    if not clean_functions.startswith("<?php"):
        clean_functions = "<?php\n" + clean_functions.lstrip("php\n")

    # 一時ファイルに保存
    temp_file = f"deploy_system/temp/functions_emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}.php"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(clean_functions)

    print(f"✅ クリーンなfunctions.php生成: {temp_file}")
    print()

    # デプロイ
    print("🚀 WordPressに緊急デプロイ中...")

    wp_url = config["wp_url"].rstrip("/")
    wp_user = config["wp_user"]
    wp_pass = config["wp_password"]

    credentials = f"{wp_user}:{wp_pass}"
    token = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

    endpoint = f"{wp_url}/wp-json/custom/v1/deploy-functions"

    payload = {"file_content": clean_functions, "timestamp": datetime.now().isoformat()}

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            print("✅ 緊急デプロイ成功！")
            print()
            print("=" * 70)
            print("🎉 エラー修正完了！")
            print("=" * 70)
            print()
            print("📋 次のステップ:")
            print("1. WordPressサイトを再読み込み")
            print("   👉 https://uzbek-ma.com/wp-admin/")
            print()
            print("2. パーマリンク設定にアクセス")
            print("   👉 設定 → パーマリンク設定")
            print()
            print("3. 「変更を保存」をクリック")
            print()
            return True
        else:
            print(f"❌ デプロイ失敗: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False


if __name__ == "__main__":
    fix_functions_php()

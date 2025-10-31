<?php
/**
 * ============================================================
 * M&Aポータルサイト - 完全版
 * ============================================================
 * 自動生成日: 2025-10-31
 * フレームワーク: WordPress Dev Framework v1.0
 * 
 * 機能:
 * - カスタム投稿タイプ: ma_company
 * - タクソノミー: ma_industry（業種）
 * - デフォルトカテゴリー自動作成
 * - 管理画面カスタムカラム
 * - カスタムスタイル
 * ============================================================
 */

// ============================================================
// 1. カスタム投稿タイプ: ma_company
// ============================================================

function ma_company_register_post_type() {
    // 既に登録されているかチェック
    if (post_type_exists('ma_company')) {
        return;
    }
    
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
        'description' => 'M&A対象企業の情報管理',
        'public' => true,
        'has_archive' => true,
        'menu_position' => 6,
        'menu_icon' => 'dashicons-building',
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'show_in_rest' => true,
        'rewrite' => array('slug' => 'companies'),
        'capability_type' => 'post',
        'show_in_nav_menus' => true,
    ));
}
add_action('init', 'ma_company_register_post_type');

// ============================================================
// 2. タクソノミー: ma_industry（業種）
// ============================================================

function ma_industry_register_taxonomy() {
    // 既に登録されているかチェック
    if (taxonomy_exists('ma_industry')) {
        return;
    }
    
    register_taxonomy('ma_industry', 'ma_company', array(
        'labels' => array(
            'name' => '業種',
            'singular_name' => '業種',
            'search_items' => '業種を検索',
            'all_items' => '全ての業種',
            'edit_item' => '業種を編集',
            'add_new_item' => '新しい業種を追加',
        ),
        'hierarchical' => true,
        'show_ui' => true,
        'show_in_rest' => true,
        'show_admin_column' => true,
        'query_var' => true,
        'rewrite' => array('slug' => 'industry'),
    ));
}
add_action('init', 'ma_industry_register_taxonomy');

// ============================================================
// 3. デフォルト業種カテゴリーの自動作成
// ============================================================

function ma_industry_create_default_terms() {
    // 既に実行済みかチェック
    if (get_option('ma_industry_default_terms_created')) {
        return;
    }
    
    $default_industries = array(
        'IT・ソフトウェア' => 'IT・ソフトウェア開発企業',
        '製造業' => '製造業・工場関連',
        'サービス業' => 'サービス業全般',
        '小売業' => '小売・販売業',
        '建設業' => '建設・不動産関連',
        'その他' => 'その他の業種',
    );
    
    foreach ($default_industries as $name => $description) {
        if (!term_exists($name, 'ma_industry')) {
            wp_insert_term($name, 'ma_industry', array(
                'description' => $description,
                'slug' => sanitize_title($name),
            ));
        }
    }
    
    // 実行済みフラグ
    update_option('ma_industry_default_terms_created', true);
}
add_action('init', 'ma_industry_create_default_terms', 100);

// ============================================================
// 4. 管理画面: カスタムカラム
// ============================================================

function ma_company_custom_columns($columns) {
    $new_columns = array();
    
    $new_columns['cb'] = $columns['cb'];
    $new_columns['title'] = '企業名';
    $new_columns['industry'] = '業種';
    $new_columns['location'] = '所在地';
    $new_columns['capital'] = '資本金';
    $new_columns['deal_type'] = '希望条件';
    $new_columns['date'] = $columns['date'];
    
    return $new_columns;
}
add_filter('manage_ma_company_posts_columns', 'ma_company_custom_columns');

function ma_company_custom_column_content($column, $post_id) {
    switch ($column) {
        case 'industry':
            $terms = get_the_terms($post_id, 'ma_industry');
            if ($terms && !is_wp_error($terms)) {
                $names = array_map(function($term) {
                    return $term->name;
                }, $terms);
                echo implode(', ', $names);
            } else {
                echo '—';
            }
            break;
            
        case 'location':
            // ACFフィールドから取得
            $location = get_field('location', $post_id);
            echo $location ? esc_html($location) : '—';
            break;
            
        case 'capital':
            // ACFフィールドから取得
            $capital = get_field('capital', $post_id);
            if ($capital) {
                echo number_format($capital) . '万円';
            } else {
                echo '—';
            }
            break;
            
        case 'deal_type':
            // ACFフィールドから取得
            $deal_type = get_field('deal_type', $post_id);
            if ($deal_type) {
                $class = ($deal_type == '売却希望') ? 'sell' : 'buy';
                echo '<span class="ma-deal-type-' . $class . '">' . esc_html($deal_type) . '</span>';
            } else {
                echo '—';
            }
            break;
    }
}
add_action('manage_ma_company_posts_custom_column', 'ma_company_custom_column_content', 10, 2);

// ============================================================
// 5. 管理画面: カスタムスタイル
// ============================================================

function ma_company_admin_styles() {
    global $post_type;
    if ($post_type == 'ma_company') {
        ?>
        <style>
            .ma-deal-type-sell {
                background: #ffebee;
                color: #c62828;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }
            .ma-deal-type-buy {
                background: #e8f5e9;
                color: #2e7d32;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }
        </style>
        <?php
    }
}
add_action('admin_head', 'ma_company_admin_styles');

// ============================================================
// 完了
// ============================================================
/*
このコードは WordPress Dev Framework v1.0 により自動生成されました。

インストール方法:
1. このファイルの全内容をコピー
2. WordPress管理画面 → 外観 → テーマファイルエディター
3. functions.php を開く
4. 既存コードの最後に貼り付け
5. 「ファイルを更新」をクリック

次のステップ:
- ACFプラグインでカスタムフィールドを設定
- デモ企業データを入力
- 検索ページを作成
*/

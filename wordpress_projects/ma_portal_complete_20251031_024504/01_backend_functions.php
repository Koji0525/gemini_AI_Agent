<?php
/**
 * M&Aポータルサイト - バックエンド機能
 * 自動生成日時: 2025-10-31 02:45:04
 * 汎用フレームワーク: WordPress Portal Generator v1.0
 */

// ===================================
// 1. カスタム投稿タイプ登録
// ===================================
function ma_register_company_post_type() {
    $labels = array(
        'name'               => 'M&A企業情報',
        'singular_name'      => 'M&A企業',
        'menu_name'          => 'M&A企業情報',
        'add_new'            => '新規追加',
        'add_new_item'       => '新しい企業を追加',
        'edit_item'          => '企業情報を編集',
        'new_item'           => '新しい企業',
        'view_item'          => '企業を表示',
        'search_items'       => '企業を検索',
        'not_found'          => '企業が見つかりません',
        'all_items'          => 'すべての企業',
    );

    $args = array(
        'labels'              => $labels,
        'public'              => true,
        'has_archive'         => true,
        'publicly_queryable'  => true,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'show_in_rest'        => true,
        'menu_icon'           => 'dashicons-building',
        'supports'            => array('title', 'editor', 'thumbnail', 'custom-fields'),
        'rewrite'             => array('slug' => 'ma-company'),
    );

    register_post_type('ma_company', $args);
}
add_action('init', 'ma_register_company_post_type');

// ===================================
// 2. タクソノミー（業種分類）
// ===================================
function ma_register_industry_taxonomy() {
    $labels = array(
        'name'              => '業種',
        'singular_name'     => '業種',
        'search_items'      => '業種を検索',
        'all_items'         => 'すべての業種',
        'edit_item'         => '業種を編集',
        'update_item'       => '業種を更新',
        'add_new_item'      => '新しい業種を追加',
        'new_item_name'     => '新しい業種名',
        'menu_name'         => '業種',
    );

    $args = array(
        'labels'            => $labels,
        'hierarchical'      => true,
        'public'            => true,
        'show_ui'           => true,
        'show_in_rest'      => true,
        'show_admin_column' => true,
        'rewrite'           => array('slug' => 'ma-industry'),
    );

    register_taxonomy('ma_industry', array('ma_company'), $args);
}
add_action('init', 'ma_register_industry_taxonomy');

// ===================================
// 3. 管理画面カスタムカラム
// ===================================
function ma_custom_columns($columns) {
    $new_columns = array(
        'cb'       => $columns['cb'],
        'title'    => '企業名',
        'industry' => '業種',
        'location' => '所在地',
        'capital'  => '資本金',
        'date'     => '登録日',
    );
    return $new_columns;
}
add_filter('manage_ma_company_posts_columns', 'ma_custom_columns');

function ma_custom_column_content($column, $post_id) {
    switch ($column) {
        case 'industry':
            $terms = get_the_terms($post_id, 'ma_industry');
            if ($terms && !is_wp_error($terms)) {
                echo esc_html($terms[0]->name);
            }
            break;
        case 'location':
            echo esc_html(get_post_meta($post_id, 'location', true));
            break;
        case 'capital':
            $capital = get_post_meta($post_id, 'capital', true);
            echo $capital ? number_format($capital) . '万円' : '-';
            break;
    }
}
add_action('manage_ma_company_posts_custom_column', 'ma_custom_column_content', 10, 2);
?>
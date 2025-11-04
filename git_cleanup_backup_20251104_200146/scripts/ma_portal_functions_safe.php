<?php
/**
 * ============================================================
 * M&Aポータルサイト - カスタム投稿タイプ & タクソノミー
 * ============================================================
 * 追加日: 2025-10-31
 * 目的: M&A企業情報の管理
 * 注意: 既存の翻訳システムとは独立して動作
 * ============================================================
 */

// ============================================================
// 1. カスタム投稿タイプ: ma_company（M&A企業情報）
// ============================================================

function uzbek_ma_create_company_post_type() {
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
            'not_found_in_trash' => 'ゴミ箱に企業情報はありません',
        ),
        'description' => 'M&A対象企業の情報管理',
        'public' => true,
        'has_archive' => true,
        'menu_position' => 6,  // portfolioの下に配置
        'menu_icon' => 'dashicons-building',
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'show_in_rest' => true,  // Gutenberg対応
        'rewrite' => array('slug' => 'companies'),
        'capability_type' => 'post',
        'show_in_nav_menus' => true,
    ));
}
add_action('init', 'uzbek_ma_create_company_post_type');

// ============================================================
// 2. タクソノミー: ma_industry（業種）
// ============================================================

function uzbek_ma_create_industry_taxonomy() {
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
            'parent_item' => '親業種',
            'parent_item_colon' => '親業種:',
            'edit_item' => '業種を編集',
            'update_item' => '業種を更新',
            'add_new_item' => '新しい業種を追加',
            'new_item_name' => '新しい業種名',
            'menu_name' => '業種',
        ),
        'hierarchical' => true,  // カテゴリー型
        'show_ui' => true,
        'show_in_rest' => true,
        'show_admin_column' => true,  // 管理画面のカラムに表示
        'query_var' => true,
        'rewrite' => array('slug' => 'industry'),
    ));
}
add_action('init', 'uzbek_ma_create_industry_taxonomy');

// ============================================================
// 3. デフォルト業種カテゴリーの自動作成
// ============================================================

function uzbek_ma_create_default_industries() {
    // 既に実行済みかチェック
    if (get_option('uzbek_ma_default_industries_created')) {
        return;
    }
    
    $industries = array(
        'IT・ソフトウェア' => 'IT・ソフトウェア開発企業',
        '製造業' => '製造業・工場関連',
        'サービス業' => 'サービス業全般',
        '小売業' => '小売・販売業',
        '建設業' => '建設・不動産関連',
        'その他' => 'その他の業種',
    );
    
    foreach ($industries as $name => $description) {
        // 既に存在するかチェック
        if (!term_exists($name, 'ma_industry')) {
            wp_insert_term($name, 'ma_industry', array(
                'description' => $description,
                'slug' => sanitize_title($name),
            ));
        }
    }
    
    // 実行済みフラグ
    update_option('uzbek_ma_default_industries_created', true);
}
add_action('init', 'uzbek_ma_create_default_industries', 100);

// ============================================================
// 4. 管理画面: カスタムカラム追加
// ============================================================

function uzbek_ma_custom_columns($columns) {
    $new_columns = array();
    
    // チェックボックス
    $new_columns['cb'] = $columns['cb'];
    
    // タイトル
    $new_columns['title'] = '企業名';
    
    // カスタムカラム
    $new_columns['industry'] = '業種';
    $new_columns['location'] = '所在地';
    $new_columns['capital'] = '資本金';
    $new_columns['deal_type'] = '希望条件';
    
    // 日付
    $new_columns['date'] = $columns['date'];
    
    return $new_columns;
}
add_filter('manage_ma_company_posts_columns', 'uzbek_ma_custom_columns');

// カスタムカラムの内容表示
function uzbek_ma_custom_column_content($column, $post_id) {
    switch ($column) {
        case 'industry':
            $terms = get_the_terms($post_id, 'ma_industry');
            if ($terms && !is_wp_error($terms)) {
                $industry_names = array();
                foreach ($terms as $term) {
                    $industry_names[] = $term->name;
                }
                echo implode(', ', $industry_names);
            } else {
                echo '—';
            }
            break;
            
        case 'location':
            $location = get_field('location', $post_id);
            echo $location ? esc_html($location) : '—';
            break;
            
        case 'capital':
            $capital = get_field('capital', $post_id);
            if ($capital) {
                echo number_format($capital) . '万円';
            } else {
                echo '—';
            }
            break;
            
        case 'deal_type':
            $deal_type = get_field('deal_type', $post_id);
            if ($deal_type) {
                $class = ($deal_type == '売却希望') ? 'sell' : 'buy';
                echo '<span class="uzbek-ma-deal-type-' . $class . '">' . esc_html($deal_type) . '</span>';
            } else {
                echo '—';
            }
            break;
    }
}
add_action('manage_ma_company_posts_custom_column', 'uzbek_ma_custom_column_content', 10, 2);

// ============================================================
// 5. 管理画面: カスタムスタイル
// ============================================================

function uzbek_ma_admin_styles() {
    global $post_type;
    if ($post_type == 'ma_company') {
        ?>
        <style>
            .uzbek-ma-deal-type-sell {
                background: #ffebee;
                color: #c62828;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }
            .uzbek-ma-deal-type-buy {
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
add_action('admin_head', 'uzbek_ma_admin_styles');

// ============================================================
// 6. M&A企業情報を既存の翻訳システムから除外
// ============================================================

function uzbek_ma_exclude_from_auto_translation($should_translate, $post_id, $post) {
    // ma_company 投稿タイプは自動翻訳しない
    if ($post->post_type === 'ma_company') {
        return false;
    }
    return $should_translate;
}
// 既存の翻訳システムが除外フックを提供している場合に使用
// add_filter('uzbek_should_auto_translate', 'uzbek_ma_exclude_from_auto_translation', 10, 3);

// ============================================================
// 注意事項
// ============================================================
/*
このコードは以下の点で既存システムと競合しません:

1. 独自のプレフィックス (uzbek_ma_) を使用
2. 既存の投稿タイプ (portfolio) と重複しない
3. 既存のタクソノミー (skill) と重複しない
4. save_post フックを使用していない
5. 既存の翻訳システムには干渉しない

M&A企業情報の多言語化が必要な場合は、
Polylangの手動翻訳機能を使用してください。
*/

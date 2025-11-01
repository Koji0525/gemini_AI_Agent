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

// ============================================================
// Phase 14-1: 検索フォームとソート機能（echo形式）
// ============================================================

/**
 * 検索フォームのショートコード
 */
function ma_search_form_shortcode() {
    // 業種タクソノミーの取得
    $industries = get_terms(array(
        'taxonomy' => 'ma_industry',
        'hide_empty' => false,
    ));
    
    $html = '<div class="ma-search-form-container">';
    $html .= '<form method="GET" action="' . esc_url(home_url('/ma-search-results/')) . '" class="ma-search-form">';
    $html .= '<div class="ma-form-group">';
    $html .= '<label for="ma-keyword">キーワード</label>';
    $html .= '<input type="text" id="ma-keyword" name="keyword" placeholder="企業名で検索" class="ma-input">';
    $html .= '</div>';
    
    $html .= '<div class="ma-form-group">';
    $html .= '<label for="ma-industry">業種</label>';
    $html .= '<select id="ma-industry" name="industry" class="ma-select">';
    $html .= '<option value="">すべて</option>';
    
    if (!empty($industries) && !is_wp_error($industries)) {
        foreach ($industries as $industry) {
            $html .= '<option value="' . esc_attr($industry->slug) . '">';
            $html .= esc_html($industry->name);
            $html .= '</option>';
        }
    }
    
    $html .= '</select>';
    $html .= '</div>';
    $html .= '<button type="submit" class="ma-submit-btn">検索</button>';
    $html .= '</form>';
    $html .= '</div>';
    
    $html .= '<style>
    .ma-search-form-container {
        max-width: 800px;
        margin: 30px auto;
        padding: 30px;
        background: #f8f9fa;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .ma-search-form {
        display: grid;
        gap: 20px;
    }
    .ma-form-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .ma-form-group label {
        font-weight: bold;
        color: #333;
    }
    .ma-input, .ma-select {
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 16px;
    }
    .ma-submit-btn {
        padding: 15px 30px;
        background: #0073aa;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        cursor: pointer;
        transition: background 0.3s;
    }
    .ma-submit-btn:hover {
        background: #005a87;
    }
    </style>';
    
    return $html;
}
add_shortcode('ma_search_form', 'ma_search_form_shortcode');

/**
 * 検索結果表示（ソート機能付き）のショートコード
 */
function ma_search_results_shortcode() {
    // クエリパラメータの取得
    $keyword = isset($_GET['keyword']) ? sanitize_text_field($_GET['keyword']) : '';
    $industry = isset($_GET['industry']) ? sanitize_text_field($_GET['industry']) : '';
    $orderby = isset($_GET['orderby']) ? sanitize_text_field($_GET['orderby']) : 'date_desc';
    
    // WP_Query引数の準備
    $args = array(
        'post_type' => 'ma_company',
        'posts_per_page' => -1,
        'post_status' => 'publish',
    );
    
    // キーワード検索
    if (!empty($keyword)) {
        $args['s'] = $keyword;
    }
    
    // 業種フィルター
    if (!empty($industry)) {
        $args['tax_query'] = array(
            array(
                'taxonomy' => 'ma_industry',
                'field' => 'slug',
                'terms' => $industry,
            ),
        );
    }
    
    // ソート設定
    switch ($orderby) {
        case 'date_asc':
            $args['orderby'] = 'date';
            $args['order'] = 'ASC';
            break;
        case 'founded_asc':
            $args['meta_key'] = 'founded_year';
            $args['orderby'] = 'meta_value_num';
            $args['order'] = 'ASC';
            break;
        case 'founded_desc':
            $args['meta_key'] = 'founded_year';
            $args['orderby'] = 'meta_value_num';
            $args['order'] = 'DESC';
            break;
        case 'title_asc':
            $args['orderby'] = 'title';
            $args['order'] = 'ASC';
            break;
        default:
            $args['orderby'] = 'date';
            $args['order'] = 'DESC';
    }
    
    // クエリ実行
    $query = new WP_Query($args);
    
    $html = '<div class="ma-search-results-container">';
    
    // ソートUI
    $html .= '<div class="ma-sort-container">';
    $html .= '<div class="ma-results-count">検索結果: <strong>' . $query->found_posts . '</strong>件</div>';
    $html .= '<div class="ma-sort-controls">';
    $html .= '<label for="ma-sort-select">並び替え:</label>';
    $html .= '<select id="ma-sort-select" class="ma-sort-select">';
    $html .= '<option value="date_desc"' . selected($orderby, 'date_desc', false) . '>新着順</option>';
    $html .= '<option value="date_asc"' . selected($orderby, 'date_asc', false) . '>登録が古い順</option>';
    $html .= '<option value="founded_desc"' . selected($orderby, 'founded_desc', false) . '>設立年（新しい順）</option>';
    $html .= '<option value="founded_asc"' . selected($orderby, 'founded_asc', false) . '>設立年（古い順）</option>';
    $html .= '<option value="title_asc"' . selected($orderby, 'title_asc', false) . '>企業名（50音順）</option>';
    $html .= '</select>';
    $html .= '</div>';
    $html .= '</div>';
    
    // 検索結果
    $html .= '<div class="ma-results-list">';
    
    if ($query->have_posts()) {
        $html .= '<h2>検索結果</h2>';
        
        // 目次生成（4件以上の場合）
        if ($query->found_posts > 3) {
            $html .= '<div class="ma-toc">';
            $html .= '<h3>目次（全' . $query->found_posts . '件）</h3>';
            $html .= '<ol>';
            
            while ($query->have_posts()) {
                $query->the_post();
                $html .= '<li><a href="#company-' . get_the_ID() . '">' . get_the_title() . '</a></li>';
            }
            
            $html .= '</ol>';
            $html .= '</div>';
            
            $query->rewind_posts();
        }
        
        // 各企業の詳細表示
        while ($query->have_posts()) {
            $query->the_post();
            $company_id = get_the_ID();
            
            // カスタムフィールド取得
            $founded_year = get_post_meta($company_id, 'founded_year', true);
            $capital = get_post_meta($company_id, 'capital', true);
            $employees = get_post_meta($company_id, 'employees', true);
            $revenue = get_post_meta($company_id, 'revenue', true);
            $website = get_post_meta($company_id, 'website', true);
            
            // 業種取得
            $industries = wp_get_post_terms($company_id, 'ma_industry');
            $industry_names = array();
            if (!empty($industries) && !is_wp_error($industries)) {
                foreach ($industries as $industry) {
                    $industry_names[] = $industry->name;
                }
            }
            
            $html .= '<div id="company-' . $company_id . '" class="ma-company-card">';
            $html .= '<h3>' . get_the_title() . '</h3>';
            
            if (!empty($industry_names)) {
                $html .= '<p><strong>業種:</strong> ' . implode(', ', $industry_names) . '</p>';
            }
            
            if ($founded_year) {
                $html .= '<p><strong>設立年:</strong> ' . esc_html($founded_year) . '年</p>';
            }
            
            if ($capital) {
                $html .= '<p><strong>資本金:</strong> ' . esc_html($capital) . '</p>';
            }
            
            if ($employees) {
                $html .= '<p><strong>従業員数:</strong> ' . esc_html($employees) . '名</p>';
            }
            
            if ($revenue) {
                $html .= '<p><strong>売上高:</strong> ' . esc_html($revenue) . '</p>';
            }
            
            if ($website) {
                $html .= '<p><strong>Webサイト:</strong> <a href="' . esc_url($website) . '" target="_blank">' . esc_html($website) . '</a></p>';
            }
            
            $html .= '<div class="ma-company-description">' . get_the_content() . '</div>';
            $html .= '<p><a href="' . get_permalink() . '" class="ma-details-link">詳細 →</a></p>';
            $html .= '</div>';
        }
    } else {
        $html .= '<p class="ma-no-results">検索条件に一致する企業が見つかりませんでした。</p>';
    }
    
    wp_reset_postdata();
    
    $html .= '</div>';
    $html .= '</div>';
    
    // CSS
    $html .= '<style>
    .ma-sort-container {
        margin: 20px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }
    .ma-results-count {
        font-weight: bold;
        color: #333;
    }
    .ma-sort-controls {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ma-sort-select {
        padding: 8px 15px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
    }
    .ma-company-card {
        margin: 20px 0;
        padding: 20px;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .ma-company-card h3 {
        margin-top: 0;
        color: #0073aa;
    }
    .ma-details-link {
        display: inline-block;
        margin-top: 10px;
        color: #0073aa;
        text-decoration: none;
        font-weight: bold;
    }
    .ma-details-link:hover {
        text-decoration: underline;
    }
    .ma-toc {
        background: #f0f0f0;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
    }
    .ma-toc h3 {
        margin-top: 0;
    }
    .ma-toc ol {
        margin: 0;
        padding-left: 20px;
    }
    .ma-toc a {
        color: #0073aa;
        text-decoration: none;
    }
    .ma-toc a:hover {
        text-decoration: underline;
    }
    .ma-no-results {
        text-align: center;
        padding: 40px;
        color: #666;
        font-size: 18px;
    }
    </style>';
    
    // JavaScript
    $html .= '<script>
    jQuery(document).ready(function($) {
        $("#ma-sort-select").on("change", function() {
            var sortBy = $(this).val();
            var url = new URL(window.location.href);
            url.searchParams.set("orderby", sortBy);
            window.location.href = url.toString();
        });
    });
    </script>';
    
    return $html;
}
add_shortcode('ma_search_results', 'ma_search_results_shortcode');

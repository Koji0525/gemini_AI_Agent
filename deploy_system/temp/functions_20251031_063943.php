<?php
/**
 * Cocoon Child Theme - functions.php
 * 自動デプロイ: 2025-10-31 06:39:43
 */

// M&Aポータルサイト - バックエンド
function ma_company_register_post_type() {
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
}
add_action('init', 'ma_company_register_post_type');

function ma_industry_register_taxonomy() {
    if (taxonomy_exists('ma_industry')) return;
    register_taxonomy('ma_industry', 'ma_company', array(
        'labels' => array('name' => '業種'),
        'hierarchical' => true,
        'show_in_rest' => true,
        'show_admin_column' => true,
        'rewrite' => array('slug' => 'industry'),
    ));
}
add_action('init', 'ma_industry_register_taxonomy');

function ma_industry_create_default_terms() {
    if (get_option('ma_industry_default_terms_created')) return;
    $industries = array('IT・ソフトウェア', '製造業', 'サービス業', '小売業', '建設業', 'その他');
    foreach ($industries as $name) {
        if (!term_exists($name, 'ma_industry')) {
            wp_insert_term($name, 'ma_industry', array('slug' => sanitize_title($name)));
        }
    }
    update_option('ma_industry_default_terms_created', true);
}
add_action('init', 'ma_industry_create_default_terms', 100);

function ma_company_custom_columns($columns) {
    return array(
        'cb' => $columns['cb'],
        'title' => '企業名',
        'industry' => '業種',
        'location' => '所在地',
        'capital' => '資本金',
        'deal_type' => '希望条件',
        'date' => $columns['date'],
    );
}
add_filter('manage_ma_company_posts_columns', 'ma_company_custom_columns');

function ma_company_custom_column_content($column, $post_id) {
    switch ($column) {
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
            if ($type) {
                $class = ($type == '売却希望') ? 'sell' : 'buy';
                echo '<span class="ma-deal-type-' . $class . '">' . esc_html($type) . '</span>';
            } else {
                echo '—';
            }
            break;
    }
}
add_action('manage_ma_company_posts_custom_column', 'ma_company_custom_column_content', 10, 2);

function ma_company_admin_styles() {
    global $post_type;
    if ($post_type == 'ma_company') {
        echo '<style>
            .ma-deal-type-sell { background: #ffebee; color: #c62828; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }
            .ma-deal-type-buy { background: #e8f5e9; color: #2e7d32; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }
        </style>';
    }
}
add_action('admin_head', 'ma_company_admin_styles');

// M&Aポータルサイト - 検索機能
/**
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * M&Aポータル - 検索機能追加コード
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * このコードをfunctions.phpの一番下に追加してください
 * 既存のM&A関連コードはそのまま残してOKです
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 */

// ===================================
// 検索フォーム（ショートコード）
// ===================================
if (!function_exists('ma_search_form_shortcode')) {
    function ma_search_form_shortcode() {
        ob_start();
        
        <div class="ma-search-container">
            <form method="GET" action="echo esc_url(home_url('/ma-search-results')); " class="ma-search-form">
                <div class="search-row">
                    <div class="search-field">
                        <label>キーワード</label>
                        <input type="text" name="keyword" placeholder="企業名で検索" value="echo esc_attr(isset($_GET['keyword']) ? $_GET['keyword'] : ''); ">
                    </div>
                    
                    <div class="search-field">
                        <label>業種</label>
                        <select name="industry">
                            <option value="">すべて</option>
                            $industries = get_terms(array('taxonomy' => 'ma_industry', 'hide_empty' => false));
                            if (!is_wp_error($industries)) {
                                foreach ($industries as $industry) {
                                    $selected = (isset($_GET['industry']) && $_GET['industry'] == $industry->term_id) ? 'selected' : '';
                                    echo '<option value="' . esc_attr($industry->term_id) . '" ' . $selected . '>' . esc_html($industry->name) . '</option>';
                                }
                            }
                            
                        </select>
                    </div>
                    
                    <div class="search-field">
                        <label>所在地</label>
                        <input type="text" name="location" placeholder="東京都" value="echo esc_attr(isset($_GET['location']) ? $_GET['location'] : ''); ">
                    </div>
                </div>
                
                <div class="search-row">
                    <div class="search-field">
                        <label>資本金（万円以上）</label>
                        <input type="number" name="capital_min" placeholder="1000" value="echo esc_attr(isset($_GET['capital_min']) ? $_GET['capital_min'] : ''); ">
                    </div>
                    
                    <div class="search-field">
                        <label>希望条件</label>
                        <select name="deal_type">
                            <option value="">指定なし</option>
                            <option value="売却希望" echo (isset($_GET['deal_type']) && $_GET['deal_type'] == '売却希望') ? 'selected' : ''; >売却希望</option>
                            <option value="買収希望" echo (isset($_GET['deal_type']) && $_GET['deal_type'] == '買収希望') ? 'selected' : ''; >買収希望</option>
                        </select>
                    </div>
                </div>
                
                <button type="submit" class="search-button">🔍 検索する</button>
            </form>
        </div>
        
        <style>
        .ma-search-container {
            max-width: 900px;
            margin: 30px auto;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .ma-search-form .search-row {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
        .ma-search-form .search-field {
            flex: 1;
        }
        .ma-search-form label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }
        .ma-search-form input,
        .ma-search-form select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .search-button {
            width: 100%;
            padding: 15px;
            background: #0073aa;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
        }
        .search-button:hover {
            background: #005177;
        }
        @media (max-width: 768px) {
            .ma-search-form .search-row {
                flex-direction: column;
            }
        }
        </style>
        return ob_get_clean();
    }
    add_shortcode('ma_search_form', 'ma_search_form_shortcode');
}

// ===================================
// 検索結果表示（ショートコード）
// ===================================
if (!function_exists('ma_search_results_shortcode')) {
    function ma_search_results_shortcode() {
        ob_start();
        
        $args = array(
            'post_type'      => 'ma_company',
            'posts_per_page' => 20,
            'post_status'    => 'publish',
        );
        
        // キーワード検索
        if (!empty($_GET['keyword'])) {
            $args['s'] = sanitize_text_field($_GET['keyword']);
        }
        
        // 業種フィルター
        if (!empty($_GET['industry'])) {
            $args['tax_query'] = array(
                array(
                    'taxonomy' => 'ma_industry',
                    'field'    => 'term_id',
                    'terms'    => intval($_GET['industry']),
                ),
            );
        }
        
        // メタクエリ（カスタムフィールド）
        $meta_query = array('relation' => 'AND');
        
        if (!empty($_GET['location'])) {
            $meta_query[] = array(
                'key'     => 'location',
                'value'   => sanitize_text_field($_GET['location']),
                'compare' => 'LIKE',
            );
        }
        
        if (!empty($_GET['capital_min'])) {
            $meta_query[] = array(
                'key'     => 'capital',
                'value'   => intval($_GET['capital_min']),
                'compare' => '>=',
                'type'    => 'NUMERIC',
            );
        }
        
        if (!empty($_GET['deal_type'])) {
            $meta_query[] = array(
                'key'   => 'deal_type',
                'value' => sanitize_text_field($_GET['deal_type']),
            );
        }
        
        if (count($meta_query) > 1) {
            $args['meta_query'] = $meta_query;
        }
        
        $query = new WP_Query($args);
        
        
        <div class="ma-results-container">
            <h2>検索結果: echo esc_html($query->found_posts); 件</h2>
            
            if ($query->have_posts()) : 
                <div class="ma-results-grid">
                    while ($query->have_posts()) : $query->the_post(); 
                        <div class="ma-result-card">
                            <h3>the_title(); </h3>
                            
                            <div class="company-meta">
                                $industry = get_the_terms(get_the_ID(), 'ma_industry');
                                if ($industry && !is_wp_error($industry)) {
                                    echo '<span class="meta-tag">🏢 ' . esc_html($industry[0]->name) . '</span>';
                                }
                                
                                $location = get_post_meta(get_the_ID(), 'location', true);
                                if ($location) {
                                    echo '<span class="meta-tag">📍 ' . esc_html($location) . '</span>';
                                }
                                
                                $capital = get_post_meta(get_the_ID(), 'capital', true);
                                if ($capital) {
                                    echo '<span class="meta-tag">💰 資本金: ' . number_format($capital) . '万円</span>';
                                }
                                
                                $employees = get_post_meta(get_the_ID(), 'employees', true);
                                if ($employees) {
                                    echo '<span class="meta-tag">👥 ' . esc_html($employees) . '名</span>';
                                }
                                
                                $deal_type = get_post_meta(get_the_ID(), 'deal_type', true);
                                if ($deal_type) {
                                    echo '<span class="meta-tag deal-type">' . esc_html($deal_type) . '</span>';
                                }
                                
                            </div>
                            
                            <div class="company-description">
                                echo wp_trim_words(get_the_content(), 30); 
                            </div>
                            
                            <a href="the_permalink(); " class="view-detail">詳細を見る →</a>
                        </div>
                    endwhile; 
                </div>
            else : 
                <p class="no-results">該当する企業が見つかりませんでした。検索条件を変更してお試しください。</p>
            endif; 
            
            wp_reset_postdata(); 
        </div>
        
        <style>
        .ma-results-container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .ma-results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }
        .ma-result-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .ma-result-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        .ma-result-card h3 {
            margin-top: 0;
            color: #0073aa;
            font-size: 20px;
        }
        .company-meta {
            margin: 15px 0;
        }
        .meta-tag {
            display: inline-block;
            background: #f0f0f0;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 13px;
            margin: 5px 5px 5px 0;
        }
        .meta-tag.deal-type {
            background: #e8f5e9;
            color: #2e7d32;
            font-weight: bold;
        }
        .company-description {
            color: #666;
            line-height: 1.6;
            margin: 15px 0;
        }
        .view-detail {
            display: inline-block;
            color: #0073aa;
            text-decoration: none;
            font-weight: bold;
            margin-top: 10px;
        }
        .view-detail:hover {
            text-decoration: underline;
        }
        .no-results {
            text-align: center;
            padding: 50px 20px;
            color: #666;
            font-size: 16px;
        }
        @media (max-width: 768px) {
            .ma-results-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        return ob_get_clean();
    }
    add_shortcode('ma_search_results', 'ma_search_results_shortcode');
}

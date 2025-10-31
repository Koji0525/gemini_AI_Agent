<?php
/**
 * ═══════════════════════════════════════════════════════
 * M&Aポータルサイト 完全版
 * ═══════════════════════════════════════════════════════
 * 自動生成: 2025-10-31
 * WordPress Portal Generator v1.0 - AI Framework
 * 
 * このコードをfunctions.phpの末尾にコピペするだけで完成！
 * ═══════════════════════════════════════════════════════
 */

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// パート1: バックエンド機能
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// パート2: フロントエンド検索システム
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<?php
/**
 * M&Aポータル - フロントエンド検索システム
 * ユーザーが企業を検索・フィルターできる機能
 */

// ===================================
// 4. 検索フォーム（ショートコード）
// ===================================
function ma_search_form_shortcode() {
    ob_start();
    ?>
    <div class="ma-search-container">
        <form method="GET" action="<?php echo esc_url(home_url('/ma-search-results')); ?>" class="ma-search-form">
            <div class="search-row">
                <div class="search-field">
                    <label>キーワード</label>
                    <input type="text" name="keyword" placeholder="企業名で検索" value="<?php echo esc_attr($_GET['keyword'] ?? ''); ?>">
                </div>
                
                <div class="search-field">
                    <label>業種</label>
                    <select name="industry">
                        <option value="">すべて</option>
                        <?php
                        $industries = get_terms(array('taxonomy' => 'ma_industry', 'hide_empty' => false));
                        foreach ($industries as $industry) {
                            $selected = (isset($_GET['industry']) && $_GET['industry'] == $industry->term_id) ? 'selected' : '';
                            echo '<option value="' . $industry->term_id . '" ' . $selected . '>' . esc_html($industry->name) . '</option>';
                        }
                        ?>
                    </select>
                </div>
                
                <div class="search-field">
                    <label>所在地</label>
                    <input type="text" name="location" placeholder="東京都" value="<?php echo esc_attr($_GET['location'] ?? ''); ?>">
                </div>
            </div>
            
            <div class="search-row">
                <div class="search-field">
                    <label>資本金（万円以上）</label>
                    <input type="number" name="capital_min" placeholder="1000" value="<?php echo esc_attr($_GET['capital_min'] ?? ''); ?>">
                </div>
                
                <div class="search-field">
                    <label>希望条件</label>
                    <select name="deal_type">
                        <option value="">指定なし</option>
                        <option value="売却希望" <?php echo (isset($_GET['deal_type']) && $_GET['deal_type'] == '売却希望') ? 'selected' : ''; ?>>売却希望</option>
                        <option value="買収希望" <?php echo (isset($_GET['deal_type']) && $_GET['deal_type'] == '買収希望') ? 'selected' : ''; ?>>買収希望</option>
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
    </style>
    <?php
    return ob_get_clean();
}
add_shortcode('ma_search_form', 'ma_search_form_shortcode');

// ===================================
// 5. 検索結果表示（ショートコード）
// ===================================
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
    ?>
    
    <div class="ma-results-container">
        <h2>検索結果: <?php echo $query->found_posts; ?>件</h2>
        
        <?php if ($query->have_posts()) : ?>
            <div class="ma-results-grid">
                <?php while ($query->have_posts()) : $query->the_post(); ?>
                    <div class="ma-result-card">
                        <h3><?php the_title(); ?></h3>
                        
                        <div class="company-meta">
                            <?php
                            $industry = get_the_terms(get_the_ID(), 'ma_industry');
                            if ($industry) {
                                echo '<span class="meta-tag">🏢 ' . esc_html($industry[0]->name) . '</span>';
                            }
                            
                            $location = get_post_meta(get_the_ID(), 'location', true);
                            if ($location) {
                                echo '<span class="meta-tag">📍 ' . esc_html($location) . '</span>';
                            }
                            
                            $capital = get_post_meta(get_the_ID(), 'capital', true);
                            if ($capital) {
                                echo '<span class="meta-tag">�� 資本金: ' . number_format($capital) . '万円</span>';
                            }
                            
                            $employees = get_post_meta(get_the_ID(), 'employees', true);
                            if ($employees) {
                                echo '<span class="meta-tag">👥 ' . esc_html($employees) . '名</span>';
                            }
                            
                            $deal_type = get_post_meta(get_the_ID(), 'deal_type', true);
                            if ($deal_type) {
                                echo '<span class="meta-tag deal-type">' . esc_html($deal_type) . '</span>';
                            }
                            ?>
                        </div>
                        
                        <div class="company-description">
                            <?php echo wp_trim_words(get_the_content(), 30); ?>
                        </div>
                        
                        <a href="<?php the_permalink(); ?>" class="view-detail">詳細を見る →</a>
                    </div>
                <?php endwhile; ?>
            </div>
        <?php else : ?>
            <p class="no-results">該当する企業が見つかりませんでした。検索条件を変更してお試しください。</p>
        <?php endif; ?>
        
        <?php wp_reset_postdata(); ?>
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
    </style>
    <?php
    
    return ob_get_clean();
}
add_shortcode('ma_search_results', 'ma_search_results_shortcode');
?>
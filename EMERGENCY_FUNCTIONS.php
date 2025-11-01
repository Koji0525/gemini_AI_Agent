<?php
/**
 * Cocoon Child Theme - functions.php
 * Emergency Fix - 2025-10-31
 */

// M&A企業情報 - カスタム投稿タイプ
function ma_company_register_post_type() {
    if (post_type_exists('ma_company')) return;
    register_post_type('ma_company', array(
        'labels' => array(
            'name' => 'M&A企業情報',
            'singular_name' => '企業情報',
            'add_new' => '新規追加',
            'edit_item' => '企業情報を編集',
        ),
        'public' => true,
        'has_archive' => true,
        'menu_icon' => 'dashicons-building',
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'show_in_rest' => true,
        'rewrite' => array('slug' => 'companies'),
    ));
}
add_action('init', 'ma_company_register_post_type');

// 業種タクソノミー
function ma_industry_register_taxonomy() {
    if (taxonomy_exists('ma_industry')) return;
    register_taxonomy('ma_industry', 'ma_company', array(
        'labels' => array('name' => '業種'),
        'hierarchical' => true,
        'show_in_rest' => true,
        'show_admin_column' => true,
    ));
}
add_action('init', 'ma_industry_register_taxonomy');

// デフォルト業種
function ma_industry_create_default_terms() {
    if (get_option('ma_industry_default_terms_created')) return;
    $industries = array('IT・ソフトウェア', '製造業', 'サービス業', '小売業', '建設業', 'その他');
    foreach ($industries as $name) {
        if (!term_exists($name, 'ma_industry')) {
            wp_insert_term($name, 'ma_industry');
        }
    }
    update_option('ma_industry_default_terms_created', true);
}
add_action('init', 'ma_industry_create_default_terms', 100);

// 検索フォーム
function ma_search_form_shortcode() {
    ob_start();
    ?>
    <div style="max-width:900px;margin:30px auto;padding:30px;background:#f8f9fa;border-radius:10px;">
        <form method="GET" action="<?php echo esc_url(home_url('/ma-search-results')); ?>">
            <div style="margin-bottom:15px;">
                <label style="display:block;font-weight:bold;">キーワード</label>
                <input type="text" name="keyword" placeholder="企業名" style="width:100%;padding:10px;">
            </div>
            <div style="margin-bottom:15px;">
                <label style="display:block;font-weight:bold;">業種</label>
                <select name="industry" style="width:100%;padding:10px;">
                    <option value="">すべて</option>
                    <?php
                    $industries = get_terms(array('taxonomy' => 'ma_industry', 'hide_empty' => false));
                    foreach ($industries as $industry) {
                        echo '<option value="' . $industry->term_id . '">' . esc_html($industry->name) . '</option>';
                    }
                    ?>
                </select>
            </div>
            <button type="submit" style="width:100%;padding:15px;background:#0073aa;color:white;border:none;cursor:pointer;">検索</button>
        </form>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('ma_search_form', 'ma_search_form_shortcode');

// 検索結果
function ma_search_results_shortcode() {
    ob_start();
    
    $args = array(
        'post_type' => 'ma_company',
        'posts_per_page' => 20,
    );
    
    if (!empty($_GET['keyword'])) {
        $args['s'] = sanitize_text_field($_GET['keyword']);
    }
    
    if (!empty($_GET['industry'])) {
        $args['tax_query'] = array(
            array(
                'taxonomy' => 'ma_industry',
                'field' => 'term_id',
                'terms' => intval($_GET['industry']),
            ),
        );
    }
    
    $query = new WP_Query($args);
    ?>
    
    <div style="max-width:1200px;margin:30px auto;">
        <h2>検索結果: <?php echo $query->found_posts; ?>件</h2>
        
        <?php if ($query->have_posts()) : ?>
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;">
                <?php while ($query->have_posts()) : $query->the_post(); ?>
                    <div style="background:white;padding:20px;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                        <h3 style="margin-top:0;"><?php the_title(); ?></h3>
                        <div><?php echo wp_trim_words(get_the_content(), 20); ?></div>
                        <a href="<?php the_permalink(); ?>" style="color:#0073aa;">詳細 →</a>
                    </div>
                <?php endwhile; ?>
            </div>
        <?php else : ?>
            <p>該当する企業が見つかりませんでした。</p>
        <?php endif; ?>
        
        <?php wp_reset_postdata(); ?>
    </div>
    
    <?php
    return ob_get_clean();
}
add_shortcode('ma_search_results', 'ma_search_results_shortcode');

#!/usr/bin/env python3
"""
FTP経由でfunctions.phpを緊急復旧
"""

from ftplib import FTP
import json
from datetime import datetime


def emergency_ftp_fix():
    """FTP経由で最小限のfunctions.phpをアップロード"""

    print("=" * 70)
    print("🚨 FTP経由緊急復旧")
    print("=" * 70)
    print()

    # 設定読み込み
    with open("tools/wp_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    # 最小限の動作するfunctions.php
    minimal_functions = """<?php
/**
 * Cocoon Child Theme - functions.php
 * Emergency Fix
 */

// M&A企業情報 - カスタム投稿タイプ
function ma_company_register_post_type() {
    if (post_type_exists('ma_company')) return;
    register_post_type('ma_company', array(
        'labels' => array(
            'name' => 'M&A企業情報',
            'singular_name' => '企業情報',
        ),
        'public' => true,
        'has_archive' => true,
        'menu_icon' => 'dashicons-building',
        'supports' => array('title', 'editor', 'thumbnail'),
        'show_in_rest' => true,
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
    ));
}
add_action('init', 'ma_industry_register_taxonomy');

// デフォルト業種を作成
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
                <label style="display:block;font-weight:bold;margin-bottom:5px;">キーワード</label>
                <input type="text" name="keyword" placeholder="企業名で検索" style="width:100%;padding:10px;">
            </div>
            <div style="margin-bottom:15px;">
                <label style="display:block;font-weight:bold;margin-bottom:5px;">業種</label>
                <select name="industry" style="width:100%;padding:10px;">
                    <option value="">すべて</option>
                    <?php
                    $industries = get_terms(array('taxonomy' => 'ma_industry', 'hide_empty' => false));
                    if (!is_wp_error($industries)) {
                        foreach ($industries as $industry) {
                            echo '<option value="' . $industry->term_id . '">' . esc_html($industry->name) . '</option>';
                        }
                    }
                    ?>
                </select>
            </div>
            <button type="submit" style="width:100%;padding:15px;background:#0073aa;color:white;border:none;border-radius:5px;font-size:16px;cursor:pointer;">検索する</button>
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
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:25px;margin-top:30px;">
                <?php while ($query->have_posts()) : $query->the_post(); ?>
                    <div style="background:white;padding:25px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                        <h3><?php the_title(); ?></h3>
                        <div><?php echo wp_trim_words(get_the_content(), 30); ?></div>
                        <a href="<?php the_permalink(); ?>" style="color:#0073aa;">詳細を見る →</a>
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
"""

    # 一時ファイルに保存
    temp_file = "deploy_system/temp/functions_minimal.php"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(minimal_functions)

    print(f"✅ 最小限のfunctions.php生成: {temp_file}")
    print()

    # FTP接続
    print("📤 FTP接続中...")
    try:
        ftp = FTP()
        ftp.connect(config["ftp_host"], 21, timeout=30)
        ftp.login(config["ftp_user"], config["ftp_pass"])

        print("✅ FTP接続成功")
        print()

        # functions.phpのパス
        wp_path = config["ftp_wp_path"]
        functions_path = f"{wp_path}/wp-content/themes/cocoon-child-master/functions.php"

        print(f"📁 アップロード先: {functions_path}")
        print()

        # ディレクトリに移動
        ftp.cwd(f"{wp_path}/wp-content/themes/cocoon-child-master")

        # バックアップ作成
        backup_name = f"functions.php.broken.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            ftp.rename("functions.php", backup_name)
            print(f"✅ バックアップ作成: {backup_name}")
        except:
            print("⚠️ バックアップスキップ")

        print()

        # 新しいfunctions.phpをアップロード
        print("📤 新しいfunctions.phpをアップロード中...")
        with open(temp_file, "rb") as f:
            ftp.storbinary("STOR functions.php", f)

        print("✅ アップロード完了！")
        print()

        ftp.quit()

        print("=" * 70)
        print("🎉 緊急復旧完了！")
        print("=" * 70)
        print()
        print("📋 次のステップ:")
        print("1. WordPressサイトを再読み込み")
        print("   👉 https://uzbek-ma.com/wp-admin/")
        print()
        print("2. エラーが消えているか確認")
        print()
        print("3. パーマリンク設定にアクセス")
        print("   👉 設定 → パーマリンク設定")
        print()
        print("4. 「変更を保存」をクリック")
        print()

        return True

    except Exception as e:
        print(f"❌ FTPエラー: {str(e)}")
        return False


if __name__ == "__main__":
    emergency_ftp_fix()

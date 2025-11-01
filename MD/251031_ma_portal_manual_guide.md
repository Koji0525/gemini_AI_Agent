# M&Aポータル手動実装ガイド

## Step 1: カスタム投稿タイプ作成

**場所**: テーマの functions.php
```php
// M&A企業情報カスタム投稿タイプ
function create_ma_company_post_type() {
    register_post_type('ma_company', array(
        'labels' => array(
            'name' => 'M&A企業情報',
            'singular_name' => '企業情報'
        ),
        'public' => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail'),
        'menu_icon' => 'dashicons-building',
        'show_in_rest' => true,
        'rewrite' => array('slug' => 'companies'),
    ));
    
    // 業種タクソノミー
    register_taxonomy('ma_industry', 'ma_company', array(
        'labels' => array(
            'name' => '業種',
            'singular_name' => '業種'
        ),
        'hierarchical' => true,
        'show_in_rest' => true,
    ));
}
add_action('init', 'create_ma_company_post_type');
```

## Step 2: Advanced Custom Fields (ACF) 設定

**プラグイン**: Advanced Custom Fields をインストール

**フィールドグループ**: 企業詳細情報

| フィールド名 | フィールドタイプ | 必須 |
|-------------|----------------|------|
| location | テキスト | Yes |
| capital | 数値 | Yes |
| employees | 数値 | Yes |
| revenue | 数値 | Yes |
| deal_type | 選択 | Yes |

**deal_type の選択肢**:
- 売却希望
- 買収希望

**Location Rules**: Post Type is equal to M&A企業情報

## Step 3: デモデータ入力

WordPress管理画面 → M&A企業情報 → 新規追加

### デモ企業1: テックカンパニーA
- タイトル: テックカンパニーA
- 業種: IT・ソフトウェア
- 所在地: 東京都渋谷区
- 資本金: 10000（万円）
- 従業員数: 50
- 年商: 100000（万円）
- 希望条件: 売却希望
- 本文: AIを活用したSaaSプロダクトを展開する成長企業

### デモ企業2-5: 同様に入力

## Step 4: 検索フォーム作成

**新規ページ**: 企業検索
```php
<?php
// 検索フォーム
?>
<form method="get" action="<?php echo home_url('/'); ?>">
    <input type="hidden" name="post_type" value="ma_company">
    
    <label>業種</label>
    <?php
    wp_dropdown_categories(array(
        'taxonomy' => 'ma_industry',
        'name' => 'ma_industry',
        'show_option_all' => '全て',
    ));
    ?>
    
    <label>資本金（万円）</label>
    <input type="number" name="capital_min" placeholder="最小">
    <input type="number" name="capital_max" placeholder="最大">
    
    <label>希望条件</label>
    <select name="deal_type">
        <option value="">全て</option>
        <option value="売却希望">売却希望</option>
        <option value="買収希望">買収希望</option>
    </select>
    
    <button type="submit">検索</button>
</form>

<?php
// 検索結果表示
$args = array(
    'post_type' => 'ma_company',
    'posts_per_page' => 10,
);

// 業種フィルター
if (!empty($_GET['ma_industry'])) {
    $args['tax_query'] = array(
        array(
            'taxonomy' => 'ma_industry',
            'field' => 'id',
            'terms' => $_GET['ma_industry'],
        ),
    );
}

// カスタムフィールドフィルター
$meta_query = array();

if (!empty($_GET['capital_min'])) {
    $meta_query[] = array(
        'key' => 'capital',
        'value' => $_GET['capital_min'],
        'compare' => '>=',
        'type' => 'NUMERIC',
    );
}

if (!empty($_GET['capital_max'])) {
    $meta_query[] = array(
        'key' => 'capital',
        'value' => $_GET['capital_max'],
        'compare' => '<=',
        'type' => 'NUMERIC',
    );
}

if (!empty($_GET['deal_type'])) {
    $meta_query[] = array(
        'key' => 'deal_type',
        'value' => $_GET['deal_type'],
        'compare' => '=',
    );
}

if (!empty($meta_query)) {
    $args['meta_query'] = $meta_query;
}

$query = new WP_Query($args);

if ($query->have_posts()) {
    while ($query->have_posts()) {
        $query->the_post();
        
        echo '<div class="company-item">';
        echo '<h2>' . get_the_title() . '</h2>';
        echo '<p>所在地: ' . get_field('location') . '</p>';
        echo '<p>資本金: ' . number_format(get_field('capital')) . '万円</p>';
        echo '<p>従業員数: ' . get_field('employees') . '名</p>';
        echo '<p>年商: ' . number_format(get_field('revenue')) . '万円</p>';
        echo '<p>希望: ' . get_field('deal_type') . '</p>';
        echo '</div>';
    }
} else {
    echo '<p>条件に合う企業が見つかりませんでした。</p>';
}

wp_reset_postdata();
?>
```

## 確認項目

- [ ] カスタム投稿タイプが表示される
- [ ] カスタムフィールドが入力できる
- [ ] デモデータ5社が入力済み
- [ ] 検索フォームが動作する
- [ ] 条件に合う企業が表示される

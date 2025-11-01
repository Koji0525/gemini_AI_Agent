# M&Aポータル実装計画（ハイブリッドアプローチ）

**実装日**: 2025-10-31
**サイトURL**: https://uzbek-ma.com
**アプローチ**: 人間が実装 + エージェントが進捗管理

---

## �� 実装ゴール

デモ企業情報を検索できるM&Aポータルサイトを構築し、動作確認する

---

## 📋 実装タスク（所要時間: 約2-3時間）

### Task 1: カスタム投稿タイプ作成（20分）

**実装場所**: WordPress管理画面 → 外観 → テーマファイルエディター → functions.php

**追加するコード**:
```php
// M&A企業情報カスタム投稿タイプ
function create_ma_company_post_type() {
    register_post_type('ma_company', array(
        'labels' => array(
            'name' => 'M&A企業情報',
            'singular_name' => '企業情報',
            'add_new' => '新規追加',
            'add_new_item' => '新しい企業情報を追加',
            'edit_item' => '企業情報を編集',
            'view_item' => '企業情報を表示',
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
            'singular_name' => '業種',
        ),
        'hierarchical' => true,
        'show_in_rest' => true,
        'rewrite' => array('slug' => 'industry'),
    ));
}
add_action('init', 'create_ma_company_post_type');

// 業種カテゴリーを自動作成
function create_ma_industries() {
    $industries = array(
        'IT・ソフトウェア',
        '製造業',
        'サービス業',
        '小売業',
        '建設業',
        'その他',
    );
    
    foreach ($industries as $industry) {
        if (!term_exists($industry, 'ma_industry')) {
            wp_insert_term($industry, 'ma_industry');
        }
    }
}
add_action('init', 'create_ma_industries');
```

**確認方法**:
- 管理画面の左メニューに「M&A企業情報」が表示される
- 新規追加をクリックして編集画面が表示される

---

### Task 2: Advanced Custom Fields プラグイン導入（10分）

**手順**:
1. プラグイン → 新規追加 → 「Advanced Custom Fields」で検索
2. インストール → 有効化
3. ACF → フィールドグループ → 新規追加

**フィールドグループ名**: 企業詳細情報

**追加するフィールド**:

| フィールドラベル | フィールド名 | フィールドタイプ | 必須 |
|-----------------|-------------|----------------|------|
| 所在地 | location | テキスト | Yes |
| 資本金（万円） | capital | 数値 | Yes |
| 従業員数 | employees | 数値 | Yes |
| 年商（万円） | revenue | 数値 | Yes |
| 希望条件 | deal_type | 選択 | Yes |

**deal_type の選択肢**:
```
売却希望
買収希望
```

**表示ルール**:
- 投稿タイプ = M&A企業情報

---

### Task 3: デモ企業データ入力（30分）

**手順**: M&A企業情報 → 新規追加

#### 企業1: テックカンパニーA
```
タイトル: テックカンパニーA
業種: IT・ソフトウェア
所在地: 東京都渋谷区
資本金: 10000
従業員数: 50
年商: 100000
希望条件: 売却希望

本文:
AIを活用したSaaSプロダクトを展開する成長企業。
クラウドベースの業務効率化ツールで、中小企業を中心に
5,000社以上の導入実績。直近3年の売上成長率は年平均40%。
今後のさらなる成長のため、大手企業との資本提携を検討中。
```

#### 企業2: 製造業B
```
タイトル: 製造業B
業種: 製造業
所在地: 愛知県名古屋市
資本金: 5000
従業員数: 30
年商: 50000
希望条件: 売却希望

本文:
精密部品製造で高いシェアを持つ中堅企業。
自動車業界向けの金属加工を主力事業とし、
トヨタグループとの取引実績30年以上。
後継者不在のため、事業承継を前提とした売却を希望。
```

#### 企業3: サービスC
```
タイトル: サービスC
業種: サービス業
所在地: 大阪府大阪市
資本金: 3000
従業員数: 20
年商: 30000
希望条件: 買収希望

本文:
介護・福祉サービスで地域に根ざした事業展開。
訪問介護・デイサービスを運営し、利用者満足度95%以上。
施設数拡大のため、同業他社の買収を積極的に検討中。
```

#### 企業4: 小売店D
```
タイトル: 小売店D
業種: 小売業
所在地: 福岡県福岡市
資本金: 2000
従業員数: 15
年商: 20000
希望条件: 売却希望

本文:
地域密着型のスーパーマーケットチェーン（店舗数5店舗）。
地元産品を中心とした品揃えで、固定客多数。
オーナーの高齢化により、事業承継または売却を検討。
```

#### 企業5: 建設E
```
タイトル: 建設E
業種: 建設業
所在地: 北海道札幌市
資本金: 15000
従業員数: 80
年商: 150000
希望条件: 買収希望

本文:
公共工事を中心とした総合建設会社。
道路・橋梁工事で道内シェアトップクラス。
本州への事業エリア拡大のため、
同業者または関連企業の買収を検討中。
```

---

### Task 4: 検索ページ作成（60分）

**手順**:
1. 固定ページ → 新規追加
2. タイトル: 企業検索
3. テンプレート: カスタムテンプレート（以下のコード）

**page-company-search.php を作成**:
```php
<?php
/*
Template Name: 企業検索
*/
get_header();
?>

<div class="company-search-page">
    <h1>M&A企業検索</h1>
    
    <!-- 検索フォーム -->
    <form method="get" class="search-form">
        <div class="form-group">
            <label>業種</label>
            <?php
            $terms = get_terms(array(
                'taxonomy' => 'ma_industry',
                'hide_empty' => false,
            ));
            ?>
            <select name="industry">
                <option value="">全て</option>
                <?php foreach ($terms as $term): ?>
                    <option value="<?php echo $term->term_id; ?>" 
                        <?php selected($_GET['industry'] ?? '', $term->term_id); ?>>
                        <?php echo $term->name; ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>
        
        <div class="form-group">
            <label>資本金（万円）</label>
            <input type="number" name="capital_min" placeholder="最小" 
                value="<?php echo $_GET['capital_min'] ?? ''; ?>">
            〜
            <input type="number" name="capital_max" placeholder="最大"
                value="<?php echo $_GET['capital_max'] ?? ''; ?>">
        </div>
        
        <div class="form-group">
            <label>年商（万円）</label>
            <input type="number" name="revenue_min" placeholder="最小"
                value="<?php echo $_GET['revenue_min'] ?? ''; ?>">
            〜
            <input type="number" name="revenue_max" placeholder="最大"
                value="<?php echo $_GET['revenue_max'] ?? ''; ?>">
        </div>
        
        <div class="form-group">
            <label>希望条件</label>
            <select name="deal_type">
                <option value="">全て</option>
                <option value="売却希望" <?php selected($_GET['deal_type'] ?? '', '売却希望'); ?>>売却希望</option>
                <option value="買収希望" <?php selected($_GET['deal_type'] ?? '', '買収希望'); ?>>買収希望</option>
            </select>
        </div>
        
        <button type="submit" class="btn-search">検索</button>
    </form>
    
    <!-- 検索結果 -->
    <div class="search-results">
        <?php
        $args = array(
            'post_type' => 'ma_company',
            'posts_per_page' => 20,
        );
        
        // 業種フィルター
        if (!empty($_GET['industry'])) {
            $args['tax_query'] = array(
                array(
                    'taxonomy' => 'ma_industry',
                    'field' => 'term_id',
                    'terms' => $_GET['industry'],
                ),
            );
        }
        
        // カスタムフィールドフィルター
        $meta_query = array('relation' => 'AND');
        
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
        
        if (!empty($_GET['revenue_min'])) {
            $meta_query[] = array(
                'key' => 'revenue',
                'value' => $_GET['revenue_min'],
                'compare' => '>=',
                'type' => 'NUMERIC',
            );
        }
        
        if (!empty($_GET['revenue_max'])) {
            $meta_query[] = array(
                'key' => 'revenue',
                'value' => $_GET['revenue_max'],
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
        
        if (count($meta_query) > 1) {
            $args['meta_query'] = $meta_query;
        }
        
        $query = new WP_Query($args);
        
        if ($query->have_posts()):
            echo '<h2>検索結果: ' . $query->found_posts . '件</h2>';
            
            while ($query->have_posts()): $query->the_post();
                $location = get_field('location');
                $capital = get_field('capital');
                $employees = get_field('employees');
                $revenue = get_field('revenue');
                $deal_type = get_field('deal_type');
                $industries = get_the_terms(get_the_ID(), 'ma_industry');
                ?>
                
                <div class="company-item">
                    <h3><?php the_title(); ?></h3>
                    
                    <div class="company-meta">
                        <span class="industry">
                            <?php 
                            if ($industries) {
                                echo $industries[0]->name;
                            }
                            ?>
                        </span>
                        <span class="deal-type <?php echo sanitize_title($deal_type); ?>">
                            <?php echo $deal_type; ?>
                        </span>
                    </div>
                    
                    <div class="company-details">
                        <p><strong>所在地:</strong> <?php echo $location; ?></p>
                        <p><strong>資本金:</strong> <?php echo number_format($capital); ?>万円</p>
                        <p><strong>従業員数:</strong> <?php echo number_format($employees); ?>名</p>
                        <p><strong>年商:</strong> <?php echo number_format($revenue); ?>万円</p>
                    </div>
                    
                    <div class="company-excerpt">
                        <?php the_excerpt(); ?>
                    </div>
                    
                    <a href="<?php the_permalink(); ?>" class="btn-detail">詳細を見る</a>
                </div>
                
            <?php endwhile;
            
        else:
            echo '<p class="no-results">条件に合う企業が見つかりませんでした。</p>';
        endif;
        
        wp_reset_postdata();
        ?>
    </div>
</div>

<style>
.company-search-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.search-form {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 30px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    font-weight: bold;
    margin-bottom: 5px;
}

.form-group input,
.form-group select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.btn-search {
    background: #0073aa;
    color: white;
    padding: 10px 30px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.company-item {
    background: white;
    border: 1px solid #ddd;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 8px;
}

.company-meta {
    margin: 10px 0;
}

.industry {
    background: #e3f2fd;
    padding: 5px 10px;
    border-radius: 4px;
    margin-right: 10px;
}

.deal-type {
    padding: 5px 10px;
    border-radius: 4px;
}

.deal-type.売却希望 {
    background: #ffebee;
    color: #c62828;
}

.deal-type.買収希望 {
    background: #e8f5e9;
    color: #2e7d32;
}

.btn-detail {
    display: inline-block;
    background: #0073aa;
    color: white;
    padding: 8px 20px;
    text-decoration: none;
    border-radius: 4px;
    margin-top: 10px;
}
</style>

<?php get_footer(); ?>
```

---

## ✅ 動作確認チェックリスト

- [ ] **Task 1完了**: 管理画面に「M&A企業情報」メニューが表示される
- [ ] **Task 2完了**: ACFでカスタムフィールドが設定される
- [ ] **Task 3完了**: デモ企業5社が入力される
- [ ] **Task 4完了**: 企業検索ページが表示される
- [ ] **検索テスト1**: 業種「IT・ソフトウェア」で検索 → テックカンパニーAが表示
- [ ] **検索テスト2**: 資本金「5000〜15000万円」で検索 → 3社表示
- [ ] **検索テスト3**: 希望条件「売却希望」で検索 → 3社表示
- [ ] **検索テスト4**: 希望条件「買収希望」で検索 → 2社表示
- [ ] **検索テスト5**: 年商「50000万円以上」で検索 → 3社表示

---

## 🎉 完成後のデモ

**URL**: https://uzbek-ma.com/企業検索/

**デモシナリオ**:
1. 「IT企業で売却希望の案件を探したい」
   → 業種: IT・ソフトウェア、希望: 売却希望 → テックカンパニーA が表示
   
2. 「資本金5000万円以上の製造業を探したい」
   → 業種: 製造業、資本金: 5000〜 → 製造業B が表示
   
3. 「買収を希望している企業を探したい」
   → 希望: 買収希望 → サービスC、建設E が表示


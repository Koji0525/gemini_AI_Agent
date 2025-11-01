# WordPress実環境適用ガイド

## 🎯 目的

生成したカスタム投稿タイプとタクソノミーを実際のWordPressサイト（https://uzbek-ma.com）に適用する。

**所要時間**: 30分

---

## 📋 準備

### 必要なもの
- ✅ WordPressサイトへの管理者アクセス
- ✅ テーマエディター編集権限 または FTP/SFTP アクセス
- ✅ 生成されたPHPファイル

### 生成されたファイル
```
agent_outputs/
├── wordpress_cpt/
│   ├── cpt_portfolio_YYYYMMDD_HHMMSS.php  # ポートフォリオ投稿タイプ
│   └── cpt_event_YYYYMMDD_HHMMSS.php      # イベント投稿タイプ
└── wordpress_taxonomy/
    ├── taxonomy_project_category_YYYYMMDD_HHMMSS.php  # プロジェクトカテゴリー
    ├── taxonomy_project_tag_YYYYMMDD_HHMMSS.php       # プロジェクトタグ
    └── taxonomy_skill_YYYYMMDD_HHMMSS.php             # スキル
```

---

## 🚀 方法1: functions.phpに追加（推奨・最速）

### STEP 1: PHPコードの準備

1. 最新のportfolioファイルを開く
```bash
   cat agent_outputs/wordpress_cpt/cpt_portfolio_*.php | head -50
```

2. `<?php` と `?>` を除いたコードをコピー
   - 先頭の `<?php` を削除
   - 末尾の `?>` を削除
   - 関数本体とadd_action部分のみをコピー

### STEP 2: WordPress管理画面での作業

1. **WordPressにログイン**
   - URL: https://uzbek-ma.com/wp-admin
   - ログイン情報: .envファイルの認証情報を使用

2. **テーマエディターを開く**
   - 外観 → テーマファイルエディター
   - 「編集するテーマを選択」で現在のテーマを選択
   - 右側のファイル一覧から「functions.php」をクリック

3. **コードを追加**
```php
   // === カスタム投稿タイプ: ポートフォリオ ===
   function register_cpt_portfolio() {
       $labels = array(
           // ... (コピーした内容)
       );
       
       $args = array(
           // ... (コピーした内容)
       );
       
       register_post_type('portfolio', $args);
   }
   add_action('init', 'register_cpt_portfolio');
   
   // === カスタムタクソノミー: スキル ===
   function register_taxonomy_skill() {
       $labels = array(
           // ... (コピーした内容)
       );
       
       $args = array(
           // ... (コピーした内容)
       );
       
       register_taxonomy('skill', array('portfolio'), $args);
   }
   add_action('init', 'register_taxonomy_skill');
```

4. **保存**
   - 「ファイルを更新」ボタンをクリック
   - エラーが表示されないことを確認

### STEP 3: パーマリンク設定の更新（重要！）

1. **設定 → パーマリンク設定**
2. そのまま一番下の「変更を保存」をクリック
   - これでカスタム投稿タイプのリライトルールが更新される

### STEP 4: 確認

1. **管理画面の左メニューを確認**
   - 「ポートフォリオ一覧」が表示されているはず
   - クリックして投稿一覧画面が開くことを確認

2. **新規作成をテスト**
   - 「ポートフォリオ一覧」→「新規追加」
   - タイトルと内容を入力
   - 右側に「スキル」タクソノミーが表示されていることを確認
   - 下書き保存または公開

3. **REST APIで確認**
```bash
   curl https://uzbek-ma.com/wp-json/wp/v2/types/portfolio
```
   - JSON形式でポートフォリオ投稿タイプの情報が返ってくれば成功

---

## 🔧 方法2: カスタムプラグインとして使用

### STEP 1: プラグインファイルの作成

1. 生成されたPHPファイルにプラグインヘッダーを追加
```php
<?php
/**
 * Plugin Name: Custom Post Types & Taxonomies
 * Description: ポートフォリオサイト用のカスタム投稿タイプとタクソノミー
 * Version: 1.0
 * Author: Gemini AI Agent
 */

// === 以下、生成されたコード ===
function register_cpt_portfolio() {
    // ...
}
add_action('init', 'register_cpt_portfolio');

function register_taxonomy_skill() {
    // ...
}
add_action('init', 'register_taxonomy_skill');
?>
```

### STEP 2: FTP/SFTPでアップロード

1. ファイル名を `custom-post-types.php` にリネーム
2. FTP/SFTPでWordPressサーバーに接続
3. `wp-content/plugins/custom-post-types/` ディレクトリを作成
4. `custom-post-types.php` をアップロード

### STEP 3: プラグインを有効化

1. WordPress管理画面 → プラグイン
2. 「Custom Post Types & Taxonomies」を探す
3. 「有効化」をクリック

---

## ✅ 成功の確認チェックリスト

- [ ] WordPress管理画面の左メニューに「ポートフォリオ一覧」が表示される
- [ ] 「ポートフォリオ一覧」→「新規追加」が開ける
- [ ] 投稿編集画面で「スキル」タクソノミーが選択できる
- [ ] REST API (`/wp-json/wp/v2/types/portfolio`) がJSONを返す
- [ ] パーマリンク設定を更新済み
- [ ] task_execution_logシートに記録が残っている

---

## 🐛 トラブルシューティング

### エラー: Parse error
- **原因**: PHPの構文エラー
- **対処**: コピーしたコードに `<?php` や `?>` が含まれていないか確認

### 投稿タイプが表示されない
- **原因**: パーマリンク設定の未更新
- **対処**: 設定 → パーマリンク設定 → 変更を保存

### 404エラーが出る
- **原因**: リライトルールの未更新
- **対処**: パーマリンク設定を2回保存してみる

### functions.phpが保存できない
- **原因**: ファイル権限の問題
- **対処**: FTP/SFTPで直接編集するか、サーバー管理者に確認

---

## 📸 完成イメージ

### 管理画面
```
WordPress管理画面
├── ダッシュボード
├── 投稿
├── メディア
├── 固定ページ
├── ポートフォリオ一覧 ← ★ 追加される
│   ├── 新規追加
│   ├── スキル ← ★ タクソノミー
│   └── ...
└── ...
```

### 投稿編集画面
```
[タイトル]
┌─────────────────────────┐
│ プロジェクト名を入力    │
└─────────────────────────┘

[本文エディター]
┌─────────────────────────┐
│ プロジェクトの説明...   │
└─────────────────────────┘

[右サイドバー]
┌─────────────────────────┐
│ 公開                    │
│ カテゴリー              │
│ タグ                    │
│ アイキャッチ画像        │
│                         │
│ スキル ← ★ 追加された  │
│ □ PHP                   │
│ □ WordPress             │
│ □ Python                │
└─────────────────────────┘
```

---

**作成日**: 2025-10-28  
**更新日**: 2025-10-28  
**対象サイト**: https://uzbek-ma.com

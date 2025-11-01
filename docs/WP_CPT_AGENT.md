# WPCPTAgent - カスタム投稿タイプ管理

## 📋 概要

WordPressのカスタム投稿タイプ（CPT）を自動生成するエージェント。
PHPコード生成方式を採用し、WordPress標準の`register_post_type()`を使用。

**実装日**: 2025-10-28  
**バージョン**: v1.0

---

## 🚀 使い方

### 基本的な使用方法
```python
from configuration.config_loader import ConfigLoader
from agents.wordpress.specialized import WPCPTAgent, CPTSpecification

# 初期化
config = ConfigLoader()
agent = WPCPTAgent(config)

# CPT仕様を定義
spec = CPTSpecification(
    post_type="portfolio",           # 投稿タイプ名（slug）
    singular_name="ポートフォリオ",    # 単数形ラベル
    plural_name="ポートフォリオ一覧",  # 複数形ラベル
    description="作品ポートフォリオを管理",
    has_archive=True,                # アーカイブページ有無
    hierarchical=False,              # 階層構造（固定ページ風）
    supports=['title', 'editor', 'thumbnail', 'excerpt'],
    menu_icon="dashicons-portfolio"  # メニューアイコン
)

# CPT作成（PHPコード生成）
result = await agent.create_cpt(spec)

print(f"保存先: {result['filepath']}")
```

---

## 📊 主な機能

### 1. 既存投稿タイプの一覧取得
```python
# 既存の投稿タイプを取得
types = await agent.list_post_types()
```

### 2. 投稿タイプの存在確認
```python
# 特定の投稿タイプが存在するか確認
exists = await agent.verify_post_type("portfolio")
```

### 3. PHPコード生成
```python
# register_post_type()のPHPコードを生成
php_code = agent.generate_php_code(spec)
```

---

## 🔧 CPTSpecification パラメータ

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-------|------|-----------|------|
| `post_type` | str | ✅ | - | 投稿タイプ名（slug）英数字とアンダースコア |
| `singular_name` | str | ✅ | - | 単数形ラベル |
| `plural_name` | str | ✅ | - | 複数形ラベル |
| `description` | str | ❌ | "" | 説明文 |
| `public` | bool | ❌ | True | 公開するか |
| `has_archive` | bool | ❌ | True | アーカイブページを持つか |
| `hierarchical` | bool | ❌ | False | 階層構造（固定ページ風） |
| `supports` | List[str] | ❌ | `['title', 'editor', 'thumbnail', 'excerpt']` | サポート機能 |
| `menu_icon` | str | ❌ | "dashicons-admin-post" | メニューアイコン |
| `show_in_rest` | bool | ❌ | True | REST APIで表示 |

### サポート機能の選択肢

- `title`: タイトル
- `editor`: エディター
- `thumbnail`: アイキャッチ画像
- `excerpt`: 抜粋
- `custom-fields`: カスタムフィールド
- `comments`: コメント
- `revisions`: リビジョン
- `author`: 投稿者
- `page-attributes`: ページ属性

---

## 📦 生成されるファイル

### 出力先
```
agent_outputs/wordpress_cpt/
└── cpt_[post_type]_[timestamp].php
```

### 生成されるPHPコード例
```php
<?php
/**
 * カスタム投稿タイプ: ポートフォリオ一覧
 * 生成日時: 2025-10-28 19:39:07
 */

function register_cpt_portfolio() {
    $labels = array(
        'name' => 'ポートフォリオ一覧',
        'singular_name' => 'ポートフォリオ',
        'add_new' => '新規ポートフォリオ追加',
        // ... 他のラベル
    );
    
    $args = array(
        'labels' => $labels,
        'description' => '作品ポートフォリオを管理',
        'public' => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'menu_icon' => 'dashicons-portfolio',
        'show_in_rest' => true,
    );
    
    register_post_type('portfolio', $args);
}

add_action('init', 'register_cpt_portfolio');
?>
```

---

## 🔄 WordPressへの適用方法

### 方法1: functions.phpに追加（推奨）

1. 生成されたPHPファイルを開く
2. `<?php` と `?>` を除いたコードをコピー
3. テーマの `functions.php` に貼り付け
4. WordPressダッシュボード → 設定 → パーマリンク設定 → 変更を保存

### 方法2: カスタムプラグインとして使用

1. 生成されたファイルを `wp-content/plugins/` に配置
2. WordPressダッシュボード → プラグイン → 有効化
3. パーマリンク設定を更新

⚠️ **重要**: パーマリンク設定の更新を忘れずに！

---

## 🧪 テスト

### テストスクリプト実行
```bash
python3 agents/wordpress/specialized/wp_cpt_agent.py
```

### 動作確認

1. PHPコードが生成されるか
2. ファイルが保存されるか
3. REST APIで投稿タイプが確認できるか（適用後）

---

## 🐛 トラブルシューティング

### 投稿タイプ名のルール
- 英数字とアンダースコアのみ
- 20文字以内
- WordPressの予約語を避ける（post, page, attachment など）

### よくあるエラー
- **"投稿タイプが表示されない"**: パーマリンク設定を更新
- **"404エラー"**: パーマリンク設定を更新
- **"権限エラー"**: functions.phpの編集権限を確認

---

## 📚 関連ドキュメント

- [WordPress Codex: register_post_type()](https://developer.wordpress.org/reference/functions/register_post_type/)
- [Dashicons一覧](https://developer.wordpress.org/resource/dashicons/)

---

**作成日**: 2025-10-28  
**最終更新**: 2025-10-28  
**バージョン**: 1.0

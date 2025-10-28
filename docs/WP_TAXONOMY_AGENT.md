# WPTaxonomyAgent - カスタムタクソノミー管理

## 📋 概要

WordPressのカスタムタクソノミー（分類）を自動生成するエージェント。
階層型（カテゴリー風）と非階層型（タグ風）の両方に対応。

**実装日**: 2025-10-28  
**バージョン**: v2.0

---

## 🚀 使い方

### 基本的な使用方法
```python
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager
from agents.wordpress.specialized import WPTaxonomyAgent, TaxonomySpecification

# 初期化
config = ConfigLoader()
sheets_manager = GoogleSheetsManager(
    spreadsheet_id=config._config.get("SPREADSHEET_ID"),
    service_account_file=config._config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
)
agent = WPTaxonomyAgent(config, sheets_manager)

# タクソノミー仕様を定義（階層型）
spec = TaxonomySpecification(
    taxonomy="skill",
    singular_name="スキル",
    plural_name="スキル一覧",
    post_types=['portfolio', 'post'],
    hierarchical=True  # カテゴリー風
)

# タクソノミー作成（PHPコード生成 + ログ記録）
result = await agent.create_taxonomy(spec)
```

---

## 📊 主な機能

### 1. 階層型（カテゴリー風）タクソノミー

親子関係を持つ階層構造のタクソノミー。
```python
spec = TaxonomySpecification(
    taxonomy="project_category",
    singular_name="プロジェクトカテゴリー",
    plural_name="プロジェクトカテゴリー一覧",
    hierarchical=True  # 階層型
)
```

### 2. 非階層型（タグ風）タクソノミー

フラットな構造のタクソノミー。
```python
spec = TaxonomySpecification(
    taxonomy="project_tag",
    singular_name="プロジェクトタグ",
    plural_name="プロジェクトタグ一覧",
    hierarchical=False  # 非階層型
)
```

---

## 🔧 TaxonomySpecification パラメータ

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-------|------|-----------|------|
| `taxonomy` | str | ✅ | - | タクソノミー名（slug） |
| `singular_name` | str | ✅ | - | 単数形ラベル |
| `plural_name` | str | ✅ | - | 複数形ラベル |
| `post_types` | List[str] | ❌ | `['post']` | 対象投稿タイプ |
| `hierarchical` | bool | ❌ | True | 階層構造（True=カテゴリー風, False=タグ風） |
| `show_admin_column` | bool | ❌ | True | 管理画面のカラムに表示 |

---

## 📊 スプレッドシート記録

タクソノミー作成時、`task_execution_log`シートに自動記録:
- **task_id**: タイムスタンプ（数字）
- **agent_role**: WPTaxonomyAgent
- **status**: completed / failed
- **Quality_Score**: 10 (成功) / 1 (失敗)

---

**作成日**: 2025-10-28  
**最終更新**: 2025-10-28  
**バージョン**: 2.0

# 🤖 Gemini AI Agent - WordPress自動構築システム

WordPress サイトを AI で自動構築するエージェントシステム

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![WordPress Compatible](https://img.shields.io/badge/WordPress-6.0+-blue.svg)](https://wordpress.org/)

---

## 🎯 概要

このプロジェクトは、Google Gemini API を使用して WordPress サイトの構築を自動化するマルチエージェントシステムです。

### ✨ 主な機能

- 🏗️ **カスタム投稿タイプ（CPT）の自動生成**
- 🏷️ **カスタムタクソノミーの自動生成**
- 📝 **ACF カスタムフィールドの自動生成**
- 📊 **Google Sheets 統合（実行ログ記録）**
- 🔍 **WordPress 設定検証システム**
- 🎬 **統合デモ（5分でポートフォリオサイト構築）**

---

## 🚀 クイックスタート

### 必要な環境

- Python 3.8+
- WordPress 6.0+（REST API有効）
- Google Cloud Platform アカウント
- Advanced Custom Fields（ACF）プラグイン

### インストール
```bash
# リポジトリのクローン
git clone https://github.com/yourusername/gemini_AI_Agent.git
cd gemini_AI_Agent

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して認証情報を設定
```

### 設定

`.env` ファイルに以下を設定:
```env
# WordPress設定
WP_URL=https://your-site.com
wp_user=your_username
wp_pass=your_password

# Google API
GEMINI_API_KEY=your_gemini_api_key
SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json
```

### 基本的な使用方法
```bash
# WordPress設定確認
python3 configuration/config_validation_system.py

# デモ実行：完全版ポートフォリオサイト構築
python3 demos/complete_portfolio_site_demo.py
```

---

## 📚 エージェント一覧

### 1. WPCPTAgent（カスタム投稿タイプ）
```python
from agents.wordpress.specialized import WPCPTAgent, CPTSpecification

cpt_spec = CPTSpecification(
    post_type="portfolio",
    singular_name="ポートフォリオ",
    plural_name="ポートフォリオ一覧"
)

agent = WPCPTAgent(config, sheets_manager)
result = await agent.create_cpt(cpt_spec)
```

**生成物:**
- `cpt_portfolio_YYYYMMDD_HHMMSS.php`

### 2. WPTaxonomyAgent（タクソノミー）
```python
from agents.wordpress.specialized import WPTaxonomyAgent, TaxonomySpecification

tax_spec = TaxonomySpecification(
    taxonomy="skill",
    singular_name="スキル",
    plural_name="スキル一覧",
    hierarchical=True  # カテゴリー風
)

agent = WPTaxonomyAgent(config, sheets_manager)
result = await agent.create_taxonomy(tax_spec)
```

**生成物:**
- `taxonomy_skill_YYYYMMDD_HHMMSS.php`

### 3. WPACFAgent（カスタムフィールド）
```python
from agents.wordpress.specialized import WPACFAgent, ACFFieldGroupSpec, ACFFieldSpec

acf_spec = ACFFieldGroupSpec(
    key="group_portfolio",
    title="ポートフォリオ詳細",
    fields=[
        ACFFieldSpec(
            key="field_client",
            label="クライアント名",
            name="client_name",
            type="text"
        )
    ]
)

agent = WPACFAgent(config, sheets_manager)
result = await agent.create_field_group(acf_spec)
```

**生成物:**
- `acf_group_portfolio_YYYYMMDD_HHMMSS.json`
- `acf_group_portfolio_YYYYMMDD_HHMMSS.php`

---

## 🎬 デモ

### 完全版ポートフォリオサイト構築
```bash
python3 demos/complete_portfolio_site_demo.py
```

**5分で以下を自動生成:**
- ✅ portfolio 投稿タイプ
- ✅ skill タクソノミー（階層型）
- ✅ project_category タクソノミー（階層型）
- ✅ project_tag タクソノミー（非階層型）
- ✅ ACF カスタムフィールド（5個）

---

## 📁 プロジェクト構造
```
gemini_AI_Agent/
├── agents/
│   └── wordpress/
│       ├── specialized/
│       │   ├── wp_cpt_agent.py         # CPT管理
│       │   ├── wp_taxonomy_agent.py    # タクソノミー管理
│       │   ├── wp_acf_agent.py         # ACF管理
│       │   └── wp_agent_logger.py      # ログ記録
│       └── wp_site_builder.py          # 統合オーケストレーター
├── tools/
│   ├── sheets_manager.py               # Google Sheets統合
│   └── gemini_api_client.py            # Gemini API
├── configuration/
│   ├── config_loader.py                # 設定管理
│   └── config_validation_system.py     # 設定検証
├── demos/
│   └── complete_portfolio_site_demo.py # 完全版デモ
├── scripts/
│   ├── show_project_structure.py       # プロジェクト構造可視化
│   └── generate_progress_report.sh     # 進捗レポート
└── agent_outputs/                      # 生成されたファイル
    ├── wordpress_cpt/
    ├── wordpress_taxonomy/
    └── wordpress_acf/
```

---

## 📊 実行ログ

すべてのエージェント実行は Google Sheets の `task_execution_log` シートに自動記録されます。

**記録内容:**
- task_id（タイムスタンプ）
- agent_role（エージェント名）
- output_summary（実行サマリー）
- output_data（生成ファイルパス）
- status（completed/failed）
- Quality_Score（1-10）

---

## 🔧 カスタマイズ

### プロジェクト構造の表示
```bash
# Pythonファイルのみ表示
python3 scripts/show_project_structure.py
```

### 進捗レポート
```bash
# 最新の進捗状況を表示
./scripts/generate_progress_report.sh
```

---

## 📖 ドキュメント

- [WP_CPT_AGENT.md](docs/WP_CPT_AGENT.md) - CPTエージェント詳細
- [WP_TAXONOMY_AGENT.md](docs/WP_TAXONOMY_AGENT.md) - タクソノミーエージェント詳細
- [WP_ACF_AGENT.md](docs/WP_ACF_AGENT.md) - ACFエージェント詳細
- [WORDPRESS_DEPLOYMENT_GUIDE.md](docs/WORDPRESS_DEPLOYMENT_GUIDE.md) - WordPress適用ガイド

---

## 🧪 テスト
```bash
# 個別エージェントテスト
python3 agents/wordpress/specialized/wp_cpt_agent.py
python3 agents/wordpress/specialized/wp_taxonomy_agent.py
python3 agents/wordpress/specialized/wp_acf_agent.py

# 統合テスト
python3 demos/complete_portfolio_site_demo.py
```

---

## 📈 進捗状況

- ✅ コアシステム: 100%
- ✅ WordPress エージェント: 100%
- ✅ 設定確認システム: 100%
- ✅ 統合テスト: 100%
- ✅ ドキュメント: 100%

**総合進捗: 100% 🎉**

---

## 🤝 コントリビューション

プルリクエストを歓迎します！

---

## 📝 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

---

## 👤 作者

Gemini AI Agent Project Team

---

## 🙏 謝辞

- WordPress Community
- Google Gemini API
- Advanced Custom Fields

---

**作成日**: 2025-10-28  
**バージョン**: 1.0.0  
**Status**: ✅ Production Ready

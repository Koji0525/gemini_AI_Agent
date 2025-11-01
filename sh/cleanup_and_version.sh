#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "🧹 プロジェクト整理とバージョン管理"
echo "=========================================="

# ====================================================================
# STEP 1: .gitignore 作成・更新
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/6] .gitignore 作成${NC}"
echo "=========================================="

cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# 環境変数・認証情報
.env
.env.local
credentials.json
configuration/service_account.json
*.key
*.pem

# Google Sheets認証
token.json
token.pickle

# ブラウザデータ
cookies/
*.pkl
session_data/
chrome_profile/
browser_profile/

# ログファイル
*.log
logs/

# テンポラリファイル
*.tmp
*.bak
*.swp
*~
.DS_Store

# 出力ファイル（オプション - 必要に応じてコメントアウト）
# agent_outputs/
# downloads/

# IDE設定
.vscode/
.idea/
*.sublime-*

# テストファイル
.pytest_cache/
.coverage
htmlcov/

# スクリプト実行結果
*.md.backup
*_backup.*

# 一時的なテストスクリプト（本番用スクリプトは含める）
test_*.sh
*_temp.py
*_tmp.py

GITIGNORE

echo "✅ .gitignore 作成完了"

# ====================================================================
# STEP 2: 不要ファイルの特定
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/6] 不要ファイルの特定${NC}"
echo "=========================================="

echo ""
echo "削除推奨ファイル:"
echo ""

# バックアップファイル
find . -name "*.backup" -o -name "*.bak" -o -name "*_backup.*" | head -20

# 一時ファイル
find . -name "*.tmp" -o -name "*.swp" -o -name "*~" | head -20

# Pythonキャッシュ
find . -name "__pycache__" -type d | head -20

echo ""
echo -e "${YELLOW}これらのファイルを削除しますか？ (y/n)${NC}"
read -p "> " delete_confirm

if [ "$delete_confirm" = "y" ]; then
    echo "🗑️  削除中..."
    
    find . -name "*.backup" -delete
    find . -name "*.bak" -delete
    find . -name "*_backup.*" -delete
    find . -name "*.tmp" -delete
    find . -name "*.swp" -delete
    find . -name "*~" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    echo "✅ 削除完了"
else
    echo "⏭️  スキップ"
fi

# ====================================================================
# STEP 3: README.md 作成
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/6] README.md 作成${NC}"
echo "=========================================="

cat > README.md << 'README'
# 🤖 Gemini AI Agent - WordPress統合システム

Google Gemini AIとWordPressを統合した自動タスク実行システム

## 🎯 概要

このシステムは、Google Sheetsでタスクを管理し、Gemini AIとWordPressエージェントを使って自動実行します。

### 主な機能

- ✅ Google Sheets連携（タスク管理）
- ✅ Gemini AI統合（テキスト生成）
- ✅ WordPressエージェント（記事投稿・管理）
- ✅ タスク間の依存関係管理
- ✅ 実行ログの自動記録
- ✅ ハイブリッドストレージ（GitHub + Sheets）

## 📋 必要要件

### 環境
- Python 3.12+
- Google Chrome
- Xvfb（ヘッドレスブラウザ用）

### 認証情報
- Google Sheets API認証情報（`configuration/service_account.json`）
- Google Sheetsスプレッドシート（タスク管理用）

## 🚀 セットアップ

### 1. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 2. Google Sheets認証設定
```bash
# サービスアカウントJSONを配置
cp your_service_account.json configuration/service_account.json

# スプレッドシートIDを設定
./setup_sheets_properly.sh
```

### 3. Xvfb起動（ヘッドレス環境）
```bash
./setup_xvfb.sh
```

## 📊 使い方

### 基本的なタスク実行
```bash
# 統合システム実行（推奨）
DISPLAY=:1 python3 run_hybrid_storage_fixed.py

# 最大タスク数を指定
DISPLAY=:1 python3 run_hybrid_storage_fixed.py --max-tasks 5
```

### 高度な機能
```bash
# 高度なフィードバックシステム（優先度制御）
DISPLAY=:1 python3 run_advanced_feedback_system.py --max-tasks 10
```

## 📁 プロジェクト構造
```
gemini_AI_Agent/
├── browser_control/
│   ├── browser_controller.py      # ブラウザ操作
│   └── browser_cookie_and_session.py
├── wordpress/
│   ├── wp_agent.py                 # WordPressメインエージェント
│   ├── wp_dev/
│   │   ├── wp_cpt_agent.py        # カスタム投稿タイプ
│   │   ├── wp_acf_agent.py        # ACFエージェント
│   │   └── wp_requirements_agent.py
│   └── wp_post_creator.py
├── tools/
│   └── sheets_manager.py          # Google Sheets管理
├── configuration/
│   ├── config_loader.py           # 設定読み込み
│   └── service_account.json       # 認証情報（要作成）
├── agent_outputs/
│   └── tasks/                     # タスク出力ファイル
└── run_hybrid_storage_fixed.py   # メイン実行スクリプト
```

## 🔄 ワークフロー

1. **タスク作成**: Google Sheetsの`pm_tasks`シートにタスク追加
2. **自動実行**: システムがpendingタスクを検出・実行
3. **結果保存**: 
   - GitHub: 完全な出力（`agent_outputs/tasks/`）
   - Sheets: サマリーとメタデータ（`task_execution_log`）
4. **依存関係**: 前のタスクの出力を次のタスクで活用

## 📊 Google Sheetsの構造

### pm_tasks シート
| task_id | description | required_role | status | priority | dependencies |
|---------|-------------|---------------|--------|----------|--------------|
| 1 | タスク内容 | design | pending | high | - |
| 2 | 次のタスク | wp_dev | pending | high | 1 |

### task_execution_log シート
| log_id | task_id | agent_role | status | output_summary | output_data |
|--------|---------|------------|--------|----------------|-------------|
| 1 | 1 | design | completed | サマリー | GitHub参照リンク |

## 🎯 バージョン管理

このプロジェクトは[セマンティックバージョニング](https://semver.org/)を使用します。

### バージョン形式
```
vMAJOR.MINOR.PATCH[-LABEL]

例:
v1.0.0        - 初回リリース
v1.1.0        - 新機能追加
v1.0.1        - バグ修正
v2.0.0        - 破壊的変更
v1.0.0-beta   - ベータ版
```

### 現在のバージョン
**v1.0.0-integrated** - 統合システム初回リリース

## 🛠️ トラブルシューティング

### Gemini接続エラー
```bash
# クッキーを削除して再ログイン
rm -rf cookies/
```

### Google Sheets認証エラー
```bash
# サービスアカウントの権限を確認
# スプレッドシートに編集者権限で共有されているか確認
```

### ブラウザエラー
```bash
# Xvfbを再起動
./setup_xvfb.sh
```

## 📝 ライセンス

MIT License

## 👥 コントリビューション

プルリクエスト歓迎！

## 📧 サポート

問題がある場合は、Issueを作成してください。

---

**最終更新**: 2025-10-19  
**バージョン**: v1.0.0-integrated

README

echo "✅ README.md 作成完了"

# ====================================================================
# STEP 4: requirements.txt 作成
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 4/6] requirements.txt 作成${NC}"
echo "=========================================="

cat > requirements.txt << 'REQUIREMENTS'
# ブラウザ自動化
playwright==1.40.0
selenium==4.15.2

# Google APIs
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
gspread==5.12.0

# データ処理
pandas==2.1.3
openpyxl==3.1.2

# HTTP
requests==2.31.0
httpx==0.25.2

# 環境変数
python-dotenv==1.0.0

# ログ
colorlog==6.8.0

# ユーティリティ
python-dateutil==2.8.2
pytz==2023.3

REQUIREMENTS

echo "✅ requirements.txt 作成完了"

# ====================================================================
# STEP 5: バージョン情報ファイル作成
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 5/6] バージョン情報作成${NC}"
echo "=========================================="

cat > VERSION << 'VERSION_FILE'
v1.0.0-integrated
VERSION_FILE

cat > CHANGELOG.md << 'CHANGELOG'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-integrated] - 2025-10-19

### Added
- ✨ Google Sheets統合（タスク管理）
- ✨ Gemini AI統合（テキスト生成）
- ✨ WordPressエージェント統合
- ✨ タスク間の依存関係管理
- ✨ ハイブリッドストレージ（GitHub + Sheets）
- ✨ task_execution_log自動記録
- ✨ 優先度ベースのタスク実行
- ✨ レート制限機能（10秒間隔）

### Changed
- 🔧 ブラウザコントローラー改善
- 🔧 エラーハンドリング強化

### Fixed
- 🐛 パスエラー修正
- 🐛 インポートエラー修正

## [Unreleased]

### Planned
- 📝 WordPress自動投稿機能強化
- 📝 品質評価と再実行機能
- 📝 学習・改善機能

CHANGELOG

echo "✅ VERSION, CHANGELOG.md 作成完了"

# ====================================================================
# STEP 6: Git状態確認とコミット準備
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 6/6] Git状態確認${NC}"
echo "=========================================="

echo ""
echo "現在のブランチ:"
git branch --show-current

echo ""
echo "Git状態:"
git status --short | head -20

echo ""
echo "コミット対象ファイル数:"
git status --short | wc -l

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 整理完了${NC}"
echo "=========================================="

echo ""
echo "次のステップ:"
echo ""
echo "1. 変更内容を確認:"
echo "   git status"
echo ""
echo "2. ファイルをステージング:"
echo "   git add ."
echo ""
echo "3. コミット:"
echo "   git commit -m \"v1.0.0-integrated: 統合システム初回リリース\""
echo ""
echo "4. プッシュ:"
echo "   git push origin v1.0.0-integrated"
echo ""
echo "5. タグ作成（オプション）:"
echo "   git tag -a v1.0.0-integrated -m \"統合システム初回リリース\""
echo "   git push origin v1.0.0-integrated --tags"
echo ""


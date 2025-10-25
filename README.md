# 🤖 Gemini AI Agent - タスク管理システム

[![Version](https://img.shields.io/badge/version-v1.3.0--add--operation-blue)](./VERSION)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-Phase%201%20Complete-success)](./PHASE2_DESIGN.md)

## 📊 現在のバージョン

**v1.3.0-add-operation** - Phase 1完了版

---

## 🎯 概要

Google SheetsベースのPM（プロジェクト管理）システムと連携し、Gemini AIおよびWordPressを使用してタスクを自動実行するシステムです。

### ✨ Phase 1で実装された機能

#### 🤖 タスク実行
- ✅ **Geminiタスク自動実行** - AIによる自動処理
- ✅ **WordPressタスク実行** - WP管理画面での自動操作
- ✅ **タスクルーティング** - execution_type による自動振り分け

#### 📊 品質管理
- ✅ **自動レビュー機能** - 実行結果を10点満点で評価
- ✅ **品質スコア記録** - task_execution_logシートに記録
- ✅ **ステータス管理** - pending → in_progress → completed/failed

#### 🔧 システム機能
- ✅ **execution_type自動判定** - タスク内容からGemini/WPを判別
- ✅ **WordPress認証** - クッキーベース自動ログイン
- ✅ **WordPressDevAgent** - CPT/ACF/Requirements統合エージェント

---

## 🏗️ システム構成
```
┌──────────────────────────────────────┐
│  📊 Google Sheets (pm_tasks)         │
│  - タスク管理                         │
│  - execution_type設定                │
│  - ステータス管理                     │
└──────────────┬───────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│  🎛️ run_pm_tasks_adaptive.py        │
│  - タスクルーティング                 │
│  - ステータス自動更新                 │
└──────────────┬───────────────────────┘
               │
        ┌──────┴──────┐
        ↓             ↓
┌──────────┐  ┌──────────────────┐
│ Gemini   │  │ WordPress        │
│ AI       │  │ DevAgent         │
└────┬─────┘  └─────┬────────────┘
     │              │
     └──────┬───────┘
            ↓
    ┌───────────────────┐
    │ ReviewAgent       │
    │ 品質評価 (10点満点)│
    └───────┬───────────┘
            ↓
    ┌───────────────────────────┐
    │ task_execution_log        │
    │ 実行結果・品質スコア記録  │
    └───────────────────────────┘
```

---

## 📁 主要ファイル

### コアシステム
- `run_pm_tasks_adaptive.py` - メインシステム（タスク実行・ルーティング）
- `tools/pm_tasks_loader.py` - Google Sheetsからタスク読み込み
- `tools/execution_type_manager.py` - execution_type判定・管理

### エージェント
- `core_agents/review_agent.py` - レビューエージェント
- `wordpress/wp_dev/wp_dev_agent.py` - WordPress統合エージェント
- `wordpress/wp_dev/wp_cpt_agent.py` - CPT（カスタム投稿タイプ）
- `wordpress/wp_dev/wp_acf_agent.py` - ACF（カスタムフィールド）
- `wordpress/wp_dev/wp_requirements_agent.py` - 要件定義

### ブラウザ制御
- `browser_control/browser_controller.py` - ブラウザ操作
- `browser_control/browser_wp_session_manager.py` - WPセッション管理
- `wordpress/wp_auth.py` - WordPress認証

---

## 🚀 使い方

### 1. タスク準備
Google Sheets の `pm_tasks` シートにタスクを登録：

| task_id | Title | Description | Status | execution_type |
|---------|-------|-------------|--------|----------------|
| 1 | 要件定義 | システムの要件を定義 | pending | gemini |
| 2 | CPT作成 | M&A案件CPT作成 | pending | wordpress |

### 2. execution_type 自動設定（オプション）
```bash
python3 tools/execution_type_manager.py
```

### 3. タスク実行
```bash
# 最大5タスクを実行
DISPLAY=:1 python3 run_pm_tasks_adaptive.py --max-tasks 5 --status pending

# 特定のタスクを実行
DISPLAY=:1 python3 run_pm_tasks_adaptive.py --task-id 1
```

### 4. 結果確認
- **pm_tasks シート** - ステータスが updated
- **task_execution_log シート** - 実行ログ・品質スコア記録
- **agent_outputs/tasks/** - 詳細な出力ファイル

---

## 📊 実行例
```bash
$ DISPLAY=:1 python3 run_pm_tasks_adaptive.py --max-tasks 2 --status pending

======================================================================
📝 タスク 1/2
======================================================================
  TaskID     : 1
  Agent      : design
  ExecutionType: gemini
  
🤖 Gemini タスクとして実行します
💬 タスク実行中...
✅ レスポンス取得成功

======================================================================
🎯 レビュー結果
======================================================================
⭐ 品質スコア: 9/10
✅ レビュー完了
📝 実行ログをシートに記録中...
✅ タスク 1 完了

======================================================================
📝 タスク 2/2
======================================================================
  TaskID     : 2
  Agent      : wp_dev
  ExecutionType: wordpress
  
🌐 WordPress タスクとして実行します
🔐 WordPress ログイン中...
✅ WordPress ログイン成功
📝 CPTエージェントで処理中...
✅ CPT作成完了

⭐ 品質スコア: 8/10
✅ タスク 2 完了

======================================================================
🎉 すべてのタスク処理完了
======================================================================
```

---

## ⚙️ 設定

### 環境変数（.env）
```bash
# Google Sheets
SPREADSHEET_ID=your_spreadsheet_id

# WordPress
WP_URL=https://your-site.com
WP_USER=your_username
WP_PASS=your_password
```

### Google Sheets構造

#### pm_tasks シート
```
task_id | Title | Description | Status | Agent | Dependencies | ExecutionType
```

#### task_execution_log シート
```
log_id | task_id | output | timestamp | Status | Quality_Score | Quality_description
```

---

## 🗺️ ロードマップ

### ✅ Phase 1（完了）
- Gemini/WordPressタスク実行
- レビュー機能
- ステータス管理
- execution_type対応

### 🔄 Phase 2（次）
- タスク依存関係システム
- 前タスク結果の自動取得
- コンテキスト付き実行
- 品質スコアフィルタリング

詳細: [PHASE2_DESIGN.md](./PHASE2_DESIGN.md)

### 🔮 Phase 3（将来）
- PM Agent自動化
- ゴール分析・タスク自動生成
- 進捗モニタリング
- 動的タスク追加

---

## 📝 開発履歴

### v1.3.0-add-operation (2025-10-24)
- ✅ Phase 1完了
- ✅ WordPress連携完全実装
- ✅ WordPressDevAgent統合
- ✅ execution_type自動判定
- ✅ レビュー機能統合
- ✅ 品質スコア記録

### v1.2.0-add-operation
- レビュー機能実装
- ステータス管理追加

---

## 🐛 トラブルシューティング

### WordPress ログイン失敗
```bash
# 1. .env のパスワード確認
cat .env | grep WP_PASS

# 2. 手動ログインテスト
ブラウザで https://your-site.com/wp-login.php を開く

# 3. クッキーをクリア
rm wordpress_cookies.json
```

### execution_type が設定されていない
```bash
# 自動判定ツールを実行
python3 tools/execution_type_manager.py
```

---

## 📞 サポート

- **設計書**: [PHASE2_DESIGN.md](./PHASE2_DESIGN.md)
- **バージョン**: [VERSION](./VERSION)

---

## 📄 ライセンス

MIT License

---

**🎉 Phase 1 完了記念 - v1.3.0-add-operation**

---

## 🎉 v1.4.0 Phase 2実装完了（2025-10-25）

### ✨ 新機能：タスク依存関係管理

#### 実装内容
- **柔軟な依存関係チェック**：依存タスクに問題があっても実行継続
- **前タスク結果の自動取得**：task_execution_logから品質スコア≧7の結果を取得
- **コンテキスト付きプロンプト生成**：前タスクの成果物を含めてGeminiに依頼
- **GitHubファイル統合**：長文の成果物はGitHubから完全版を取得

#### 解決した問題
- ✅ Google Sheets認証エラー（CRITICAL-2）
  - SERVICE_ACCOUNT_FILEのパス修正
  - Credentials.from_service_account_fileの引数修正
  
#### 新規追加ファイル
- `tools/task_dependency_manager.py`：依存関係管理の中核

#### 修正ファイル
- `tools/sheets_manager.py`：Google Sheets認証修正
- `run_pm_tasks_adaptive.py`：Phase 2統合
- `.env`：SERVICE_ACCOUNT_FILEパス修正

#### 使用方法
```bash
# VNC環境変数設定
export DISPLAY=:1

# Phase 2統合版を実行
python3 run_pm_tasks_adaptive.py --max-tasks 1 --status pending
```

#### Phase 2の動作例
```
TaskID=7 (Dependencies="4,6")
  ↓
1. 依存タスク4,6の完了チェック
2. task_execution_logから結果取得（品質≧7）
3. コンテキスト付きプロンプト生成
4. Geminiに実行依頼
5. レビュー＆品質スコア記録
```

#### 次のフェーズ（Phase 3）
- PM Agentによるタスク自動分解
- 進捗モニタリング
- 動的タスク生成


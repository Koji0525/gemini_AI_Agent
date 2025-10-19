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


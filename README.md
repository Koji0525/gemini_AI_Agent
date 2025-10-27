# 🤖 Gemini AI Agent System

**バージョン: v1.4.1-phase2-complete**

完全自動化されたAIエージェントシステム with Git統合ワークフロー

---

## 📋 プロジェクト概要

このプロジェクトは、Gemini AIを活用した複数のエージェントシステムを統合し、
自動化されたタスク管理、進捗監視、品質チェック、Git操作を提供します。

---

## 🚀 主要機能

### 1. PM Agent（プロジェクト管理エージェント）
- **自動進捗監視**: progress_dashboardから低進捗ゴールを検出
- **AI駆動タスク分解**: Gemini APIでタスクを自動生成
- **自動登録**: Google Sheetsへの一括登録
- **完全自動化**: activeなゴールを自動処理

**実行方法:**
```bash
DISPLAY=:1 python3 agents/pm_agent/automation.py
```

### 2. Git自動化エージェント
- **完全自動化ワークフロー**: STEP 1-9を一括実行
- **セキュリティチェック**: 認証ファイル自動検出
- **品質保証**: 重複メソッド・構文エラー検出
- **対話式テスト**: 開発プログラムのテスト実行

**実行方法:**
```bash
python3 agents/git_agent/auto_commit_push.py 'コミットメッセージ'
```

**エイリアス設定（推奨）:**
```bash
echo "alias gauto='python3 agents/git_agent/auto_commit_push.py'" >> ~/.bashrc
source ~/.bashrc
gauto '✨ 新機能追加'
```

---

## �� ディレクトリ構造
```
gemini_AI_Agent/
├── agents/                     # エージェントシステム
│   ├── pm_agent/              # PM Agent
│   │   ├── automation.py      # メイン自動化スクリプト
│   │   ├── progress_monitor.py
│   │   ├── task_breakdown_gemini.py
│   │   ├── task_registration.py
│   │   └── task_exporter.py
│   └── git_agent/             # Git自動化エージェント
│       ├── auto_commit_push.py     # ワンコマンド実行
│       ├── commit_agent.py
│       ├── push_agent.py
│       ├── branch_agent.py
│       └── run_git_workflow.py
├── configs/                    # 設定ファイル
│   └── git_workflows/
│       ├── auto_workflow_config.yaml
│       └── commit_config.yaml
├── scripts/                    # 昇格スクリプト
│   └── promote_to_production_v2.sh
├── _WIP/                      # 一時的なテストコード専用
├── _BACKUP/                   # 自動バックアップ
└── _ARCHIVE/                  # アーカイブ

開発用ディレクトリ（機能別バージョン管理）:
各ディレクトリ内で命名規則に従って開発
例: agents/pm_agent/
  ├── automation.py              # 安定版
  ├── automation_v01-gemini.py   # 新機能開発中
  └── automation_v02-fix_bug.py  # バグ修正中
```
### 初回セットアップ方法

# 基本インストール
pip install -r requirements.txt

# Playwrightブラウザのインストール
python -m playwright install chromium

# 開発モード（開発ツールも含む）
pip install -r requirements.txt
pre-commit install

# Playwrightシステム依存関係
sudo apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libxfixes3 \
    libxss1 \
    libgbm1 \
    libasound2

---

## 🎯 開発フロー v2.0（改定版）

### 基本原則
1. **_WIPは一時的なテストコードのみ**
2. **安定的な環境はブランチごとに担保**
3. **適切なディレクトリで開発（移動をほぼしない）**
4. **不安定になったら前のブランチに戻る**

### ファイル配置ルール

#### 基本ルール
- 既存のフォルダ内に同じディレクトリで作成
- 2つ以上の機能が実装される場合は階層を作成
```
agents/pm_agent/
├── core/                      # コア機能
│   ├── monitor/              # 進捗監視機能
│   │   ├── progress_monitor.py
│   │   └── progress_monitor_v01-realtime.py
│   └── breakdown/            # タスク分解機能
│       ├── task_breakdown_gemini.py
│       └── task_breakdown_gemini_v01-enhanced.py
└── automation.py              # メインスクリプト
```

### 命名規則

| 目的 | 命名規則 | 例 |
|------|---------|-----|
| **新規機能のテスト** | `[ベース名]_vXX-[機能名].py` | `review_agent_v01-auto_select.py` |
| **デバッグ・修正** | `[ベース名]_vXX-fix_[内容].py` | `review_agent_v02-fix_init_bug.py` |

**重要な原則:**
> 同じディレクトリ内では常に最も数字が大きいファイルが「作業中の最新版」

#### 具体例

**review_agent.pyに対して新機能を作る場合:**
```
agents/review/
├── review_agent.py                    # 安定版
├── review_agent_v01-auto_select.py    # 新機能開発中
├── review_agent_v02-auto_select.py    # 機能改善
└── review_agent_v03-fix_timeout.py    # バグ修正
```

**最新版を安定版に昇格:**
```bash
# v03が完成したら
cp review_agent_v03-fix_timeout.py review_agent.py
gauto "✨ review_agent: タイムアウト修正完了"
```

---

## 🔄 ブランチ運用

### ブランチ命名規則
```
v{major}.{minor}.{patch}-{feature}
```

例:
- `v1.4.0-phase2-complete` (安定版)
- `v1.4.1-pm_agent_enhance` (機能開発)
- `v1.5.0-major_refactor` (大規模変更)

### ブランチ作成＋切り替え
```bash
# 自動バージョンアップ
python3 agents/git_agent/branch_agent.py auto patch pm_agent_enhance

# 手動作成
python3 agents/git_agent/branch_agent.py new v1.4.1-custom_feature
```

### 不安定時の対処
```bash
# 前のブランチに戻る
git checkout v1.4.0-phase2-complete

# または特定のブランチに
git checkout v1.3.0-stable
```

---

## 📝 Git統合ワークフロー

### ワンコマンド実行
```bash
gauto 'コミットメッセージ'
```

### 実行されるステップ

| STEP | 項目 | 説明 |
|------|------|------|
| 1 | CLEANUP | 一時ファイルを_WIPに移動 |
| 2 | LIST | コミット対象を列挙 |
| 3 | SECURITY CHECK | 認証ファイル検出 |
| 3 | DUPLICATE CHECK | 重複メソッド検出 |
| 3 | COMPILE CHECK | 構文チェック |
| 5 | TEST | 開発プログラムのテスト（対話式） |
| 6 | FINAL CLEANUP | 不要ファイル削除 |
| 8 | UPDATE .gitignore | 必要なパターンを追加 |
| 9 | UPDATE README | README更新（対話式） |
| 10 | COMMIT & PUSH | コミット＋プッシュ |

### STEP 5: テスト（対話式）
```
📝 開発したプログラムのテストコマンドを入力してください
   例: DISPLAY=:1 python3 agents/pm_agent/automation.py
   スキップする場合は Enter

テストコマンド: _
```

### STEP 9: README更新（対話式）
```
📝 READMEに追加する内容を入力してください
   スキップする場合は Enter

README更新内容: _
```

---

## 🔒 セキュリティ

### 自動検出される認証ファイル
- `service_account.json`
- `**/*_key.json`
- `**/*.pem`
- `**/credentials.json`
- `**/.env`

### Push Protection対応
GitHubのPush Protectionが発動した場合、自動的にガイドを表示

---

## 🛠️ セットアップ

### 必須ツール
```bash
pip install pyyaml flake8 black --break-system-packages
```

### 初期設定
```bash
# エイリアス設定
echo "alias gauto='python3 agents/git_agent/auto_commit_push.py'" >> ~/.bashrc
source ~/.bashrc

# .gitignore確認
cat .gitignore  # 認証ファイルが除外されているか確認
```

---

## 📊 プロジェクト統計

- **総ファイル数**: 274個
- **エージェント数**: 10個以上
- **自動化ワークフロー**: 完全対応
- **セキュリティチェック**: 自動化

---

## 🎯 今後の予定

- [ ] GitHub Actions統合
- [ ] 自動テストカバレッジ
- [ ] CI/CDパイプライン構築
- [ ] ドキュメント自動生成

---

## 📝 変更履歴

# ==

### v1.4.1-phase2-complete (2025-10-27)
- ✅ PM Agent完成: activeなゴール自動処理
- ✅ Git自動化エージェント追加
- ✅ セキュリティチェック強化
- ✅ 完全自動化ワークフロー実装
- ✅ 開発フロー v2.0導入

### v1.4.0-phase2-complete
- PM Agent基本機能実装
- Google Sheets連携

---

## 📧 サポート

問題が発生した場合:
1. GitHub Issuesで報告
2. 前のブランチに戻る
3. ドキュメント確認

---

**安定版ブランチ**: `v1.4.1-phase2-complete`
**最終更新**: 2025-10-27

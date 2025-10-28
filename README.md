# 🤖 Gemini AI Agent System v2.0
**完全自動化AIエージェントシステム - 自己進化型プロジェクト管理**

バージョン: v1.5.0-phase3-complete → v2.0.0-integrated (移行中)  
最終更新: 2025-10-27

---

## 🎯 システム概要

ゴールを入力するだけで、タスク分解から実行、エラー分析、改善提案まで
**完全自動化**された次世代プロジェクト管理システム。

### コア機能
```
ゴール入力
    ↓
自動タスク分解 (Gemini AI)
    ↓
依存関係解決 + 優先順位付け
    ↓
並列自動実行 (複数エージェント)
    ↓
リアルタイム監視 + ログ分析
    ↓
エラー検知 → 自動リトライ/ロールバック
    ↓
改善提案生成 (人間承認 → 次回反映)
```

---

## 📊 現在の到達段階

| Phase | 機能 | 状態 | 完成度 |
|-------|------|------|--------|
| **Phase 1** | 基本タスク管理 | ✅ 完了 | 100% |
| **Phase 2** | 半自動実行 | ✅ 完了 | 100% |
| **Phase 3** | 統合自動実行 | 🚧 開発中 | 60% |
| **Phase 4** | エラー分析 | 🚧 統合中 | 40% |
| **Phase 5** | フィードバックループ | 📋 設計中 | 20% |
| **Phase 6** | 自己修復 | 📋 計画中 | 5% |
| **Phase 7** | 動的エージェント生成 | 📋 計画中 | 0% |

---

## 🚀 クイックスタート

### 1. ゴール → タスク分解
```bash
# activeなゴールを自動処理
DISPLAY=:1 python3 agents/pm_agent/automation.py
```

### 2. タスク実行
```bash
# 最大5タスクを実行
DISPLAY=:1 python3 run_pm_tasks_adaptive.py --max-tasks 5
```

### 3. **新機能** 統合実行（開発中）
```bash
# ゴール4を完全自動実行
python3 agents/integrated_executor.py 4
```

---

## 🏗️ システムアーキテクチャ

### コアコンポーネント

#### 1. PM Agent（プロジェクト管理）
- **automation.py**: activeなゴールを自動処理
- **task_breakdown_gemini.py**: Gemini APIでタスク分解
- **task_registration.py**: Google Sheetsへ登録

#### 2. 実行エンジン
- **run_pm_tasks_adaptive.py**: タスク実行（現行）
- **integrated_executor.py**: 統合実行（新規開発中）

#### 3. 高度機能（既存・活性化中）
- **hybrid_orchestrator.py**: リトライ・並列実行制御
- **log_analyzer.py**: ログ分析・異常検知・根本原因分析
- **rollback_agent.py**: ロールバック管理
- **dependency_resolver.py**: 依存関係解決

#### 4. Git自動化
- **auto_commit_push.py**: セキュリティチェック付きコミット

---

## 📋 Google Sheetsスキーマ

### 既存シート
| シート名 | 用途 | 列数 |
|----------|------|------|
| `project_goal` | ゴール管理 | 8列 |
| `pm_tasks` | タスク一覧 | 13列 |
| `task_execution_log` | 実行ログ | 10列 |
| `progress_dashboard` | 進捗ダッシュボード | 12列 |

### 新規追加予定（Phase 4-5）
| シート名 | 用途 | 優先度 |
|----------|------|--------|
| `error_analysis` | エラー分析結果 | 🔴 高 |
| `feedback_queue` | 改善提案キュー | 🟡 中 |
| `agent_registry` | エージェント登録簿 | 🟢 低 |
| `system_health` | システム健全性 | 🟢 低 |

---

## 🗺️ 開発ロードマップ（6週間）

### Week 1-2: Phase 3完成（統合自動実行）
- [ ] task_execution_log構造修正（status列問題）
- [ ] integrated_executor.py実装
- [ ] 依存関係解決の統合
- [ ] 並列実行機能のテスト

### Week 3: Phase 4開始（エラー分析）
- [ ] log_analyzerの完全統合
- [ ] error_analysisシート作成
- [ ] エラー自動分類機能

### Week 4: Phase 5開始（フィードバックループ）
- [ ] feedback_queue実装
- [ ] 改善提案生成（Gemini API）
- [ ] 人間承認インターフェース

### Week 5-6: Phase 6開始（自己修復）
- [ ] 安全な自動修正パターンDB
- [ ] rollback_agentの完全統合
- [ ] リトライ戦略の高度化

---

## 🎯 使用例

### 例1: 新しいゴールを完全自動実行
```bash
# 1. project_goalシートに新しいゴールを追加
# 2. 統合実行
python3 agents/integrated_executor.py 5

# 出力例:
# 🎯 目標 5 の完全自動実行を開始
# 【Phase 1】過去の実行ログを分析...
#    ✅ 過去50件のログを分析
# 【Phase 2】タスク分解...
#    ✅ 8個のタスクを生成
# 【Phase 3】依存関係解決...
#    ✅ 3グループに分割
# 【Phase 4-6】タスク実行...
# --- グループ 1/3 ---
#    🔄 タスク 456: デザイン設計
#    🔄 タスク 457: 技術検証
# ...
# 📊 実行結果サマリー
# 実行タスク: 8件
# 成功: 7件
# 失敗: 1件
# 💡 改善提案: 2件
#   1. WordPressエージェントのタイムアウト設定を見直してください
#   2. 画像最適化タスクの依存関係を追加することを推奨します
```

### 例2: Git自動化
```bash
# エイリアス設定（初回のみ）
echo "alias gauto='python3 agents/git_agent/auto_commit_push.py'" >> ~/.bashrc
source ~/.bashrc

# 使用
gauto '✨ integrated_executor実装'
```

---

## 🔧 セットアップ

### 必須要件
- Python 3.10+
- Google Sheets API認証
- Playwright（ブラウザ自動化）

### インストール
```bash
# 1. 依存パッケージ
pip install -r requirements.txt --break-system-packages

# 2. Playwright
python -m playwright install chromium

# 3. システム依存関係（Debian/Ubuntu）
sudo apt-get install -y \
    libnss3 libatk-bridge2.0-0 libx11-xcb1 \
    libxcomposite1 libxrandr2 libgbm1 libasound2

# 4. 環境変数設定
cp .env.example .env
# .envを編集してAPI キーを設定
```

---

## 📂 ディレクトリ構造
```
gemini_AI_Agent/
├── agents/                      # エージェントシステム
│   ├── integrated_executor.py  # 統合実行エンジン（新規）
│   ├── hybrid_orchestrator.py  # リトライ・並列実行
│   ├── log_analyzer.py         # ログ分析
│   ├── rollback_agent.py       # ロールバック管理
│   ├── pm_agent/               # PM Agent
│   │   ├── automation.py       # ゴール自動処理
│   │   └── task_breakdown_gemini.py
│   └── git_agent/              # Git自動化
│       └── auto_commit_push.py
├── tools/                       # ツール群
│   ├── sheets_manager.py       # Google Sheets操作
│   └── task_dependency_manager.py
├── configuration/               # 設定管理
│   └── config_loader.py
├── _WIP/                        # 一時的なテストコード
├── _BACKUP/                     # 自動バックアップ
└── requirements.txt
```

---

## 🐛 トラブルシューティング

### よくある問題

#### 1. task_execution_logのstatus列がおかしい
```bash
# 現在の問題: status列にファイルパスが入っている
# 修正予定: Week 1で対応
```

#### 2. 並列実行時のエラー
```bash
# hybrid_orchestratorが未統合
# 修正予定: Week 2で統合
```

#### 3. ログ分析が動かない
```bash
# log_analyzerが呼ばれていない
# 修正予定: Week 3で統合
```

---

## �� 統計情報

- **総ファイル数**: 280+
- **エージェント数**: 15個
- **Google Sheetsシート数**: 4個（+4個追加予定）
- **自動化カバレッジ**: 65% → 95%（目標）

---

## 🎓 開発ガイドライン

### 命名規則
```
[ベース名]_vXX-[機能名].py

例:
- integrated_executor_v01-parallel.py
- log_analyzer_v02-fix_memory.py
```

### ブランチ戦略
```
v{major}.{minor}.{patch}-{feature}

例:
- v2.0.0-integrated（次期メジャー）
- v1.4.2-hotfix_log（緊急修正）
```

---

## 📝 変更履歴

### v2.0.0-integrated (開発中)
- 🚀 統合実行エンジン実装開始
- ✨ 眠っていた高度機能の活性化
- 🔧 task_execution_log構造修正

### v1.5.0-phase3-complete (2025-10-27)
- ✅ PM Agent完成
- ✅ Git自動化エージェント
- ✅ セキュリティチェック強化

---

## 📧 サポート・コントリビュート

### 問題報告
- GitHub Issues

### ブランチ戻し
```bash
git checkout v1.5.0-phase3-complete
```

### ドキュメント
- このREADME
- 各エージェントのdocstring
- `運用ルール.md`

---

**安定版ブランチ**: `v1.5.0-phase3-complete`  
**開発ブランチ**: `v2.0.0-integrated`  
**最終更新**: 2025-10-27

---

## 🔍 WordPress設定確認システム

WordPress環境の設定を自動確認し、Quality Scoreを算出するシステムを実装しました。

### クイックスタート
```bash
# 設定確認の実行
python3 scripts/config_validation_system.py
```

### 主な機能
- ✅ WordPress接続テスト
- ✅ REST API確認
- ✅ Quality Score算出（合格ライン: 7/10）
- ✅ Google Sheetsへのログ記録
- ✅ Markdownレポート生成

### 詳細ドキュメント
詳しい使い方は [CONFIG_VALIDATION_SYSTEM.md](docs/CONFIG_VALIDATION_SYSTEM.md) を参照してください。

**現在のQuality Score**: 9/10 (合格)


# Gemini AI Agent プロジェクト

## 🎯 概要
WordPress連携と高度なレビューシステムを備えたAIエージェントプロジェクト。Google Sheetsでタスク管理し、Gemini AIと連携して自動実行します。

## 🚀 主な機能

### 🤖 コアシステム
- **タスク自動実行**: Google Sheetsからタスクを読み込み自動実行
- **品質評価**: 10点満点での自動品質評価と詳細なレビュー
- **WordPress連携**: 自動ログイン、プラグイン管理、記事作成

### 🔧 レビューシステム
- **コンテンツ品質レビュー**: 正確性・実用性・完全性の評価
- **技術的実現性レビュー**: 技術的正確性・実装可能性の評価  
- **WordPress実装レビュー**: WordPress適合性・セキュリティの評価
- **自動エージェント選択**: タスク内容に応じた最適なレビューアー選択

### 📊 連携機能
- **Google Sheets連携**: タスク管理と実行ログ記録
- **Gemini AI連携**: AIによるタスク実行と品質評価
- **WordPress自動化**: プラグインインストール・設定・確認

## 📁 プロジェクト構造

ファイルを整理して、必要なものだけをコミットし、READMEも更新しましょう。

```bash
# ==========================================
# 1. 現在のファイル状態を確認
# ==========================================

echo "📁 現在のファイル構造を確認..."
find . -name "*.py" -type f | grep -v __pycache__ | sort
echo ""
echo "📊 ファイル数: $(find . -name "*.py" -type f | grep -v __pycache__ | wc -l)"

# ==========================================
# 2. 主要ファイルの整理と不要ファイルの削除
# ==========================================

echo "🧹 不要な一時ファイルを整理..."
# バックアップファイルを削除
find . -name "*.backup*" -type f -delete
find . -name "*_backup*" -type f -delete
find . -name "*_fixed*" -type f -delete

# 重複している可能性のあるファイルを確認
echo "🔍 重複ファイルをチェック..."
ls -la run_*.py 2>/dev/null || echo "実行ファイルなし"

# ==========================================
# 3. 主要ファイルの整理
# ==========================================

echo "📋 主要ファイルを整理..."

# 必要なディレクトリ構造を確認
echo "📁 ディレクトリ構造:"
tree -I '__pycache__|*.pyc|*.backup*' -L 3

# ==========================================
# 4. README.mdの更新
# ==========================================

echo "📝 README.mdを更新..."
cat > README.md << 'README'
# Gemini AI Agent プロジェクト

## 🎯 概要
WordPress連携と高度なレビューシステムを備えたAIエージェントプロジェクト。Google Sheetsでタスク管理し、Gemini AIと連携して自動実行します。

## 🚀 主な機能

### 🤖 コアシステム
- **タスク自動実行**: Google Sheetsからタスクを読み込み自動実行
- **品質評価**: 10点満点での自動品質評価と詳細なレビュー
- **WordPress連携**: 自動ログイン、プラグイン管理、記事作成

### 🔧 レビューシステム
- **コンテンツ品質レビュー**: 正確性・実用性・完全性の評価
- **技術的実現性レビュー**: 技術的正確性・実装可能性の評価  
- **WordPress実装レビュー**: WordPress適合性・セキュリティの評価
- **自動エージェント選択**: タスク内容に応じた最適なレビューアー選択

### 📊 連携機能
- **Google Sheets連携**: タスク管理と実行ログ記録
- **Gemini AI連携**: AIによるタスク実行と品質評価
- **WordPress自動化**: プラグインインストール・設定・確認

## 📁 プロジェクト構造

```
gemini_AI_Agent/
├── configuration/           # 設定管理
│   ├── config_loader.py
│   ├── wp_config_loader_fixed.py
│   └── wp_config_loader.py
├── browser_control/         # ブラウザ操作
│   ├── browser_controller.py
│   └── wordpress_auth.py
├── tools/                   # ユーティリティ
│   ├── sheets_manager_final.py
│   ├── sheets_manager.py
│   └── sheets_manager_async.py
├── review_agents/           # レビューエージェント
│   ├── specialized_reviewers.py
│   └── review_orchestrator.py
├── wordpress/               # WordPress機能
│   ├── wp_plugin_manager.py
│   ├── wp_plugin_agent.py
│   └── wp_review_agent.py
├── run_advanced_review_system.py    # メイン実行
├── run_with_retry_failed.py         # 失敗タスク再実行
├── run_simple_wp_integration_fixed.py # シンプル版
└── run_quality_evaluation_fixed.py   # 品質評価版
```

## 🛠 セットアップ

### 1. 環境設定
```bash
# 必要なパッケージのインストール
pip install gspread google-auth playwright

# ブラウザのインストール
playwright install chromium
```

### 2. Google Sheets設定
1. Google Cloud Consoleでサービスアカウントを作成
2. `credentials.json` を配置
3. スプレッドシートをサービスアカウントと共有

### 3. WordPress設定
`setting` シートに以下を設定:
- `wp_url`: WordPressサイトURL
- `wp_user`: 管理者ユーザー名
- `wp_pass`: パスワード

## 🎯 実行方法

### 高度なレビューシステム（推奨）
```bash
DISPLAY=:1 python3 run_advanced_review_system.py --max-tasks 5
```

### 失敗タスクの再実行
```bash
DISPLAY=:1 python3 run_with_retry_failed.py --retry-failed
```

### 特定タスクの実行
```bash
DISPLAY=:1 python3 run_advanced_review_system.py --task-id 8
```

### シンプル版実行
```bash
DISPLAY=:1 python3 run_simple_wp_integration_fixed.py --max-tasks 3
```

## 📊 品質評価システム

### レビューエージェント
1. **📝 コンテンツ品質レビューアー**
   - 内容の正確性、実用性、完全性を評価
   - 具体例やコード例の有無を確認

2. **🔧 技術的実現性レビューアー** 
   - 技術的正確性、実装可能性、拡張性を評価
   - ベストプラクティスへの準拠を確認

3. **🏠 WordPress実装レビューアー**
   - WordPress標準への準拠を評価
   - セキュリティ、パフォーマンスを確認

### 評価基準
- **9-10点**: 優秀 - 追加価値がある完成度の高い成果物
- **7-8点**: 良好 - 要件を満たし実用的な内容
- **6点**: 平均 - 基本的な要件は満たしている
- **4-5点**: 要改善 - 改善の余地が大きい
- **1-3点**: 不合格 - 重大な問題がある

## 🔧 カスタマイズ

### 新しいレビューエージェントの追加
`review_agents/specialized_reviewers.py` に新しいクラスを追加:

```python
class NewReviewAgent:
    async def review_specialized(self, task_description: str, output: str) -> Dict:
        # レビュー実装
        return review_result
```

### タスクタイプの拡張
`review_agents/review_orchestrator.py` の `select_reviewers` メソッドを修正:

```python
def _detect_specialized_task(self, description: str, output: str) -> bool:
    # 新しいタスクタイプの検出ロジック
    pass
```

## 📈 ログと監視

### Google Sheetsログ
- **pm_tasks**: タスク管理シート
- **task_execution_log**: 実行ログシート
- **I列**: 品質スコア (quality_score)
- **J列**: 評価根拠 (quality_evaluation)

### 実行結果の確認
```python
# ログ確認スクリプト
python3 check_log_sheet_fixed.py
```

## 🐛 トラブルシューティング

### 一般的な問題
1. **ブラウザ接続エラー**: `DISPLAY=:1` を設定
2. **Sheets接続エラー**: サービスアカウントの権限を確認
3. **WordPressログインエラー**: 設定シートの認証情報を確認

### デバッグモード
```bash
# 詳細ログを有効化
DEBUG=1 DISPLAY=:1 python3 run_advanced_review_system.py --max-tasks 2
```

## 📄 ライセンス

このプロジェクトは独自ライセンスの下で提供されています。

## 🤝 貢献

バグ報告や機能要望はIssueで受け付けています。

---

*最終更新: $(date +%Y年%m月%d日)*

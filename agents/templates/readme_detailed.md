# GitHub開発効率化ツール

**タスクID**: {task_id}  
**説明**: {description}  
**生成日時**: {timestamp}

Claude, GPT-4, Geminiを統合したAI駆動の開発支援CLIツール

---

## 🎯 特徴

### コア機能
- 🤖 **AIコード生成**: タスク説明から実装コードを自動生成
- 📝 **自動コミットメッセージ**: git diffから最適なメッセージ生成
- 🔍 **コードレビュー支援**: 静的解析とチェック
- 📄 **PR説明文生成**: コミット履歴から詳細な説明を作成

### 対応コードタイプ
- `feature`: 新機能実装
- `fix`: バグ修正
- `docs`: ドキュメント
- `test`: テストコード
- `refactor`: リファクタリング

---

## 📦 インストール

### 必要要件
- Python 3.8+
- Git 2.0+
- pip

### インストール手順
```bash
# リポジトリをクローン
git clone https://github.com/your-org/github-dev-tools
cd github-dev-tools

# 依存パッケージをインストール
pip install -r requirements.txt

# CLIをインストール（開発モード）
pip install -e .

# または直接実行
python cli.py --help
```

---

## 🚀 使い方

### 1. コード生成

#### 基本的な使い方
```bash
# 新機能のコード生成
github-dev-tools generate --type feature -d "ユーザー認証機能" -o auth.py

# バグ修正コード
github-dev-tools generate --type fix -d "ログインエラー修正" -o fix_login.py

# テストコード
github-dev-tools generate --type test -d "認証テスト" -o test_auth.py
```

#### オプション
- `--type`: コードタイプ（feature, fix, docs, test, refactor）
- `--description, -d`: 機能の説明（必須）
- `--output, -o`: 出力先ファイルパス
- `--language, -l`: プログラミング言語（デフォルト: python）

### 2. コミット支援

#### 基本的な使い方
```bash
# 変更をステージング
git add .

# AI生成メッセージで自動コミット
github-dev-tools commit --auto

# コミット＋プッシュ
github-dev-tools commit --auto --push

# カスタムメッセージ
github-dev-tools commit -m "✨ feat: Add authentication" --auto
```

#### オプション
- `--auto`: 自動実行フラグ
- `--message, -m`: カスタムメッセージ
- `--push`: コミット後に自動プッシュ

### 3. PR説明文生成

#### 基本的な使い方
```bash
# 最新5コミットから生成
github-dev-tools pr

# 詳細テンプレート使用
github-dev-tools pr --template detailed

# 特定コミットを指定
github-dev-tools pr -c abc123 -c def456

# 出力先指定
github-dev-tools pr -o my_pr_description.md
```

#### オプション
- `--commits, -c`: コミットハッシュ（複数指定可）
- `--output, -o`: 出力先（デフォルト: pr_description.md）
- `--template`: テンプレート（simple/detailed）

### 4. コードレビュー

#### 基本的な使い方
```bash
# 基本レビュー
github-dev-tools review -f src/main.py

# 詳細レビュー
github-dev-tools review -f src/main.py --detailed

# JSON形式で出力
github-dev-tools review -f src/main.py --format json
```

#### チェック項目
- ファイルサイズ（500行超過チェック）
- TODO/FIXMEコメント
- 長い行（100文字超）
- コーディングスタイル

### 5. 設定管理

#### 設定の表示
```bash
github-dev-tools config show
```

#### 設定の変更
```bash
# デフォルトブランチ
github-dev-tools config set default_branch develop

# AIモデル
github-dev-tools config set ai_model claude-opus-4

# 自動コミット
github-dev-tools config set auto_commit true
```

---

## ⚙️ 設定ファイル

設定は `~/.github-dev-tools/config.json` に保存されます
```json
{
  "default_branch": "main",
  "ai_model": "claude-sonnet-4",
  "auto_commit": false,
  "code_style": "google"
}
```

### 設定項目

| 項目 | 説明 | デフォルト |
|------|------|-----------|
| `default_branch` | デフォルトブランチ | `main` |
| `ai_model` | 使用するAIモデル | `claude-sonnet-4` |
| `auto_commit` | 自動コミット有効化 | `false` |
| `code_style` | コーディングスタイル | `google` |

---

## 🧪 開発

### テスト実行
```bash
# 全テスト
pytest tests/

# カバレッジ付き
pytest --cov=. tests/

# 特定のテスト
pytest tests/test_cli.py
```

### コード品質
```bash
# Linter
flake8 .

# Formatter
black .

# 型チェック
mypy .

# 全チェック
make lint
```

---

## 📝 ライセンス

MIT License

---

## 🤝 貢献

プルリクエスト歓迎！

1. Fork
2. Feature branch作成
3. Commit
4. Push
5. Pull Request作成

---

## 📞 サポート

- Issue: https://github.com/your-org/github-dev-tools/issues
- Discussions: https://github.com/your-org/github-dev-tools/discussions

---

**生成日時**: {timestamp}

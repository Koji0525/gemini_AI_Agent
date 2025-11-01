# 🛡️ KeyError 'credentials_path' 問題の完全分析

## 📊 発生した問題

### エラー内容
```
KeyError: 'credentials_path'
```

### 発生箇所
`scripts/goal_input_agent_v01_initial.py` の初期化処理

---

## �� なぜなぜ分析（5Why）

### なぜ1: なぜエラーが発生したのか？
→ `config['credentials_path']` にアクセスしようとしたが、キーが存在しなかった

### なぜ2: なぜキーが存在しなかったのか？
→ `get_config()` の返り値の構造を誤解していた

### なぜ3: なぜ構造を誤解したのか？
→ 既存の成功パターン（active_goal_manager.py）を確認せずに実装した

### なぜ4: なぜ確認しなかったのか？
→ 運用ルール「既存コードを参照する」を徹底していなかった

### なぜ5: なぜ徹底できなかったのか？
→ 新規実装時のチェックリストが存在しなかった

---

## ✅ 正しいパターン

### active_goal_manager.pyの成功パターン
```python
# ❌ 誤ったパターン
config = get_config()
self.sheets = GoogleSheetsManager(
    credentials_path=config['credentials_path'],  # ← このキーは存在しない
    spreadsheet_id=config['spreadsheet_id']
)

# ✅ 正しいパターン
self.spreadsheet_id = os.getenv("SPREADSHEET_ID", "デフォルト値")
service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
self.sheets = GoogleSheetsManager(
    self.spreadsheet_id,
    service_account_file
)
```

---

## 🛡️ 再発防止策

### 1. 新規ファイル作成時のチェックリスト

**必ず以下を実行すること:**
```bash
# ステップ1: 類似機能のファイルを検索
find scripts/ -name "*.py" -exec grep -l "GoogleSheetsManager" {} \;

# ステップ2: インポートパターンを抽出
head -40 <見つかったファイル> | grep -A 5 "GoogleSheetsManager"

# ステップ3: パターンを完全コピー
# （推測や創造はしない）
```

### 2. インポートパターンガイドの更新

| クラス | 正しい初期化 | 誤ったパターン |
|--------|------------|--------------|
| `GoogleSheetsManager` | `GoogleSheetsManager(spreadsheet_id, service_account_file)` | `GoogleSheetsManager(credentials_path=..., spreadsheet_id=...)` |

### 3. 環境変数の統一

プロジェクト全体で以下を徹底：

- `GOOGLE_APPLICATION_CREDENTIALS`: サービスアカウントJSONファイルのパス
- `SPREADSHEET_ID`: スプレッドシートID
- これらは `.env` で管理し、`os.getenv()` で取得

### 4. 運用ルールの強化

**新規ファイル作成時の必須手順:**

1. **既存パターンの確認**（5分）
2. **パターンの完全コピー**（推測禁止）
3. **構文チェック**（`python3 -m py_compile`）
4. **インポートテスト**（独立実行）
5. **動作テスト**（最小限の機能確認）

---

## 📚 横展開

### 同様の問題が発生しうる箇所
```bash
# 全てのファイルで GoogleSheetsManager の使用パターンを確認
grep -r "GoogleSheetsManager(" scripts/ core_agents/ agents/ --include="*.py"
```

### 修正が必要なファイルの特定
```bash
# 誤ったパターンを使用しているファイルを検索
grep -r "credentials_path=" scripts/ core_agents/ agents/ --include="*.py"
```

---

## 🎯 今後の改善アクション

1. **ドキュメント更新**: インポートパターンガイドの作成 ✅
2. **自動チェック**: プレコミットフックでパターン違反を検出
3. **テンプレート化**: 新規エージェント作成時のボイラープレート
4. **ナレッジベース登録**: この問題を自己修復システムに登録

---

**作成日時**: $(date '+%Y年%m月%d日 %H:%M:%S')  
**目的**: 同じエラーの再発防止  
**適用**: 全ての新規ファイル作成時

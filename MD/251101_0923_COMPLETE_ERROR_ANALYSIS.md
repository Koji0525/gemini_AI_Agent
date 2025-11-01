# 🛡️ Goal Input Agent 開発における完全エラー分析

## 📊 発生した問題の時系列

### 問題1: KeyError 'credentials_path'
- **原因**: `get_config()` の返り値構造を誤解
- **解決**: 環境変数から直接取得する方式に変更

### 問題2: ValueError 'GOOGLE_APPLICATION_CREDENTIALS が未設定'
- **原因**: 使用する環境変数名が誤っていた
- **解決**: `GOOGLE_SERVICE_ACCOUNT_FILE` を使用

### 問題3: AttributeError 'append_row'
- **原因**: メソッド名が誤っていた（正: `append_rows`）
- **解決**: 複数形の `append_rows` を使用し、引数を `[goal_data]` とリストで囲む

### 問題4: AttributeError 'spreadsheet'
- **原因**: `GoogleSheetsManager` に `spreadsheet` 属性が存在しない
- **解決**: Google Sheets API v4 の `self.sheets.service` を直接使用

---

## 🔍 根本原因（なぜなぜ分析）

### なぜ問題が3回以上繰り返されたのか？

1. **既存コードの確認不足**
   - v02_fixed, v03_env_fixed という正解コードが既に存在していた
   - 最初からこれらを参照すれば即解決だった

2. **API仕様の理解不足**
   - `GoogleSheetsManager` が Google Sheets API v4 ベースであることを把握していなかった
   - gspread ライブラリの `spreadsheet` 属性を期待していた

3. **段階的な構造変化の追跡不足**
   - プロジェクトが進化する中で、`GoogleSheetsManager` の実装が変化
   - 古いパターンと新しいパターンが混在

---

## ✅ 正しい実装パターン（確定版）

### GoogleSheetsManager の正しい使い方
```python
# ✅ 初期化
from tools.sheets_manager import GoogleSheetsManager

spreadsheet_id = os.getenv("SPREADSHEET_ID", "デフォルト値")
sheets = GoogleSheetsManager(spreadsheet_id)
# service_account_file は環境変数 GOOGLE_SERVICE_ACCOUNT_FILE から自動取得

# ✅ データ追加
goal_data = ['値1', '値2', '値3']
sheets.append_rows('シート名', [goal_data])  # List[List[str]] 形式

# ✅ シート操作
spreadsheet = sheets.service.spreadsheets().get(
    spreadsheetId=sheets.spreadsheet_id
).execute()
sheet_names = [s['properties']['title'] for s in spreadsheet.get('sheets', [])]
```

---

## 🛡️ 再発防止策

### 1. チェックリスト化

**新規エージェント作成時の必須確認事項:**
```bash
# ステップ1: 類似機能を検索
find scripts/ -name "*類似キーワード*.py"

# ステップ2: 最新バージョンを特定
ls -lt scripts/*類似キーワード*.py | head -1

# ステップ3: インポートとメソッド呼び出しをコピー
head -50 <最新ファイル> | grep -A 5 "GoogleSheetsManager"

# ステップ4: パターンを完全コピー（推測禁止）
```

### 2. ドキュメント整備

プロジェクトルートに `IMPORT_PATTERNS.md` を作成：

| クラス | 初期化 | 主要メソッド | 参照ファイル |
|--------|--------|------------|------------|
| `GoogleSheetsManager` | `GoogleSheetsManager(spreadsheet_id)` | `append_rows(sheet, [data])` | `scripts/goal_input_agent_v02_fixed.py` |

### 3. 自動チェックの導入

プレコミットフックで非推奨パターンを検出：
```bash
# .git/hooks/pre-commit
grep -r "\.append_row(" scripts/ && echo "❌ append_row は非推奨。append_rows を使用" && exit 1
grep -r "\.spreadsheet\." scripts/ && echo "⚠️ spreadsheet 属性の使用を確認" && exit 1
```

---

## 📚 今後の横展開

### 同様の問題が発生しうる箇所

1. **BrowserController**: Playwright の API 変更
2. **TaskExecutor**: 非同期処理のパターン
3. **WordPress Orchestrator**: WordPress REST API の仕様

### 対策

各エージェントに「正しい使用例」を埋め込む：
```python
"""
正しい使用例:
    sheets = GoogleSheetsManager(spreadsheet_id)
    sheets.append_rows('pm_task_queue', [data])
    
誤った使用例:
    sheets.append_row('pm_task_queue', data)  # ❌ メソッド名が誤り
    sheets.spreadsheet.append()  # ❌ spreadsheet 属性は存在しない
"""
```

---

**作成日時**: $(date '+%Y年%m月%d日 %H:%M:%S')  
**目的**: 同類エラーの完全防止  
**適用**: 全ての新規開発時

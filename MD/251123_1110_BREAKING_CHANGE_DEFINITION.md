# 🔍 破壊的変更検知システム：定義と実例

**作成日時**: 2025-11-23 11:10 JST  
**目的**: 破壊的変更の定義を明確化し、検知される変更の種類を具体例で説明

---

## 📖 破壊的変更（Breaking Change）とは

**定義**: 既存のコードが依存している機能を変更・削除することで、そのコードが動作しなくなる変更

**重要性**: 
- 既存システムを壊さずに安全に開発を進めるため
- 変更の影響範囲を事前に把握し、適切なテスト計画を立てるため
- リリース前にリスクを可視化するため

---

## 🎯 検知する破壊的変更の種類

### 1. 関数シグネチャの変更 ⚠️

**ケース1: 引数の追加（デフォルト値なし）**
```python
# ❌ 変更前
def get_sheet_data(sheet_name):
    return sheets_manager.read(sheet_name)

# ⚠️ 変更後（破壊的）
def get_sheet_data(sheet_name, range_name):  # range_nameが必須引数に
    return sheets_manager.read(sheet_name, range_name)
```

**影響**: 
- この関数を呼び出している257ファイル全てでエラー
- `TypeError: get_sheet_data() missing 1 required positional argument: 'range_name'`

**検知結果**:
```json
{
  "type": "signature_change",
  "severity": "high",
  "affected_files": 257,
  "old_signature": "get_sheet_data(sheet_name)",
  "new_signature": "get_sheet_data(sheet_name, range_name)"
}
```

---

**ケース2: 引数の削除**
```python
# ❌ 変更前
def execute_task(task_id, retry_count, timeout):
    ...

# ⚠️ 変更後（破壊的）
def execute_task(task_id, timeout):  # retry_countを削除
    ...
```

**影響**:
- 呼び出し側で `execute_task(123, 3, 60)` のように3引数で呼んでいる場合エラー
- `TypeError: execute_task() takes 2 positional arguments but 3 were given`

---

**ケース3: 引数の順序変更**
```python
# ❌ 変更前
def create_report(title, date, author):
    ...

# ⚠️ 変更後（破壊的）
def create_report(date, title, author):  # 順序変更
    ...
```

**影響**:
- キーワード引数を使っていない場合、引数の値が入れ替わる
- バグが発生するが、エラーにならない場合があり危険

---

### 2. 関数・クラスの削除 🔴

**ケース4: 公開関数の削除**
```python
# ❌ 変更前
def validate_input(data):
    return data is not None

def process_data(data):
    if validate_input(data):
        ...

# ⚠️ 変更後（破壊的）
# validate_input()を削除

def process_data(data):
    if data is not None:  # 直接チェックに変更
        ...
```

**影響**:
- 他のファイルで `validate_input()` をインポートして使っている場合
- `ImportError: cannot import name 'validate_input'`

**検知結果**:
```json
{
  "type": "deletion",
  "severity": "critical",
  "function": "validate_input",
  "affected_files": 45
}
```

---

**ケース5: クラスの削除**
```python
# ❌ 変更前
class TaskExecutor:
    def execute(self, task):
        ...

# ⚠️ 変更後（破壊的）
# TaskExecutorクラスを削除し、関数に変更

def execute_task(task):
    ...
```

**影響**:
- `from task_executor import TaskExecutor` でエラー
- インスタンス化している箇所 `executor = TaskExecutor()` でエラー

---

### 3. 戻り値の型変更 ⚠️

**ケース6: 戻り値の構造変更**
```python
# ❌ 変更前
def get_user_data(user_id):
    return {
        'name': 'John',
        'age': 30,
        'email': 'john@example.com'
    }

# ⚠️ 変更後（破壊的）
def get_user_data(user_id):
    return User(name='John', age=30, email='john@example.com')  # オブジェクトに変更
```

**影響**:
- 呼び出し側で `user['name']` のように辞書としてアクセスしている場合エラー
- `TypeError: 'User' object is not subscriptable`

---

### 4. 例外の変更 ⚠️

**ケース7: 例外の種類変更**
```python
# ❌ 変更前
def read_file(path):
    if not path.exists():
        raise FileNotFoundError("File not found")

# ⚠️ 変更後（破壊的）
def read_file(path):
    if not path.exists():
        raise ValueError("Invalid path")  # 例外の種類変更
```

**影響**:
- 呼び出し側で `except FileNotFoundError:` でキャッチしている場合、キャッチできない
- 予期しない例外が上位に伝播

---

## 🔍 検知の重要度レベル

### 🔴 Critical（緊急対応必要）
- 公開APIの削除
- 10個以上のファイルに影響する変更

### 🟠 High（高優先度対応）
- 必須引数の追加
- 3-9個のファイルに影響する変更

### 🟡 Medium（中優先度対応）
- オプション引数の追加（デフォルト値なし）
- 1-2個のファイルに影響する変更

### 🟢 Low（監視のみ）
- 内部関数の変更
- 影響なしまたは極小

---

## 🧪 実際の検知例

### 例1: sheets_manager.pyの変更

**変更内容**:
```python
# 変更前
def get_sheet_data(sheet_name):
    ...

# 変更後
def get_sheet_data(sheet_name, range_name):
    ...
```

**検知結果**:
```
🔴 CRITICAL: シグネチャ変更
ファイル: tools/sheets_manager.py
関数: get_sheet_data
影響: 257ファイルに影響
推奨アクション:
  1. 後方互換性を保つため、range_nameにデフォルト値を設定
  2. または、全257ファイルを一括で更新
  3. 段階的移行期間を設ける
```

---

### 例2: review_agent.pyの変更

**変更内容**:
```python
# 変更前
def validate_task(task_data):
    ...

# 変更後
# validate_task()を削除
```

**検知結果**:
```
🔴 CRITICAL: 関数削除
ファイル: core_agents/review_agent.py
関数: validate_task
影響: 55ファイルに影響
推奨アクション:
  1. 関数を復元
  2. または、代替関数を提供し、全55ファイルを更新
  3. 非推奨警告を出した上で段階的に削除
```

---

## 💡 破壊を防ぐベストプラクティス

### 1. デフォルト引数を使う
```python
# ✅ 良い例（非破壊的）
def get_sheet_data(sheet_name, range_name=None):  # デフォルト値あり
    if range_name:
        return sheets_manager.read(sheet_name, range_name)
    return sheets_manager.read(sheet_name)
```

### 2. 非推奨警告を出す
```python
# ✅ 良い例（段階的削除）
import warnings

def old_function():
    warnings.warn(
        "old_function() is deprecated, use new_function() instead",
        DeprecationWarning
    )
    return new_function()
```

### 3. バージョン管理
```python
# ✅ 良い例（バージョン対応）
def process_data(data, version='v1'):
    if version == 'v1':
        return _process_v1(data)
    elif version == 'v2':
        return _process_v2(data)
```

---

## 📊 システムの動作フロー
```
1. コミット発生
   ↓
2. Git diff取得
   ↓
3. 変更されたPythonファイルを検出
   ↓
4. 変更前後のASTを比較
   ↓
5. シグネチャ変更・削除を検出
   ↓
6. 依存関係マップから影響範囲を計算
   ↓
7. 重要度を判定（Critical/High/Medium/Low）
   ↓
8. JSON形式で結果を出力
   ↓
9. ダッシュボードで可視化（Task 2-5で実装予定）
```

---

## 🎯 期待される効果

1. **事前リスク把握**: コミット前に影響範囲を確認
2. **安全なリファクタリング**: 影響を可視化してから実施
3. **レビュー効率化**: PRレビュー時に自動で影響範囲を提示
4. **テスト範囲特定**: 影響を受けるファイルのテストを優先実施
5. **ドキュメント生成**: 変更履歴として自動記録

---

**作成者**: AI Development Assistant  
**参照**: Phase 2 Task 2-3 実装完了

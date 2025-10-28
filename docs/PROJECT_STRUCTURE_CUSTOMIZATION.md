# プロジェクト構造可視化ツール - カスタマイズガイド

## �� カスタマイズ方法

`scripts/show_project_structure.py` の先頭にある設定セクションを編集するだけ！

---

## 📝 設定項目

### 1. 対象拡張子の変更
```python
# Pythonファイルのみ表示
TARGET_EXTENSIONS = ['.py']

# 複数の拡張子を指定
TARGET_EXTENSIONS = ['.py', '.js', '.html', '.css']

# すべてのファイルを表示
TARGET_EXTENSIONS = []
```

### 2. 除外ディレクトリの変更
```python
CUSTOM_EXCLUDE_DIRS = {
    '_ARCHIVE',      # 削除すると表示される
    '_BACKUP',       # 削除すると表示される
    '_WIP',          # 削除すると表示される
    '__pycache__',   
    '.git',          
    'node_modules',  
}
```

### 3. 表示深度の変更
```python
# 2階層まで表示
MAX_DEPTH = 2

# 5階層まで表示
MAX_DEPTH = 5
```

### 4. 表示オプション
```python
# ファイルサイズを非表示
SHOW_FILE_SIZE = False

# 行数を非表示
SHOW_LINE_COUNT = False
```

---

## 💡 よくある設定例

### 例1: すべてのPythonファイルを表示（_WIP含む）
```python
TARGET_EXTENSIONS = ['.py']
CUSTOM_EXCLUDE_DIRS = {
    '__pycache__',
    '.git',
    'node_modules',
}
MAX_DEPTH = 4
```

### 例2: Webファイルのみ表示
```python
TARGET_EXTENSIONS = ['.html', '.css', '.js', '.php']
CUSTOM_EXCLUDE_DIRS = {
    '_ARCHIVE',
    '_BACKUP',
    '__pycache__',
    '.git',
    'node_modules',
}
MAX_DEPTH = 3
```

### 例3: すべてのファイルを浅く表示
```python
TARGET_EXTENSIONS = []  # すべて
CUSTOM_EXCLUDE_DIRS = {
    '__pycache__',
    '.git',
}
MAX_DEPTH = 2  # 浅く
```

---

**作成日**: 2025-10-28

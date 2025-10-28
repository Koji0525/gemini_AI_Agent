# プロジェクト構造可視化ツール

## 📋 概要

プロジェクトのフォルダ構造とファイルを視覚的に表示するツール。

**作成日**: 2025-10-28  
**バージョン**: v1.0

---

## 🚀 使い方

### 方法1: Pythonスクリプト直接実行
```bash
python3 scripts/show_project_structure.py
```

### 方法2: シェルスクリプト実行
```bash
./scripts/show_structure.sh
```

### 方法3: どこからでも実行（エイリアス設定）
```bash
# ~/.bashrcまたは~/.zshrcに追加
alias show-structure='python3 /workspaces/gemini_AI_Agent/scripts/show_project_structure.py'

# 設定を反映
source ~/.bashrc  # または source ~/.zshrc

# 実行
show-structure
```

---

## 📊 出力内容

### 1. ツリー構造
```
📁 agents/
├── 🤖 wordpress/
│   ├── 📁 specialized/
│   │   ├── 🐍 wp_cpt_agent.py (15.2KB, 380行)
│   │   ├── 🐍 wp_taxonomy_agent.py (18.5KB, 450行)
│   │   └── 🐍 wp_agent_logger.py (8.1KB, 210行)
│   └── 🐍 wp_orchestrator.py (15KB, 350行)
```

### 2. 統計情報
```
📊 プロジェクト統計
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 ディレクトリ数: 45
📄 ファイル数: 235
🐍 Pythonファイル数: 156
📝 総行数: 45,823
📈 平均行数/ファイル: 293.7
```

### 3. 重要なディレクトリの説明
```
📚 重要なディレクトリの説明
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 agents               → エージェント（WordPress、コンテンツ生成など）
🔨 tools                → ツール（SheetsManager、BrowserControllerなど）
⚙️ configuration       → 設定ファイル（ConfigLoader、.envなど）
�� scripts             → 実行可能スクリプト
📚 docs                → ドキュメント
```

---

## 🎨 機能

### アイコン表示
- �� 一般フォルダ
- 🤖 agentsフォルダ
- 🔨 toolsフォルダ
- 🐍 Pythonファイル
- 📝 Markdownファイル
- 🐘 PHPファイル
- ⚙️ 設定ファイル

### ファイル情報
- ファイルサイズ（KB/MB）
- Pythonファイルの行数
- 平均行数の計算

### 除外機能
- `__pycache__`
- `.git`
- `node_modules`
- その他キャッシュファイル

---

## ⚙️ カスタマイズ

### 表示深度の変更

スクリプト内の`max_depth`を変更:
```python
visualizer = ProjectStructureVisualizer(project_root, max_depth=5)  # デフォルト: 3
```

### アイコンの追加

`FILE_ICONS`または`FOLDER_ICONS`辞書に追加:
```python
FILE_ICONS = {
    # ...
    '.tsx': '⚛️',  # React TypeScript
    '.vue': '💚',  # Vue.js
}
```

---

## 🔄 更新履歴

- **v1.0** (2025-10-28): 初回リリース
  - ツリー構造表示
  - 統計情報
  - アイコン表示

---

**作成日**: 2025-10-28  
**最終更新**: 2025-10-28

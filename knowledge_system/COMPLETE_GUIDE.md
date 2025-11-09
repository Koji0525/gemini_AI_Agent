# 📚 SQLiteナレッジシステム 完全ガイド

## 🗂️ システム構造（完全版）
```
knowledge_system/
│
├── 📁 database/                    ← ★ここにデータが溜まる★
│   ├── knowledge.db               ← SQLiteデータベース（全ナレッジ）
│   ├── faiss_index/               ← ベクトル検索インデックス
│   │   ├── knowledge.index        ← FAISSインデックス本体
│   │   └── index_mapping.json     ← ID→ベクトルマッピング
│   └── backups/                   ← 自動バックアップ
│       └── backup_YYYYMMDD_HHMMSS/
│
├── 📁 core_agents/                 ← コアロジック（触らない）
│   ├── sqlite_manager.py          ← SQLite操作
│   ├── vector_search_agent.py     ← ベクトル検索
│   ├── knowledge_manager_v2.py    ← 統合マネージャー（v2.0）
│   └── advanced_features.py       ← キャッシュ/品質評価/バックアップ
│
├── 📁 scripts/                     ← 実行スクリプト（これを使う）
│   ├── auto_extract_knowledge.py  ← ★MDから自動抽出★
│   ├── test_search.py             ← ★検索テスト★
│   ├── phase3_operations.py       ← 運用操作
│   └── final_verification.py      ← システム確認
│
├── �� configuration/
│   └── knowledge_config.yaml      ← 設定ファイル
│
├── README.md                       ← システム説明
├── OPERATION_GUIDE.md             ← 運用ガイド
└── COMPLETE_GUIDE.md              ← このファイル
```

---

## 🎯 データの保存場所

### Q: ナレッジはどこに保存される？

**A: 2箇所に保存されます**

1. **SQLiteデータベース** (メインストレージ)
```
   knowledge_system/database/knowledge.db
```
   - すべてのナレッジが構造化されて保存
   - シナリオ、解決策、信頼度、成功率など
   - サイズ: 現在 44KB (27件)

2. **FAISSベクトルインデックス** (検索用)
```
   knowledge_system/database/faiss_index/
   ├── knowledge.index        ← ベクトルデータ
   └── index_mapping.json     ← ID対応表
```
   - 高速検索のためのインデックス
   - SQLiteのIDと紐付け

### データの流れ
```
MDファイル
  ↓ (自動抽出)
SQLite DB ← ここにテキストデータ保存
  ↓ (ベクトル化)
FAISSインデックス ← ここに検索用データ保存
  ↓
検索時に両方使用（ハイブリッド検索）
```

---

## 📝 ナレッジの登録方法（3つの方法）

### 方法1: 自動抽出（推奨・最速）

**MDファイルから自動で抽出**
```bash
# STEP 1: MDファイルをMD/フォルダに配置（すでにある）
# STEP 2: 自動抽出を実行
python3 knowledge_system/scripts/auto_extract_knowledge.py
```

**何が起きるか？**
- MD/フォルダ内の最初の10個のMDファイルをスキャン
- 以下のパターンを自動検出：
  - 「問題: 〜 解決: 〜」
  - 「✅ 〜」（成功パターン）
  - 「学び: 〜」
- 自動でSQLite + FAISSに登録

**登録される例**
```
元のMDファイル:
  ✅ スプレッドシート更新エラーを修正

↓ 自動で以下に変換

ナレッジ:
  scenario: "スプレッドシート更新エラーを修正"
  solution: "実行成功"
  confidence: 0.6
  category: "成功パターン"
```

---

### 方法2: Pythonで直接登録

**コードから登録する場合**
```python
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 手動登録スクリプト例
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import sys
from pathlib import Path
import yaml

project_root = Path('/workspaces/gemini_AI_Agent')
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager_v2 import KnowledgeManagerV2

# 設定読み込み
config_path = project_root / 'knowledge_system/configuration/knowledge_config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# ナレッジマネージャー初期化
db_path = project_root / config['database']['path']
index_path = project_root / config['vector_search']['index_path']
km = KnowledgeManagerV2(str(db_path), str(index_path))

# ナレッジ登録
knowledge = {
    'scenario': 'エラーが発生した時の対処法',
    'cause': 'モジュールが見つからない',
    'solution': 'pip install --break-system-packages で再インストール',
    'success_rate': 0.95,
    'confidence': 0.9,
    'category': 'エラー対処',
    'task_type': 'troubleshooting',
    'learnings': ['依存関係の事前確認が重要'],
    'prevention': ['requirements.txtの更新']
}

knowledge_id = km.register_knowledge(knowledge)
print(f"✅ 登録完了: {knowledge_id}")

# ベクトルインデックス保存（重要！）
km.save_vector_index()
```

**保存して実行**
```bash
# 上記をファイルに保存
cat > /tmp/register_knowledge.py << 'EOF'
（上記のコード）

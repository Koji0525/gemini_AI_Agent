# �� SQLite + FAISSナレッジ管理システム

## 📊 システム概要

**ゼロコスト**で高性能なナレッジ検索を実現する完全ローカルシステム

### 主な特徴
- ✅ **SQLite**: 軽量で堅牢なデータベース
- ✅ **FAISS**: 高速ベクトル検索（0.024秒 < 目標0.2秒）
- ✅ **日本語対応**: multilingual埋め込みモデル
- ✅ **自動品質評価**: 0-10スコアリング
- ✅ **自動バックアップ**: 定期的なデータ保護
- ✅ **キャッシュ最適化**: 検索パフォーマンス向上

## 🎯 性能指標

| 指標 | 目標 | 達成値 | 状態 |
|------|------|--------|------|
| 検索時間 | 200ms | 24ms | ✅ 8.3倍高速 |
| ナレッジ数 | 100件 | 27件 | 🔄 拡充中 |
| 信頼度 | 0.7 | 0.61 | 🔄 改善中 |
| キャッシュヒット率 | 30% | 25% | 🔄 最適化中 |

## 🚀 クイックスタート

### 1. 基本的な使い方
```python
from knowledge_system.core_agents.knowledge_manager_v2 import KnowledgeManagerV2

# 初期化
km = KnowledgeManagerV2(
    db_path='knowledge_system/database/knowledge.db',
    index_path='knowledge_system/database/faiss_index/knowledge.index'
)

# 検索
results = km.hybrid_search("エラー対処方法", top_k=5)

for r in results:
    print(f"{r['scenario'][:50]}... (信頼度: {r['confidence']})")
```

### 2. ナレッジ登録
```python
knowledge = {
    'scenario': '問題の説明',
    'cause': '原因',
    'solution': '解決策',
    'success_rate': 0.9,
    'confidence': 0.8,
    'category': 'カテゴリ'
}

km.register_knowledge(knowledge)
```

### 3. 自動抽出（MDファイルから）
```bash
python3 knowledge_system/scripts/auto_extract_knowledge.py
```

## 📁 ディレクトリ構造
```
knowledge_system/
├── core_agents/           # コアロジック
│   ├── sqlite_manager.py          # SQLite管理
│   ├── vector_search_agent.py     # FAISS検索
│   ├── knowledge_manager_v2.py    # 統合マネージャー
│   └── advanced_features.py       # 高度機能
├── scripts/               # 実行スクリプト
│   ├── auto_extract_knowledge.py  # 自動抽出
│   ├── test_search.py             # 検索テスト
│   └── phase3_operations.py       # Phase 3運用
├── database/              # データストア
│   ├── knowledge.db               # SQLiteDB
│   ├── faiss_index/               # ベクトルインデックス
│   └── backups/                   # 自動バックアップ
└── configuration/         # 設定
    └── knowledge_config.yaml
```

## 🔧 統合方法

### IntegratedOrchestratorとの統合
```python
# v30で自動統合済み
from scripts.integrated_orchestrator_v30_knowledge import IntegratedOrchestrator

orchestrator = IntegratedOrchestrator()
# ナレッジマネージャーが自動で利用可能
```

### TaskExecutorとの統合
```python
from task_executor.task_executor import TaskExecutor
from knowledge_system.core_agents.knowledge_manager_v2 import KnowledgeManagerV2

km = KnowledgeManagerV2(...)
executor = TaskExecutor(km)

# タスク実行時に自動でナレッジ検索
result = await executor.execute_task(task)
```

## 📊 運用

### 定期バックアップ
```python
km.create_backup()  # 自動バックアップ作成
```

### パフォーマンスモニタリング
```python
stats = km.get_stats()
print(stats['performance'])
```

## 🎯 Phase別達成状況

| Phase | 内容 | 状態 |
|-------|------|------|
| Phase 0 | 環境構築 | ✅ 完了 |
| Phase 1 | コア実装 | ✅ 完了 |
| Phase 2 | 統合 | ✅ 完了 |
| Phase 3 | 最適化 | ✅ 完了 |
| Phase 4 | 本番導入 | ✅ 完了 |

## 📌 次のステップ

1. ナレッジ拡充（100件目標）
2. 信頼度向上（0.7目標）
3. 自動学習パイプライン強化

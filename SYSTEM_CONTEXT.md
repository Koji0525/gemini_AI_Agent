# 📚 システムコンテキスト情報

## 開発環境情報
```
プロジェクト名: gemini_AI_Agent
開発環境: GitHub Codespaces
プロジェクトルート: /workspaces/gemini_AI_Agent
Python バージョン: 3.10+
主要ライブラリ:
  - google-api-python-client (Sheets API)
  - sentence-transformers (ベクトル化)
  - faiss-cpu (ベクトル検索)
  - pytest (テスト)
```

## 現在のシステム状態
```
総合評価: 78.2/100点
ファイル数: 47件
コード行数: 12,847行
コンポーネント数: 18個
ナレッジ数: 511件
テスト成功率: 84.3%
```

## 主要な実装ファイル一覧
```
データアクセス層:
  - tools/sheets_manager.py (645行)
  - tools/safe_sheets_wrapper.py (312行)
  - tools/base_data_accessor.py (288行)

エージェント層:
  - core_agents/pm_agent_v3_fixed.py (423行)
  - agents/complete_engine_ultimate.py (387行)
  - core_agents/review_agent.py (234行)

ナレッジ管理:
  - knowledge_system/core_agents/knowledge_manager.py (456行)
  - knowledge_system/database/sqlite_manager.py (378行)

観測可能性:
  - agents/observability/dashboard.py (198行)
```

## Git操作のベストプラクティス
```bash
# ブランチ作成
git checkout -b feature/self-healing

# コミット（小さく頻繁に）
git add <files>
git commit -m "feat: Add SelfHealingAgent basic structure"

# プッシュ
git push origin feature/self-healing

# Codespaces での確認
python3 -m pytest tests/
python3 agents/complete_engine_ultimate.py
```

## よく使うコマンド
```bash
# システム起動
python3 agents/complete_engine_ultimate.py --count 1

# ダッシュボード表示
python3 agents/observability/dashboard.py

# テスト実行
python3 -m pytest tests/ -v

# ナレッジ確認
python3 -c "from knowledge_system.core_agents.knowledge_manager import KnowledgeManager; km = KnowledgeManager(); print(km.get_statistics())"
```

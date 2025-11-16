# 自動GitHub連携システム

## 概要
タスク完了後に自動的にGitコミット・プッシュを実行するシステム

## 機能
- ✅ タスク実行結果の自動コミット
- ✅ コミット前の安全性チェック
- ✅ 機密ファイルの保護
- ✅ 詳細なコミットメッセージ自動生成
- ✅ Dry-runモード対応

## 使用方法

### 基本的な使い方
```python
from agents.task_execution.executor_with_github import TaskExecutorWithGitHub

# 自動コミット有効
executor = TaskExecutorWithGitHub(auto_commit=True)
result = executor.execute_task_with_details(task)

# 自動コミット無効（従来通り）
executor = TaskExecutorWithGitHub(auto_commit=False)
```

### CLI使用
```bash
# Dry-runテスト
python agents/github_integration/auto_committer.py TEST_001 "テスト" --dry-run

# 実際にコミット
python agents/github_integration/auto_committer.py TASK_123 "UI改善"
```

## 安全機能
- 機密ファイルの自動検出・除外
- ファイルサイズチェック（10MB制限）
- 保護ファイルの変更防止
- Dry-runモードでの事前確認

## 統合例
既存のrun_task_with_details_v2.pyに統合:
```python
# Before
from agents.task_execution.enhanced_executor_v2 import EnhancedTaskExecutorV2
executor = EnhancedTaskExecutorV2()

# After
from agents.task_execution.executor_with_github import TaskExecutorWithGitHub
executor = TaskExecutorWithGitHub(auto_commit=True)  # 自動コミット有効
```

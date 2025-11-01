#!/bin/bash

echo "=========================================="
echo "📊 Google Sheets結果書き戻し準備"
echo "=========================================="

cat > docs/next_tasks/sheets_writeback_plan.md << 'PLAN'
# Google Sheets 結果書き戻し機能の実装計画

## 🎯 目標
TaskExecutorが実行した結果をGoogle Sheetsに自動で書き戻す

## 📋 実装内容

### 1. SheetsManager に書き戻しメソッド追加
```python
def update_task_status(
    self, 
    task_id: str, 
    status: str, 
    result: Dict = None,
    error: str = None
) -> bool:
    """
    タスクの実行結果をSheetsに書き戻す
    
    Args:
        task_id: タスクID
        status: 'completed' | 'failed' | 'in_progress'
        result: 実行結果（オプション）
        error: エラーメッセージ（オプション）
    """
```

### 2. TaskExecutor との統合
- execute_task 完了時に自動的に書き戻し
- エラー時もステータス更新

### 3. テスト
- 単体テスト作成
- 統合テスト実行

## 📁 対象ファイル
- `tools/sheets_manager.py`
- `scripts/task_executor.py`

PLAN

mkdir -p docs/next_tasks

echo "✅ 次のタスク計画作成完了"
echo "   docs/next_tasks/sheets_writeback_plan.md"


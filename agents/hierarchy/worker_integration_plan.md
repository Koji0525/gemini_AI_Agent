# Worker統合計画

## 目的
既存TaskExecutor（Worker相当）を階層型アーキテクチャに統合

## 現状分析
- 既存: TaskExecutor単独実行
- 目標: TeamLeaderからのメッセージで起動

## 統合アプローチ

### Option A: Wrapper方式（推奨）
```python
class HierarchicalWorker:
    """既存TaskExecutorをラップ"""
    def __init__(self, worker_id, task_executor):
        self.worker_id = worker_id
        self.executor = task_executor  # 既存を保護
        self.messenger = HierarchicalMessenger()
    
    def run(self):
        """メッセージ駆動でタスク実行"""
        while True:
            messages = self.messenger.receive(self.worker_id)
            for msg in messages:
                if msg.type == MessageType.TASK_ASSIGNMENT:
                    result = self.executor.execute(msg.content['task_details'])
                    self.report_progress(result)
```

### Option B: 継承方式（既存修正が必要）
❌ 既存コード変更が必要なため非推奨

## 実装ステップ
1. HierarchicalWorkerクラス作成（Wrapper）
2. メッセージ受信ループ
3. TaskExecutorへの委譲
4. 進捗報告の自動化
5. テスト

## 成功基準
- 既存TaskExecutor変更なし
- メッセージ駆動でタスク実行
- 進捗自動報告

"""
task_ID連番形式のナレッジ登録
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager


def register_knowledge():
    """task_ID連番形式をナレッジ登録"""

    print("=" * 60)
    print("task_ID連番形式 ナレッジ登録")
    print("=" * 60)
    print()

    km = KnowledgeManager()

    km.add_knowledge(
        title="task_ID連番形式_既存最大値+1採番",
        content="""
【要件】
task_idを数字連番（1, 2, 3, ...）にする。

【実装方法】
1. pm_tasksシートのA列（task_id）から既存の最大値を取得
2. 最大値+1から採番開始
3. 複数エピック処理時は連続して採番

【コード例】
```python
def _get_next_task_id(self) -> int:
    tasks_data = self.sheets.read_range('pm_tasks!A:A')
    
    if not tasks_data or len(tasks_data) <= 1:
        return 1
    
    max_id = 0
    for row in tasks_data[1:]:
        if row and row[0]:
            try:
                task_id = int(row[0])
                max_id = max(max_id, task_id)
            except ValueError:
                continue
    
    return max_id + 1

# 使用例
start_task_id = self._get_next_task_id()
generator = StoryGenerator(epic, start_task_id)
```

【採番ルール】
- 既存タスク387行 → 次は388から
- エピック1で5タスク作成（388-392）
- エピック2で5タスク作成（393-397）
- ...連続採番

【メリット】
1. シンプルで理解しやすい
2. 既存システムとの互換性
3. 人間が読みやすい
4. ソート順が自然

【注意点】
- 並行実行時の重複を避けるため、batch処理推奨
- 削除されたIDは再利用しない（欠番OK）
        """,
        category="implementation",
        tags=["task_id", "sequential", "pm_tasks", "numbering"],
    )

    print("✅ ナレッジ登録完了")
    print("=" * 60)


if __name__ == "__main__":
    try:
        register_knowledge()
    except Exception as e:
        print(f"❌ ナレッジ登録エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

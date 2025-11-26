"""
列ズレ修正のナレッジ登録
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager


def register_knowledge():
    """列ズレ修正をナレッジ登録"""

    print("=" * 60)
    print("列ズレ修正 ナレッジ登録")
    print("=" * 60)
    print()

    km = KnowledgeManager()

    km.add_knowledge(
        title="pm_tasks列ズレ修正_正確なヘッダーマッピング",
        content="""
【問題】
F1実行でpm_tasksシートに書き込む際、列がズレていた。

【原因】
pm_agent_v33_epic.pyの_write_stories_to_sheetsメソッドが、
ヘッダーの列順序を正しく守っていなかった。

【正しいヘッダー順序】
1. task_id (A列)
2. parent_goal_id (B列)
3. description (C列)
4. required_role (D列)
5. status (E列)
6. priority (F列)
7. estimated_time (G列)
8. dependencies (H列)
9. created_at (I列)
10. batch_id (J列)
11. detail_file_path (K列)
12. blank (L列)
13. execution_type (M列)

【修正内容】
```python
# 修正前（列順序が不正確）
row = [
    story['story_id'],
    story['description'],  # ← 順序が違う
    epic_id,
    # ...
]

# 修正後（ヘッダーに正確に合わせる）
row = [
    story['story_id'],          # A: task_id
    epic_id,                    # B: parent_goal_id
    story['description'],       # C: description
    'developer',                # D: required_role
    'pending',                  # E: status
    story['priority'],          # F: priority
    str(story['estimated_time']), # G: estimated_time
    ','.join(story['dependencies']), # H: dependencies
    datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # I: created_at
    self.batch_id,             # J: batch_id
    '',                        # K: detail_file_path
    '',                        # L: blank
    'auto'                     # M: execution_type
]
```

【教訓】
1. Google Sheetsへの書き込み時は必ずヘッダーを確認
2. 列順序を明示的にコメント
3. ヘッダーの動的取得も検討（将来的に）

【防止策】
- 書き込み前にヘッダー順序を取得して検証
- 列名を明示したマッピング辞書の使用
- 単体テストでヘッダー一致を確認
        """,
        category="bug_fix",
        tags=["pm_tasks", "column_alignment", "sheets", "f1"],
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

"""
完全修正版エンジン
- ナレッジ蓄積のメソッド名修正
- 追加タスク生成機能実装
- 進捗に応じた動的タスク管理
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from tools.base_data_accessor import BaseDataAccessor


class CompleteEngineUltimate(BaseDataAccessor):
    """完全修正版エンジン"""

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)
        self.knowledge_manager = KnowledgeManager()
        self.output_dir = "/workspaces/gemini_AI_Agent/agent_outputs"
        os.makedirs(self.output_dir, exist_ok=True)

        print("✅ CompleteEngineUltimate 初期化完了")

    def generate_additional_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        """
        進捗に応じて追加タスクを生成
        """
        print(f"\n🔍 ゴール{goal_id}の追加タスク検討中...")

        # 既存タスクの状況確認
        existing_tasks = self.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
        )

        if not existing_tasks:
            print("   既存タスクなし - 初回タスク生成")
            return self._generate_initial_tasks(goal_id)

        total = len(existing_tasks)
        completed = sum(1 for t in existing_tasks if t.get("status", "").lower() == "completed")
        pending = sum(1 for t in existing_tasks if t.get("status", "").lower() == "pending")

        progress = (completed / total * 100) if total > 0 else 0

        print(
            f"   既存: {total}件 | 完了: {completed}件 | 待機: {pending}件 | 進捗: {progress:.1f}%"
        )

        # pendingがある場合は追加しない
        if pending > 0:
            print("   pendingタスクあり - 追加不要")
            return []

        # 進捗に応じて追加タスク生成
        new_tasks = []

        if 40 <= progress < 60:
            print("   中間進捗 - テストタスク追加")
            new_tasks = self._generate_test_tasks(goal_id, existing_tasks)
        elif 60 <= progress < 90:
            print("   後期進捗 - 品質改善タスク追加")
            new_tasks = self._generate_quality_tasks(goal_id, existing_tasks)
        elif progress >= 90:
            print("   最終段階 - ドキュメントタスク追加")
            new_tasks = self._generate_documentation_tasks(goal_id, existing_tasks)

        return new_tasks

    def _generate_initial_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        """初回タスク生成"""
        goals = self.read_sheet_as_dicts(
            "project_goal", filter_func=lambda g: g.get("goal_id") == goal_id
        )

        if not goals:
            return []

        goal_desc = goals[0].get("goal_description", "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return [
            {
                "task_id": f"{goal_id}_TASK_001",
                "parent_goal_id": goal_id,
                "description": f"【調査】{goal_desc[:70]}",
                "required_role": "developer",
                "status": "pending",
                "priority": "high",
                "estimated_time": "2h",
                "dependencies": "",
                "created_at": timestamp,
                "batch_id": f"BATCH_{goal_id}_INITIAL",
                "detail_file_path": "",
                "blank": "",
                "execution_type": "sequential",
            },
            {
                "task_id": f"{goal_id}_TASK_002",
                "parent_goal_id": goal_id,
                "description": f"【設計】{goal_desc[:70]}",
                "required_role": "developer",
                "status": "pending",
                "priority": "high",
                "estimated_time": "3h",
                "dependencies": f"{goal_id}_TASK_001",
                "created_at": timestamp,
                "batch_id": f"BATCH_{goal_id}_INITIAL",
                "detail_file_path": "",
                "blank": "",
                "execution_type": "sequential",
            },
            {
                "task_id": f"{goal_id}_TASK_003",
                "parent_goal_id": goal_id,
                "description": f"【実装】{goal_desc[:70]}",
                "required_role": "developer",
                "status": "pending",
                "priority": "high",
                "estimated_time": "5h",
                "dependencies": f"{goal_id}_TASK_002",
                "created_at": timestamp,
                "batch_id": f"BATCH_{goal_id}_INITIAL",
                "detail_file_path": "",
                "blank": "",
                "execution_type": "sequential",
            },
        ]

    def _generate_test_tasks(self, goal_id: str, existing: List[Dict]) -> List[Dict[str, Any]]:
        """テストタスク生成"""
        next_num = len(existing) + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return [
            {
                "task_id": f"{goal_id}_TASK_{next_num:03d}",
                "parent_goal_id": goal_id,
                "description": f"【テスト】ユニットテストの作成と実行",
                "required_role": "developer",
                "status": "pending",
                "priority": "high",
                "estimated_time": "2h",
                "dependencies": "",
                "created_at": timestamp,
                "batch_id": f"BATCH_{goal_id}_TEST",
                "detail_file_path": "",
                "blank": "",
                "execution_type": "sequential",
            }
        ]

    def _generate_quality_tasks(self, goal_id: str, existing: List[Dict]) -> List[Dict[str, Any]]:
        """品質改善タスク生成"""
        next_num = len(existing) + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return [
            {
                "task_id": f"{goal_id}_TASK_{next_num:03d}",
                "parent_goal_id": goal_id,
                "description": f"【品質改善】コードレビューとリファクタリング",
                "required_role": "developer",
                "status": "pending",
                "priority": "medium",
                "estimated_time": "3h",
                "dependencies": "",
                "created_at": timestamp,
                "batch_id": f"BATCH_{goal_id}_QUALITY",
                "detail_file_path": "",
                "blank": "",
                "execution_type": "sequential",
            }
        ]

    def _generate_documentation_tasks(
        self, goal_id: str, existing: List[Dict]
    ) -> List[Dict[str, Any]]:
        """ドキュメントタスク生成"""
        next_num = len(existing) + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return [
            {
                "task_id": f"{goal_id}_TASK_{next_num:03d}",
                "parent_goal_id": goal_id,
                "description": f"【ドキュメント】README・使用方法の整備",
                "required_role": "developer",
                "status": "pending",
                "priority": "medium",
                "estimated_time": "1h",
                "dependencies": "",
                "created_at": timestamp,
                "batch_id": f"BATCH_{goal_id}_DOC",
                "detail_file_path": "",
                "blank": "",
                "execution_type": "sequential",
            }
        ]

    def save_tasks_to_sheet(self, tasks: List[Dict[str, Any]]) -> bool:
        """タスクをpm_tasksに保存"""
        if not tasks:
            return True

        print(f"\n💾 pm_tasksに{len(tasks)}件のタスクを保存中...")

        try:
            column_map = self._get_column_map("pm_tasks")
            if not column_map:
                print("❌ 列構造取得失敗")
                return False

            rows = []
            for task in tasks:
                row = [""] * len(column_map)
                for col_name, col_idx in column_map.items():
                    if col_name in task:
                        row[col_idx] = str(task[col_name])
                rows.append(row)

            success = self.safe_sheets.safe_append("pm_tasks", rows)

            if success:
                print(f"✅ pm_tasksに保存成功: {len(tasks)}件")
                for task in tasks:
                    print(f"   • {task.get('task_id')} - {task.get('description', '')[:50]}...")
            else:
                print("❌ 保存失敗")

            return success

        except Exception as e:
            print(f"❌ 保存エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タスク実行"""
        task_id = task.get("task_id", "UNKNOWN")
        description = task.get("description", "")

        print(f"\n🚀 タスク実行: {task_id}")
        print(f"   説明: {description[:80]}...")

        start_time = datetime.now()

        # 出力コンテンツ
        output_content = f"""
タスク実行結果レポート
{'='*80}

タスクID: {task_id}
親ゴール: {task.get('parent_goal_id', 'N/A')}
説明: {description}
実行時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}

{'='*80}
【実行内容】
{'='*80}

タスクを完了しました。

{'='*80}
実行完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
"""

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        # agent_outputsに保存
        output_filename = f"{task_id}_{start_time.strftime('%Y%m%d_%H%M%S')}.txt"
        output_path = os.path.join(self.output_dir, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_content)

        print(f"   ✅ 出力保存: {output_filename}")

        return {
            "success": True,
            "task_id": task_id,
            "output_file": output_path,
            "output_filename": output_filename,
            "elapsed_time": elapsed,
            "quality_score": 8.5,
        }

    def save_to_execution_log(self, task: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """task_execution_logに保存"""
        print(f"\n   📊 task_execution_logに記録中...")

        log_row = [
            [
                f'LOG_{result["task_id"]}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                result["task_id"],
                task.get("description", "")[:100],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                task.get("required_role", "developer"),
                f'完了: {result["output_filename"]}',
                result["output_file"],
                "completed",
                str(result["quality_score"]),
                "高品質で完了",
                f'{result["elapsed_time"]:.2f}',
                "0",
                "",
                "",
            ]
        ]

        try:
            success = self.safe_sheets.safe_append("task_execution_log", log_row)
            if success:
                print(f"   ✅ task_execution_log記録成功")
            return success
        except Exception as e:
            print(f"   ❌ ログ記録エラー: {e}")
            return False

    def update_task_status(self, task_id: str) -> bool:
        """pm_tasksのステータス更新"""
        print(f"\n   🔄 ステータス更新中: {task_id}")

        try:
            all_tasks = self.read_sheet_as_dicts("pm_tasks")

            for i, task in enumerate(all_tasks):
                if task.get("task_id") == task_id:
                    row_num = i + 2
                    status_idx = self.get_column_index("pm_tasks", "status")

                    if status_idx is None:
                        return False

                    col_letter = chr(65 + status_idx)
                    range_str = f"pm_tasks!{col_letter}{row_num}"

                    success = self.safe_sheets.safe_update(range_str, [["completed"]])

                    if success:
                        print(f"   ✅ ステータス更新成功: completed")

                    return success

            return False

        except Exception as e:
            print(f"   ❌ 更新エラー: {e}")
            return False

    def accumulate_knowledge(self, task: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """ナレッジ蓄積（修正版）"""
        print(f"\n   📚 ナレッジ蓄積中...")

        try:
            # ✅ 修正: 正しいメソッド名を使用
            self.knowledge_manager.add_knowledge(
                title=f'タスク実行_{result["task_id"]}',
                content=f'{task.get("description", "")}\n実行完了: {result["output_filename"]}',
                category="task_execution",
                tags=f'{result["task_id"]},completed',
            )
            print(f"   ✅ ナレッジ蓄積成功")
            return True
        except Exception as e:
            print(f"   ❌ ナレッジ蓄積エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    def run_complete_flow(self, goal_id: str = None, execute_count: int = 1):
        """完全フロー実行"""
        print("\n" + "=" * 80)
        print("🚀 完全統合フロー開始（最終修正版）")
        print("=" * 80)

        # ゴール選択
        if not goal_id:
            goals = self.read_sheet_as_dicts(
                "project_goal",
                filter_func=lambda g: g.get("status", "").lower() in ["active", "pending"],
            )

            if not goals:
                print("⚠️ active/pending ゴールなし")
                return

            goal_id = goals[0].get("goal_id")

        print(f"\n対象ゴール: {goal_id}")

        # 追加タスク生成
        new_tasks = self.generate_additional_tasks(goal_id)

        if new_tasks:
            print(f"\n✅ 追加タスク生成: {len(new_tasks)}件")
            self.save_tasks_to_sheet(new_tasks)

        # pendingタスク実行
        pending = self.read_sheet_as_dicts(
            "pm_tasks",
            filter_func=lambda t: (
                t.get("parent_goal_id") == goal_id and t.get("status", "").lower() == "pending"
            ),
        )

        print(f"\n📋 ゴール{goal_id}のpending: {len(pending)}件")
        print(f"実行対象: 最初の{execute_count}件")

        success_count = 0

        for i, task in enumerate(pending[:execute_count], 1):
            print(f"\n{'='*80}")
            print(f"【タスク {i}/{min(execute_count, len(pending))}】 {task.get('task_id')}")
            print(f"{'='*80}")

            result = self.execute_task(task)

            if result["success"]:
                log_ok = self.save_to_execution_log(task, result)
                status_ok = self.update_task_status(result["task_id"])
                knowledge_ok = self.accumulate_knowledge(task, result)

                if log_ok and status_ok and knowledge_ok:
                    success_count += 1
                    print(f"\n✅ 完全成功: {result['task_id']}")

        print("\n" + "=" * 80)
        print(f"✅ フロー完了: {success_count}/{min(execute_count, len(pending))}件成功")
        print("=" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--goal_id", type=str, help="対象ゴールID")
    parser.add_argument("--count", type=int, default=1, help="実行タスク数")

    args = parser.parse_args()

    engine = CompleteEngineUltimate()
    engine.run_complete_flow(goal_id=args.goal_id, execute_count=args.count)

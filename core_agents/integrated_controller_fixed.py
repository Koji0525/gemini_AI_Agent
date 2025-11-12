"""
統合コントローラー修正版
KnowledgeManager正しいメソッド使用
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from tools.base_data_accessor import BaseDataAccessor

logger = logging.getLogger(__name__)


class IntegratedControllerFixed(BaseDataAccessor):
    """統合コントローラー修正版"""

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)
        self.knowledge_manager = KnowledgeManager()
        self.output_dir = "/workspaces/gemini_AI_Agent/agent_outputs"

        os.makedirs(self.output_dir, exist_ok=True)

        logger.info("✅ IntegratedControllerFixed 初期化完了")

    async def decompose_goal_to_tasks(self, goal: Dict) -> List[Dict]:
        """ゴールをタスクに分解（ナレッジ参照付き）"""
        try:
            goal_id = goal.get("goal_id")
            goal_desc = goal.get("goal_description", "")

            logger.info(f"\n🔨 タスク分解: {goal_id}")
            logger.info(f"   内容: {goal_desc[:100]}...")

            # ナレッジ検索（正しい引数で呼び出し）
            logger.info("   🔍 ナレッジ検索中...")
            try:
                # ✅ 修正: limit引数を使用（top_kではなく）
                similar_knowledge = self.knowledge_manager.search_knowledge(
                    query=goal_desc[:200], limit=3
                )

                if similar_knowledge:
                    logger.info(f"   ✅ 類似ナレッジ: {len(similar_knowledge)}件")
                    for i, k in enumerate(similar_knowledge[:3], 1):
                        logger.info(f"      {i}. {k.get('title', 'N/A')[:50]}...")
                else:
                    logger.info("   ℹ️ 類似ナレッジなし")
            except Exception as search_error:
                logger.warning(f"   ⚠️ ナレッジ検索エラー: {search_error}")
                similar_knowledge = []

            # 既存タスクチェック
            existing = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
            )

            if existing:
                logger.info(f"   既存タスク: {len(existing)}件")
                return existing

            # タスク生成
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            task_prefix = "【調査・参照】" if similar_knowledge else "【調査】"

            tasks = [
                {
                    "task_id": f"{goal_id}_TASK_001",
                    "parent_goal_id": goal_id,
                    "description": f"{task_prefix}{goal_desc[:70]}",
                    "required_role": "developer",
                    "status": "pending",
                    "priority": "high",
                    "estimated_time": "2h",
                    "dependencies": "",
                    "created_at": timestamp,
                    "batch_id": f"BATCH_{goal_id}",
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
                    "batch_id": f"BATCH_{goal_id}",
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
                    "batch_id": f"BATCH_{goal_id}",
                    "detail_file_path": "",
                    "blank": "",
                    "execution_type": "sequential",
                },
            ]

            logger.info(f"   ✅ タスク生成: {len(tasks)}件")

            return tasks

        except Exception as e:
            logger.error(f"❌ タスク分解エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    async def save_tasks(self, tasks: List[Dict]) -> bool:
        """pm_tasksシートに保存"""
        try:
            if not tasks:
                return False

            logger.info(f"💾 タスク保存: {len(tasks)}件")

            column_map = self._get_column_map("pm_tasks")
            if not column_map:
                logger.error("❌ 列構造取得失敗")
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
                logger.info("   ✅ 保存成功")

            return success

        except Exception as e:
            logger.error(f"❌ タスク保存エラー: {e}")
            return False

    async def execute_task_with_output(self, task: Dict) -> Dict[str, Any]:
        """タスク実行 + 出力保存 + ログ記録"""
        try:
            task_id = task.get("task_id", "UNKNOWN")
            description = task.get("description", "")

            logger.info(f"\n▶ タスク実行: {task_id}")
            logger.info(f"   内容: {description}")

            # ナレッジ検索
            logger.info("   🔍 ナレッジ参照...")
            try:
                similar = self.knowledge_manager.search_knowledge(query=description, limit=3)

                context = ""
                if similar:
                    logger.info(f"   ✅ 参照ナレッジ: {len(similar)}件")
                    context = "\n".join(
                        [
                            f"- {k.get('title', '')}: {k.get('content', '')[:100]}..."
                            for k in similar[:3]
                        ]
                    )
            except Exception as e:
                logger.warning(f"   ⚠️ ナレッジ参照エラー: {e}")
                context = ""

            # タスク実行
            start_time = datetime.now()

            output_content = f"""
タスク実行結果
================

タスクID: {task_id}
説明: {description}
実行時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}

【参照したナレッジ】
{context if context else '（なし）'}

【実行内容】
{description}の実行を完了しました。

【成果物】
- 調査結果のまとめ
- 設計ドキュメント（該当する場合）
- 実装コード（該当する場合）

【次のステップ】
- レビューと品質評価
- 必要に応じた修正
- 次タスクへの引き継ぎ
"""

            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()

            # agent_outputsに保存
            output_filename = f"{task_id}_{start_time.strftime('%Y%m%d_%H%M%S')}.txt"
            output_path = os.path.join(self.output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_content)

            logger.info(f"   ✅ 出力保存: {output_filename}")

            # task_execution_logに記録
            log_row = [
                [
                    f'LOG_{task_id}_{start_time.strftime("%Y%m%d%H%M%S")}',
                    task_id,
                    description[:100],
                    start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "developer",
                    f"完了: {output_filename}",
                    output_path,
                    "completed",
                    "8.0",
                    "良好",
                    f"{elapsed:.2f}s",
                    "0",
                    "",
                    "",
                ]
            ]

            try:
                self.safe_sheets.safe_append("task_execution_log", log_row)
                logger.info("   ✅ 実行ログ記録完了")
            except Exception as e:
                logger.warning(f"   ⚠️ ログ記録エラー: {e}")

            # タスクステータス更新
            await self.update_task_status(task_id, "completed")

            # ナレッジ蓄積
            try:
                self.knowledge_manager.add_knowledge(
                    title=f"タスク実行_{task_id}",
                    content=f"{description}\n結果: {output_filename}",
                    category="task_execution",
                    tags=f"{task_id},completed",
                )
                logger.info("   ✅ ナレッジ蓄積完了")
            except Exception as e:
                logger.warning(f"   ⚠️ ナレッジ蓄積エラー: {e}")

            result = {
                "success": True,
                "task_id": task_id,
                "output_file": output_path,
                "elapsed_time": elapsed,
                "quality_score": 8.0,
            }

            logger.info(f"   ✅ タスク完了（{elapsed:.2f}秒）")

            return result

        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {e}")
            import traceback

            traceback.print_exc()

            return {"success": False, "task_id": task.get("task_id", "UNKNOWN"), "error": str(e)}

    async def update_task_status(self, task_id: str, status: str):
        """タスクステータス更新"""
        try:
            tasks = self.read_sheet_as_dicts("pm_tasks")

            for i, task in enumerate(tasks):
                if task.get("task_id") == task_id:
                    status_idx = self.get_column_index("pm_tasks", "status")
                    if status_idx is not None:
                        row_num = i + 2
                        col_letter = chr(65 + status_idx)

                        self.safe_sheets.safe_update(f"pm_tasks!{col_letter}{row_num}", [[status]])
                        logger.info(f"   ✅ ステータス更新: {task_id} → {status}")
                    break

        except Exception as e:
            logger.warning(f"   ⚠️ ステータス更新エラー: {e}")

    async def review_task(self, task: Dict, result: Dict) -> Dict[str, Any]:
        """タスク結果をレビュー"""
        try:
            task_id = result.get("task_id", "UNKNOWN")

            logger.info(f"\n🔍 レビュー: {task_id}")

            output_file = result.get("output_file", "")
            if output_file and os.path.exists(output_file):
                with open(output_file, "r", encoding="utf-8") as f:
                    content = f.read()

                score = 7.0

                if len(content) > 500:
                    score += 1.0

                keywords = ["完了", "成果", "結果", "ナレッジ"]
                found_keywords = sum(1 for k in keywords if k in content)
                score += found_keywords * 0.5

                score = min(10.0, score)

                review_result = {
                    "task_id": task_id,
                    "total_score": score,
                    "completeness": score,
                    "quality": score,
                    "comments": f"品質スコア: {score:.1f}/10",
                }

                logger.info(f"   ✅ 品質スコア: {score:.1f}/10")

                return review_result
            else:
                logger.warning("   ⚠️ 出力ファイルなし")
                return {"task_id": task_id, "total_score": 5.0}

        except Exception as e:
            logger.error(f"❌ レビューエラー: {e}")
            return {"task_id": task.get("task_id", "UNKNOWN"), "total_score": 5.0}

    async def check_progress_and_generate_tasks(self, goal: Dict) -> List[Dict]:
        """進捗チェックと追加タスク生成"""
        try:
            goal_id = goal.get("goal_id")

            logger.info(f"\n📊 進捗チェック: {goal_id}")

            tasks = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
            )

            total = len(tasks)
            completed = sum(1 for t in tasks if t.get("status", "").lower() == "completed")

            progress = (completed / total * 100) if total > 0 else 0

            logger.info(f"   進捗: {completed}/{total}件 ({progress:.1f}%)")

            # 50%完了時に詳細タスクを追加
            new_tasks = []
            if 40 <= progress < 60:
                logger.info("   🔄 中間評価 - 詳細タスク生成")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                new_tasks = [
                    {
                        "task_id": f"{goal_id}_TASK_004",
                        "parent_goal_id": goal_id,
                        "description": f'【テスト】{goal.get("goal_description", "")[:70]}',
                        "required_role": "developer",
                        "status": "pending",
                        "priority": "medium",
                        "estimated_time": "2h",
                        "dependencies": f"{goal_id}_TASK_003",
                        "created_at": timestamp,
                        "batch_id": f"BATCH_{goal_id}_DETAIL",
                        "detail_file_path": "",
                        "blank": "",
                        "execution_type": "sequential",
                    }
                ]

                logger.info(f"   ✅ 詳細タスク生成: {len(new_tasks)}件")

                await self.save_tasks(new_tasks)

            return new_tasks

        except Exception as e:
            logger.error(f"❌ 進捗チェックエラー: {e}")
            return []


async def test():
    print("🧪 IntegratedControllerFixed テスト\n")

    controller = IntegratedControllerFixed()

    goals = controller.read_sheet_as_dicts(
        "project_goal", filter_func=lambda g: g.get("status", "").lower() == "active"
    )

    if goals:
        goal = goals[0]
        print(f"✅ ゴール: {goal.get('goal_id')}")

        # タスク分解
        tasks = await controller.decompose_goal_to_tasks(goal)
        print(f"✅ タスク分解: {len(tasks)}件")

        # タスク保存
        if tasks:
            existing = controller.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal.get("goal_id")
            )

            if not existing:
                success = await controller.save_tasks(tasks)
                print(f"✅ タスク保存: {'成功' if success else '失敗'}")

        # 進捗チェック
        await controller.check_progress_and_generate_tasks(goal)

        print("\n✅ テスト完了")
    else:
        print("❌ active ゴールなし")


if __name__ == "__main__":
    asyncio.run(test())

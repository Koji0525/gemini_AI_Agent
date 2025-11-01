"""
DynamicTaskGenerator - 実行結果を分析して追加タスクを自動生成
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamicTaskGenerator:
    """タスク実行結果を分析し、必要に応じて追加タスクを自動生成"""

    def __init__(self, sheets_manager, browser_controller=None):
        self.sheets_manager = sheets_manager
        self.browser = browser_controller
        self.spreadsheet_id = sheets_manager.spreadsheet_id

        # エージェント切り替えマッピング
        self.agent_alternatives = {
            "design": ["dev", "wordpress"],  # 設計→開発 or WordPress
            "dev": ["wordpress", "design"],  # 開発→WordPress or 再設計
            "wordpress": ["dev", "design"],  # WordPress→開発 or 設計
            "review": ["design", "dev"],  # レビュー→設計 or 開発
            "writer": ["writer_ja", "content"],
            "writer_ja": ["writer", "content"],
        }

    async def analyze_execution_log(self, log_id: str) -> Optional[Dict]:
        """実行ログを分析"""
        try:
            sheet = self.sheets_manager.gc.open_by_key(self.spreadsheet_id)
            log_sheet = sheet.worksheet("task_execution_log")
            all_values = log_sheet.get_all_values()

            if len(all_values) < 2:
                return None

            headers = all_values[0]

            # log_idに該当する行を検索
            for row in all_values[1:]:
                if row and str(row[0]) == str(log_id):
                    log_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                    return log_dict

            return None

        except Exception as e:
            logger.error(f"❌ ログ分析エラー: {e}")
            return None

    async def should_generate_tasks(self, log_entry: Dict) -> Tuple[bool, str, Dict]:
        """
        タスク生成が必要か判断

        Returns:
            (bool, reason, context): (生成必要性, 理由, コンテキスト情報)
        """
        if not log_entry:
            return (False, "", {})

        task_id = log_entry.get("task_id")
        quality_score_str = str(log_entry.get("Quality_Score", "")).strip()
        status = log_entry.get("status", "").lower()
        output_summary = log_entry.get("output_summary", "")
        agent_role = log_entry.get("agent_role", "")

        # 1. 品質スコアが低い（<7.0）→ 別エージェントで再実行
        if quality_score_str and quality_score_str.replace(".", "").isdigit():
            quality_score = float(quality_score_str)

            if quality_score < 7.0:
                logger.info(f"🔍 TaskID={task_id}: 品質スコア={quality_score} < 7.0")

                # 代替エージェントを取得
                alternative_agents = self.agent_alternatives.get(agent_role, [])

                context = {
                    "original_task_id": task_id,
                    "original_agent": agent_role,
                    "quality_score": quality_score,
                    "alternative_agents": alternative_agents,
                    "task_description": log_entry.get("task_description", ""),
                }

                return (True, "low_quality_switch_agent", context)

        # 2. タスク失敗 → 代替アプローチ
        if status == "failed":
            logger.info(f"🔍 TaskID={task_id}: タスク失敗")

            context = {
                "original_task_id": task_id,
                "original_agent": agent_role,
                "task_description": log_entry.get("task_description", ""),
                "failure_reason": output_summary[:200],
            }

            return (True, "task_failed", context)

        # 3. 新しい要件を発見（キーワード検出）
        requirement_keywords = ["必要", "追加で", "実装すべき", "TODO", "次のステップ"]

        if any(keyword in output_summary for keyword in requirement_keywords):
            logger.info(f"🔍 TaskID={task_id}: 新しい要件を検出")

            context = {"original_task_id": task_id, "requirement_hint": output_summary[:300]}

            return (True, "new_requirement", context)

        return (False, "", {})

    async def generate_followup_tasks(self, reason: str, context: Dict) -> List[Dict]:
        """
        フォローアップタスクを生成

        Returns:
            生成されたタスクのリスト
        """
        tasks = []

        if reason == "low_quality_switch_agent":
            # 品質改善：別エージェントで再実行
            original_task_id = context["original_task_id"]
            original_agent = context["original_agent"]
            quality_score = context["quality_score"]
            alternative_agents = context["alternative_agents"]
            description = context["task_description"]

            if alternative_agents:
                # 最初の代替エージェントを使用
                new_agent = alternative_agents[0]

                task = {
                    "description": f"【品質改善・エージェント切替】TaskID={original_task_id}を{new_agent}エージェントで再実行（前回スコア={quality_score}）\n元のタスク: {description[:100]}",
                    "required_role": new_agent,
                    "priority": "high",
                    "dependencies": str(original_task_id),
                    "estimated_time": "1日",
                    "execution_type": "gemini" if new_agent in ["design", "review", "writer"] else "wordpress",
                }

                tasks.append(task)

                logger.info(f"✨ 品質改善タスク生成: {original_agent} → {new_agent}")

        elif reason == "task_failed":
            # タスク失敗：代替アプローチ
            original_task_id = context["original_task_id"]
            description = context["task_description"]

            task = {
                "description": f"【代替アプローチ】TaskID={original_task_id}が失敗したため、別の方法で実装\n元のタスク: {description[:100]}",
                "required_role": "design",  # まず設計で再検討
                "priority": "high",
                "dependencies": "",
                "estimated_time": "1日",
                "execution_type": "gemini",
            }

            tasks.append(task)

            logger.info(f"✨ 代替アプローチタスク生成")

        elif reason == "new_requirement":
            # 新しい要件：Geminiに分析させる
            original_task_id = context["original_task_id"]
            requirement_hint = context["requirement_hint"]

            task = {
                "description": f"【追加要件分析】TaskID={original_task_id}の実行中に発見された要件を分析・タスク化\nヒント: {requirement_hint[:150]}",
                "required_role": "design",
                "priority": "medium",
                "dependencies": str(original_task_id),
                "estimated_time": "0.5日",
                "execution_type": "gemini",
            }

            tasks.append(task)

            logger.info(f"✨ 追加要件タスク生成")

        return tasks

    async def add_tasks_to_sheet(self, tasks: List[Dict], parent_task_id: str = "") -> bool:
        """生成したタスクをpm_tasksシートに追加"""
        try:
            if not tasks:
                return True

            logger.info(f"📝 {len(tasks)}件のタスクをpm_tasksシートに追加中...")

            sheet = self.sheets_manager.gc.open_by_key(self.spreadsheet_id)
            pm_tasks_sheet = sheet.worksheet("pm_tasks")
            all_values = pm_tasks_sheet.get_all_values()

            # 次のタスクIDを決定
            existing_task_ids = []
            for row in all_values[1:]:
                if row and row[0]:
                    try:
                        existing_task_ids.append(int(row[0]))
                    except:
                        pass

            next_task_id = max(existing_task_ids) + 1 if existing_task_ids else 1

            # バッチID生成
            batch_id = f"auto_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # タスクデータ準備
            rows_data = []

            for i, task in enumerate(tasks):
                row = [
                    next_task_id + i,  # task_id
                    parent_task_id,  # parent_goal_id（元のタスクID）
                    task.get("description", ""),  # description
                    task.get("required_role", "design"),  # required_role
                    "pending",  # status
                    task.get("priority", "medium"),  # priority
                    task.get("estimated_time", "1日"),  # estimated_time
                    task.get("dependencies", ""),  # dependencies
                    datetime.now().isoformat(),  # created_at
                    batch_id,  # batch_id
                    "",  # 11列目（予備）
                    "",  # 12列目（予備）
                    task.get("execution_type", "gemini"),  # execution_type
                ]
                rows_data.append(row)

            # シートに追加
            start_row = len(all_values) + 1
            end_row = start_row + len(rows_data) - 1

            pm_tasks_sheet.update(f"A{start_row}:M{end_row}", rows_data)

            logger.info(f"✅ {len(tasks)}件のタスクを追加しました（バッチ: {batch_id}）")

            return True

        except Exception as e:
            logger.error(f"❌ タスク追加エラー: {e}")
            return False

    async def monitor_and_generate(self, max_tasks: int = 5) -> int:
        """
        全ログを監視して必要に応じてタスク生成

        Args:
            max_tasks: 1回の実行で生成する最大タスク数

        Returns:
            生成したタスク数
        """
        try:
            logger.info("🔍 タスク実行ログを監視中...")

            sheet = self.sheets_manager.gc.open_by_key(self.spreadsheet_id)
            log_sheet = sheet.worksheet("task_execution_log")
            all_values = log_sheet.get_all_values()

            if len(all_values) < 2:
                logger.info("⚠️ ログが見つかりません")
                return 0

            headers = all_values[0]

            # すべてのログをパース
            all_logs = []
            for row in all_values[1:]:
                if row:
                    log_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                    all_logs.append(log_dict)

            # 最新のログから順に分析
            all_logs.reverse()

            generated_count = 0

            for log in all_logs[:20]:  # 最新20件を確認
                if generated_count >= max_tasks:
                    break

                # タスク生成判定
                should_gen, reason, context = await self.should_generate_tasks(log)

                if should_gen:
                    # タスク生成
                    new_tasks = await self.generate_followup_tasks(reason, context)

                    if new_tasks:
                        # シートに追加
                        parent_task_id = context.get("original_task_id", "")
                        success = await self.add_tasks_to_sheet(new_tasks, parent_task_id)

                        if success:
                            generated_count += len(new_tasks)

            logger.info(f"✅ タスク生成完了: {generated_count}件")

            return generated_count

        except Exception as e:
            logger.error(f"❌ 監視エラー: {e}")
            return 0

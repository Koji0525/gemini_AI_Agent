"""
ProgressMonitor - タスク進捗の可視化と分析
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ProgressMonitor:
    """タスクの進捗状況と品質を監視・可視化"""

    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.spreadsheet_id = sheets_manager.spreadsheet_id

    async def analyze_batch_progress(self, batch_id: str) -> Dict:
        """
        指定バッチの進捗を分析

        Args:
            batch_id: バッチID (例: batch_20251025_033321)

        Returns:
            進捗サマリー辞書
        """
        try:
            logger.info(f"📊 バッチ進捗分析: {batch_id}")

            # 1. pm_tasksシートからバッチのタスク一覧を取得
            sheet = self.sheets_manager.gc.open_by_key(self.spreadsheet_id)
            pm_tasks_sheet = sheet.worksheet("pm_tasks")
            all_values = pm_tasks_sheet.get_all_values()

            if len(all_values) < 2:
                logger.warning("⚠️ pm_tasksシートにデータがありません")
                return {}

            # ヘッダー（1行目）
            headers = all_values[0]

            # データ行を辞書に変換
            all_tasks = []
            for row in all_values[1:]:
                if row and row[0]:  # task_idがある行のみ
                    task_dict = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            task_dict[header] = row[i]
                        else:
                            task_dict[header] = ""
                    all_tasks.append(task_dict)

            # バッチのタスクをフィルタ
            batch_tasks = [t for t in all_tasks if t.get("batch_id") == batch_id]

            if not batch_tasks:
                logger.warning(f"⚠️ バッチ {batch_id} のタスクが見つかりません")
                return {}

            # 2. ステータス集計
            total_tasks = len(batch_tasks)
            completed_tasks = sum(1 for t in batch_tasks if t.get("status") == "completed")
            pending_tasks = sum(1 for t in batch_tasks if t.get("status") == "pending")
            in_progress_tasks = sum(1 for t in batch_tasks if t.get("status") == "in_progress")
            failed_tasks = sum(1 for t in batch_tasks if t.get("status") == "failed")

            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            # 3. task_execution_logから品質スコアを取得
            try:
                log_sheet = sheet.worksheet("task_execution_log")
                all_logs = self._parse_sheet_to_dicts(log_sheet)

                # バッチのタスクIDリスト
                batch_task_ids = [str(t.get("task_id")) for t in batch_tasks]

                # 該当するログをフィルタ
                batch_logs = [log for log in all_logs if str(log.get("task_id")) in batch_task_ids]

                # 品質スコア集計
                quality_scores = []
                high_quality_count = 0
                problem_count = 0

                for log in batch_logs:
                    score_str = str(log.get("Quality_Score", "")).strip()
                    if score_str and score_str.replace(".", "").isdigit():
                        score = float(score_str)
                        quality_scores.append(score)

                        if score >= 8.0:
                            high_quality_count += 1
                        elif score < 7.0:
                            problem_count += 1

                avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

            except Exception as e:
                logger.warning(f"⚠️ 品質スコア取得エラー: {e}")
                avg_quality = 0.0
                high_quality_count = 0
                problem_count = 0

            # 4. サマリー作成
            summary = {
                "batch_id": batch_id,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "failed_tasks": failed_tasks,
                "completion_rate": round(completion_rate, 1),
                "avg_quality_score": round(avg_quality, 1),
                "high_quality_count": high_quality_count,
                "problem_count": problem_count,
                "last_updated": datetime.now().isoformat(),
            }

            logger.info(f"✅ バッチ分析完了: {completion_rate:.1f}% 完了, 品質={avg_quality:.1f}")

            return summary

        except Exception as e:
            logger.error(f"❌ バッチ進捗分析エラー: {e}")
            return {}

    async def detect_problem_tasks(self, min_quality: float = 7.0) -> List[Dict]:
        """
        品質スコアが基準未満のタスクを検出

        Args:
            min_quality: 最低品質基準

        Returns:
            問題タスクのリスト
        """
        try:
            logger.info(f"🔍 問題タスク検出（基準: {min_quality}以上）")

            sheet = self.sheets_manager.gc.open_by_key(self.spreadsheet_id)
            log_sheet = sheet.worksheet("task_execution_log")
            all_values = log_sheet.get_all_values()

            if len(all_values) < 2:
                return []

            headers = all_values[0]
            all_logs = []
            for row in all_values[1:]:
                if row:
                    log_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                    all_logs.append(log_dict)

            problem_tasks = []

            for log in all_logs:
                score_str = str(log.get("Quality_Score", "")).strip()

                if score_str and score_str.replace(".", "").isdigit():
                    score = float(score_str)

                    if score < min_quality:
                        problem_tasks.append(
                            {
                                "task_id": log.get("task_id"),
                                "description": log.get("task_description", "")[:50],
                                "quality_score": score,
                                "agent_role": log.get("agent_role"),
                                "status": "completed",
                                "issue": f"品質スコアが基準値({min_quality})未満",
                            }
                        )

            logger.info(f"⚠️ 問題タスク: {len(problem_tasks)}件")

            return problem_tasks

        except Exception as e:
            logger.error(f"❌ 問題タスク検出エラー: {e}")
            return []

    async def get_overall_summary(self) -> Dict:
        """プロジェクト全体のサマリーを取得"""
        try:
            logger.info("📊 プロジェクト全体サマリーを取得中...")

            sheet = self.sheets_manager.gc.open_by_key(self.spreadsheet_id)

            # 1. pm_tasksシートから全タスク取得
            pm_tasks_sheet = sheet.worksheet("pm_tasks")
            all_values = pm_tasks_sheet.get_all_values()

            if len(all_values) < 2:
                logger.warning("⚠️ pm_tasksシートにデータがありません")
                return {}

            # ヘッダー（1行目）
            headers = all_values[0]

            # データ行を辞書に変換
            all_tasks = []
            for row in all_values[1:]:
                if row and row[0]:  # task_idがある行のみ
                    task_dict = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            task_dict[header] = row[i]
                        else:
                            task_dict[header] = ""
                    all_tasks.append(task_dict)

            # バッチ数（ユニーク）
            batch_ids = set(t.get("batch_id") for t in all_tasks if t.get("batch_id"))

            # ステータス集計
            total_tasks = len(all_tasks)
            completed = sum(1 for t in all_tasks if t.get("status") == "completed")
            overall_completion = (completed / total_tasks * 100) if total_tasks > 0 else 0

            # 2. task_execution_logから品質スコア集計
            log_sheet = sheet.worksheet("task_execution_log")
            all_values = log_sheet.get_all_values()

            if len(all_values) < 2:
                return []

            headers = all_values[0]
            all_logs = []
            for row in all_values[1:]:
                if row:
                    log_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                    all_logs.append(log_dict)

            quality_scores = []
            high_quality = 0
            problem = 0

            for log in all_logs:
                score_str = str(log.get("Quality_Score", "")).strip()
                if score_str and score_str.replace(".", "").isdigit():
                    score = float(score_str)
                    quality_scores.append(score)

                    if score >= 8.0:
                        high_quality += 1
                    elif score < 7.0:
                        problem += 1

            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

            summary = {
                "total_batches": len(batch_ids),
                "total_tasks": total_tasks,
                "completed_tasks": completed,
                "overall_completion_rate": round(overall_completion, 1),
                "overall_quality_score": round(avg_quality, 1),
                "high_quality_tasks": high_quality,
                "problem_tasks": problem,
                "last_updated": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ プロジェクト全体: {total_tasks}タスク, {overall_completion:.1f}%完了, 品質={avg_quality:.1f}"
            )

            return summary

        except Exception as e:
            logger.error(f"❌ 全体サマリー取得エラー: {e}")
            return {}

    async def update_dashboard(self) -> bool:
        """progress_dashboardシートを更新（最適化版：1回のシート読み取り）"""
        try:
            logger.info("📊 ダッシュボードを更新中...")

            sheet = self.sheets_manager.gc.open_by_key(self.spreadsheet_id)

            # === 1回だけシートを読み取る ===
            pm_tasks_sheet = sheet.worksheet("pm_tasks")
            pm_tasks_values = pm_tasks_sheet.get_all_values()

            log_sheet = sheet.worksheet("task_execution_log")
            log_values = log_sheet.get_all_values()

            # データをパース
            if len(pm_tasks_values) < 2:
                logger.warning("⚠️ pm_tasksシートにデータがありません")
                return False

            pm_headers = pm_tasks_values[0]
            all_tasks = []
            for row in pm_tasks_values[1:]:
                if row and row[0]:
                    task_dict = {pm_headers[i]: row[i] if i < len(row) else "" for i in range(len(pm_headers))}
                    all_tasks.append(task_dict)

            log_headers = log_values[0] if len(log_values) > 0 else []
            all_logs = []
            for row in log_values[1:]:
                if row:
                    log_dict = {log_headers[i]: row[i] if i < len(row) else "" for i in range(len(log_headers))}
                    all_logs.append(log_dict)

            # === バッチごとにメモリ上で分析 ===
            batch_ids = set(t.get("batch_id") for t in all_tasks if t.get("batch_id"))

            logger.info(f"📊 {len(batch_ids)}バッチを分析中...")

            dashboard_data = []

            for batch_id in sorted(batch_ids, reverse=True):
                # バッチのタスクをフィルタ
                batch_tasks = [t for t in all_tasks if t.get("batch_id") == batch_id]

                if not batch_tasks:
                    continue

                # ステータス集計
                total = len(batch_tasks)
                completed = sum(1 for t in batch_tasks if t.get("status") == "completed")
                pending = sum(1 for t in batch_tasks if t.get("status") == "pending")
                in_progress = sum(1 for t in batch_tasks if t.get("status") == "in_progress")
                failed = sum(1 for t in batch_tasks if t.get("status") == "failed")

                completion_rate = (completed / total * 100) if total > 0 else 0

                # 品質スコア集計
                batch_task_ids = [str(t.get("task_id")) for t in batch_tasks]
                batch_logs = [log for log in all_logs if str(log.get("task_id")) in batch_task_ids]

                quality_scores = []
                high_quality = 0
                problem = 0

                for log in batch_logs:
                    score_str = str(log.get("Quality_Score", "")).strip()
                    if score_str and score_str.replace(".", "").isdigit():
                        score = float(score_str)
                        quality_scores.append(score)

                        if score >= 8.0:
                            high_quality += 1
                        elif score < 7.0:
                            problem += 1

                avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

                # goal_idを取得（バッチの最初のタスクから）
                goal_id = batch_tasks[0].get("parent_goal_id", "") if batch_tasks else ""

                # ダッシュボード行を作成
                row = [
                    batch_id,
                    goal_id,
                    total,
                    completed,
                    pending,
                    failed,
                    round(completion_rate, 1),
                    round(avg_quality, 1),
                    high_quality,
                    problem,
                    datetime.now().isoformat(),
                ]
                dashboard_data.append(row)

            # === progress_dashboardシートを更新 ===
            try:
                dashboard_sheet = sheet.worksheet("progress_dashboard")
            except:
                logger.info("progress_dashboardシートを作成します")
                dashboard_sheet = sheet.add_worksheet(title="progress_dashboard", rows=100, cols=10)

                headers = [
                    "batch_id",
                    "goal_id",
                    "total_tasks",
                    "completed_tasks",
                    "pending_tasks",
                    "failed_tasks",
                    "completion_rate(%)",
                    "avg_quality_score",
                    "high_quality_count(>=8)",
                    "problem_count(<7)",
                    "last_updated",
                ]
                dashboard_sheet.update("A1:K1", [headers])

            if dashboard_data:
                # 既存データをクリア
                dashboard_sheet.batch_clear(["A2:K1000"])

                # 新しいデータを挿入
                end_row = len(dashboard_data) + 1
                dashboard_sheet.update(f"A2:K{end_row}", dashboard_data)

                logger.info(f"✅ ダッシュボード更新完了: {len(dashboard_data)}バッチ")
                return True
            else:
                logger.warning("⚠️ 更新するデータがありません")
                return False

        except Exception as e:
            logger.error(f"❌ ダッシュボード更新エラー: {e}")
            return False

    def _parse_sheet_to_dicts(self, worksheet) -> List[Dict]:
        """シートデータを辞書のリストに変換"""
        all_values = worksheet.get_all_values()

        if len(all_values) < 2:
            return []

        headers = all_values[0]
        result = []

        for row in all_values[1:]:
            if row and any(row):  # 空行をスキップ
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ""
                result.append(row_dict)

        return result

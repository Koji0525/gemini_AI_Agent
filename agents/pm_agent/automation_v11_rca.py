#!/usr/bin/env python3

"""

PM Agent 完全自動化システム（RCA統合版）

import google.generativeai as genai



v10 からの変更:

+ Phase 5 拡張: 根本原因分析（RCA）

+ エラー傾向分析

+ 再発防止策の提案

"""


import asyncio
import sys
import traceback
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# プロジェクトルートをパスに追加

project_root = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(project_root))


from agents.error_analyzer import ErrorAnalyzer
from agents.pm_agent.task_breakdown_gemini import GeminiTaskBreakdownAgent
from agents.pm_agent.task_exporter import TaskExportAgent
from agents.pm_agent.task_registration import TaskRegistrationAgent
from browser_control.browser_controller import BrowserController
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager


class RCAEngine:
    """根本原因分析（Root Cause Analysis）エンジン"""

    def __init__(self, error_analyzer: ErrorAnalyzer):

        self.error_analyzer = error_analyzer

    def analyze_error_trends(self, days: int = 7) -> Dict[str, Any]:
        """エラー傾向を分析"""

        print(f"\n📊 過去{days}日間のエラー傾向を分析中...")

        # エラーログ取得

        all_logs = self.error_analyzer.get_execution_logs(status_filter="failed")

        if not all_logs:

            print("✅ エラーログなし")

            return {"total_errors": 0}

        # 日付フィルタ

        cutoff_date = datetime.now() - timedelta(days=days)

        recent_logs = []

        for log in all_logs:

            timestamp_str = log.get("timestamp") or log.get("created_at", "")

            if timestamp_str:

                try:

                    log_date = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

                    if log_date >= cutoff_date:

                        recent_logs.append(log)

                except Exception:

                    pass

        print(f"✅ {len(recent_logs)}件のエラーを検出")

        # 傾向分析

        error_types = []

        task_ids = []

        for log in recent_logs:

            error_msg = log.get("error", "") or log.get("result", "")

            error_type = self.error_analyzer.classify_error(error_msg)

            error_types.append(error_type)

            task_ids.append(log.get("task_id", "Unknown"))

        # 集計

        type_counter = Counter(error_types)

        task_counter = Counter(task_ids)

        trends = {
            "total_errors": len(recent_logs),
            "by_type": dict(type_counter.most_common()),
            "by_task": dict(task_counter.most_common(5)),
            "most_common_type": type_counter.most_common(1)[0] if type_counter else ("none", 0),
        }

        # 表示

        print("\n【エラータイプ別】")

        for error_type, count in type_counter.most_common():

            percentage = (count / len(recent_logs)) * 100

            print(f"  {error_type}: {count}件 ({percentage:.1f}%)")

        print("\n【頻発タスク（上位5件）】")

        for task_id, count in task_counter.most_common(5):

            print(f"  タスク#{task_id}: {count}件")

        return trends

    def suggest_preventions(self, trends: Dict[str, Any]) -> List[str]:
        """再発防止策を提案"""

        if trends["total_errors"] == 0:

            return []

        suggestions = []

        most_common_type, count = trends["most_common_type"]

        # エラータイプ別の提案

        prevention_map = {
            "timeout": [
                f"タイムアウトが{count}件発生しています",
                "→ 対策1: タイムアウト時間を60秒→90秒に延長",
                "→ 対策2: 処理を分割して軽量化",
                "→ 対策3: リトライ回数を2回→3回に増加",
            ],
            "authentication": [
                f"認証エラーが{count}件発生しています",
                "→ 対策1: セッション有効期限を確認",
                "→ 対策2: 自動ログイン機能を強化",
                "→ 対策3: クッキーの定期更新",
            ],
            "network": [
                f"ネットワークエラーが{count}件発生しています",
                "→ 対策1: リトライ間隔を2秒→5秒に延長",
                "→ 対策2: 接続タイムアウトを延長",
                "→ 対策3: ネットワーク状態の事前チェック",
            ],
            "data_format": [
                f"データフォーマットエラーが{count}件発生しています",
                "→ 対策1: 入力データのバリデーション強化",
                "→ 対策2: JSONパースのエラーハンドリング改善",
                "→ 対策3: データ型チェックの追加",
            ],
        }

        if most_common_type in prevention_map:

            suggestions = prevention_map[most_common_type]

        else:

            suggestions = [
                f"{most_common_type}エラーが{count}件発生しています",
                "→ 詳細な分析が必要です",
            ]

        return suggestions

    def generate_rca_report(self, trends: Dict[str, Any]) -> str:
        """RCAレポートを生成"""

        report = []

        report.append("=" * 70)

        report.append("🔍 根本原因分析（RCA）レポート")

        report.append("=" * 70)

        report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        report.append("")

        if trends["total_errors"] == 0:

            report.append("✅ エラーなし - システムは正常に動作しています")

        else:

            report.append(f"📊 総エラー数: {trends['total_errors']}件")

            report.append("")

            # 最も多いエラータイプ

            most_common_type, count = trends["most_common_type"]

            percentage = (count / trends["total_errors"]) * 100

            report.append("【最頻発エラー】")

            report.append(f"  タイプ: {most_common_type}")

            report.append(f"  発生件数: {count}件 ({percentage:.1f}%)")

            report.append("")

            # 再発防止策

            suggestions = self.suggest_preventions(trends)

            if suggestions:

                report.append("【推奨される対策】")

                for suggestion in suggestions:

                    report.append(f"  {suggestion}")

                report.append("")

        report.append("=" * 70)

        return "\n".join(report)


class ErrorHandler:
    """エラーハンドリング用クラス（RCA対応版）"""

    def __init__(self, error_analyzer: ErrorAnalyzer = None):

        self.error_log = []

        self.error_analyzer = error_analyzer

        self.rca_engine = RCAEngine(error_analyzer) if error_analyzer else None

    def log_error(self, phase: str, error: Exception, context: dict = None):
        """エラーをログに記録"""

        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        }

        self.error_log.append(error_entry)

        print(f"❌ [{phase}] {type(error).__name__}: {error}")

    async def record_task_error(self, task_id: str, error: Exception, task_name: str = ""):
        """タスクエラーを error_analysis に記録"""

        if not self.error_analyzer:

            return

        try:

            error_type = self.error_analyzer.classify_error(str(error))

            spreadsheet = self.error_analyzer.sheets_manager.gc.open_by_key(
                self.error_analyzer.spreadsheet_id
            )

            worksheet = spreadsheet.worksheet("error_analysis")

            all_values = worksheet.get_all_values()

            next_error_id = len(all_values)

            new_row = [
                str(next_error_id),
                str(task_id),
                error_type,
                "medium",
                str(error)[:500],
                "",
                "1",
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                "open",
                "",
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                f"Task: {task_name}",
                "medium",
            ]

            worksheet.append_rows(new_row)

            print(f"  📝 エラー記録: error_id={next_error_id}, type={error_type}")

        except Exception as e:

            print(f"  ⚠️ エラー記録失敗: {e}")

    def run_rca(self) -> Dict[str, Any]:
        """RCA分析を実行"""

        if not self.rca_engine:

            return {}

        trends = self.rca_engine.analyze_error_trends(days=7)

        if trends["total_errors"] > 0:

            report = self.rca_engine.generate_rca_report(trends)

            print("\n" + report)

        return trends

    def get_summary(self):
        """エラーサマリーを取得"""

        if not self.error_log:

            return "✅ エラーなし"

        summary = f"⚠️ {len(self.error_log)}件のエラー:\n"

        for i, error in enumerate(self.error_log[:5], 1):

            summary += f"  {i}. [{error['phase']}] {error['error_type']}\n"

        return summary


async def retry_async(func, max_retries=3, delay=2):
    """非同期関数のリトライ実行"""

    for attempt in range(max_retries):

        try:

            return await func()

        except Exception:

            if attempt < max_retries - 1:

                await asyncio.sleep(delay)

            else:

                raise


def get_all_active_goals(sheets_manager, spreadsheet_id):
    """アクティブなゴールを取得"""

    spreadsheet = sheets_manager.gc.open_by_key(spreadsheet_id)

    worksheet = spreadsheet.worksheet("project_goal")

    all_values = worksheet.get_all_values()

    if len(all_values) < 2:

        return []

    headers = all_values[0]

    valid_headers = {}

    for i, header in enumerate(headers):

        if header and header.strip():

            valid_headers[i] = header.strip()

    result = []

    for row_values in all_values[1:]:

        row_dict = {}

        for col_idx, header_name in valid_headers.items():

            if col_idx < len(row_values):

                row_dict[header_name] = row_values[col_idx]

            else:

                row_dict[header_name] = ""

        if any(row_dict.values()):

            goal_id = row_dict.get("goal_id")

            status = row_dict.get("status", "").lower()

            goal_desc = row_dict.get("goal_description", "")

            if goal_id and status in ["planning", "active"] and goal_desc:

                result.append(row_dict)

    return result


def get_pending_tasks(sheets_manager, spreadsheet_id, goal_id=None, max_tasks=10):
    """pendingタスクを取得（完全書き直し版）"""
    try:
        # スプレッドシートからタスク取得
        spreadsheet = sheets_manager.gc.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet("pm_tasks")
        all_values = worksheet.get_all_values()

        if len(all_values) < 2:
            print("⚠️ タスクが見つかりません")
            return []

        headers = all_values[0]
        tasks = []  # ← 初期化！

        # ヘッダーのインデックスマップ作成
        header_map = {}
        for i, header in enumerate(headers):
            if header and header.strip():
                header_map[i] = header.strip()

        print(f"📋 {len(all_values)-1}行のタスクをスキャン中...")

        # 各行を処理
        for row_values in all_values[1:]:
            if not any(row_values):  # 空行スキップ
                continue

            # 行データを辞書に変換
            row_dict = {}
            for col_idx, header_name in header_map.items():
                if col_idx < len(row_values):
                    row_dict[header_name] = row_values[col_idx]
                else:
                    row_dict[header_name] = ""

            # pending状態のみ抽出
            status = row_dict.get("status", "").lower()

            if status == "pending":
                task_goal_id = row_dict.get("parent_goal_id", "")

                # goal_id指定がある場合はフィルタ
                if goal_id is None or str(task_goal_id) == str(goal_id):
                    tasks.append(row_dict)

                    # max_tasks に達したら終了
                    if len(tasks) >= max_tasks:
                        break

        print(f"✅ {len(tasks)}件のpendingタスクを取得")
        return tasks

    except Exception as e:
        print(f"❌ get_pending_tasks エラー: {e}")
        import traceback

        traceback.print_exc()
        return []

    spreadsheet = sheets_manager.gc.open_by_key(spreadsheet_id)

    worksheet = spreadsheet.worksheet("pm_tasks")

    all_values = worksheet.get_all_values()

    if len(all_values) < 2:

        return []

    headers = all_values[0]

    valid_headers = {}

    for i, header in enumerate(headers):

        if header and header.strip():

            valid_headers[i] = header.strip()

    for row_values in all_values[1:]:

        row_dict = {}

        for col_idx, header_name in valid_headers.items():

            if col_idx < len(row_values):

                row_dict[header_name] = row_values[col_idx]

            else:

                row_dict[header_name] = ""

        if any(row_dict.values()):

            status = row_dict.get("status", "").lower()

            task_goal_id = row_dict.get("goal_id")

            if status == "pending":

                if goal_id is None or str(task_goal_id) == str(goal_id):

                    task_name = (
                        row_dict.get("title")
                        or row_dict.get("task_name")
                        or row_dict.get("description", "")[:50]
                        or "Untitled Task"
                    )

                    row_dict["_display_name"] = task_name

                    tasks.append(row_dict)

                    if len(tasks) >= max_tasks:

                        break

    return tasks


async def process_goal(
    goal: Dict[str, Any],
    task_breakdown: GeminiTaskBreakdownAgent,
    task_registration: TaskRegistrationAgent,
    task_exporter: TaskExportAgent,
    error_handler: ErrorHandler,
) -> Dict[str, Any]:
    """1つのゴールを処理"""

    goal_id = goal["goal_id"]

    goal_title = goal.get("title", f"目標{goal_id}")

    goal_description = goal.get("goal_description", "")

    result = {"goal_id": goal_id, "tasks_generated": 0, "tasks_registered": 0, "success": False}

    try:

        print(f"\n🎯 目標{goal_id}を処理中...")

        if not goal_description or goal_description.strip() == "":

            goal_description = f"{goal_title}を達成するためのタスクを実行する"

        generated_tasks = await retry_async(
            lambda: task_breakdown.generate_tasks_for_goal(
                goal_id=goal_id, goal_title=goal_title, goal_description=goal_description
            ),
            max_retries=2,
            delay=5,
        )

        if not generated_tasks:

            return result

        result["tasks_generated"] = len(generated_tasks)

        print(f"✅ 目標{goal_id}: {len(generated_tasks)}個のタスクを生成")

        export_path = task_exporter.export_tasks(
            goal_id=goal_id, goal_title=goal_title, tasks=generated_tasks
        )

        registered_count = await task_registration.register_tasks(
            goal_id=goal_id, tasks=generated_tasks, detail_file_path=export_path
        )

        result["tasks_registered"] = registered_count

        result["success"] = True

        print(f"✅ 目標{goal_id}: {registered_count}個のタスクを登録")

    except Exception as e:

        error_handler.log_error(f"Goal {goal_id}", e, {"goal_id": goal_id})

    return result


async def execute_task_with_timeout(
    task: Dict[str, Any], browser: BrowserController, error_handler: ErrorHandler, timeout: int = 60
) -> Dict[str, Any]:
    """タイムアウト付きタスク実行"""

    task_id = task.get("task_id", "Unknown")

    task_name = task.get("_display_name", "Untitled Task")

    description = task.get("description", "")

    try:

        prompt = f"""以下のタスクを実行してください：



タスク名: {task_name}

説明: {description}



実行結果を簡潔に報告してください。"""

        await asyncio.wait_for(browser.send_prompt(prompt), timeout=timeout)

        await asyncio.sleep(3)

        response = await asyncio.wait_for(browser.extract_latest_text_response(), timeout=timeout)

        if response:

            return {"task_id": task_id, "success": True, "response": response}

        else:

            error = Exception("No response from Gemini")

            await error_handler.record_task_error(task_id, error, task_name)

            return {"task_id": task_id, "success": False, "error": "No response"}

    except asyncio.TimeoutError as e:

        await error_handler.record_task_error(task_id, e, task_name)

        return {"task_id": task_id, "success": False, "error": f"Timeout {timeout}s"}

    except Exception as e:

        await error_handler.record_task_error(task_id, e, task_name)

        return {"task_id": task_id, "success": False, "error": str(e)}


async def execute_tasks_parallel(
    tasks: List[Dict[str, Any]],
    browser: BrowserController,
    error_handler: ErrorHandler,
    max_concurrent: int = 3,
) -> List[Dict[str, Any]]:
    """タスクを並列実行"""

    semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_with_semaphore(task):

        async with semaphore:

            task_id = task.get("task_id", "Unknown")

            task_name = task.get("_display_name", "Untitled")

            print(f"  🔄 タスク#{task_id}: {task_name[:30]}...")

            result = await retry_async(
                lambda: execute_task_with_timeout(task, browser, error_handler, timeout=60),
                max_retries=2,
                delay=3,
            )

            status = "✅" if result.get("success") else "❌"

            print(f"  {status} タスク#{task_id} 完了")

            return result

    results = await asyncio.gather(
        *[execute_with_semaphore(task) for task in tasks], return_exceptions=True
    )

    processed_results = []

    for i, result in enumerate(results):

        if isinstance(result, Exception):

            task = tasks[i]

            task_id = task.get("task_id", "Unknown")

            task_name = task.get("_display_name", "Untitled")

            await error_handler.record_task_error(task_id, result, task_name)

            processed_results.append({"task_id": task_id, "success": False, "error": str(result)})

        else:

            processed_results.append(result)

    return processed_results


async def main():
    """メイン実行関数"""

    print("=" * 70)

    print("🤖 PM Agent 完全自動化システム（RCA統合版）")

    print("=" * 70)

    print(f"開始日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print()

    stats = {
        "goals_processed": 0,
        "tasks_generated": 0,
        "tasks_registered": 0,
        "tasks_executed": 0,
        "tasks_succeeded": 0,
        "tasks_failed": 0,
        "errors_recorded": 0,
    }

    browser = None

    try:

        print("【初期化】")

        print("-" * 70)

        config = ConfigLoader()

        spreadsheet_id = config.get("SPREADSHEET_ID")

        service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")

        sheets_manager = GoogleSheetsManager(spreadsheet_id, service_account_file)

        print("✅ Google Sheets接続成功")

        error_analyzer = ErrorAnalyzer(sheets_manager)

        error_handler = ErrorHandler(error_analyzer)

        print("✅ エラー分析エンジン初期化完了")

        print("✅ RCAエンジン初期化完了")

        browser = BrowserController()

        await retry_async(lambda: browser.setup_browser(), max_retries=3, delay=5)

        await retry_async(lambda: browser.navigate_to_gemini(), max_retries=3, delay=5)

        print("✅ Gemini準備完了")

        print()

        task_breakdown = GeminiTaskBreakdownAgent()

        task_registration = TaskRegistrationAgent(sheets_manager)

        task_exporter = TaskExportAgent()

        # Phase 1-3

        print("【Phase 1-3】ゴール処理")

        print("-" * 70)

        active_goals = get_all_active_goals(sheets_manager, spreadsheet_id)

        if not active_goals:

            print("⚠️ アクティブなゴールがありません")

            return

        print(f"✅ {len(active_goals)}個のアクティブなゴールを検出")

        goal_results = await asyncio.gather(
            *[
                process_goal(goal, task_breakdown, task_registration, task_exporter, error_handler)
                for goal in active_goals[:3]
            ],
            return_exceptions=True,
        )

        for result in goal_results:

            if isinstance(result, Exception):

                continue

            if result.get("success"):

                stats["goals_processed"] += 1

                stats["tasks_generated"] += result.get("tasks_generated", 0)

                stats["tasks_registered"] += result.get("tasks_registered", 0)

        print(f"\n✅ Phase 1-3 完了: {stats['goals_processed']}個のゴールを処理")

        # Phase 4

        print()

        print("【Phase 4】タスク実行")

        print("-" * 70)

        pending_tasks = get_pending_tasks(sheets_manager, spreadsheet_id, max_tasks=6)

        if not pending_tasks:

            print("⚠️ 実行可能なタスクがありません")

        else:

            print(f"✅ {len(pending_tasks)}個のpendingタスクを取得")

            print(f"📊 並列実行（最大3タスク同時）")

            print()

            task_results = await execute_tasks_parallel(
                pending_tasks, browser, error_handler, max_concurrent=3
            )

            for result in task_results:

                stats["tasks_executed"] += 1

                if result.get("success"):

                    stats["tasks_succeeded"] += 1

                else:

                    stats["tasks_failed"] += 1

        # Phase 5: エラー分析 + RCA

        print()

        print("【Phase 5】エラー分析とRCA")

        print("-" * 70)

        if stats["tasks_failed"] > 0:

            stats["errors_recorded"] = len(error_handler.error_log)

            print(f"✅ {stats['errors_recorded']}件のエラーを記録")

        # RCA実行

        rca_trends = error_handler.run_rca()

        # サマリー

        print()

        print("=" * 70)

        print("📊 実行結果サマリー")

        print("=" * 70)

        print(f"処理したゴール: {stats['goals_processed']}個")

        print(f"生成したタスク: {stats['tasks_generated']}個")

        print(f"登録したタスク: {stats['tasks_registered']}個")

        print(f"実行したタスク: {stats['tasks_executed']}個")

        print(f"  成功: {stats['tasks_succeeded']}個")

        print(f"  失敗: {stats['tasks_failed']}個")

        print(f"記録したエラー: {stats['errors_recorded']}個")

        if rca_trends.get("total_errors", 0) > 0:

            print(f"\n🔍 RCA分析: {rca_trends['total_errors']}件のエラーを分析")

        print()

        print(error_handler.get_summary())

        print("=" * 70)

    except Exception as e:

        if "error_handler" in locals():

            error_handler.log_error("System", e)

        print(f"❌ システムエラー: {e}")

        traceback.print_exc()

    finally:

        if browser:

            print("\n🧹 ブラウザをクリーンアップ中...")

            try:

                await browser.cleanup()

                print("✅ クリーンアップ完了")

            except Exception as e:

                print(f"⚠️ クリーンアップエラー: {e}")


if __name__ == "__main__":

    asyncio.run(main())

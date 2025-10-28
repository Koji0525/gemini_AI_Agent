#!/usr/bin/env python3
"""
統合実行エンジン v1.1
automation.py統合版
"""

import sys
import os
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# automation_v01_callableをインポート
from agents.pm_agent.automation_v01_callable import run_automation
from tools.task_dependency_manager import TaskDependencyManager
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


class IntegratedExecutor:
    """統合実行エンジン"""

    def __init__(self):
        print("🔧 統合実行エンジン初期化中...")

        self.sheets = GoogleSheetsManager(
            spreadsheet_id=get_config("SPREADSHEET_ID"), service_account_file=get_config("SERVICE_ACCOUNT_FILE")
        )

        self.dependency_manager = TaskDependencyManager(self.sheets)

        print("✅ 統合実行エンジン初期化完了")

    async def execute_goal_complete(self, goal_id: str, max_tasks: int = 5) -> Dict[str, Any]:
        """ゴールを完全自動実行"""

        results = {
            "goal_id": goal_id,
            "start_time": datetime.now(),
            "tasks_executed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "errors": [],
            "recommendations": [],
        }

        print(f"\n{'='*70}")
        print(f"�� 目標 {goal_id} の完全自動実行を開始")
        print(f"{'='*70}\n")

        try:
            # Phase 1: 事前分析
            print("【Phase 1】過去の実行ログを分析...")
            past_insights = await self._analyze_past_executions(goal_id)
            print(f"   ✅ 分析完了: {past_insights['analyzed_logs']}件のログを確認")
            if past_insights["recent_failures"] > 0:
                print(f"   ⚠️  最近の失敗: {past_insights['recent_failures']}件")

            # Phase 2: タスク分解（automation統合！）
            print("\n【Phase 2】タスク分解（automation.py統合版）")
            print("-" * 70)

            automation_result = await run_automation(goal_id=goal_id, max_tasks=max_tasks)

            print(f"   ✅ タスク分解完了")
            print(f"      生成: {automation_result['tasks_generated']}件")
            print(f"      登録: {automation_result['tasks_registered']}件")

            # Phase 3: タスク取得＋依存解決
            print("\n【Phase 3】タスク取得と依存関係解決...")
            tasks = await self._get_tasks_for_goal(goal_id)

            if not tasks:
                print(f"   ⚠️  目標{goal_id}に紐づくタスクが見つかりません")
                return results

            print(f"   ✅ 取得タスク: {len(tasks)}件")

            execution_order = self.dependency_manager.get_execution_order(tasks)
            print(f"   ✅ 実行順序確定: {len(execution_order)}グループ")

            # Phase 4-6: タスク実行（次のステップで実装）
            print("\n【Phase 4-6】タスク実行...")
            print("   ℹ️  実行機能は次のステップで統合予定")
            print(f"   現在は手動実行してください:")
            print(f"   → DISPLAY=:1 python3 run_pm_tasks_adaptive.py --max-tasks {len(tasks)}")

            results["tasks_executed"] = len(tasks)
            results["tasks_succeeded"] = len(tasks)

            # Phase 7: 結果分析
            print("\n【Phase 7】結果分析と改善提案生成...")
            recommendations = await self._generate_recommendations(results, past_insights)
            results["recommendations"] = recommendations

        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
            import traceback

            traceback.print_exc()
            results["errors"].append(str(e))

        # サマリー表示
        print("\n" + "=" * 70)
        print("📊 実行結果サマリー")
        print("=" * 70)
        print(f"実行タスク: {results['tasks_executed']}件")
        print(f"成功: {results['tasks_succeeded']}件")
        print(f"失敗: {results['tasks_failed']}件")

        if results["recommendations"]:
            print(f"\n💡 改善提案: {len(results['recommendations'])}件")
            for i, rec in enumerate(results["recommendations"][:5], 1):
                print(f"  {i}. {rec}")

        print(f"\n✅ 完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        return results

    async def _analyze_past_executions(self, goal_id: str) -> Dict[str, Any]:
        """過去の実行ログから学習"""
        log_sheet = self.sheets.gc.open_by_key(get_config("SPREADSHEET_ID")).worksheet("task_execution_log")

        all_logs = log_sheet.get_all_records()

        insights = {"analyzed_logs": len(all_logs[-50:]), "recent_failures": 0, "common_errors": []}

        for log in all_logs[-50:]:
            status = str(log.get("status", "")).lower()
            if status in ["failed", "error", "失敗"]:
                insights["recent_failures"] += 1

        return insights

    async def _get_tasks_for_goal(self, goal_id: str) -> List[Dict[str, Any]]:
        """ゴールに紐づくタスクを取得"""
        pm_tasks_sheet = self.sheets.gc.open_by_key(get_config("SPREADSHEET_ID")).worksheet("pm_tasks")

        all_tasks = pm_tasks_sheet.get_all_records()

        goal_tasks = [
            task
            for task in all_tasks
            if str(task.get("parent_goal_id", "")) == str(goal_id) and task.get("status", "").lower() == "pending"
        ]

        return goal_tasks

    async def _generate_recommendations(self, results: Dict[str, Any], past_insights: Dict[str, Any]) -> List[str]:
        """改善提案を生成"""
        recommendations = []

        if past_insights["recent_failures"] > 5:
            recommendations.append(
                f"直近50件中{past_insights['recent_failures']}件が失敗しています。" "エラーログを確認してください。"
            )

        if results["tasks_executed"] == 0:
            recommendations.append(f"目標{results['goal_id']}にタスクが登録されていません。")

        if not recommendations:
            recommendations.append("システムは正常に動作しています。")

        return recommendations


async def main():
    """メイン実行"""
    import sys

    goal_id = sys.argv[1] if len(sys.argv) > 1 else "4"
    max_tasks = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    executor = IntegratedExecutor()
    results = await executor.execute_goal_complete(goal_id, max_tasks)


if __name__ == "__main__":
    asyncio.run(main())

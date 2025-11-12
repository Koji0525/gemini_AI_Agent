"""
システム自動診断ツール
全シートの構造とデータ整合性をチェック
"""

import sys

sys.path.insert(0, ".")

from typing import Any, Dict, List

from tools.base_data_accessor import BaseDataAccessor


class SystemDiagnostics:
    """システム自動診断"""

    REQUIRED_SHEETS = ["project_goal", "pm_tasks", "task_execution_log", "quality_feedback"]

    REQUIRED_COLUMNS = {
        "project_goal": ["goal_id", "goal_description", "status"],
        "pm_tasks": ["task_id", "parent_goal_id", "status", "description"],
    }

    def __init__(self):
        self.accessor = BaseDataAccessor()

    def diagnose_all_sheets(self) -> List[Dict[str, Any]]:
        """全シート診断"""
        results = []

        print("\n" + "=" * 80)
        print("🔍 システム診断開始")
        print("=" * 80 + "\n")

        for sheet_name in self.REQUIRED_SHEETS:
            print(f"📋 {sheet_name}")

            diagnosis = self.accessor.diagnose_sheet_structure(sheet_name)

            # 必須列チェック
            if sheet_name in self.REQUIRED_COLUMNS:
                required_cols = self.REQUIRED_COLUMNS[sheet_name]
                existing_cols = diagnosis.get("columns", [])

                missing_cols = [col for col in required_cols if col not in existing_cols]

                if missing_cols:
                    diagnosis["missing_columns"] = missing_cols
                    diagnosis["status"] = "warning"
                    print(f"  ⚠️ 不足列: {missing_cols}")
                else:
                    print(f"  ✅ 必須列: すべて存在")

            if diagnosis["status"] == "ok":
                print(f"  ✅ ステータス: 正常")
                print(f"  📊 列数: {diagnosis['column_count']}")
                print(f"  📈 データ行数: {diagnosis['data_row_count']}")
            else:
                print(f"  ❌ ステータス: エラー")
                if "error" in diagnosis:
                    print(f"  エラー: {diagnosis['error']}")

            print()
            results.append(diagnosis)

        # サマリー
        print("=" * 80)
        ok_count = sum(1 for r in results if r["status"] == "ok")
        print(f"📊 診断サマリー: {ok_count}/{len(results)} シート正常")
        print("=" * 80 + "\n")

        return results

    def check_data_consistency(self) -> Dict[str, Any]:
        """データ整合性チェック"""
        print("\n" + "=" * 80)
        print("🔍 データ整合性チェック")
        print("=" * 80 + "\n")

        issues = []

        # 1. active/pending ゴールの存在確認
        print("1️⃣ active/pending ゴールの確認")
        goals = self.accessor.read_sheet_as_dicts(
            "project_goal",
            filter_func=lambda g: g.get("status", "").lower() in ["active", "pending"],
        )
        print(f"   active/pending ゴール: {len(goals)}件")
        if len(goals) == 0:
            issues.append("active/pending ゴールが存在しません")
            print("   ⚠️ active/pending ゴールが存在しません")
        else:
            for goal in goals:
                print(f"   ✅ {goal.get('goal_id')} - {goal.get('status')}")

        # 2. pending タスクの存在確認
        print("\n2️⃣ pending タスクの確認")
        tasks = self.accessor.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("status", "").lower() == "pending"
        )
        print(f"   pending タスク: {len(tasks)}件")
        if len(tasks) == 0:
            print("   ℹ️ pending タスクはありません")
        else:
            for task in tasks[:5]:
                print(f"   ✅ {task.get('task_id')} - {task.get('description', '')[:50]}...")

        # 3. 孤児タスクチェック（親ゴールが存在しないタスク）
        print("\n3️⃣ 孤児タスクチェック")
        all_goals = self.accessor.read_sheet_as_dicts("project_goal")
        all_tasks = self.accessor.read_sheet_as_dicts("pm_tasks")

        goal_ids = {g.get("goal_id") for g in all_goals}
        orphan_tasks = [
            t
            for t in all_tasks
            if t.get("parent_goal_id") and t.get("parent_goal_id") not in goal_ids
        ]

        print(f"   孤児タスク: {len(orphan_tasks)}件")
        if len(orphan_tasks) > 0:
            issues.append(f"孤児タスクが{len(orphan_tasks)}件存在")
            for task in orphan_tasks[:3]:
                print(f"   ⚠️ {task.get('task_id')} - parent: {task.get('parent_goal_id')}")
        else:
            print("   ✅ 孤児タスクなし")

        print("\n" + "=" * 80)
        if len(issues) == 0:
            print("✅ データ整合性: 問題なし")
        else:
            print(f"⚠️ データ整合性: {len(issues)}件の問題")
            for issue in issues:
                print(f"  • {issue}")
        print("=" * 80 + "\n")

        return {
            "active_goals": len(goals),
            "pending_tasks": len(tasks),
            "orphan_tasks": len(orphan_tasks),
            "issues": issues,
            "status": "ok" if len(issues) == 0 else "warning",
        }


def main():
    diagnostics = SystemDiagnostics()

    # 全シート診断
    sheet_results = diagnostics.diagnose_all_sheets()

    # データ整合性チェック
    consistency_results = diagnostics.check_data_consistency()

    # 総合判定
    all_ok = all(r["status"] == "ok" for r in sheet_results)
    consistency_ok = consistency_results["status"] == "ok"

    print("\n" + "=" * 80)
    print("🎯 総合判定")
    print("=" * 80)
    if all_ok and consistency_ok:
        print("✅ システム正常 - 24時間稼働可能")
    else:
        print("⚠️ 問題あり - 修正が必要")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

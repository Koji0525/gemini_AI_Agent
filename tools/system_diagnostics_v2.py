"""
システム自動診断ツール v2
オプションシート対応版
"""

import sys

sys.path.insert(0, ".")

from typing import Any, Dict, List

from tools.base_data_accessor import BaseDataAccessor


class SystemDiagnosticsV2:
    """システム自動診断 v2"""

    REQUIRED_SHEETS = ["project_goal", "pm_tasks", "task_execution_log"]

    OPTIONAL_SHEETS = ["quality_feedback", "knowledge_base", "error_log"]

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

        # 必須シート
        print("【必須シート】")
        for sheet_name in self.REQUIRED_SHEETS:
            print(f"📋 {sheet_name}")
            diagnosis = self.accessor.diagnose_sheet_structure(sheet_name)
            self._print_diagnosis(sheet_name, diagnosis, required=True)
            results.append(diagnosis)

        # オプションシート
        print("\n【オプションシート】")
        for sheet_name in self.OPTIONAL_SHEETS:
            print(f"📋 {sheet_name}")
            diagnosis = self.accessor.diagnose_sheet_structure(sheet_name)
            if diagnosis["status"] == "error":
                print(f"  ℹ️ スキップ（オプション）")
            else:
                self._print_diagnosis(sheet_name, diagnosis, required=False)
            results.append(diagnosis)

        # サマリー
        print("\n" + "=" * 80)
        required_ok = sum(1 for r in results[: len(self.REQUIRED_SHEETS)] if r["status"] == "ok")
        print(f"📊 診断サマリー: {required_ok}/{len(self.REQUIRED_SHEETS)} 必須シート正常")
        print("=" * 80 + "\n")

        return results

    def _print_diagnosis(self, sheet_name: str, diagnosis: Dict, required: bool):
        """診断結果表示"""
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
        elif diagnosis["status"] == "warning":
            print(f"  ⚠️ ステータス: 警告")
        else:
            if required:
                print(f"  ❌ ステータス: エラー")
                if "error" in diagnosis:
                    print(f"  エラー: {diagnosis['error']}")

        print()

    def check_data_consistency(self) -> Dict[str, Any]:
        """データ整合性チェック"""
        print("\n" + "=" * 80)
        print("🔍 データ整合性チェック")
        print("=" * 80 + "\n")

        issues = []

        # 1. active/pending ゴールの確認
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
                print(
                    f"   ✅ {goal.get('goal_id')} - {goal.get('status')} - {goal.get('goal_description', '')[:50]}..."
                )

        # 2. 各ゴールのタスク数
        print("\n2️⃣ 各ゴールのタスク数")
        all_goals = self.accessor.read_sheet_as_dicts("project_goal")
        all_tasks = self.accessor.read_sheet_as_dicts("pm_tasks")

        for goal in goals:
            goal_id = goal.get("goal_id")
            goal_tasks = [t for t in all_tasks if t.get("parent_goal_id") == goal_id]
            pending_tasks = [t for t in goal_tasks if t.get("status", "").lower() == "pending"]

            print(
                f"   ゴール {goal_id}: タスク {len(goal_tasks)}件（pending: {len(pending_tasks)}件）"
            )

            if len(goal_tasks) == 0:
                issues.append(f"ゴール{goal_id}にタスクが存在しません")
                print(f"     ⚠️ タスクなし - タスク分解が必要")

        # 3. pending タスクの確認
        print("\n3️⃣ pending タスクの確認")
        pending_tasks = self.accessor.read_sheet_as_dicts(
            "pm_tasks", filter_func=lambda t: t.get("status", "").lower() == "pending"
        )
        print(f"   pending タスク: {len(pending_tasks)}件")
        if len(pending_tasks) == 0:
            print("   ℹ️ pending タスクはありません")
        else:
            for task in pending_tasks[:5]:
                print(f"   ✅ {task.get('task_id')} - {task.get('description', '')[:50]}...")

        # 4. 孤児タスクチェック
        print("\n4️⃣ 孤児タスクチェック")
        goal_ids = {g.get("goal_id") for g in all_goals}
        orphan_tasks = [
            t
            for t in all_tasks
            if t.get("parent_goal_id") and t.get("parent_goal_id") not in goal_ids
        ]

        print(f"   孤児タスク: {len(orphan_tasks)}件")
        if len(orphan_tasks) > 0:
            print(f"   ℹ️ 古いゴールのタスク（削除推奨）")
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
            "pending_tasks": len(pending_tasks),
            "orphan_tasks": len(orphan_tasks),
            "issues": issues,
            "status": "ok" if len(issues) == 0 else "warning",
        }


def main():
    diagnostics = SystemDiagnosticsV2()

    # 全シート診断
    sheet_results = diagnostics.diagnose_all_sheets()

    # データ整合性チェック
    consistency_results = diagnostics.check_data_consistency()

    # 総合判定
    required_ok = all(
        r["status"] == "ok" for r in sheet_results[: len(diagnostics.REQUIRED_SHEETS)]
    )

    print("\n" + "=" * 80)
    print("🎯 総合判定")
    print("=" * 80)
    if required_ok:
        print("✅ 必須シート正常")
        if consistency_results["issues"]:
            print(f"⚠️ {len(consistency_results['issues'])}件の推奨事項あり")
    else:
        print("❌ 必須シートにエラーあり")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

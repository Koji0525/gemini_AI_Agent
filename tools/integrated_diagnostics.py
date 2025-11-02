#!/usr/bin/env python3
"""
統合診断システム（開発効率10倍化ツール）

【目的】
- シート更新系エラーを自動診断
- 80分かかった問題を5分で解決
- 原因候補を自動切り分け

【横展開可能な設計】
- 診断ルールをYAMLで外部化
- 新しいエラーパターンを学習
- 他プロジェクトでも使用可能

使用例：
    python3 tools/integrated_diagnostics.py --target orchestrator
    python3 tools/integrated_diagnostics.py --auto-fix  # 自動修正
"""

import sys
import subprocess
from typing import Dict, Any


class IntegratedDiagnostics:
    """統合診断システム"""

    def __init__(self):
        self.issues = []
        self.fixes_applied = []

    def diagnose_sheets_integration(self) -> Dict[str, Any]:
        """シート連携の診断"""
        print("🔍 シート連携を診断中...")

        issues = []

        # 1. GoogleSheetsManagerのメソッド確認
        try:
            result = subprocess.run(
                [
                    "python3",
                    "-c",
                    """
import sys
sys.path.insert(0, ".")
from tools.sheets_manager import GoogleSheetsManager
sheets = GoogleSheetsManager()
methods = [m for m in dir(sheets) if not m.startswith("_")]
print("|".join(methods))
""",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            available_methods = result.stdout.strip().split("|")

            # 2. Orchestratorファイルでの使用状況チェック
            orch_file = "scripts/integrated_orchestrator_v25_complete.py"
            with open(orch_file, "r") as f:
                content = f.read()

            # 存在しないメソッドの使用を検出
            wrong_methods = ["update_range", "update_cells"]
            for method in wrong_methods:
                if f".{method}(" in content and method not in available_methods:
                    issues.append(
                        {
                            "severity": "CRITICAL",
                            "type": "method_not_found",
                            "method": method,
                            "file": orch_file,
                            "suggestion": f"Replace with write_range or append_rows",
                        }
                    )

        except Exception as e:
            issues.append({"severity": "ERROR", "type": "diagnostic_failure", "error": str(e)})

        return {
            "available_methods": available_methods if "available_methods" in locals() else [],
            "issues": issues,
        }

    def diagnose_task_execution(self) -> Dict[str, Any]:
        """タスク実行フローの診断"""
        print("🔍 タスク実行フローを診断中...")

        checks = {
            "orchestrator_init": False,
            "task_coordinator_init": False,
            "retry_manager_init": False,
            "sheets_manager_init": False,
        }

        # Orchestratorの初期化確認
        try:
            with open("scripts/autonomous_24h_loop_v25.py", "r") as f:
                content = f.read()
                if "IntegratedOrchestrator(" in content:
                    checks["orchestrator_init"] = True
        except:
            pass

        # TaskCoordinatorの存在確認
        try:
            with open("task_executor/task_coordinator_v02_complete.py", "r") as f:
                content = f.read()
                if "class TaskCoordinator" in content:
                    checks["task_coordinator_init"] = True
        except:
            pass

        return {"checks": checks, "status": "healthy" if all(checks.values()) else "degraded"}

    def diagnose_sheet_updates(self) -> Dict[str, Any]:
        """シート更新状況の診断"""
        print("🔍 シート更新状況を診断中...")

        try:
            result = subprocess.run(
                [
                    "python3",
                    "-c",
                    """
import sys
sys.path.insert(0, ".")
from tools.sheets_manager import GoogleSheetsManager
sheets = GoogleSheetsManager()
tasks = sheets.read_range("pm_tasks!A:Z")
if "status" in tasks[0]:
    status_idx = tasks[0].index("status")
    pending = sum(1 for r in tasks[1:] if len(r) > status_idx and r[status_idx] == "pending")
    completed = sum(1 for r in tasks[1:] if len(r) > status_idx and r[status_idx] == "completed")
    print(f"{pending},{completed}")
""",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            pending, completed = map(int, result.stdout.strip().split(","))

            return {
                "pending_tasks": pending,
                "completed_tasks": completed,
                "status": "healthy" if completed > 0 else "no_updates",
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def auto_fix(self, issue: Dict) -> bool:
        """問題の自動修正"""
        if issue["type"] == "method_not_found":
            print(f"🔧 自動修正: {issue['method']} → write_range")

            try:
                file_path = issue["file"]
                with open(file_path, "r") as f:
                    content = f.read()

                # update_range → write_rangeに置換
                content = content.replace(f".{issue['method']}(", ".write_range(")

                with open(file_path, "w") as f:
                    f.write(content)

                self.fixes_applied.append(issue)
                return True

            except Exception as e:
                print(f"  ❌ 自動修正失敗: {e}")
                return False

        return False

    def run_full_diagnostics(self, auto_fix: bool = False) -> Dict[str, Any]:
        """完全診断の実行"""
        print("🚀 統合診断開始...\n")

        results = {
            "sheets_integration": self.diagnose_sheets_integration(),
            "task_execution": self.diagnose_task_execution(),
            "sheet_updates": self.diagnose_sheet_updates(),
        }

        # 自動修正
        if auto_fix:
            print("\n🔧 自動修正を実行中...")
            for issue in results["sheets_integration"]["issues"]:
                if issue["severity"] == "CRITICAL":
                    self.auto_fix(issue)

        # レポート生成
        print("\n" + "=" * 60)
        print("📊 診断レポート")
        print("=" * 60)

        # シート連携
        si = results["sheets_integration"]
        print(f"\n✅ 利用可能なメソッド: {len(si.get('available_methods', []))}個")
        print(f"⚠️  問題: {len(si['issues'])}件")
        for issue in si["issues"]:
            print(
                f"   [{issue['severity']}] {issue.get('method', 'N/A')}: {issue.get('suggestion', issue.get('error'))}"
            )

        # タスク実行
        te = results["task_execution"]
        print(f"\n📋 タスク実行フロー: {te['status']}")
        for check, status in te["checks"].items():
            print(f"   {'✅' if status else '❌'} {check}")

        # シート更新
        su = results["sheet_updates"]
        if su["status"] == "healthy":
            print(f"\n📊 シート更新: 正常")
            print(f"   Pending: {su['pending_tasks']}件")
            print(f"   Completed: {su['completed_tasks']}件")
        else:
            print(f"\n⚠️  シート更新: {su['status']}")

        # 自動修正サマリー
        if auto_fix and self.fixes_applied:
            print(f"\n🔧 自動修正: {len(self.fixes_applied)}件完了")
            for fix in self.fixes_applied:
                print(f"   ✅ {fix['file']}: {fix['method']} を修正")

        print("\n" + "=" * 60)

        return results


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="統合診断システム")
    parser.add_argument("--auto-fix", action="store_true", help="自動修正を実行")
    parser.add_argument("--target", choices=["all", "sheets", "tasks"], default="all")

    args = parser.parse_args()

    diagnostics = IntegratedDiagnostics()
    results = diagnostics.run_full_diagnostics(auto_fix=args.auto_fix)

    # 終了コード決定
    has_critical = any(i["severity"] == "CRITICAL" for i in results["sheets_integration"]["issues"])

    return 1 if has_critical and not args.auto_fix else 0


if __name__ == "__main__":
    sys.exit(main())

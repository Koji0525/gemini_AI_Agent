#!/usr/bin/env python3
"""
システム自動診断ツール v2.0

開発ログ:
何が起きた: epic_orchestratorでインポートエラーが発生し、システム統合が失敗
原因: コンポーネント間の依存関係が複雑化し、インポートエラーや属性エラーが頻発
狙い（解決策）: 事前診断により問題を未然に防ぎ、修正提案を自動生成する
"""

import importlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# プロジェクトルート設定
PROJECT_ROOT = Path("/workspaces/gemini_AI_Agent")
if not PROJECT_ROOT.exists():
    PROJECT_ROOT = Path("/home/codespace/gemini_AI_Agent")
    if not PROJECT_ROOT.exists():
        PROJECT_ROOT = Path.cwd()

os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))


class SystemDiagnostics:
    """システム診断クラス"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "errors": [],
            "warnings": [],
            "suggestions": [],
        }
        self.critical_errors = []

    def check_environment(self) -> bool:
        """環境変数のチェック"""
        print("\n🔍 環境変数チェック")
        required_vars = ["GEMINI_API_KEY", "SPREADSHEET_ID", "WP_URL", "WP_USER", "WP_PASS"]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.results["errors"].append(f"環境変数不足: {', '.join(missing_vars)}")
            print(f"  ❌ 環境変数不足: {', '.join(missing_vars)}")
            self.results["suggestions"].append(
                f".envファイルに以下を追加: {', '.join(missing_vars)}"
            )
            return False
        else:
            print("  ✅ 全環境変数設定済み")
            self.results["checks"]["environment"] = "OK"
            return True

    def check_critical_imports(self) -> bool:
        """重要なインポートのチェック"""
        print("\n🔍 コアコンポーネントのインポートチェック")

        critical_modules = [
            ("agents.integrated.integrated_controller_fixed", "IntegratedControllerFixed"),
            ("agents.google_sheets_manager", "GoogleSheetsManager"),
            ("agents.task_executor", "TaskExecutor"),
            ("core_agents.pm_agent_v33_epic", "PMAgentV33Epic"),
            ("agents.integration.error_classifier", "ErrorClassifier"),
            ("agents.integration.self_repair_agent", "SelfRepairAgent"),
            ("agents.integration.progress_analyzer_v2", "ProgressAnalyzer"),
            ("knowledge_system.core_agents.knowledge_manager", "KnowledgeManager"),
            ("agents.observability.observability_manager", "ObservabilityManager"),
        ]

        import_errors = []
        import_success = []

        for module_path, class_name in critical_modules:
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, class_name):
                    import_success.append(f"{module_path}.{class_name}")
                    print(f"  ✅ {class_name}")
                else:
                    error_msg = f"{module_path}に{class_name}クラスが存在しません"
                    import_errors.append(error_msg)
                    print(f"  ❌ {error_msg}")

                    # 実際のクラス名を探す
                    actual_classes = [name for name in dir(module) if name[0].isupper()]
                    if actual_classes:
                        suggestion = f"{class_name} → {actual_classes[0]}を使用"
                        self.results["suggestions"].append(suggestion)

            except ImportError as e:
                error_msg = f"{module_path}: {str(e)}"
                import_errors.append(error_msg)
                print(f"  ❌ {error_msg}")

                # ImportErrorの詳細を解析して修正提案
                if "No module named" in str(e):
                    self.results["suggestions"].append(
                        f"モジュール{module_path}が存在しません。パスを確認してください"
                    )
                elif "cannot import name" in str(e):
                    match = re.search(r"cannot import name '(\w+)'", str(e))
                    if match:
                        wrong_name = match.group(1)
                        self.results["suggestions"].append(
                            f"{wrong_name}という名前は存在しません。正しいクラス名を確認してください"
                        )

        if import_errors:
            self.results["errors"].extend(import_errors)
            self.critical_errors.extend(import_errors)
            return False
        else:
            self.results["checks"]["imports"] = "OK"
            return True

    def check_file_structure(self) -> bool:
        """ファイル構造のチェック"""
        print("\n🔍 ファイル構造チェック")

        required_dirs = [
            "agents",
            "agents/integrated",
            "agents/integration",
            "agents/observability",
            "core_agents",
            "knowledge_system",
            "knowledge_system/core_agents",
            "scripts",
            "tests",
            "logs",
            "MD",
            "sh",
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            full_path = PROJECT_ROOT / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
                print(f"  ❌ ディレクトリ不足: {dir_path}")

        if missing_dirs:
            self.results["warnings"].append(f"ディレクトリ不足: {', '.join(missing_dirs)}")
            for dir_path in missing_dirs:
                self.results["suggestions"].append(f"mkdir -p {dir_path}")
            return False
        else:
            print("  ✅ 全必須ディレクトリ存在")
            self.results["checks"]["file_structure"] = "OK"
            return True

    def check_spreadsheet_connection(self) -> bool:
        """スプレッドシート接続のチェック"""
        print("\n🔍 スプレッドシート接続チェック")

        try:
            from agents.google_sheets_manager import GoogleSheetsManager

            sheets = GoogleSheetsManager()

            # 必須シートの存在確認
            required_sheets = ["project_goal", "pm_tasks", "task_execution_log"]
            sheet_status = {}

            for sheet_name in required_sheets:
                try:
                    data = sheets.read_sheet(sheet_name, range_name="A1:A2")
                    if data:
                        sheet_status[sheet_name] = "OK"
                        print(f"  ✅ {sheet_name}: アクセス可能")
                    else:
                        sheet_status[sheet_name] = "Empty"
                        print(f"  ⚠️ {sheet_name}: データなし")
                        self.results["warnings"].append(f"{sheet_name}シートが空です")
                except Exception as e:
                    sheet_status[sheet_name] = f"Error: {str(e)}"
                    print(f"  ❌ {sheet_name}: {str(e)}")
                    self.results["errors"].append(f"{sheet_name}シートアクセスエラー: {str(e)}")

            self.results["checks"]["spreadsheet"] = sheet_status
            return all(status == "OK" or status == "Empty" for status in sheet_status.values())

        except Exception as e:
            self.results["errors"].append(f"スプレッドシート接続失敗: {str(e)}")
            print(f"  ❌ 接続失敗: {str(e)}")
            return False

    def check_data_integrity(self) -> bool:
        """データ整合性のチェック"""
        print("\n🔍 データ整合性チェック")

        try:
            from agents.google_sheets_manager import GoogleSheetsManager

            sheets = GoogleSheetsManager()

            # pm_tasksの必須列チェック
            print("  pm_tasksシート構造:")
            pm_tasks_headers = sheets.read_sheet("pm_tasks", range_name="1:1")
            if pm_tasks_headers and len(pm_tasks_headers) > 0:
                required_columns = [
                    "Task_ID",
                    "Task_Name",
                    "Goal_ID",
                    "Status",
                    "Priority",
                    "Assigned_To",
                    "Start_Date",
                    "End_Date",
                ]
                header_row = pm_tasks_headers[0] if pm_tasks_headers else []
                missing_columns = [col for col in required_columns if col not in header_row]

                if missing_columns:
                    self.results["errors"].append(
                        f"pm_tasks必須列不足: {', '.join(missing_columns)}"
                    )
                    print(f"    ❌ 必須列不足: {', '.join(missing_columns)}")
                    self.results["suggestions"].append(
                        f"pm_tasksシートに以下の列を追加: {', '.join(missing_columns)}"
                    )
                    return False
                else:
                    print("    ✅ 必須列すべて存在")

            # アクティブなゴールの存在確認
            print("  アクティブなゴール:")
            goals = sheets.read_sheet("project_goal", range_name="A:H")
            if goals and len(goals) > 1:
                active_goals = [row for row in goals[1:] if len(row) > 2 and row[2] == "active"]
                if not active_goals:
                    self.results["warnings"].append("アクティブなゴールが存在しません")
                    print("    ⚠️ アクティブなゴールなし")
                    self.results["suggestions"].append(
                        "project_goalシートでStatusをactiveに設定してください"
                    )
                else:
                    print(f"    ✅ {len(active_goals)}個のアクティブなゴール")

            self.results["checks"]["data_integrity"] = "OK"
            return True

        except Exception as e:
            self.results["errors"].append(f"データ整合性チェック失敗: {str(e)}")
            print(f"  ❌ チェック失敗: {str(e)}")
            return False

    def check_epic_orchestrator(self) -> bool:
        """Epic Orchestratorの特別チェック"""
        print("\n🔍 Epic Orchestratorチェック")

        epic_file = PROJECT_ROOT / "agents" / "epic_orchestrator.py"
        if not epic_file.exists():
            print("  ❌ epic_orchestrator.pyが存在しません")
            self.results["errors"].append("epic_orchestrator.pyが存在しません")
            return False

        with open(epic_file, "r", encoding="utf-8") as f:
            content = f.read()

        # インポート文のチェック
        import_issues = []

        # ProgressAnalyzerV2のチェック
        if "import ProgressAnalyzerV2" in content:
            import_issues.append("ProgressAnalyzerV2は存在しません（ProgressAnalyzerを使用）")
            self.results["suggestions"].append(
                "sed -i 's/ProgressAnalyzerV2/ProgressAnalyzer/g' agents/epic_orchestrator.py"
            )

        # 他の潜在的な問題をチェック
        problematic_imports = [
            ("IntegratedControllerV31", "IntegratedControllerFixed"),
            ("ObservabilityDashboard", "ObservabilityManager"),
            ("KnowledgeBase", "KnowledgeManager"),
        ]

        for wrong_name, correct_name in problematic_imports:
            if wrong_name in content:
                import_issues.append(f"{wrong_name} → {correct_name}を使用")
                self.results["suggestions"].append(
                    f"sed -i 's/{wrong_name}/{correct_name}/g' agents/epic_orchestrator.py"
                )

        if import_issues:
            print(f"  ⚠️ インポート問題: {len(import_issues)}件")
            for issue in import_issues:
                print(f"    - {issue}")
            self.results["warnings"].extend(import_issues)
            return False
        else:
            print("  ✅ Epic Orchestrator正常")
            self.results["checks"]["epic_orchestrator"] = "OK"
            return True

    def generate_fix_script(self):
        """修正スクリプトの生成"""
        if self.results["suggestions"]:
            print("\n📝 修正スクリプト生成")

            script_content = ["#!/bin/bash", "# 自動生成された修正スクリプト", ""]

            for suggestion in self.results["suggestions"]:
                if suggestion.startswith("sed"):
                    script_content.append(suggestion)
                elif suggestion.startswith("mkdir"):
                    script_content.append(suggestion)
                else:
                    script_content.append(f"# TODO: {suggestion}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_path = PROJECT_ROOT / "sh" / f"auto_fix_{timestamp}.sh"
            script_path.parent.mkdir(exist_ok=True)

            with open(script_path, "w") as f:
                f.write("\n".join(script_content))

            os.chmod(script_path, 0o755)
            print(f"  ✅ 修正スクリプト生成: {script_path}")
            return script_path
        return None

    def run_diagnostics(self) -> Dict[str, Any]:
        """全診断を実行"""
        print("=" * 60)
        print("🏥 システム自動診断 v2.0")
        print("=" * 60)

        # 各種チェックを実行
        checks = [
            ("環境変数", self.check_environment),
            ("ファイル構造", self.check_file_structure),
            ("コンポーネントインポート", self.check_critical_imports),
            ("スプレッドシート接続", self.check_spreadsheet_connection),
            ("データ整合性", self.check_data_integrity),
            ("Epic Orchestrator", self.check_epic_orchestrator),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"  ❌ {check_name}チェック中にエラー: {str(e)}")
                self.results["errors"].append(f"{check_name}: {str(e)}")
                all_passed = False

        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 診断結果サマリー")
        print("=" * 60)

        if self.critical_errors:
            print("\n🚨 クリティカルエラー:")
            for error in self.critical_errors:
                print(f"  - {error}")

        if self.results["errors"]:
            print(f"\n❌ エラー: {len(self.results['errors'])}件")
            for error in self.results["errors"][:5]:  # 最初の5件のみ表示
                print(f"  - {error}")

        if self.results["warnings"]:
            print(f"\n⚠️ 警告: {len(self.results['warnings'])}件")
            for warning in self.results["warnings"][:5]:  # 最初の5件のみ表示
                print(f"  - {warning}")

        if self.results["suggestions"]:
            print(f"\n💡 修正提案: {len(self.results['suggestions'])}件")
            for suggestion in self.results["suggestions"][:5]:  # 最初の5件のみ表示
                print(f"  - {suggestion}")

        # 総合判定
        print("\n" + "=" * 60)
        if all_passed and not self.critical_errors:
            print("✅ システム正常 - 24時間稼働可能")
            self.results["status"] = "HEALTHY"
        elif self.critical_errors:
            print("🚨 クリティカルエラー - 即座の修正が必要")
            self.results["status"] = "CRITICAL"
        else:
            print("⚠️ 問題あり - 修正が推奨されます")
            self.results["status"] = "WARNING"
        print("=" * 60)

        # 修正スクリプト生成
        if self.results["suggestions"]:
            fix_script = self.generate_fix_script()
            if fix_script:
                print(f"\n実行コマンド: bash {fix_script}")

        # 結果をJSONファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = PROJECT_ROOT / "logs" / f"diagnostics_{timestamp}.json"
        result_file.parent.mkdir(exist_ok=True)

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n📄 詳細レポート: {result_file}")

        return self.results


def main():
    """メイン処理"""
    diagnostics = SystemDiagnostics()
    results = diagnostics.run_diagnostics()

    # 終了コード
    if results["status"] == "HEALTHY":
        return 0
    elif results["status"] == "WARNING":
        return 1
    else:  # CRITICAL
        return 2


if __name__ == "__main__":
    sys.exit(main())

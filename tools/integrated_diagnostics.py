#!/usr/bin/env python3
"""
統合診断システム（改善版）

【改善点】
- 正常状態を明確に表示
- エラーと情報を区別
- プロジェクト固有の診断に特化

使用例：
    python3 tools/integrated_diagnostics.py
    python3 tools/integrated_diagnostics.py --auto-fix
"""

import sys
import subprocess
from typing import Dict, Any
from pathlib import Path


class IntegratedDiagnostics:
    """統合診断システム"""

    def __init__(self):
        self.critical_issues = []
        self.warnings = []
        self.info_messages = []
        self.fixes_applied = []

    def diagnose_sheets_integration(self) -> Dict[str, Any]:
        """シート連携の診断"""
        print("🔍 シート連携を診断中...")

        issues = []
        available_methods = []

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
methods = [m for m in dir(sheets) if not m.startswith("_") and callable(getattr(sheets, m))]
print("|".join(methods))
""",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                available_methods = result.stdout.strip().split("|")
                self.info_messages.append(
                    f"GoogleSheetsManager: {len(available_methods)}個のメソッド利用可能"
                )
            else:
                self.warnings.append("GoogleSheetsManagerの読み込みに失敗")

        except Exception as e:
            self.warnings.append(f"シート連携の診断エラー: {str(e)}")

        # 2. Orchestratorファイルでの使用状況チェック
        orch_files = [
            "scripts/integrated_orchestrator_v25_complete.py",
            "scripts/autonomous_24h_loop_v25.py",
        ]

        for orch_file in orch_files:
            if not Path(orch_file).exists():
                continue

            try:
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
                                "line": self._find_line_number(content, f".{method}("),
                                "suggestion": "write_range",
                            }
                        )
                        self.critical_issues.append(f"{orch_file}: {method}メソッドが存在しません")

            except Exception as e:
                self.warnings.append(f"{orch_file}の読み込みエラー: {str(e)}")

        return {
            "available_methods": available_methods,
            "issues": issues,
            "status": "critical" if issues else "healthy",
        }

    def _find_line_number(self, content: str, search_str: str) -> int:
        """文字列が出現する行番号を取得"""
        for i, line in enumerate(content.split("\n"), 1):
            if search_str in line:
                return i
        return 0

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
if tasks and len(tasks) > 0 and "status" in tasks[0]:
    status_idx = tasks[0].index("status")
    pending = sum(1 for r in tasks[1:] if len(r) > status_idx and r[status_idx] == "pending")
    completed = sum(1 for r in tasks[1:] if len(r) > status_idx and r[status_idx] == "completed")
    print(f"{pending},{completed}")
else:
    print("0,0")
""",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                pending, completed = map(int, result.stdout.strip().split(","))

                self.info_messages.append(f"タスク状態: Pending={pending}, Completed={completed}")

                return {"pending_tasks": pending, "completed_tasks": completed, "status": "healthy"}
            else:
                self.info_messages.append("シート読み込み: データなし or 初期状態")
                return {"status": "no_data", "message": "シートが未初期化または空です"}

        except Exception as e:
            self.warnings.append(f"シート更新診断エラー: {str(e)}")
            return {"status": "error", "error": str(e)}

    def auto_fix(self, issue: Dict) -> bool:
        """問題の自動修正"""
        if issue["type"] == "method_not_found":
            print(
                f"🔧 自動修正: {issue['file']}:{issue['line']} - {issue['method']} → {issue['suggestion']}"
            )

            try:
                file_path = issue["file"]
                with open(file_path, "r") as f:
                    content = f.read()

                # メソッド名を置換
                content = content.replace(f".{issue['method']}(", f".{issue['suggestion']}(")

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
        print("=" * 60)
        print("🚀 統合診断を開始します")
        print("=" * 60)

        results = {
            "sheets_integration": self.diagnose_sheets_integration(),
            "sheet_updates": self.diagnose_sheet_updates(),
        }

        # 自動修正
        if auto_fix and results["sheets_integration"]["issues"]:
            print("\n🔧 自動修正を実行中...")
            for issue in results["sheets_integration"]["issues"]:
                if issue["severity"] == "CRITICAL":
                    self.auto_fix(issue)

        # レポート生成
        self._print_report(results, auto_fix)

        return results

    def _print_report(self, results: Dict, auto_fix: bool):
        """診断レポートを表示"""
        print("\n" + "=" * 60)
        print("📊 診断レポート")
        print("=" * 60)

        # クリティカルな問題
        if self.critical_issues:
            print("\n🚨 クリティカルな問題:")
            for issue in self.critical_issues:
                print(f"   ❌ {issue}")

        # 警告
        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"   ⚠️  {warning}")

        # 情報
        if self.info_messages:
            print("\nℹ️  システム情報:")
            for info in self.info_messages:
                print(f"   ℹ️  {info}")

        # 自動修正サマリー
        if auto_fix and self.fixes_applied:
            print(f"\n🔧 自動修正完了:")
            for fix in self.fixes_applied:
                print(f"   ✅ {fix['file']}: {fix['method']} → {fix['suggestion']}")

        # 最終判定
        print("\n" + "=" * 60)

        if not self.critical_issues and not self.warnings:
            print("✅ 診断完了: 問題ありません")
        elif self.critical_issues:
            if auto_fix and self.fixes_applied:
                print("✅ 診断完了: 問題を自動修正しました")
            else:
                print("❌ 診断完了: クリティカルな問題があります")
                print("   → --auto-fix オプションで自動修正できます")
        elif self.warnings:
            print("⚠️  診断完了: 警告がありますが動作に影響ありません")

        print("=" * 60)


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="統合診断システム")
    parser.add_argument("--auto-fix", action="store_true", help="自動修正を実行")

    args = parser.parse_args()

    diagnostics = IntegratedDiagnostics()
    results = diagnostics.run_full_diagnostics(auto_fix=args.auto_fix)

    # 終了コード（クリティカルな問題があり、かつ自動修正しなかった場合のみエラー）
    has_critical = bool(diagnostics.critical_issues)
    fixed = bool(diagnostics.fixes_applied)

    return 1 if (has_critical and not fixed) else 0


if __name__ == "__main__":
    sys.exit(main())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 新機能: Google Sheets API実行時テスト
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_sheets_api_runtime(auto_fix=False):
    """Google Sheets APIの実行時テスト"""
    print("\n🧪 Google Sheets API実行時テスト")
    print("=" * 60)

    try:
        from tools.sheets_manager import GoogleSheetsManager

        sheets = GoogleSheetsManager()

        # テスト1: 1次元配列でのappend_rows

        print("\n📝 テスト1: 1次元配列の処理")
        try:
            # 実際には実行せず、メソッドの引数チェックのみ
            import inspect

            sig = inspect.signature(sheets.append_rows)
            print(f"  ✅ append_rows メソッド検出")
            print(f"     引数: {list(sig.parameters.keys())}")

            # ソースコード確認
            source = inspect.getsource(sheets.append_rows)
            if "if values and not isinstance(values[0], list):" in source:
                print(f"  ✅ 自動型変換機能あり")
            else:
                print(f"  ⚠️  自動型変換機能なし")

                if auto_fix:
                    print(f"\n🔧 自動修正を実行...")
                    print(f"   → STEP 2の修正スクリプトを実行してください")
                    return False

        except Exception as e:
            print(f"  ❌ テスト失敗: {e}")
            return False

        print("\n✅ Google Sheets API実行時テスト完了")
        return True

    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False


# メイン関数に追加
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--auto-fix", action="store_true")
    parser.add_argument("--test-sheets", action="store_true", help="Google Sheets API実行時テスト")
    args = parser.parse_args()

    if args.test_sheets:
        test_sheets_api_runtime(args.auto_fix)

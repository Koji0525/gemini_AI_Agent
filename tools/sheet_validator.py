#!/usr/bin/env python3
"""
スプレッドシートバリデータ - シート存在確認と自動修復
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from browser_control.sheets_manager import GoogleSheetsManager


class SheetValidator:
    """シート検証と自動修復クラス"""

    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        self.required_sheets = {
            "project_goal": ["goal_id", "goal_description", "status", "created_at"],
            "pm_tasks": ["task_id", "parent_goal_id", "description", "status"],
            "task_execution_log": ["log_id", "task_id", "timestamp", "status"],
            "quality_feedback": ["feedback_id", "task_id", "quality_score", "review_status"],
        }

    def validate_all_sheets(self):
        """全必須シートを検証"""
        print("🔍 必須シート検証開始...")

        results = {}
        for sheet_name, required_columns in self.required_sheets.items():
            result = self.validate_sheet(sheet_name, required_columns)
            results[sheet_name] = result

        # 結果集計
        total_sheets = len(results)
        valid_sheets = sum(1 for r in results.values() if r["status"] == "valid")

        print(f"\n📊 検証結果: {valid_sheets}/{total_sheets} シート正常")

        for sheet_name, result in results.items():
            status_icon = "✅" if result["status"] == "valid" else "❌"
            print(f"  {status_icon} {sheet_name}: {result['status']}")

            if result["status"] != "valid" and "error" in result:
                print(f"     エラー: {result['error']}")

        return all(r["status"] == "valid" for r in results.values())

    def validate_sheet(self, sheet_name, required_columns=None):
        """個別シートを検証"""
        try:
            # シート存在確認
            test_data = self.sheets_manager.read_range(f"{sheet_name}!A1:Z1")

            if not test_data:
                return {"status": "missing", "error": "シートが存在しませんまたは空です"}

            # ヘッダー確認
            headers = test_data[0] if test_data else []

            if required_columns:
                missing_columns = [col for col in required_columns if col not in headers]
                if missing_columns:
                    return {
                        "status": "invalid_headers",
                        "error": f"必須カラム不足: {missing_columns}",
                    }

            return {
                "status": "valid",
                "headers": headers,
                "row_count": (
                    len(self.sheets_manager.read_range(f"{sheet_name}!A2:Z1000"))
                    if test_data
                    else 0
                ),
            }

        except Exception as e:
            error_msg = str(e)
            if "Unable to parse range" in error_msg:
                return {"status": "missing", "error": "シートが存在しません"}
            else:
                return {"status": "error", "error": error_msg}

    def repair_missing_sheet(self, sheet_name, headers):
        """不足シートを修復"""
        try:
            print(f"🔧 {sheet_name}シートを修復中...")

            # ヘッダー行を書き込み
            success = self.sheets_manager.append_rows(sheet_name, [headers])

            if success:
                print(f"✅ {sheet_name}シート修復完了")
                return True
            else:
                print(f"❌ {sheet_name}シート修復失敗")
                return False

        except Exception as e:
            print(f"❌ {sheet_name}シート修復エラー: {e}")
            return False

    def auto_repair_all(self):
        """全不足シートを自動修復"""
        print("🚀 自動修復を開始...")

        repair_results = {}
        for sheet_name, required_columns in self.required_sheets.items():
            validation = self.validate_sheet(sheet_name, required_columns)

            if validation["status"] != "valid":
                print(f"🛠️  {sheet_name} を修復します...")
                success = self.repair_missing_sheet(sheet_name, required_columns)
                repair_results[sheet_name] = success
            else:
                repair_results[sheet_name] = True  # 修復不要

        repaired_count = sum(1 for result in repair_results.values() if result)
        total_count = len(repair_results)

        print(f"\n📊 自動修復結果: {repaired_count}/{total_count} シート正常")

        for sheet_name, success in repair_results.items():
            status_icon = "✅" if success else "❌"
            print(f"  {status_icon} {sheet_name}")

        return all(repair_results.values())


def main():
    """メイン実行"""
    validator = SheetValidator()

    print("🎯 スプレッドシート整合性チェック")
    print("=" * 50)

    # 検証実行
    is_valid = validator.validate_all_sheets()

    if not is_valid:
        print("\n⚠️ シートに問題があります。自動修復を実行しますか？")
        print("   自動修復を実行するには以下のコマンドを実行してください:")
        print("   python3 tools/sheet_validator.py --repair")

    return is_valid


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--repair":
        validator = SheetValidator()
        success = validator.auto_repair_all()
        sys.exit(0 if success else 1)
    else:
        success = main()
        sys.exit(0 if success else 1)

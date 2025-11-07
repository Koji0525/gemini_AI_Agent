#!/usr/bin/env python3
"""
🩺 Google Sheets クイック診断ツール v1.0
目的: 1コマンドで全問題を検出・修正提案
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def quick_diagnosis():
    """クイック診断"""
    print("=" * 60)
    print("🩺 Google Sheets クイック診断")
    print("=" * 60)
    print()

    # 1. 環境変数確認
    print("📋 1. 環境変数確認")
    import os

    from dotenv import load_dotenv

    load_dotenv()

    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    if not spreadsheet_id:
        print("   ❌ SPREADSHEET_ID が未設定")
        return False
    else:
        print(f"   ✅ SPREADSHEET_ID: {spreadsheet_id[:20]}...")

    # 2. 認証確認
    print("📋 2. Google Sheets 認証")
    try:
        from tools.sheets_manager import GoogleSheetsManager

        sheets = GoogleSheetsManager()
        sheets.open_spreadsheet(spreadsheet_id)
        print("   ✅ 認証成功")
    except Exception as e:
        print(f"   ❌ 認証失敗: {e}")
        return False

    print()

    # 3. シート構造検証
    print("📋 3. シート構造検証")
    from tools.sheets_validators.sheets_structure_validator import \
        SheetsStructureValidator

    sheet_configs = {
        "project_goal": ["goal_id", "description", "priority", "status", "created_at"],
        "pm_tasks": [
            "task_id",
            "parent_goal_id",
            "description",
            "required_role",
            "status",
            "priority",
            "estimated_time",
            "dependencies",
            "created_at",
            "batch_id",
        ],
        "task_execution_log": ["task_id", "status", "output", "executed_at", "knowledge_used"],
    }

    validator = SheetsStructureValidator(sheets)
    results = validator.validate_all_sheets(sheet_configs)

    for detail in results["details"]:
        sheet_name = detail["sheet_name"]
        if detail["valid"] and len(detail["issues"]) == 0:
            print(f"   ✅ {sheet_name}: OK")
        else:
            print(f"   ❌ {sheet_name}: 問題あり")
            for issue in detail["issues"]:
                print(f"      - {issue}")

    print()
    print("=" * 60)
    print("📊 診断完了")
    print(f"   正常: {results['valid_sheets']}/{results['total_sheets']} シート")

    if results["invalid_sheets"] > 0:
        print()
        print("🔧 修正が必要です:")
        print("   python3 tools/sheets_validators/sheets_structure_validator.py")
        return False

    print("=" * 60)
    return True


if __name__ == "__main__":
    success = quick_diagnosis()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
�� Google Sheets 構造検証ツール v1.0
目的: シート構造とコードの期待値を事前検証
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from typing import Dict, List

from tools.sheets_manager import GoogleSheetsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SheetsStructureValidator:
    """スプレッドシート構造の検証"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.validation_results = []

    def validate_sheet_structure(self, sheet_name: str, expected_headers: List[str]) -> Dict:
        """
        シート構造を検証
        """
        result = {"sheet_name": sheet_name, "valid": True, "issues": [], "warnings": []}

        try:
            # シートの存在確認
            data = self.sheets.read_sheet(sheet_name)
            logger.info(f"✅ シート '{sheet_name}' が存在")

            # 実際のヘッダーを推測（最初の行）
            if data:
                actual_headers = list(data[0].keys()) if data else []

                # 空のヘッダー検出
                empty_headers = [h for h in actual_headers if not h.strip()]
                if empty_headers:
                    result["valid"] = False
                    result["issues"].append(f"空白ヘッダーが {len(empty_headers)} 個存在")

                # 期待値との比較
                if actual_headers != expected_headers:
                    result["warnings"].append(
                        f"ヘッダー不一致:\n  期待: {expected_headers}\n  実際: {actual_headers}"
                    )

            return result

        except Exception as e:
            error_msg = str(e)
            if "unable to parse" in error_msg.lower() or sheet_name.lower() in error_msg.lower():
                result["valid"] = False
                result["issues"].append("シートが存在しないか、アクセスできません")
            else:
                result["valid"] = False
                result["issues"].append(f"シートアクセスエラー: {error_msg}")
            return result

    def validate_all_sheets(self, sheet_configs: Dict[str, List[str]]) -> Dict:
        """
        全シートを一括検証
        """
        results = {
            "total_sheets": len(sheet_configs),
            "valid_sheets": 0,
            "invalid_sheets": 0,
            "details": [],
        }

        for sheet_name, expected_headers in sheet_configs.items():
            result = self.validate_sheet_structure(sheet_name, expected_headers)
            results["details"].append(result)

            if result["valid"] and len(result["issues"]) == 0:
                results["valid_sheets"] += 1
            else:
                results["invalid_sheets"] += 1

        return results


def main():
    """メイン実行"""
    import os

    from dotenv import load_dotenv

    load_dotenv()

    sheets = GoogleSheetsManager()
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheets.open_spreadsheet(spreadsheet_id)

    # 検証対象のシート構成
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

    # 結果表示
    print("=" * 60)
    print("📋 Google Sheets 構造検証結果")
    print("=" * 60)
    print(f"総シート数: {results['total_sheets']}")
    print(f"✅ 正常: {results['valid_sheets']}")
    print(f"❌ 異常: {results['invalid_sheets']}")
    print()

    for detail in results["details"]:
        sheet_name = detail["sheet_name"]

        if detail["valid"] and len(detail["issues"]) == 0:
            print(f"✅ {sheet_name}: 問題なし")
        else:
            status = "❌" if not detail["valid"] else "⚠️"
            print(f"{status} {sheet_name}:")

            for issue in detail["issues"]:
                print(f"   {issue}")

            for warning in detail["warnings"]:
                print(f"   ⚠️  {warning}")

    print("=" * 60)

    return results["invalid_sheets"] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

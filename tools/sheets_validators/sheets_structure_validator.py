"""
Google Sheets 構造検証ツール（SafeSheetsWrapper対応版）
configuration/sheets_schema.py を参照して検証を実施
"""

import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from configuration.sheets_schema import (
    PROJECT_GOAL_SCHEMA,
    PM_TASKS_SCHEMA,
    TASK_EXECUTION_LOG_SCHEMA,
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SheetsStructureValidator:
    """スプレッドシート構造の検証（SafeSheetsWrapper使用）"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = SafeSheetsWrapper(sheets_manager)  # SafeWrapperを使用
        self.schemas = {
            "project_goal": PROJECT_GOAL_SCHEMA,
            "pm_tasks": PM_TASKS_SCHEMA,
            "task_execution_log": TASK_EXECUTION_LOG_SCHEMA,
        }

    def validate_all(self) -> dict:
        """全シートを検証"""
        results = {}

        for sheet_name, schema in self.schemas.items():
            results[sheet_name] = self.validate_sheet(sheet_name, schema)

        return results

    def validate_sheet(self, sheet_name: str, schema: dict) -> dict:
        """個別シートの構造を検証"""
        result = {
            "exists": False,
            "header_match": False,
            "expected_headers": schema["headers"],
            "actual_headers": [],
            "issues": [],
        }

        try:
            # SafeSheetsWrapperのread_rangeを使用（2次元配列を返す）
            all_data = self.sheets.read_range(f"{sheet_name}!A1:Z1", default=[])

            if not all_data or len(all_data) == 0:
                result["issues"].append(f"シート '{sheet_name}' が空またはヘッダーがありません")
                return result

            result["exists"] = True
            logger.info(f"✅ シート '{sheet_name}' が存在")

            # ヘッダー取得（1行目）
            actual_headers = all_data[0] if all_data else []

            # 空文字列を除外
            actual_headers = [h for h in actual_headers if h]
            result["actual_headers"] = actual_headers

            # ヘッダーの比較
            expected = schema["headers"]

            if actual_headers == expected:
                result["header_match"] = True
                logger.info(f"✅ シート '{sheet_name}' のヘッダーが一致")
            else:
                # 詳細な差異を記録
                if len(actual_headers) != len(expected):
                    diff = len(actual_headers) - len(expected)
                    if diff > 0:
                        result["issues"].append(f"余分な列が {diff} 個存在")
                    else:
                        result["issues"].append(f"不足している列が {-diff} 個")

                # 不一致の列を特定
                mismatches = []
                max_len = max(len(expected), len(actual_headers))

                for i in range(max_len):
                    exp = expected[i] if i < len(expected) else "（なし）"
                    act = actual_headers[i] if i < len(actual_headers) else "（なし）"

                    if exp != act:
                        mismatches.append(f"列{i+1}: 期待='{exp}' 実際='{act}'")

                if mismatches:
                    result["issues"].append("ヘッダーの不一致が検出されました")

        except Exception as e:
            result["issues"].append(f"検証エラー: {str(e)}")
            logger.error(f"❌ シート '{sheet_name}' の検証でエラー: {e}")
            import traceback

            traceback.print_exc()

        return result

    def print_results(self, results: dict):
        """検証結果を表示"""
        print("\n" + "=" * 60)
        print("📊 スプレッドシート構造検証結果")
        print("=" * 60)

        all_ok = True

        for sheet_name, result in results.items():
            print(f"\n📋 {sheet_name}:")

            if not result["exists"]:
                print(f"   ❌ シートが存在しないか、読み取れません")
                for issue in result["issues"]:
                    print(f"      {issue}")
                all_ok = False
                continue

            if result["header_match"]:
                print(f"   ✅ ヘッダーが正しい構造です")
                print(f"      列数: {len(result['actual_headers'])}")
            else:
                print(f"   ⚠️  ヘッダーに問題があります")
                print(
                    f"      期待 ({len(result['expected_headers'])}列): {result['expected_headers']}"
                )
                print(f"      実際 ({len(result['actual_headers'])}列): {result['actual_headers']}")

                for issue in result["issues"]:
                    print(f"      ⚠️  {issue}")

                all_ok = False

        print("\n" + "=" * 60)

        if all_ok:
            print("✅ すべてのシートが正しい構造です")
        else:
            print("❌ 一部のシートに問題があります")
            print("\n💡 次のステップ:")
            print("   1. configuration/sheets_schema.py で期待値を確認")
            print("   2. 実際のスプレッドシートを期待値に合わせて修正")
            print("   3. または、期待値を実際の構造に合わせて修正")

        print("=" * 60)

        return all_ok


def main():
    """メイン実行"""
    try:
        # Google Sheets Manager初期化
        sheets = GoogleSheetsManager()

        # 検証実行
        validator = SheetsStructureValidator(sheets)
        results = validator.validate_all()

        # 結果表示
        all_ok = validator.print_results(results)

        sys.exit(0 if all_ok else 1)

    except Exception as e:
        logger.error(f"❌ 検証中にエラー発生: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

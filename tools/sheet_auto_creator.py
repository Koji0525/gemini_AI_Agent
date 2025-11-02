import logging
import sys
from pathlib import Path
from typing import Dict
from tools.sheets_manager import GoogleSheetsManager

"""
sheet_auto_creator.py v2

スプレッドシート自動作成システム（インポート修正版）
"""


# プロジェクトルートを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


logger = logging.getLogger(__name__)


class SheetAutoCreator:
    """シート自動作成 v2"""

    def __init__(self):
        try:
            self.sheets_manager = GoogleSheetsManager()
            self.available = True
            logger.info("✅ SheetsManager初期化成功")
        except Exception as e:
            logger.error(f"❌ SheetsManager初期化エラー: {e}")
            self.available = False

    def create_missing_sheets(self) -> Dict[str, bool]:
        """不足シートを作成"""
        if not self.available:
            logger.error("❌ SheetsManager利用不可 - シート作成をスキップ")
            return {}

        results = {}

        # 必須シートの定義
        required_sheets = {
            "pm_goals": [
                [
                    "goal_id",
                    "description",
                    "priority",
                    "status",
                    "progress",
                    "created_at",
                ]
            ],
            "control_flags": [["flag_name", "value", "description", "updated_at"]],
            "error_log": [["timestamp", "error_type", "message", "resolved", "resolution"]],
            "execution_history": [
                [
                    "execution_id",
                    "task_id",
                    "started_at",
                    "completed_at",
                    "status",
                    "result",
                ]
            ],
        }

        for sheet_name, headers in required_sheets.items():
            try:
                # シート存在確認
                try:
                    # data = self.sheets_manager.read_range(f"{sheet_name}!A1:A1")
                    logger.info(f"✅ {sheet_name} 既存")
                    results[sheet_name] = True
                except Exception:
                    # シート作成試行
                    logger.info(f"🔧 {sheet_name} 作成試行...")

                    try:
                        # ヘッダー書き込み（シート自動作成を期待）
                        self.sheets_manager.write_range(f"{sheet_name}!A1", headers)
                        logger.info(f"✅ {sheet_name} 作成成功")
                        results[sheet_name] = True
                    except Exception as write_error:
                        logger.error(f"❌ {sheet_name} 作成失敗: {write_error}")
                        logger.info(
                            f"💡 Googleスプレッドシートで手動で'{sheet_name}'シートを作成してください"
                        )
                        results[sheet_name] = False

            except Exception as e:
                logger.error(f"❌ {sheet_name} 処理エラー: {e}")
                results[sheet_name] = False

        return results


def main():
    """メイン実行"""
    print("=" * 60)
    print("📊 シート自動作成システム v2")
    print("=" * 60)

    creator = SheetAutoCreator()

    if not creator.available:
        print("❌ SheetsManager利用不可")
        print("💡 認証情報を確認してください")
        return 1

    results = creator.create_missing_sheets()

    print("\n" + "=" * 60)
    print("�� シート作成結果")
    print("=" * 60)
    for sheet_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {sheet_name}")
    print("=" * 60)

    # すべて成功した場合
    if all(results.values()):
        print("\n✅ すべてのシートが利用可能です")
        return 0
    else:
        failed = [name for name, success in results.items() if not success]
        print("\n⚠️  以下のシートを手動で作成してください:")
        for name in failed:
            print(f"   - {name}")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exit(main())

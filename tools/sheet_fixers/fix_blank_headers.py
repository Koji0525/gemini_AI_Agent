"""
空白ヘッダー自動修正スクリプト（確認処理改善版）
運用ルール5.1: Google Sheets 構造検証ツールの実装
"""

import sys
import os
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_gspread_client():
    """gspreadクライアントを直接取得"""
    load_dotenv()

    creds_path = os.getenv("SERVICE_ACCOUNT_FILE", "configuration/service_account.json")

    if not os.path.exists(creds_path):
        logger.error(f"❌ 認証ファイルが見つかりません: {creds_path}")
        return None

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)

    logger.info("✅ gspread認証成功")
    return client


def fix_blank_headers(sheet_name: str, auto_confirm: bool = False):
    """
    シートの空白ヘッダーを削除

    Args:
        sheet_name: 修正するシート名
        auto_confirm: Trueの場合、確認なしで実行
    """
    try:
        load_dotenv()
        spreadsheet_id = os.getenv("SPREADSHEET_ID")

        if not spreadsheet_id:
            logger.error("❌ SPREADSHEET_ID が設定されていません")
            return False

        client = get_gspread_client()
        if not client:
            return False

        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)

        logger.info(f"📂 シート '{sheet_name}' を修正します...")

        all_values = worksheet.get_all_values()

        if not all_values:
            logger.warning(f"⚠️ シート '{sheet_name}' にデータがありません")
            return False

        headers = all_values[0]
        logger.info(f"   元のヘッダー ({len(headers)}列): {headers}")

        blank_indices = [i for i, h in enumerate(headers) if not h or not h.strip()]

        if not blank_indices:
            logger.info(f"✅ シート '{sheet_name}' に空白列はありません")
            return True

        logger.warning(f"⚠️ 空白列を {len(blank_indices)} 個発見")
        logger.info(f"   空白列の位置: {[chr(65 + i) for i in blank_indices]}")

        new_data = []
        for row in all_values:
            new_row = [cell for i, cell in enumerate(row) if i not in blank_indices]
            new_data.append(new_row)

        new_headers = new_data[0]
        logger.info(f"   新しいヘッダー ({len(new_headers)}列): {new_headers}")

        print("\n" + "=" * 60)
        print(f"📋 シート '{sheet_name}' の修正内容:")
        print(f"   削除する列数: {len(blank_indices)}")
        print(f"   削除する列: {[chr(65 + i) for i in blank_indices]}")
        print(f"   元の列数: {len(headers)} → 新しい列数: {len(new_headers)}")
        print(f"   新しいヘッダー: {new_headers}")
        print("=" * 60)

        if not auto_confirm:
            response = input("\n修正を実行しますか？ (y/yes): ").strip().lower()

            # "y" または "yes" を受け付ける
            if response not in ["y", "yes"]:
                logger.info("❌ 修正をキャンセルしました")
                return False

        logger.info("🔄 シートを更新中...")
        worksheet.clear()
        worksheet.update("A1", new_data)

        logger.info(f"✅ シート '{sheet_name}' の空白列を削除しました")
        logger.info(f"   {len(headers)}列 → {len(new_headers)}列")

        return True

    except gspread.exceptions.WorksheetNotFound:
        logger.error(f"❌ シート '{sheet_name}' が見つかりません")
        return False

    except Exception as e:
        logger.error(f"❌ 修正中にエラー: {e}")
        import traceback

        traceback.print_exc()
        return False


def fix_all_sheets(auto_confirm: bool = False):
    """すべての主要シートの空白ヘッダーを修正"""
    sheets = ["project_goal", "pm_tasks", "task_execution_log"]

    print("\n" + "=" * 60)
    print("🔧 複数シートの空白ヘッダー修正")
    print("=" * 60)

    results = {}

    for sheet in sheets:
        print(f"\n📋 {sheet} を処理中...")
        results[sheet] = fix_blank_headers(sheet, auto_confirm=auto_confirm)

    print("\n" + "=" * 60)
    print("📊 修正結果サマリー")
    print("=" * 60)

    for sheet, success in results.items():
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"   {sheet}: {status}")

    print("=" * 60)


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="スプレッドシートの空白ヘッダーを修正")
    parser.add_argument("sheet_name", nargs="?", help="修正するシート名（省略時は全シート）")
    parser.add_argument("--auto", action="store_true", help="確認なしで実行")
    parser.add_argument("--all", action="store_true", help="すべてのシートを修正")

    args = parser.parse_args()

    if args.all or not args.sheet_name:
        fix_all_sheets(auto_confirm=args.auto)
    else:
        fix_blank_headers(args.sheet_name, auto_confirm=args.auto)


if __name__ == "__main__":
    main()

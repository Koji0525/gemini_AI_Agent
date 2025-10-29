#!/usr/bin/env python3
"""
context_logシート作成
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


def create_context_log_sheet():
    """context_logシートを作成"""
    SHEET_NAME = "context_log"

    HEADERS = [
        "timestamp",  # 記録日時
        "log_id",  # ログID
        "task_id",  # タスクID
        "error_type",  # エラータイプ
        "error_message",  # エラーメッセージ
        "modification_reason",  # 修正理由
        "system_state",  # システム状態（JSON）
        "decision_process",  # 判断プロセス
        "modification_purpose",  # 修正目的
        "expected_result",  # 期待される結果
        "alternatives",  # 代替案（JSON）
        "prevention_strategy",  # 再発防止策
        "pattern_name",  # パターン名
        "learning_tags",  # 学習タグ
    ]

    print("=" * 60)
    print("🏗️  context_logシート作成")
    print("=" * 60)
    print()

    # 初期化
    spreadsheet_id = get_config("SPREADSHEET_ID")
    service_account_file = get_config("SERVICE_ACCOUNT_FILE")

    sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id, service_account_file=service_account_file)

    gc = sheets_manager.gc

    try:
        # スプレッドシートを開く
        spreadsheet = gc.open_by_key(spreadsheet_id)

        # 既存のシート確認
        worksheet_list = spreadsheet.worksheets()
        sheet_names = [ws.title for ws in worksheet_list]

        if SHEET_NAME in sheet_names:
            print(f"✅ {SHEET_NAME}シート存在確認")
            sheet = spreadsheet.worksheet(SHEET_NAME)
        else:
            print(f"🆕 {SHEET_NAME}シート新規作成")
            sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=20)

        # ヘッダー設定
        current_headers = sheet.row_values(1)
        if not current_headers or current_headers != HEADERS:
            sheet.update(values=[HEADERS], range_name="A1")
            print(f"✅ ヘッダー設定完了（{len(HEADERS)}列）")
        else:
            print(f"ℹ️  既に正しく設定済み")

        # サンプルデータ追加
        if not sheet.row_values(2):
            sample_data = [
                [
                    "2025-10-29 12:00:00",
                    "CTX_20251029_120000_001",
                    "438",
                    "TimeoutError",
                    "Gemini API connection timeout",
                    "Gemini APIが30秒でタイムアウト。ネットワークは正常だが、API応答が遅い。",
                    '{"cpu_percent": 35, "memory_percent": 42, "network": "normal"}',
                    "1. ネットワーク確認→正常 2. タイムアウト値確認→30秒 3. 判断: 60秒に延長",
                    "Gemini APIの安定した応答取得",
                    "3回連続成功すれば有効と判断",
                    '["リトライ回数増加", "別APIへ切り替え"]',
                    "タイムアウト設定を環境変数化して調整可能に",
                    "timeout_extension_pattern",
                    "gemini,timeout,network",
                ]
            ]

            sheet.update(values=sample_data, range_name="A2")
            print(f"✅ サンプルデータ追加")

        print()
        print("🎉 context_logシート作成完了")
        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_context_log_sheet()
    sys.exit(0 if success else 1)

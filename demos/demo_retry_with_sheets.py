"""
Week 5デモ: retry_historyシート連携

リトライ機能とGoogle Sheets記録の統合デモ
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.sheets_manager import GoogleSheetsManager
from agents.self_healing.sheets_adapter import SheetsAdapter, RetryHistoryManager
from dotenv import load_dotenv
import time
import asyncio

load_dotenv()


def demo_basic_recording():
    """基本的な記録デモ"""

    print("\n" + "=" * 70)
    print("📝 デモ1: 基本的なリトライ記録")
    print("=" * 70)

    # GoogleSheetsManager初期化
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)

    # Adapter作成
    adapter = SheetsAdapter(sheets_manager)

    # シート存在確認
    if not adapter.ensure_sheet_exists():
        print("\n❌ retry_historyシートが見つかりません")
        print("   python3 scripts/create_retry_history_sheet.py を実行してください")
        return

    print("\n✅ retry_historyシート確認完了")

    # サンプルデータ記録
    print("\n📊 サンプルリトライを記録中...")

    test_cases = [
        {
            "task_name": "test_network_task",
            "attempt": 1,
            "error_type": "network",
            "error_message": "Connection timeout after 30s",
            "strategy_used": "exponential_backoff",
            "wait_time": 2.5,
            "success": True,
            "duration": 5.3,
        },
        {
            "task_name": "test_timeout_task",
            "attempt": 2,
            "error_type": "timeout",
            "error_message": "Task execution timeout",
            "strategy_used": "timeout_strategy",
            "wait_time": 1.5,
            "success": False,
            "duration": 30.0,
        },
        {
            "task_name": "test_rate_limit_task",
            "attempt": 1,
            "error_type": "rate_limit",
            "error_message": "429 Too Many Requests",
            "strategy_used": "rate_limit_strategy",
            "wait_time": 60.0,
            "success": True,
            "duration": 62.1,
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"  {i}. {test_case['task_name']} ... ", end="")
        success = adapter.record_retry(**test_case)
        print("✅" if success else "❌")
        time.sleep(0.5)

    print("\n✅ 記録完了")


def demo_retrieve_history():
    """履歴取得デモ"""

    print("\n" + "=" * 70)
    print("📊 デモ2: リトライ履歴取得")
    print("=" * 70)

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)

    manager = RetryHistoryManager(sheets_manager)

    # 最近のリトライ表示
    manager.show_recent_retries(limit=5)


def demo_statistics():
    """統計表示デモ"""

    print("\n" + "=" * 70)
    print("�� デモ3: リトライ統計")
    print("=" * 70)

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)

    manager = RetryHistoryManager(sheets_manager)

    # 統計表示
    manager.show_stats(hours=24)


def main():
    """メイン実行"""

    print("\n" + "=" * 70)
    print("🚀 Week 5統合デモ: retry_history連携")
    print("=" * 70)

    try:
        # デモ1: 記録
        demo_basic_recording()

        # デモ2: 履歴取得
        demo_retrieve_history()

        # デモ3: 統計
        demo_statistics()

        print("\n" + "=" * 70)
        print("✅ 全デモ完了")
        print("=" * 70)
        print("\n次のステップ:")
        print("  1. Week 5の本格的なRetryManager実装")
        print("  2. エラー分類システムの構築")
        print("  3. リトライ戦略の実装")
        print()

    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

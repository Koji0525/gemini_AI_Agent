"""
Week 5: 自己修復システム完全統合デモ

ErrorClassifier + RetryManager + RetryStrategies + SheetsAdapter
の完全統合デモンストレーション
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from dotenv import load_dotenv

# 自己修復システムのインポート
from agents.self_healing import ErrorClassifier, RetryManager, RetryConfig, StrategyFactory

# Google Sheets連携（オプション）
try:
    from tools.sheets_manager import GoogleSheetsManager

    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False
    print("⚠️  Google Sheets連携は利用できません（スタンドアロンモード）")

load_dotenv()


# ================================================
# デモタスク定義
# ================================================


class DemoTasks:
    """デモ用のタスククラス"""

    def __init__(self):
        self.network_attempt = 0
        self.timeout_attempt = 0
        self.rate_limit_attempt = 0

    async def unstable_network_task(self):
        """不安定なネットワークタスク（2回目で成功）"""
        self.network_attempt += 1

        if self.network_attempt < 2:
            raise ConnectionError("Failed to connect to server")

        await asyncio.sleep(0.1)
        return {"status": "success", "data": "network_task_completed"}

    async def slow_timeout_task(self):
        """遅いタスク（3回目で成功）"""
        self.timeout_attempt += 1

        if self.timeout_attempt < 3:
            raise TimeoutError(f"Operation timed out (attempt {self.timeout_attempt})")

        return {"status": "success", "data": "timeout_task_completed"}

    async def rate_limited_task(self):
        """レート制限されるタスク（常に失敗）"""
        self.rate_limit_attempt += 1
        raise Exception("429 Too Many Requests - Please slow down")

    async def auth_error_task(self):
        """認証エラータスク（常に失敗）"""
        raise Exception("401 Unauthorized - Token expired")

    async def non_retryable_task(self):
        """リトライ不可能なタスク"""
        raise SyntaxError("Invalid syntax in code")


# ================================================
# デモシナリオ
# ================================================


async def demo_scenario_1_network_recovery(manager: RetryManager, tasks: DemoTasks):
    """
    シナリオ1: ネットワークエラーからの回復

    期待動作:
    - 1回目: ConnectionError
    - 2回目: 成功
    """
    print("\n" + "=" * 70)
    print("【シナリオ1】ネットワークエラーからの回復")
    print("=" * 70)
    print("説明: 不安定なネットワークをシミュレート")
    print("      指数バックオフ戦略で2回目に成功")
    print("-" * 70)

    result = await manager.execute_with_retry(
        task_func=tasks.unstable_network_task, task_name="unstable_network_task", max_attempts=3
    )

    if result.success:
        print(f"✅ 最終結果: {result.result}")
        print(f"📊 総試行回数: {result.total_attempts}回")
        print(f"⏱️  総実行時間: {result.total_duration:.2f}秒")


async def demo_scenario_2_timeout_retry(manager: RetryManager, tasks: DemoTasks):
    """
    シナリオ2: タイムアウトエラーのリトライ

    期待動作:
    - 1-2回目: TimeoutError
    - 3回目: 成功
    """
    print("\n" + "=" * 70)
    print("【シナリオ2】タイムアウトエラーのリトライ")
    print("=" * 70)
    print("説明: タイムアウトが発生する遅いタスク")
    print("      短い待機時間で素早くリトライ")
    print("-" * 70)

    result = await manager.execute_with_retry(
        task_func=tasks.slow_timeout_task, task_name="slow_timeout_task", max_attempts=4
    )

    if result.success:
        print(f"✅ 最終結果: {result.result}")
        print(f"📊 総試行回数: {result.total_attempts}回")
        print(f"⏱️  総実行時間: {result.total_duration:.2f}秒")


async def demo_scenario_3_rate_limit(manager: RetryManager, tasks: DemoTasks):
    """
    シナリオ3: レート制限エラー

    期待動作:
    - 全試行: 429 Too Many Requests
    - 長い待機時間（60秒+）で待機
    """
    print("\n" + "=" * 70)
    print("【シナリオ3】レート制限エラー")
    print("=" * 70)
    print("説明: APIレート制限をシミュレート")
    print("      長い待機時間で待機（実際は短縮）")
    print("-" * 70)

    # レート制限デモは待機時間が長いので試行回数を制限
    result = await manager.execute_with_retry(
        task_func=tasks.rate_limited_task, task_name="rate_limited_task", max_attempts=2
    )

    if not result.success:
        print(f"❌ 予想通り失敗: レート制限が解除されませんでした")
        print(f"📊 総試行回数: {result.total_attempts}回")
        print(f"⏱️  総実行時間: {result.total_duration:.2f}秒")


async def demo_scenario_4_non_retryable(manager: RetryManager, tasks: DemoTasks):
    """
    シナリオ4: リトライ不可能なエラー

    期待動作:
    - 1回目: SyntaxError
    - リトライせずに即座に終了
    """
    print("\n" + "=" * 70)
    print("【シナリオ4】リトライ不可能なエラー")
    print("=" * 70)
    print("説明: 構文エラーなどリトライしても意味がないエラー")
    print("      即座に失敗として終了")
    print("-" * 70)

    result = await manager.execute_with_retry(
        task_func=tasks.non_retryable_task, task_name="non_retryable_task", max_attempts=5
    )

    if not result.success:
        print(f"❌ 予想通り即座に失敗: リトライ不可能なエラー")
        print(f"📊 試行回数: {result.total_attempts}回（1回のみ）")
        print(f"🔍 エラー種別: {result.errors_encountered[0]['category']}")


async def demo_classifier_showcase():
    """
    エラー分類器のショーケース
    """
    print("\n" + "=" * 70)
    print("【補足】ErrorClassifier - エラー分類デモ")
    print("=" * 70)

    classifier = ErrorClassifier()

    test_errors = [
        (ConnectionError("Failed to connect"), "ネットワークエラー"),
        (TimeoutError("Operation timed out"), "タイムアウト"),
        (Exception("429 Too Many Requests"), "レート制限"),
        (Exception("401 Unauthorized"), "認証エラー"),
        (Exception("Selector not found"), "セレクタエラー"),
        (PermissionError("Access denied"), "権限エラー"),
        (MemoryError("Out of memory"), "リソース不足"),
        (SyntaxError("Invalid syntax"), "構文エラー"),
    ]

    print("\n各エラーの自動分類:")
    print("-" * 70)

    for error, description in test_errors:
        info = classifier.get_error_info(error)
        retry_mark = "✅" if info.is_retryable else "❌"

        print(
            f"{retry_mark} {description:20s} → カテゴリ: {info.category:15s} "
            f"深刻度: {info.severity:8s} 戦略: {info.recommended_strategy}"
        )


async def demo_strategy_showcase():
    """
    リトライ戦略のショーケース
    """
    print("\n" + "=" * 70)
    print("【補足】RetryStrategies - 戦略パターンデモ")
    print("=" * 70)

    strategies_info = [
        ("exponential_backoff", "指数バックオフ", "ネットワークエラー向け"),
        ("timeout_strategy", "タイムアウト戦略", "タイムアウト向け"),
        ("rate_limit_strategy", "レート制限戦略", "API制限向け"),
        ("selector_strategy", "セレクタ戦略", "UI要素検索向け"),
        ("auth_strategy", "認証戦略", "認証エラー向け"),
    ]

    print("\n利用可能な戦略:")
    print("-" * 70)

    for strategy_name, display_name, use_case in strategies_info:
        strategy = StrategyFactory.create(strategy_name)
        wait_time = strategy.calculate_wait_time(1, {})

        print(f"🔧 {display_name:20s} ({use_case:20s}) " f"初回待機: {wait_time:.1f}秒")


async def main():
    """メインデモ"""

    print("\n" + "=" * 70)
    print("🚀 Week 5: 自己修復システム完全統合デモ")
    print("=" * 70)
    print("\n本デモでは以下のコンポーネントを統合します:")
    print("  1. ErrorClassifier - エラーの自動分類")
    print("  2. RetryManager - リトライ管理")
    print("  3. RetryStrategies - 戦略パターン")
    print("  4. SheetsAdapter - 履歴記録（オプション）")

    # Google Sheets連携の初期化（オプション）
    sheets_manager = None
    if SHEETS_AVAILABLE:
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if spreadsheet_id:
            try:
                sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
                print("\n✅ Google Sheets連携: 有効")
                print(f"   SPREADSHEET_ID: {spreadsheet_id}")
            except Exception as e:
                print(f"\n⚠️  Google Sheets連携エラー: {e}")
                print("   スタンドアロンモードで続行します")

    if not sheets_manager:
        print("\n⚠️  Google Sheets連携: 無効（スタンドアロンモード）")

    # RetryManager初期化
    manager = RetryManager(
        sheets_manager=sheets_manager, config=RetryConfig(max_attempts=3, base_delay=1.0, max_delay=60.0)
    )

    # デモタスク準備
    tasks = DemoTasks()

    # シナリオ実行
    await demo_scenario_1_network_recovery(manager, tasks)
    await demo_scenario_2_timeout_retry(manager, tasks)
    await demo_scenario_3_rate_limit(manager, tasks)
    await demo_scenario_4_non_retryable(manager, tasks)

    # 補足デモ
    await demo_classifier_showcase()
    await demo_strategy_showcase()

    # 最終統計
    print("\n" + "=" * 70)
    print("📊 RetryManager最終統計")
    print("=" * 70)

    stats = manager.get_statistics()
    print(f"\n総リトライ数: {stats['total_retries']}")
    print(f"成功: {stats['successful_retries']}")
    print(f"失敗: {stats['failed_retries']}")
    print(f"成功率: {stats['success_rate']}")

    print("\nErrorClassifier統計:")
    for key, value in stats["classifier_stats"].items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)

    if sheets_manager:
        print("\n💡 retry_historyシートで詳細な履歴を確認できます")
        print(f"   https://docs.google.com/spreadsheets/d/{os.getenv('SPREADSHEET_ID')}")

    print("\n" + "=" * 70)
    print("🎉 Week 5: 自己修復システム完全統合デモ完了")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

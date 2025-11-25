"""
Week 5: retry_history用のSheetsアダプター（最終修正版）

GoogleSheetsManagerの実際の構造に完全対応
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List

import gspread


class SheetsAdapter:
    """
    retry_historyシート専用アダプター

    GoogleSheetsManagerの実装に合わせて修正
    """

    def __init__(self, sheets_manager):
        """
        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.sheets_manager = sheets_manager
        self.sheet_name = "retry_log"
        self._sheet = None

    def _get_sheet(self):
        """retry_historyシートを取得（修正版）"""
        try:
            if self._sheet is None:
                # GoogleSheetsManagerのクライアントを初期化
                self.sheets_manager._ensure_client()

                # gspreadクライアントを取得
                # sheets_manager.gcがgspreadのクライアントの可能性
                if hasattr(self.sheets_manager, "gc"):
                    client = self.sheets_manager.gc
                elif hasattr(self.sheets_manager, "client"):
                    client = self.sheets_manager.client
                elif hasattr(self.sheets_manager, "gspread_client"):
                    client = self.sheets_manager.gspread_client
                else:
                    # setup_client()を呼んで初期化
                    self.sheets_manager.setup_client()

                    # 再度確認
                    if hasattr(self.sheets_manager, "gc"):
                        client = self.sheets_manager.gc
                    else:
                        raise AttributeError("gspreadクライアントが見つかりません")

                # スプレッドシートを開く
                spreadsheet = client.open_by_key(self.sheets_manager.spreadsheet_id)
                self._sheet = spreadsheet.worksheet(self.sheet_name)

            return self._sheet

        except gspread.exceptions.WorksheetNotFound:
            raise ValueError(
                f"'{self.sheet_name}' シートが見つかりません。"
                f"python3 scripts/create_retry_history_sheet.py を実行してください"
            )
        except Exception as e:
            raise RuntimeError(f"シート取得エラー: {e}")

    def ensure_sheet_exists(self) -> bool:
        """
        retry_historyシートが存在することを確認

        Returns:
            True: シート確認成功
            False: 失敗
        """
        try:
            self._get_sheet()
            return True
        except ValueError as e:
            print(f"❌ {e}")
            return False
        except Exception as e:
            print(f"❌ シート確認エラー: {e}")
            return False

    def record_retry(
        self,
        task_name: str,
        attempt: int,
        error_type: str,
        error_message: str,
        strategy_used: str,
        wait_time: float,
        success: bool,
        duration: float,
    ) -> bool:
        """
        リトライ履歴を記録

        Args:
            task_name: タスク名
            attempt: 試行回数
            error_type: エラー種別
            error_message: エラーメッセージ
            strategy_used: 使用した戦略
            wait_time: 待機時間(秒)
            success: 成功したか
            duration: 実行時間(秒)

        Returns:
            記録成功か
        """
        try:
            sheet = self._get_sheet()

            retry_id = str(uuid.uuid4())[:8]  # 短縮版UUID
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            row_data = [
                retry_id,
                timestamp,
                task_name,
                str(attempt),
                error_type,
                error_message[:200],  # 200文字まで
                strategy_used,
                f"{wait_time:.2f}",
                "SUCCESS" if success else "FAILED",
                f"{duration:.2f}",
            ]

            sheet.append_rows(row_data)
            return True

        except Exception as e:
            print(f"❌ リトライ履歴記録エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_recent_retries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        最近のリトライ履歴を取得

        Args:
            limit: 取得件数

        Returns:
            リトライ履歴のリスト
        """
        try:
            sheet = self._get_sheet()

            # 全データ取得（ヘッダー除く）
            all_values = sheet.get_all_values()[1:]

            # 最新N件を取得
            recent = all_values[-limit:] if len(all_values) > limit else all_values
            recent.reverse()  # 新しい順に

            # 辞書形式に変換
            headers = [
                "retry_id",
                "timestamp",
                "task_name",
                "attempt_number",
                "error_type",
                "error_message",
                "strategy_used",
                "wait_time_sec",
                "status",
                "duration_sec",
            ]

            result = []
            for row in recent:
                if len(row) >= len(headers):
                    result.append(dict(zip(headers, row)))

            return result

        except Exception as e:
            print(f"❌ 履歴取得エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    def get_retry_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        リトライ統計を取得

        Args:
            hours: 過去何時間分のデータを集計するか

        Returns:
            統計データ
        """
        try:
            sheet = self._get_sheet()
            all_values = sheet.get_all_values()[1:]  # ヘッダー除く

            from datetime import datetime, timedelta

            cutoff_time = datetime.now() - timedelta(hours=hours)

            stats = {
                "total_retries": 0,
                "success_count": 0,
                "failure_count": 0,
                "by_error_type": {},
                "by_strategy": {},
                "avg_wait_time": 0.0,
                "total_duration": 0.0,
            }

            total_wait = 0.0
            total_duration = 0.0

            for row in all_values:
                if len(row) < 10:
                    continue

                # タイムスタンプ確認
                try:
                    timestamp = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                    if timestamp < cutoff_time:
                        continue
                except:
                    continue

                stats["total_retries"] += 1

                # 成功/失敗
                if row[8] == "SUCCESS":
                    stats["success_count"] += 1
                else:
                    stats["failure_count"] += 1

                # エラー種別
                error_type = row[4]
                stats["by_error_type"][error_type] = stats["by_error_type"].get(error_type, 0) + 1

                # 戦略
                strategy = row[6]
                stats["by_strategy"][strategy] = stats["by_strategy"].get(strategy, 0) + 1

                # 待機時間・実行時間
                try:
                    total_wait += float(row[7])
                    total_duration += float(row[9])
                except:
                    pass

            # 平均値計算
            if stats["total_retries"] > 0:
                stats["avg_wait_time"] = total_wait / stats["total_retries"]
                stats["total_duration"] = total_duration

            return stats

        except Exception as e:
            print(f"❌ 統計取得エラー: {e}")
            import traceback

            traceback.print_exc()
            return {
                "total_retries": 0,
                "success_count": 0,
                "failure_count": 0,
                "by_error_type": {},
                "by_strategy": {},
            }


class RetryHistoryManager:
    """retry_history管理のヘルパークラス"""

    def __init__(self, sheets_manager):
        self.adapter = SheetsAdapter(sheets_manager)

    def log_retry_attempt(
        self,
        task_name: str,
        attempt: int,
        error: Exception,
        error_type: str,
        strategy: str,
        wait_time: float,
        success: bool,
        duration: float,
    ):
        """リトライ試行をログ"""
        return self.adapter.record_retry(
            task_name=task_name,
            attempt=attempt,
            error_type=error_type,
            error_message=str(error),
            strategy_used=strategy,
            wait_time=wait_time,
            success=success,
            duration=duration,
        )

    def show_recent_retries(self, limit: int = 5):
        """最近のリトライを表示"""
        retries = self.adapter.get_recent_retries(limit)

        print(f"\n📊 最近のリトライ履歴 (最新{limit}件)")
        print("=" * 80)

        if not retries:
            print("  (データなし)")

        for retry in retries:
            print(f"[{retry['timestamp']}] {retry['task_name']}")
            print(
                f"  試行: {retry['attempt_number']}回目 | "
                f"エラー: {retry['error_type']} | "
                f"戦略: {retry['strategy_used']}"
            )
            print(
                f"  結果: {retry['status']} | "
                f"待機: {retry['wait_time_sec']}秒 | "
                f"実行: {retry['duration_sec']}秒"
            )
            print()

    def show_stats(self, hours: int = 24):
        """統計を表示"""
        stats = self.adapter.get_retry_stats(hours)

        print(f"\n📈 リトライ統計 (過去{hours}時間)")
        print("=" * 60)
        print(f"総リトライ数: {stats['total_retries']}回")
        print(f"成功: {stats['success_count']}回 / " f"失敗: {stats['failure_count']}回")

        if stats["total_retries"] > 0:
            success_rate = (stats["success_count"] / stats["total_retries"]) * 100
            print(f"成功率: {success_rate:.1f}%")
            print(f"平均待機時間: {stats['avg_wait_time']:.2f}秒")

        if stats["by_error_type"]:
            print("\nエラー種別:")
            for error_type, count in stats["by_error_type"].items():
                print(f"  - {error_type}: {count}回")

        if stats["by_strategy"]:
            print("\n使用戦略:")
            for strategy, count in stats["by_strategy"].items():
                print(f"  - {strategy}: {count}回")

        print("=" * 60)

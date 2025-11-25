#!/usr/bin/env python3
"""
設定可能な同期マネージャー - 設定ファイルで簡単に変更可能
"""

import os
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gspread
from google.oauth2.service_account import Credentials

from configuration.config_loader import ConfigLoader
from configuration.sync_settings import *


class ConfigurableSyncManager:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.credentials = Credentials.from_service_account_file(
            self.config.get("service_account_file"), scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get("spreadsheet_id"))

        # 設定を読み込み
        self.auto_sync_enabled = AUTO_SYNC_ENABLED
        self.sync_interval = SYNC_INTERVAL_MINUTES
        self.max_rows = MAX_SYNC_ROWS

        print("⚙️ 同期設定:")
        print(f"   • 自動同期: {'✅ 有効' if self.auto_sync_enabled else '❌ 無効'}")
        print(f"   • 同期間隔: {self.sync_interval}分")
        print(f"   • 最大行数: {self.max_rows}行")

    def cleanup_old_data(self):
        """古いデータをクリーンアップ"""
        try:
            dashboard_sheet = self.spreadsheet.worksheet("progress_dashboard")
            data = dashboard_sheet.get_all_values()

            if len(data) > self.max_rows:
                # ヘッダーを保持して古いデータを削除
                data[0]
                keep_data = data[:1] + data[-(self.max_rows - 1) :]  # 最新のデータを保持
                dashboard_sheet.clear()
                dashboard_sheet.update(values=keep_data, range_name="A1:P" + str(len(keep_data)))
                print(f"🧹 データをクリーンアップ: {len(data)} → {len(keep_data)}行")

        except Exception as e:
            print(f"⚠️ クリーンアップエラー: {e}")

    def sync_progress(self):
        """進捗を同期"""
        print(f"\n🔄 同期実行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # データ取得
            goals_sheet = self.spreadsheet.worksheet("project_goal")
            tasks_sheet = self.spreadsheet.worksheet("pm_tasks")
            dashboard_sheet = self.spreadsheet.worksheet("progress_dashboard")

            goals_data = goals_sheet.get_all_values()
            tasks_data = tasks_sheet.get_all_values()

            # 統計計算
            active_goals = [
                row
                for row in goals_data[1:]
                if len(row) > 2 and row[2].lower() in ["active", "実行中", "in progress"]
            ]

            total_tasks = len(tasks_data) - 1 if len(tasks_data) > 1 else 0
            completed_tasks = sum(
                1 for row in tasks_data[1:] if len(row) > 4 and row[4].lower() == "completed"
            )
            progress_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            # 新しい行を作成
            new_row = [
                f'AUTO-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                f"自動同期 - {len(active_goals)}個のアクティブゴール",
                str(total_tasks),
                str(completed_tasks),
                f"{progress_rate:.1f}",
                "8.5",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Active",
                "2",
                "Configurable Sync",
                datetime.now().strftime("%Y-%m-%d"),
                (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "",
                "設定ファイルで管理",
                "低",
                "自動レポート",
            ]

            # データ追加
            dashboard_sheet.append_rows(new_row)

            # クリーンアップ
            self.cleanup_old_data()

            print(f"✅ 同期完了: {progress_rate:.1f}% ({completed_tasks}/{total_tasks} タスク)")
            return True

        except Exception as e:
            print(f"❌ 同期失敗: {e}")
            return False

    def run(self):
        """メイン実行"""
        if self.auto_sync_enabled:
            print("🚀 自動同期モードで起動")
            print(f"⏰ 同期間隔: {self.sync_interval}分")
            print("🛑 Ctrl+Cで停止")
            print("=" * 50)

            sync_count = 0
            try:
                while True:
                    success = self.sync_progress()
                    if success:
                        sync_count += 1

                    print(f"⏰ 次の同期まで{self.sync_interval}分待機...")
                    time.sleep(self.sync_interval * 60)

            except KeyboardInterrupt:
                print(f"\n✅ 自動同期を停止しました (総同期回数: {sync_count}回)")
        else:
            print("🔧 手動同期モード")
            self.sync_progress()
            print("\n💡 自動同期を有効にするには:")
            print("   configuration/sync_settings.py の")
            print("   AUTO_SYNC_ENABLED = False → True に変更")


def main():
    manager = ConfigurableSyncManager()
    manager.run()


if __name__ == "__main__":
    main()

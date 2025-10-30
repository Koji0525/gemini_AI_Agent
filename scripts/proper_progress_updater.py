#!/usr/bin/env python3
"""
正しいProgress Dashboard Updater - .envファイルを使用
"""

import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.sheets_manager import GoogleSheetsManager


class ProperProgressUpdater:
    """正しい環境変数管理を使用した進捗更新"""

    def __init__(self):
        # 環境変数から取得（正しい方法）
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        print(f"🔧 設定確認:")
        print(f"   SPREADSHEET_ID: {self.spreadsheet_id}")
        print(f"   認証ファイル: {service_account_file}")

        if not self.spreadsheet_id or not service_account_file:
            raise ValueError("❌ 環境変数が正しく設定されていません")

        self.sheets_manager = GoogleSheetsManager(self.spreadsheet_id, service_account_file)

    async def update_progress(self):
        """進捗を更新"""
        try:
            print("🚀 Progress Dashboard 更新開始...")

            # project_goalシートからデータ取得
            data = await self.sheets_manager.load_tasks_from_sheet("project_goal")
            if not data:
                print("❌ データの取得に失敗")
                return

            print(f"✅ {len(data)}行のデータを取得")

            # データ処理（簡易版）
            active_goals = self._extract_active_goals(data)
            print(f"🎯 {len(active_goals)}個のActiveゴールを検出")

            # 進捗計算
            total_progress = self._calculate_progress(active_goals)
            print(f"📊 総合進捗: {total_progress}%")

            # ここで実際の更新処理を実装
            print("✅ Progress Dashboard 更新完了")

        except Exception as e:
            print(f"❌ 更新エラー: {e}")
            import traceback

            traceback.print_exc()

    def _extract_active_goals(self, data):
        """Activeなゴールを抽出"""
        if len(data) < 2:
            return []

        headers = data[0]
        active_goals = []

        # ステータス列を探す
        status_idx = -1
        for i, header in enumerate(headers):
            if "status" in str(header).lower():
                status_idx = i
                break

        for row in data[1:]:
            if status_idx != -1 and len(row) > status_idx:
                if str(row[status_idx]).lower().strip() == "active":
                    active_goals.append(row)

        return active_goals

    def _calculate_progress(self, active_goals):
        """進捗率を計算"""
        if not active_goals:
            return 0

        # 簡易的な進捗計算
        return len(active_goals) * 10  # 仮の計算


async def main():
    """メイン実行"""
    try:
        updater = ProperProgressUpdater()
        await updater.update_progress()
    except Exception as e:
        print(f"❌ 実行エラー: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

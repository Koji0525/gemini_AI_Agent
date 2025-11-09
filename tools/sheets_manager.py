#!/usr/bin/env python3
"""
モック対応版スプレッドシートマネージャー - 環境変数完全対応版
"""
import logging
import os
from typing import Any, List

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """環境変数完全対応版スプレッドシートマネージャー"""

    def __init__(self, spreadsheet_id: str = None):
        # 環境変数から設定を取得
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID", "test_spreadsheet_id")
        self.service_account_file = os.getenv(
            "GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json"
        )
        self._service = None
        self._is_test_mode = os.getenv("TEST_MODE", "False").lower() == "true"

        logger.info(f"🧪 モード: {'テスト' if self._is_test_mode else '本番'}")
        logger.info(f"📊 スプレッドシートID: {self.spreadsheet_id}")
        logger.info(f"🔑 サービスアカウントファイル: {self.service_account_file}")

        if not self._is_test_mode:
            self._initialize_service()
        else:
            logger.info("✅ テストモード: モックデータを使用します")

    def _initialize_service(self):
        """Google Sheetsサービスを初期化（本番環境のみ）"""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            # サービスアカウントファイルから認証
            if os.path.exists(self.service_account_file):
                credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_file,
                    scopes=["https://www.googleapis.com/auth/spreadsheets"],
                )
                self._service = build("sheets", "v4", credentials=credentials)
                logger.info("✅ Google Sheetsサービス初期化成功（サービスアカウントファイル使用）")
            else:
                logger.warning(
                    f"⚠️ サービスアカウントファイルが見つかりません: {self.service_account_file}"
                )
                logger.info("🔄 テストモードにフォールバックします")
                self._is_test_mode = True

        except Exception as e:
            logger.warning(f"⚠️ Google Sheetsサービス初期化失敗: {e}")
            logger.info("🔄 テストモードにフォールバックします")
            self._is_test_mode = True

    def _get_mock_data(self, range_name: str) -> List[List[Any]]:
        """モックデータを取得"""
        mock_data = {
            "会話ログ!A2:C100": [
                ["2024-01-01 10:00:00", "user", "こんにちは"],
                ["2024-01-01 10:00:01", "assistant", "こんにちは！どのようにお手伝いできますか？"],
                ["2024-01-01 10:00:02", "user", "Pythonのエラーについて教えてください"],
            ],
            "タスクログ!A2:C100": [
                ["タスク001", "完了", "2024-01-01"],
                ["タスク002", "進行中", "2024-01-01"],
                ["タスク003", "未着手", "2024-01-01"],
            ],
            "pm_tasks!A2:Z100": [
                ["プロジェクトA", "設計", "高", "2024-01-01", "2024-01-10"],
                ["プロジェクトB", "実装", "中", "2024-01-02", "2024-01-15"],
            ],
        }

        # 範囲名に基づいてモックデータを返す
        for key, data in mock_data.items():
            if range_name.startswith(key.split("!")[0]):
                logger.info(f"🧪 モックデータを返します: {range_name} -> {len(data)}行")
                return data

        # デフォルトのモックデータ
        logger.info(f"🧪 デフォルトモックデータを返します: {range_name}")
        return [["モックデータ", "テスト値"]]

    def read_range(self, range_name: str, default: Any = None) -> Any:
        """範囲を読み取る（モック対応版）"""
        if self._is_test_mode:
            return self._get_mock_data(range_name)

        if not self._service:
            logger.error("❌ Google Sheetsサービスが利用できません")
            return default or []

        try:
            result = (
                self._service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )

            values = result.get("values", [])
            logger.info(f"✅ スプレッドシート読み取り成功: {range_name} - {len(values)}行")
            return values

        except Exception as e:
            logger.error(f"❌ スプレッドシート読み取りエラー: {e}")
            return default or []

    def append_rows(self, range_name: str, values: List[List[Any]]) -> bool:
        """行を追加（モック対応版）"""
        if self._is_test_mode:
            logger.info(
                f"🧪 モックモード: 範囲 '{range_name}' に {len(values)}行 追加をシミュレート"
            )
            logger.info(f"🧪 追加データ: {values}")
            return True

        if not self._service:
            logger.error("❌ Google Sheetsサービスが利用できません")
            return False

        try:
            body = {"values": values}
            result = (
                self._service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )

            logger.info(f"✅ スプレッドシート追加成功: {range_name}")
            return True

        except Exception as e:
            logger.error(f"❌ スプレッドシート追加エラー: {e}")
            return False

    def update_range(self, range_name: str, values: List[List[Any]]) -> bool:
        """範囲を更新（モック対応版）"""
        if self._is_test_mode:
            logger.info(f"🧪 モックモード: 範囲 '{range_name}' の更新をシミュレート")
            return True

        if not self._service:
            logger.error("❌ Google Sheetsサービスが利用できません")
            return False

        try:
            body = {"values": values}
            result = (
                self._service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )

            logger.info(f"✅ スプレッドシート更新成功: {range_name}")
            return True

        except Exception as e:
            logger.error(f"❌ スプレッドシート更新エラー: {e}")
            return False


# テスト用
if __name__ == "__main__":
    # テストモードで実行
    import os

    os.environ["TEST_MODE"] = "true"

    manager = GoogleSheetsManager()
    print("✅ 環境変数対応版スプレッドシートマネージャー動作確認")

    # テスト読み取り
    data = manager.read_range("会話ログ!A2:C10")
    print(f"会話ログ: {len(data)}行")

    # テスト追加
    success = manager.append_rows("テストシート!A1", [["新しいデータ"]])
    print(f"追加結果: {success}")

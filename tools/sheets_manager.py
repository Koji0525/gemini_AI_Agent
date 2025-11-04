import logging
from typing import List, Dict, Any
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from configuration.sheet_mapping import SheetMapping

"""
sheets_manager_v02_mapped.py

シート名マッピング対応版SheetsManager

【変更の理由】
- コード内の論理名と実際のシート名の不一致を解消
- configuration/sheet_mapping.pyを使用してシート名を解決
- 既存のスプレッドシート構造を破壊せずに統合
"""


# プロジェクトルート追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


load_dotenv()
logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """Google Sheets管理（マッピング対応版）"""

    def __init__(self, spreadsheet_id: str = None, service_account_file: str = None):
        """
        初期化

        Args:
            spreadsheet_id: スプレッドシートID（省略時は環境変数から取得）
            service_account_file: サービスアカウントファイルパス
        """
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID")
        self.service_account_file = service_account_file or os.getenv(
            "GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json"
        )

        if not self.spreadsheet_id:
            raise ValueError("SPREADSHEET_IDが設定されていません")

        if not Path(self.service_account_file).exists():
            raise FileNotFoundError(f"{self.service_account_file} が見つかりません")

        # 認証
        self.creds = Credentials.from_service_account_file(
            self.service_account_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )

        self.service = build("sheets", "v4", credentials=self.creds)
        self.sheet_mapping = SheetMapping()

        logger.info(f"✅ SheetsManager初期化完了 (ID: {self.spreadsheet_id[:8]}...)")

    def _resolve_sheet_name(self, logical_name: str) -> str:
        """
        論理名を実際のシート名に解決

        Args:
            logical_name: コード内で使用する論理名

        Returns:
            実際のシート名
        """
        actual_name = self.sheet_mapping.get(logical_name)

        if actual_name != logical_name:
            logger.debug(f"📊 シート名解決: {logical_name} → {actual_name}")

        return actual_name

    def read_range(self, range_str: str, logical_sheet: bool = True) -> List[List[Any]]:
        """
        範囲を読み取り

        Args:
            range_str: 範囲文字列（例: "pm_goals!A1:F10"）
            logical_sheet: Trueの場合、シート名を論理名として解決

        Returns:
            データ（2次元リスト）
        """
        try:
            # シート名解決
            if logical_sheet and "!" in range_str:
                sheet_part, cell_part = range_str.split("!", 1)
                resolved_sheet = self._resolve_sheet_name(sheet_part)
                range_str = f"{resolved_sheet}!{cell_part}"

            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_str)
                .execute()
            )

            values = result.get("values", [])
            logger.debug(f"✅ 読み取り成功: {range_str} ({len(values)}行)")

            return values

        except HttpError as e:
            logger.error(f"❌ 読み取りエラー: {e}")
            raise

    def write_range(
        self, range_str: str, values: List[List[Any]], logical_sheet: bool = True
    ) -> Dict:
        """
        範囲に書き込み
    def update_cell(self, sheet_name: str, cell_range: str, value=None, **kwargs):
        """指定したセルを更新する
        
        Args:
            sheet_name: シート名
            cell_range: セル範囲 (例: 'A1')
            value: 設定する値
            **kwargs: 互換性のための追加引数
        """
        # cell_addressが指定された場合はcell_rangeとして使用
        if 'cell_address' in kwargs:
            cell_range = kwargs['cell_address']
        
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            sheet.update(cell_range, [[value]])
            self.logger.info(f"📊 セル更新完了: {sheet_name}!{cell_range} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"❌ セル更新失敗: {sheet_name}!{cell_range} - {e}")
            return False


    (self, sheet_name: str, cell_range: str, value=None, **kwargs):
        """指定したセルを更新する（柔軟な引数対応）
        
        Args:
            sheet_name: シート名
            cell_range: セル範囲 (例: 'A1')
            value: 設定する値
            **kwargs: 互換性のための追加引数 (cell_addressなど)
        """
        # cell_addressが指定された場合はcell_rangeとして使用
        if 'cell_address' in kwargs:
            cell_range = kwargs['cell_address']
        
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            sheet.update(cell_range, [[value]])
            self.logger.info(f"📊 セル更新完了: {sheet_name}            return True
        except Exception as e:
            self.logger.error(f"❌ セル更新失敗: {sheet_name}!{cell_range} - {e}")
            return False
            return True
        except Exception as e:
            self.logger.error(f"❌ セル更新失敗: {sheet_name}!{cell_range} - {e}")
            return False
            return True
        except Exception as e:
            self.logger.error(f"❌ セル更新失敗: {sheet_name}!{cell_range} - {e}")
            return False

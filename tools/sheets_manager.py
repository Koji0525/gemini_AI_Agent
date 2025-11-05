import logging
import os
from pathlib import Path
from typing import Any, List, Optional

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger("sheets_manager")


class GoogleSheetsManager:
    """Google Sheets management class with adaptive initialization"""

    def __init__(self, spreadsheet_id: str = None):
        """Initialize with flexible credential path detection"""
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID")
        self.client = None
        self._initialize_client()

    def _find_credentials_file(self) -> Optional[str]:
        """Find credentials file with environment variable support"""
        candidates = [
            os.getenv("GOOGLE_CREDENTIALS_PATH"),  # 🔥 環境変数優先
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            "credentials.json",
            ".credentials/credentials.json",
            "configuration/service_account.json",
            os.path.expanduser("~/.credentials/credentials.json"),
        ]

        for path in candidates:
            if path and Path(path).exists():
                logger.info(f"✅ Found credentials at: {path}")
                return path

        logger.warning("❌ No credentials file found")
        return None

    def _initialize_client(self):
        """Initialize Google Sheets client with error handling"""
        try:
            creds_path = self._find_credentials_file()

            if not creds_path:
                logger.error("❌ credentials.json not found. Please provide valid credentials.")
                logger.info("📝 Expected locations:")
                logger.info("   1. Set GOOGLE_CREDENTIALS_PATH env var")
                logger.info("   2. ./credentials.json")
                logger.info("   3. ./configuration/service_account.json")
                return

            scope = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            self.client = gspread.authorize(creds)
            logger.info(f"✅ Google Sheets client initialized with {creds_path}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Sheets client: {e}")
            self.client = None

    def _resolve_sheet_name(self, logical_name: str) -> str:
        """Resolve logical sheet name to actual sheet name"""
        sheet_mapping = {
            "pm_tasks": "pm_tasks",
            "project_goals": "project_goals",
            "knowledge_base": "knowledge_base",
            "task_execution_log": "task_execution_log",
        }
        return sheet_mapping.get(logical_name, logical_name)

    def read_range(self, sheet_name: str, range_name: str = None) -> List[List[Any]]:
        """Read data from specified range"""
        if not self.client:
            logger.warning("⚠️  Client not initialized - returning empty data")
            return []

        try:
            if "!" in sheet_name and not range_name:
                sheet_name, range_name = sheet_name.split("!", 1)

            actual_sheet_name = self._resolve_sheet_name(sheet_name)
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(actual_sheet_name)

            data = sheet.get(range_name) if range_name else sheet.get_all_values()
            logger.info(f"✅ Read {len(data)} rows from {actual_sheet_name}")
            return data

        except Exception as e:
            logger.error(f"❌ Failed to read {sheet_name}: {e}")
            return []

    def write_range(self, sheet_name: str, range_name: str, data: List[List[Any]]) -> bool:
        """Write data to specified range"""
        if not self.client:
            logger.warning("⚠️  Client not initialized - skipping write")
            return False

        try:
            actual_sheet_name = self._resolve_sheet_name(sheet_name)
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(actual_sheet_name)
            sheet.update(range_name, data)
            logger.info(f"✅ Wrote data to {actual_sheet_name}!{range_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to write {sheet_name}: {e}")
            return False

    def update_cell(self, sheet_name: str, cell_range: str, value: Any = None, **kwargs) -> bool:
        """Update specific cell"""
        if not self.client:
            logger.warning("⚠️  Client not initialized - skipping update")
            return False

        if "cell_address" in kwargs:
            cell_range = kwargs["cell_address"]

        try:
            actual_sheet_name = self._resolve_sheet_name(sheet_name)
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(actual_sheet_name)
            sheet.update(cell_range, [[value]])
            logger.info(f"✅ Updated {actual_sheet_name}!{cell_range}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update cell: {e}")
            return False

    def append_rows(self, sheet_name: str, data: List[List[Any]]) -> bool:
        """Append rows to sheet"""
        if not self.client:
            logger.warning("⚠️  Client not initialized - skipping append")
            return False

        try:
            actual_sheet_name = self._resolve_sheet_name(sheet_name)
            sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(actual_sheet_name)
            sheet.append_rows(data)
            logger.info(f"✅ Appended {len(data)} rows to {actual_sheet_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to append rows: {e}")
            return False

    def is_ready(self) -> bool:
        """Check if client is ready to use"""
        return self.client is not None

"""
system_health_checker.py v2

システムヘルスチェック（改善版）
"""

import logging
from typing import List, Tuple
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class SystemHealthChecker:
    """システムヘルスチェッカー v2"""

    def __init__(self, sheets_manager=None):
        self.sheets_manager = sheets_manager
        self.issues = []
        self.fixes_applied = []

    def run_full_check(self) -> Tuple[bool, List[str], List[str]]:
        """完全ヘルスチェック"""
        logger.info("=" * 60)
        logger.info("🏥 システムヘルスチェック開始")
        logger.info("=" * 60)

        self.issues = []
        self.fixes_applied = []

        # 1. 認証情報チェック
        self._check_credentials()

        # 2. スプレッドシート構造チェック（利用可能な場合のみ）
        if self.sheets_manager:
            self._check_spreadsheet_structure()

        # 3. 環境変数チェック
        self._check_environment_variables()

        # 4. 必須ファイルチェック
        self._check_required_files()

        # 結果サマリー
        logger.info("=" * 60)
        if not self.issues:
            logger.info("✅ システムは健全です")
        else:
            logger.warning(f"⚠️  {len(self.issues)}個の問題を検出")
            for issue in self.issues:
                logger.warning(f"   - {issue}")

        if self.fixes_applied:
            logger.info(f"🔧 {len(self.fixes_applied)}個の修正を適用")
            for fix in self.fixes_applied:
                logger.info(f"   - {fix}")

        logger.info("=" * 60)

        return len(self.issues) == 0, self.issues, self.fixes_applied

    def _check_credentials(self):
        """認証情報チェック"""
        from tools.credentials_manager import CredentialsManager

        manager = CredentialsManager()
        if not manager.ensure_credentials():
            self.issues.append("認証情報が見つかりません")
        elif not manager.validate_credentials():
            self.issues.append("認証情報が不正です")
        else:
            logger.info(f"   ✅ 認証情報OK: {manager.credentials_path}")

    def _check_spreadsheet_structure(self):
        """スプレッドシート構造チェック"""
        required_sheets = ["pm_tasks", "project_goal", "progress_dashboard"]
        optional_sheets = ["control_flags", "error_log", "execution_history"]

        for sheet_name in required_sheets:
            try:
                self.sheets_manager.read_range(f"{sheet_name}!A1:A1")
                logger.info(f"   ✅ {sheet_name} シート確認")
            except Exception as e:
                self.issues.append(f"{sheet_name}シートが存在しないか読み取れません")
                logger.warning(f"   ⚠️ {sheet_name} 問題: {str(e)[:100]}")

        for sheet_name in optional_sheets:
            try:
                self.sheets_manager.read_range(f"{sheet_name}!A1:A1")
                logger.info(f"   ✅ {sheet_name} シート確認（オプション）")
            except Exception:
                logger.info(f"   ℹ️ {sheet_name} 未作成（オプション）")

    def _check_environment_variables(self):
        """環境変数チェック"""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        required_vars = ["SPREADSHEET_ID", "GOOGLE_SERVICE_ACCOUNT_FILE"]

        for var in required_vars:
            value = os.getenv(var)
            if not value:
                self.issues.append(f"環境変数 {var} が設定されていません")
                logger.warning(f"   ⚠️ {var} 未設定")
            else:
                logger.info(f"   ✅ {var} 設定済み")

    def _check_required_files(self):
        """必須ファイルチェック"""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        service_account_file = os.getenv(
            "GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json"
        )

        required_files = [service_account_file, "requirements.txt", ".env"]

        for file in required_files:
            if not Path(file).exists():
                self.issues.append(f"必須ファイル {file} が見つかりません")
                logger.warning(f"   ⚠️ {file} 不在")
            else:
                logger.info(f"   ✅ {file} 存在")


def run_health_check(sheets_manager=None) -> bool:
    """ヘルスチェック実行"""
    checker = SystemHealthChecker(sheets_manager)
    healthy, issues, fixes = checker.run_full_check()
    return healthy


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_health_check()
    exit(0 if result else 1)

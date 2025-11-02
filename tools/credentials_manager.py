"""
credentials_manager.py v2

認証情報管理システム（.env対応版）

【修正理由】
- credentials.jsonではなくconfiguration/service_account.json
- .envファイルのGOOGLE_SERVICE_ACCOUNT_FILEから読み取り
"""

import json
import logging
from pathlib import Path
import os
from dotenv import load_dotenv

# .envファイル読み込み
load_dotenv()

logger = logging.getLogger(__name__)


class CredentialsManager:
    """認証情報管理 v2"""

    def __init__(self):
        # .envから認証ファイルパスを取得
        self.service_account_file = os.getenv(
            "GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json"
        )
        self.credentials_path = Path(self.service_account_file)

    def ensure_credentials(self) -> bool:
        """
        認証情報の存在確認

        Returns:
            bool: 利用可能かどうか
        """
        # 既存ファイル確認
        if self.credentials_path.exists():
            logger.info(f"✅ {self.credentials_path} 存在")
            return True

        # credentials.jsonも確認
        alt_path = Path("credentials.json")
        if alt_path.exists():
            logger.info(f"✅ {alt_path} 存在")
            self.credentials_path = alt_path
            return True

        # 環境変数から生成
        google_creds = os.getenv("GOOGLE_CREDENTIALS")
        if google_creds:
            try:
                creds_dict = json.loads(google_creds)

                # ディレクトリ作成
                self.credentials_path.parent.mkdir(parents=True, exist_ok=True)

                # ファイルに書き込み
                with open(self.credentials_path, "w") as f:
                    json.dump(creds_dict, f, indent=2)

                logger.info(f"✅ 環境変数から {self.credentials_path} 生成")
                return True
            except Exception as e:
                logger.error(f"❌ 認証ファイル生成エラー: {e}")

        logger.error("❌ 認証ファイルが見つかりません")
        logger.info("💡 確認してください:")
        logger.info(f"   1. {self.credentials_path} が存在するか")
        logger.info("   2. .envファイルのGOOGLE_SERVICE_ACCOUNT_FILEが正しいか")
        logger.info("   3. GOOGLE_CREDENTIALS環境変数が設定されているか")

        return False

    def validate_credentials(self) -> bool:
        """認証情報を検証"""
        if not self.credentials_path.exists():
            return False

        try:
            with open(self.credentials_path, "r") as f:
                creds = json.load(f)

            required_fields = ["type", "project_id", "private_key", "client_email"]
            for field in required_fields:
                if field not in creds:
                    logger.error(f"❌ {field} がありません")
                    return False

            logger.info(f"✅ {self.credentials_path} 検証成功")
            return True

        except Exception as e:
            logger.error(f"❌ 認証ファイル検証エラー: {e}")
            return False


def main():
    """メイン実行"""
    manager = CredentialsManager()

    print(f"🔍 認証ファイル確認: {manager.credentials_path}")

    if manager.ensure_credentials():
        if manager.validate_credentials():
            print("✅ 認証情報OK")
            return 0
        else:
            print("❌ 認証情報が不正です")
            return 1
    else:
        print("❌ 認証情報が見つかりません")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exit(main())

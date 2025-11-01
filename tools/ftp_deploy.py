#!/usr/bin/env python3
"""
FTP経由デプロイ - 確実な方法
"""

import os
import sys
from ftplib import FTP
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def ftp_deploy():
    """FTP経由でfunctions.phpを直接アップロード"""

    # FTP設定取得
    ftp_host = os.getenv("FTP_HOST", "uzbek-ma.com")
    ftp_user = os.getenv("FTP_USER")
    ftp_pass = os.getenv("FTP_PASS")
    ftp_path = os.getenv("FTP_PATH", "/public_html/wp-content/themes/cocoon-child-master/")

    if not all([ftp_user, ftp_pass]):
        print("❌ FTP認証情報が設定されていません")
        print("💡 .envファイルに以下を追加してください:")
        print("   FTP_USER=your_username")
        print("   FTP_PASS=your_password")
        return False

    # ソースファイル読み込み
    source = Path("wordpress_projects/ma_portal/functions_additions_complete.php")

    if not source.exists():
        print(f"❌ ソースファイルが見つかりません: {source}")
        return False

    try:
        print(f"📡 FTP接続中: {ftp_host}")
        ftp = FTP(ftp_host)
        ftp.login(ftp_user, ftp_pass)
        ftp.cwd(ftp_path)

        print(f"✅ FTP接続成功")
        print(f"📂 ディレクトリ: {ftp_path}")

        # バックアップ作成
        try:
            print("💾 既存ファイルをバックアップ中...")
            ftp.rename("functions.php", f"functions.php.bak.{int(os.time())}")
            print("✅ バックアップ完了")
        except:
            print("⚠️  既存ファイルなし（新規作成）")

        # アップロード
        print(f"📤 アップロード中: {source.name}")
        with open(source, "rb") as f:
            ftp.storbinary(f"STOR functions.php", f)

        print("✅ アップロード完了")

        ftp.quit()

        print("")
        print("============================================================")
        print("🎉 デプロイ成功！")
        print("============================================================")
        print("🌐 動作確認URL:")
        print("   https://uzbek-ma.com/企業検索/")
        print("   https://uzbek-ma.com/ma-search-results/")

        return True

    except Exception as e:
        print(f"❌ FTPエラー: {e}")
        return False


if __name__ == "__main__":
    import time

    os.time = lambda: time.time()
    success = ftp_deploy()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
FTP経由デプロイ - 修正版
"""

import os
import sys
import time
from ftplib import FTP
from pathlib import Path


def ftp_deploy():
    """FTP経由でfunctions.phpを直接アップロード"""

    # 環境変数を直接読み込み
    env_path = Path(".env")
    env_vars = {}

    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

    ftp_host = env_vars.get("FTP_HOST")
    ftp_user = env_vars.get("FTP_USER")
    ftp_pass = env_vars.get("FTP_PASS")
    ftp_path = env_vars.get("FTP_PATH")

    print(f"📋 設定確認:")
    print(f"   ホスト: {ftp_host}")
    print(f"   ユーザー: {ftp_user}")
    print(f"   パス: {ftp_path}")
    print("")

    if not all([ftp_host, ftp_user, ftp_pass, ftp_path]):
        print("❌ FTP設定が不完全です")
        return False

    # ソースファイル読み込み
    source = Path("wordpress_projects/ma_portal/functions_additions_complete.php")

    if not source.exists():
        print(f"❌ ソースファイルが見つかりません: {source}")
        return False

    print(f"📄 ソースファイル: {source}")
    print(f"📊 ファイルサイズ: {source.stat().st_size} bytes")
    print("")

    try:
        print(f"📡 FTP接続中: {ftp_host}")
        ftp = FTP(ftp_host)
        ftp.login(ftp_user, ftp_pass)
        print("✅ FTP接続成功")

        print(f"📂 ディレクトリ移動: {ftp_path}")
        ftp.cwd(ftp_path)
        print("✅ ディレクトリ移動成功")

        # 現在のディレクトリ確認
        print(f"📂 現在地: {ftp.pwd()}")
        print("")

        # バックアップ作成
        backup_name = f"functions.php.bak.{int(time.time())}"
        try:
            print(f"💾 バックアップ作成中: {backup_name}")
            ftp.rename("functions.php", backup_name)
            print("✅ バックアップ完了")
        except Exception as e:
            print(f"⚠️  バックアップスキップ: {e}")

        # アップロード
        print(f"📤 アップロード中...")
        with open(source, "rb") as f:
            ftp.storbinary("STOR functions.php", f)

        print("✅ アップロード完了")

        # 確認
        files = []
        ftp.retrlines("NLST", files.append)
        if "functions.php" in files:
            print("✅ functions.php 確認")

        ftp.quit()

        print("")
        print("=" * 60)
        print("🎉 デプロイ成功！")
        print("=" * 60)
        print("")
        print("🌐 動作確認URL:")
        print("   https://uzbek-ma.com/企業検索/")
        print("   https://uzbek-ma.com/ma-search-results/")
        print("")

        return True

    except Exception as e:
        print(f"❌ FTPエラー: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = ftp_deploy()
    sys.exit(0 if success else 1)

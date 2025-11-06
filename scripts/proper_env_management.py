#!/usr/bin/env python3
"""
正しい環境変数管理 - .envファイルを使用
"""

import os
from dotenv import load_dotenv


def setup_environment():
    """環境変数を正しく設定"""
    # .envファイルを読み込み
    load_dotenv()

    # 環境変数の確認

    # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
    required_vars = {
        "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "SPREADSHEET_ID": os.getenv("SPREADSHEET_ID"),
    }

    print("🔧 環境変数設定確認:")
    for key, value in required_vars.items():
        if value:
            print(f"   ✅ {key}: 設定済み")
        else:
            print(f"   ❌ {key}: 未設定")

    return all(required_vars.values())


if __name__ == "__main__":
    if setup_environment():
        print("✅ 環境変数設定完了")
    else:
        print("❌ 環境変数の設定が必要です")

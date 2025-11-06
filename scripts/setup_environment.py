#!/usr/bin/env python3
"""
環境変数設定スクリプト
すべてのスクリプトで確実に環境変数を利用できるようにする
"""

import os
import sys


def setup_environment():
    """環境変数を設定"""
    # 必須環境変数
    env_vars = {
        "GOOGLE_APPLICATION_CREDENTIALS": "/workspaces/gemini_AI_Agent/configuration/service_account.json",
        "SPREADSHEET_ID": "1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s",
    }

    print("🔧 環境変数設定中...")

    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   ✅ {key} = {value}")

    print("✅ 環境変数設定完了")

    # 設定確認

    # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
    print("\n�� 設定確認:")
    for key in env_vars.keys():
        value = os.getenv(key)
        print(f"   {key}: {value}")

    return True


if __name__ == "__main__":
    setup_environment()

"""
Day 2 テストスクリプト
functions.php自動更新のテスト
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# プロジェクトルートをパスに追加
project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)

from automation.modules.wp_file_manager import WPFileManager


async def test_file_manager():
    """ファイルマネージャーテスト"""
    print("🧪 Day 2 テスト開始: functions.php自動更新")
    print("=" * 50)

    file_manager = WPFileManager()

    # セットアップテスト
    print("1. 🔧 ブラウザセットアップテスト")
    setup_success = await file_manager.setup()
    if not setup_success:
        print("❌ セットアップテスト失敗")
        return False
    print("✅ セットアップテスト成功")

    # ログインテスト
    print("2. 🔐 WordPressログインテスト")
    login_success = await file_manager.login_to_wordpress()
    if not login_success:
        print("❌ ログインテスト失敗")
        return False
    print("✅ ログインテスト成功")

    # ファイルマネージャーテスト
    print("3. 📁 ファイルマネージャーアクセステスト")
    access_success = await file_manager.access_file_manager()
    if not access_success:
        print("❌ ファイルマネージャーテスト失敗")
        return False
    print("✅ ファイルマネージャーテスト成功")

    # コード生成テスト
    print("4. ⚙️ DDコード生成テスト")
    dd_code = await file_manager.generate_dd_code()
    if dd_code and "DD（データドリブン）機能" in dd_code:
        print("✅ DDコード生成テスト成功")
        print(f"   生成コード長: {len(dd_code)} 文字")
    else:
        print("❌ DDコード生成テスト失敗")
        return False

    print("=" * 50)
    print("🎉 Day 2 基本テスト完了")
    print("💡 本番実行: python3 automation/modules/wp_file_manager.py")

    # クリーンアップ
    await file_manager.browser.cleanup()
    return True


if __name__ == "__main__":
    success = asyncio.run(test_file_manager())
    if success:
        print("🚀 すべてのテストが成功しました！")
    else:
        print("❌ テストに失敗しました")

"""
Day 2 テストスクリプト - 改善版
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

from automation.modules.wp_file_manager_v2 import WPFileManagerV2


async def test_file_manager_v2():
    """ファイルマネージャーテスト - 改善版"""
    print("🧪 Day 2 テスト開始: functions.php自動更新 (改善版)")
    print("=" * 50)

    file_manager = WPFileManagerV2()

    try:
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

        # テーマエディターテスト
        print("3. 🎨 テーマエディターアクセステスト")
        editor_success = await file_manager.access_theme_editor()
        if not editor_success:
            print("❌ テーマエディターテスト失敗")
            return False
        print("✅ テーマエディターテスト成功")

        # 権限チェックテスト
        print("4. 🔐 ファイル権限チェックテスト")
        permission_success = await file_manager.check_file_permissions()
        if not permission_success:
            print("❌ 権限チェックテスト失敗")
            return False
        print("✅ 権限チェックテスト成功")

        # コード生成テスト
        print("5. ⚙️ DDコード生成テスト")
        dd_code = await file_manager.generate_dd_code()
        if dd_code and "DD（データドリブン）機能" in dd_code:
            print("✅ DDコード生成テスト成功")
            print(f"   生成コード長: {len(dd_code)} 文字")
        else:
            print("❌ DDコード生成テスト失敗")
            return False

        print("=" * 50)
        print("🎉 Day 2 基本テスト完了")
        print("💡 本番実行: python3 automation/modules/wp_file_manager_v2.py")

        return True

    except Exception as e:
        print(f"❌ テスト中にエラーが発生: {e}")
        return False
    finally:
        # クリーンアップ
        if file_manager.browser:
            await file_manager.browser.cleanup()


if __name__ == "__main__":
    success = asyncio.run(test_file_manager_v2())
    if success:
        print("🚀 すべてのテストが成功しました！")
    else:
        print("❌ テストに失敗しました")

#!/usr/bin/env python3
"""
WordPress自動操作テスト
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.wordpress.wp_auto_config_agent import WPAutoConfigAgent
from browser_control.browser_controller import BrowserController


@pytest.mark.asyncio
async def test_wordpress_automation():
    """WordPress自動操作のテスト"""

    print("=" * 60)
    print("🚀 WordPress自動操作テスト開始")
    print("=" * 60)

    # ブラウザコントローラー初期化
    browser = BrowserController()
    await browser.initialize()

    # WP AutoConfig Agent初期化
    wp_agent = WPAutoConfigAgent(browser)

    try:
        # STEP 1: 管理画面に自動ログイン
        print("\n[STEP 1] WordPress管理画面に自動ログイン...")
        login_success = await wp_agent.login()
        print(f"  ✅ ログイン成功" if login_success else "  ❌ ログイン失敗")

        # STEP 2: functions.phpの存在確認
        print("\n[STEP 2] functions.phpの確認...")
        functions_exists = await wp_agent.check_functions_php()
        print(f"  ✅ functions.php確認完了" if functions_exists else "  ❌ ファイルなし")

        # STEP 3: DD機能コードの追加
        print("\n[STEP 3] DD機能コードの自動追加...")

        # 既存のfunctions.phpを読み込み
        await wp_agent.get_current_functions_php()

        # 新しいコードを追加（Phase 24のDDコード）
        with open("/tmp/functions_dd_ultimate.php", "r") as f:
            new_code = f.read()

        update_success = await wp_agent.update_functions_php(new_code)
        print(f"  ✅ コード更新成功" if update_success else "  ❌ 更新失敗")

        # STEP 4: 動作確認
        print("\n[STEP 4] 更新後の動作確認...")
        verification = await wp_agent.verify_site_working()
        print(f"  ✅ サイト正常動作" if verification else "  ❌ エラー発生")

        print("\n" + "=" * 60)
        print("🎉 WordPress自動操作テスト完了")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        return False

    finally:
        await browser.cleanup()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_wordpress_automation())

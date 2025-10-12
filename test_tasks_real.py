#!/usr/bin/env python3
"""
実際にブラウザを起動してWordPressにアクセスするテスト
"""
import asyncio
from browser_controller import BrowserController
from wordpress.wp_agent import WPAgent

async def main():
    print("🚀 ブラウザ起動テスト開始")
    
    # 1. ブラウザコントローラー初期化
    browser = BrowserController()
    await browser.initialize()
    
    # 2. WordPressにアクセス
    wp = WPAgent(
        wp_url="http://localhost:8080",
        username="admin",
        password="admin",
        browser_controller=browser
    )
    
    # 3. ログイン
    print("🔐 WordPressにログイン中...")
    await wp.login()
    
    # 4. ダッシュボードを確認
    print("📊 ダッシュボードにアクセス中...")
    await wp.navigate_to_dashboard()
    
    # 5. プラグイン一覧を確認
    print("🔌 プラグイン一覧を確認中...")
    plugins = await wp.get_installed_plugins()
    print(f"インストール済みプラグイン: {len(plugins)}個")
    
    print("✅ テスト完了！")
    
    # クリーンアップ
    await browser.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

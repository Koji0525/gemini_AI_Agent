#!/usr/bin/env python3
"""DevAgent + BrowserController 統合テスト"""
import asyncio
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_dev_agent_with_browser():
    print("�� DevAgent + Browser 統合テスト")
    print("=" * 70)
    
    try:
        # BrowserController準備
        print("\n📦 Step 1/4: BrowserController準備")
        from browser_control.browser_controller import EnhancedBrowserController
        browser = EnhancedBrowserController(
            download_folder=Path("temp_workspace/downloads"),
            mode="text",
            service="google"
        )
        await browser.setup_browser()
        print("   ✅ BrowserController起動")
        
        # DevAgentインポート
        print("\n📦 Step 2/4: DevAgentインポート")
        from core_agents.dev_agent import DevAgent
        dev_agent = DevAgent(
            browser_controller=browser,
            output_folder=Path("agent_outputs/dev")
        )
        print("   ✅ DevAgent初期化")
        print(f"   ブラウザ設定: {dev_agent.browser is not None}")
        
        # メソッド確認
        print("\n🔍 Step 3/4: メソッド確認")
        required_methods = ['send_prompt', 'wait_for_text_generation', 'extract_latest_text_response']
        for method in required_methods:
            has_method = hasattr(dev_agent.browser, method) and callable(getattr(dev_agent.browser, method))
            print(f"   {'✅' if has_method else '❌'} {method}")
        
        # ブラウザ操作テスト
        print("\n🧪 Step 4/4: ブラウザ操作テスト")
        await browser.navigate_to_gemini()
        if browser.page:
            await browser.page.screenshot(path='logs/browser/dev_agent_test.png')
            print("   ✅ スクリーンショット保存")
        
        await browser.cleanup()
        
        print("\n" + "=" * 70)
        print("✅ DevAgent統合テスト完了！")
        print("=" * 70)
        return True
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_dev_agent_with_browser())
    sys.exit(0 if result else 1)

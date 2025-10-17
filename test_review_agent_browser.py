#!/usr/bin/env python3
"""ReviewAgent + BrowserController 統合テスト"""
import asyncio
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_review_agent_with_browser():
    print("🔍 ReviewAgent + Browser 統合テスト")
    print("=" * 70)
    
    try:
        # BrowserController準備
        print("\n📦 Step 1/4: BrowserController準備")
        from browser_control.enhanced_browser_controller import EnhancedBrowserController
        browser = EnhancedBrowserController(
            download_folder=Path("temp_workspace/downloads"),
            mode="text",
            service="google"
        )
        await browser.setup_browser()
        print("   ✅ BrowserController起動")
        
        # ReviewAgentインポート
        print("\n📦 Step 2/4: ReviewAgentインポート")
        from core_agents.review_agent import ReviewAgent
        review_agent = ReviewAgent(
            browser=browser,
            output_folder=Path("agent_outputs/review")
        )
        print("   ✅ ReviewAgent初期化")
        print(f"   ブラウザ設定: {review_agent.browser is not None}")
        
        # メソッド確認
        print("\n🔍 Step 3/4: メソッド確認")
        required_methods = ['send_prompt', 'wait_for_text_generation', 'extract_latest_text_response']
        for method in required_methods:
            has_method = hasattr(review_agent.browser, method) and callable(getattr(review_agent.browser, method))
            print(f"   {'✅' if has_method else '❌'} {method}")
        
        # ブラウザ操作テスト
        print("\n🧪 Step 4/4: ブラウザ操作テスト")
        await browser.navigate_to_gemini()
        if browser.page:
            await browser.page.screenshot(path='logs/browser/review_agent_test.png')
            print("   ✅ スクリーンショット保存")
        
        await browser.cleanup()
        
        print("\n" + "=" * 70)
        print("✅ ReviewAgent統合テスト完了！")
        print("=" * 70)
        return True
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_review_agent_with_browser())
    sys.exit(0 if result else 1)

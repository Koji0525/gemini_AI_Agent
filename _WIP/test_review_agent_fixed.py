#!/usr/bin/env python3
"""ReviewAgent引数確認と修正版テスト"""
import asyncio
import sys
import logging
from pathlib import Path
import inspect

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_review_agent_fixed():
    print("🔍 ReviewAgent 引数診断と修正テスト")
    print("=" * 70)
    
    try:
        # ReviewAgentのシグネチャ確認
        print("\n📋 Step 1/3: ReviewAgent.__init__ シグネチャ確認")
        from core_agents.review_agent import ReviewAgent
        
        sig = inspect.signature(ReviewAgent.__init__)
        print("   引数一覧:")
        for param_name, param in sig.parameters.items():
            if param_name != 'self':
                default = param.default if param.default != inspect.Parameter.empty else "必須"
                print(f"     - {param_name}: {default}")
        
        # BrowserController準備
        print("\n📦 Step 2/3: BrowserController準備")
        from browser_control.browser_controller import EnhancedBrowserController
        browser = EnhancedBrowserController(
            download_folder=Path("temp_workspace/downloads"),
            mode="text",
            service="google"
        )
        await browser.setup_browser()
        print("   ✅ BrowserController起動")
        
        # 正しい引数で初期化
        print("\n🧪 Step 3/3: 正しい引数でReviewAgent初期化")
        
        # パターン1: browser_controller
        try:
            review_agent = ReviewAgent(
                browser_controller=browser,
                output_folder=Path("agent_outputs/review")
            )
            print("   ✅ パターン1成功: browser_controller=")
            init_success = True
        except Exception as e1:
            print(f"   ❌ パターン1失敗: {e1}")
            
            # パターン2: browser
            try:
                review_agent = ReviewAgent(
                    browser=browser,
                    output_folder=Path("agent_outputs/review")
                )
                print("   ✅ パターン2成功: browser=")
                init_success = True
            except Exception as e2:
                print(f"   ❌ パターン2失敗: {e2}")
                
                # パターン3: 位置引数
                try:
                    review_agent = ReviewAgent(browser)
                    print("   ✅ パターン3成功: 位置引数")
                    init_success = True
                except Exception as e3:
                    print(f"   ❌ パターン3失敗: {e3}")
                    init_success = False
        
        if init_success:
            # メソッド確認
            browser_attr = review_agent.browser if hasattr(review_agent, 'browser') else None
            if browser_attr:
                required_methods = ['send_prompt', 'wait_for_text_generation', 'extract_latest_text_response']
                for method in required_methods:
                    has_method = hasattr(browser_attr, method) and callable(getattr(browser_attr, method))
                    print(f"   {'✅' if has_method else '❌'} {method}")
        
        await browser.cleanup()
        
        print("\n" + "=" * 70)
        print("✅ ReviewAgent診断完了")
        print("=" * 70)
        return init_success
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_review_agent_fixed())
    sys.exit(0 if result else 1)

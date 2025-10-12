#!/usr/bin/env python3
"""完全統合テスト"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def test_all():
    print("=" * 80)
    print("🧪 統合テスト開始")
    print("=" * 80)
    
    from safe_browser_manager import get_browser_controller, cleanup_browser
    from safe_wordpress_executor import SafeWordPressExecutor
    from fixed_review_agent import FixedReviewAgent
    from integrated_system_fixed import IntegratedSystemFixed
    
    try:
        # 1. ブラウザ
        print("\n[1/4] ブラウザテスト...")
        controller = await get_browser_controller()
        print("✅ 成功")
        
        # 2. WordPress
        print("\n[2/4] WordPressテスト...")
        wp = SafeWordPressExecutor("https://example.com")
        await wp.initialize()
        print("✅ 成功")
        
        # 3. レビュー
        print("\n[3/4] レビューテスト...")
        reviewer = FixedReviewAgent()
        await reviewer.initialize()
        print("✅ 成功")
        
        # 4. 統合
        print("\n[4/4] 統合テスト...")
        system = IntegratedSystemFixed()
        await system.initialize()
        print("✅ 成功")
        
    finally:
        await cleanup_browser()
    
    print("\n" + "=" * 80)
    print("🎉 全テスト完了！")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_all())

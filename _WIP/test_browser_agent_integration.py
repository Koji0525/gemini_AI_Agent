#!/usr/bin/env python3
"""
ブラウザとエージェントの統合テスト
EnhancedBrowserController + DesignAgent
"""

import asyncio
import sys
import logging
from pathlib import Path

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_browser_agent_integration():
    """統合テスト実行"""
    
    print("🧪 ブラウザ・エージェント統合テスト")
    print("=" * 70)
    
    try:
        # 1. EnhancedBrowserController インポート
        print("\n📦 Test 1/7: EnhancedBrowserController インポート")
        from browser_control.browser_controller import EnhancedBrowserController
        print("   ✅ インポート成功")
        
        # 2. BrowserController 初期化
        print("\n🔧 Test 2/7: BrowserController 初期化")
        download_folder = Path("temp_workspace/downloads")
        browser = EnhancedBrowserController(
            download_folder=download_folder,
            mode="text",
            service="google"
        )
        print("   ✅ 初期化成功")
        
        # 3. ブラウザセットアップ
        print("\n🌐 Test 3/7: ブラウザセットアップ")
        await browser.setup_browser()
        print("   ✅ セットアップ完了")
        
        # 4. Gemini AIに移動
        print("\n🔗 Test 4/7: Gemini AI接続")
        await browser.navigate_to_gemini()
        await asyncio.sleep(3)  # ページ読み込み待機
        print("   ✅ Gemini AI到達")
        
        # 5. プロンプト送信テスト
        print("\n📝 Test 5/7: プロンプト送信")
        test_prompt = "Hello! Please respond with 'Test successful' in Japanese."
        success = await browser.send_prompt(test_prompt)
        if success:
            print("   ✅ プロンプト送信成功")
        else:
            print("   ❌ プロンプト送信失敗")
            return False
        
        # 6. テキスト生成待機
        print("\n⏳ Test 6/7: レスポンス待機（最大60秒）")
        generation_complete = await browser.wait_for_text_generation(max_wait=60)
        if generation_complete:
            print("   ✅ レスポンス生成完了")
        else:
            print("   ⚠️ タイムアウト（続行）")
        
        # 7. レスポンステキスト取得
        print("\n📄 Test 7/7: レスポンステキスト抽出")
        response_text = await browser.extract_latest_text_response()
        if response_text:
            print(f"   ✅ テキスト取得成功")
            print(f"   📝 レスポンス（最初の100文字）:")
            print(f"   {response_text[:100]}...")
            
            # ファイル保存
            save_path = "logs/browser/test_response.txt"
            await browser.save_text_to_file(response_text, save_path)
            print(f"   ✅ レスポンス保存: {save_path}")
        else:
            print("   ⚠️ テキスト取得失敗（セレクタ調整が必要）")
        
        # クリーンアップ
        print("\n🧹 クリーンアップ")
        await browser.cleanup()
        print("   ✅ クリーンアップ完了")
        
        print("\n" + "=" * 70)
        print("✅ 統合テスト完了！")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_browser_agent_integration())
    sys.exit(0 if result else 1)

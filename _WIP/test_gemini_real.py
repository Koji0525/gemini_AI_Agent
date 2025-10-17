#!/usr/bin/env python3
"""
Gemini実機テスト（ログイン後に実行）
セレクタの動作確認とレスポンス取得
"""

import asyncio
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_gemini_real():
    print("🧪 Gemini実機テスト")
    print("=" * 70)
    print()
    print("⚠️ 注意: このテストを実行する前に:")
    print("  1. VNC画面を開く（6080ポート）")
    print("  2. Gemini AIに手動でログイン")
    print("  3. ログイン完了後、このテストを実行")
    print()
    
    response = input("ログイン完了しましたか？ (y/n): ")
    if response.lower() != 'y':
        print("ログイン後に再実行してください")
        return False
    
    try:
        from browser_control.browser_controller import EnhancedBrowserController
        
        # BrowserController準備
        print("\n📦 BrowserController準備")
        browser = EnhancedBrowserController(
            download_folder=Path("temp_workspace/downloads"),
            mode="text",
            service="google"
        )
        await browser.setup_browser()
        print("   ✅ ブラウザ起動")
        
        # Gemini AI移動
        print("\n🔗 Gemini AI接続")
        await browser.navigate_to_gemini()
        
        # 10秒待機（手動ログイン用）
        print("\n⏳ ページ読み込み待機（10秒）...")
        await asyncio.sleep(10)
        
        # テストプロンプト送信
        print("\n�� テストプロンプト送信")
        test_prompt = "こんにちは！短く「テスト成功」と返信してください。"
        success = await browser.send_prompt(test_prompt)
        
        if not success:
            print("   ❌ プロンプト送信失敗")
            await browser.cleanup()
            return False
        
        print("   ✅ プロンプト送信成功")
        
        # レスポンス待機
        print("\n⏳ レスポンス生成待機（最大60秒）")
        generation_ok = await browser.wait_for_text_generation(max_wait=60)
        
        if generation_ok:
            print("   ✅ レスポンス生成完了")
        else:
            print("   ⚠️ タイムアウト（続行）")
        
        # レスポンステキスト取得
        print("\n📄 レスポンステキスト抽出")
        response_text = await browser.extract_latest_text_response()
        
        if response_text:
            print(f"   ✅ テキスト取得成功！")
            print(f"\n   📝 Geminiの返答:")
            print(f"   {'='*66}")
            print(f"   {response_text}")
            print(f"   {'='*66}")
            
            # ファイル保存
            save_path = "logs/browser/gemini_real_test_response.txt"
            await browser.save_text_to_file(response_text, save_path)
            print(f"\n   💾 保存: {save_path}")
            
            print("\n" + "=" * 70)
            print("�� Gemini実機テスト完全成功！")
            print("=" * 70)
            print("\n✅ 確認事項:")
            print("  1. プロンプト送信: OK")
            print("  2. レスポンス生成待機: OK")
            print("  3. テキスト抽出: OK")
            print("  4. ファイル保存: OK")
            print()
            print("🎯 次のステップ:")
            print("  → アカウントA（WordPress連携）とマージ準備完了！")
            
        else:
            print("   ⚠️ テキスト取得失敗")
            print("\n   📸 デバッグ情報:")
            print("   - logs/browser/debug_no_response.png を確認")
            print("   - セレクタ調整が必要な可能性")
            
            print("\n" + "=" * 70)
            print("⚠️ レスポンス取得に課題あり")
            print("=" * 70)
            print("\n対策:")
            print("  1. ログインしているか確認")
            print("  2. デバッグスクショでHTML構造を確認")
            print("  3. セレクタ調整")
        
        await browser.cleanup()
        
        return response_text is not None
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini_real())
    sys.exit(0 if result else 1)

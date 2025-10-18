#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🧪 タイムアウト修正のテスト"
echo "=========================================="

# VNC起動確認
if ! pgrep -x "Xvnc" > /dev/null; then
    echo "🌐 VNCを起動中..."
    vncserver :1 -geometry 1150x600 -depth 24 > /dev/null 2>&1 || true
    sleep 2
fi

export DISPLAY=:1

# ====================================================================
# テスト1: 簡単なプロンプト送信
# ====================================================================
echo ""
echo -e "${BLUE}[テスト 1/2] 簡単なプロンプト送信テスト${NC}"
echo "=========================================="

DISPLAY=:1 python3 << 'TEST1'
import asyncio
from browser_control.browser_controller import BrowserController

async def test_simple_prompt():
    print("\n🎯 テスト: タイムアウト修正確認")
    
    async with BrowserController(download_folder="./downloads") as browser:
        # Geminiにアクセス（リトライ機能テスト）
        print("\n[1/3] Geminiアクセステスト（リトライ機能付き）...")
        logged_in = await browser.navigate_to_gemini()
        
        if not logged_in:
            print("⚠️  ログインが必要です")
            return False
        
        print("✅ アクセス成功")
        
        # プロンプト送信テスト
        print("\n[2/3] プロンプト送信テスト...")
        test_prompt = "Hello! Please respond with: TIMEOUT TEST SUCCESS"
        
        await browser.send_prompt(test_prompt)
        print("✅ 送信成功")
        
        # レスポンス取得
        print("\n[3/3] レスポンス取得テスト...")
        await browser.wait_for_text_generation(max_wait=30)
        
        response = await browser.extract_latest_text_response()
        
        if response and len(response) > 10:
            print(f"✅ レスポンス取得成功（{len(response)} 文字）")
            print(f"\n📝 レスポンス: {response[:100]}...")
            return True
        else:
            print("⚠️  レスポンスが短すぎます")
            return False

result = asyncio.run(test_simple_prompt())

if result:
    print("\n✅✅✅ テスト1成功！")
else:
    print("\n⚠️  テスト1失敗")

TEST1

# ====================================================================
# テスト2: ウズベキスタンタスクの再実行
# ====================================================================
echo ""
echo -e "${BLUE}[テスト 2/2] ウズベキスタンタスク再実行${NC}"
echo "=========================================="

if [ -f "run_uzbekistan_task.py" ]; then
    DISPLAY=:1 python3 run_uzbekistan_task.py
else
    echo "⚠️  run_uzbekistan_task.py が見つかりません"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ テスト完了${NC}"
echo "=========================================="


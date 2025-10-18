#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🧪 VNC修正後のテスト"
echo "=========================================="

# DISPLAY確認
export DISPLAY=:1
echo "DISPLAY: $DISPLAY"

# VNC確認
if ! pgrep -x "Xvnc" > /dev/null; then
    echo "❌ VNCが起動していません"
    echo "先に ./fix_vnc_complete.sh を実行してください"
    exit 1
fi

echo "✅ VNC起動確認"

# ====================================================================
# テスト実行
# ====================================================================
echo ""
echo -e "${BLUE}[テスト] ウズベキスタンタスク実行${NC}"
echo "=========================================="

if [ -f "run_uzbekistan_task.py" ]; then
    DISPLAY=:1 python3 run_uzbekistan_task.py
else
    echo "⚠️  run_uzbekistan_task.py が見つかりません"
    
    # 簡易テストを実行
    echo ""
    echo "簡易ブラウザテストを実行..."
    
    DISPLAY=:1 python3 << 'SIMPLE_TEST'
import asyncio
from browser_control.browser_controller import BrowserController

async def simple_test():
    print("\n🎯 簡易ブラウザテスト")
    
    async with BrowserController(download_folder="./downloads") as browser:
        print("✅ ブラウザ初期化成功")
        
        logged_in = await browser.navigate_to_gemini()
        
        if logged_in:
            print("✅ Geminiアクセス成功")
            
            await browser.send_prompt("Hello! Reply with: VNC TEST SUCCESS")
            print("✅ プロンプト送信成功")
            
            await browser.wait_for_text_generation(max_wait=30)
            response = await browser.extract_latest_text_response()
            
            if response:
                print(f"✅ レスポンス取得成功: {len(response)} 文字")
                print(f"\n📝 {response[:100]}...")
                return True
        
        return False

result = asyncio.run(simple_test())

if result:
    print("\n✅✅✅ テスト成功！")
else:
    print("\n⚠️  テスト未完了")

SIMPLE_TEST
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ テスト完了${NC}"
echo "=========================================="


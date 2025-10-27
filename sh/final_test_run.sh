#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🎯 最終テスト実行"
echo "=========================================="

# DISPLAY確認
export DISPLAY=:1
echo "DISPLAY: $DISPLAY"

# Xvfb確認
if pgrep -x "Xvfb" > /dev/null; then
    echo "✅ Xvfb起動中"
else
    echo "⚠️  Xvfb未起動"
fi

# ====================================================================
# テスト1: 簡易プロンプトテスト
# ====================================================================
echo ""
echo -e "${BLUE}[テスト 1/2] 簡易プロンプトテスト${NC}"
echo "=========================================="

DISPLAY=:1 python3 << 'TEST1'
import asyncio
from browser_control.browser_controller import BrowserController

async def test_simple():
    print("\n🎯 簡易テスト開始")
    
    async with BrowserController(download_folder="./downloads") as browser:
        print("✅ ブラウザ初期化成功")
        
        logged_in = await browser.navigate_to_gemini()
        
        if logged_in:
            print("✅ Geminiアクセス成功")
            
            await browser.send_prompt("Hello! Reply: FINAL TEST SUCCESS")
            print("✅ プロンプト送信成功")
            
            await browser.wait_for_text_generation(max_wait=30)
            response = await browser.extract_latest_text_response()
            
            if response and len(response) > 10:
                print(f"✅ レスポンス取得成功（{len(response)} 文字）")
                print(f"\n📝 レスポンス: {response[:150]}...")
                return True
        
        return False

result = asyncio.run(test_simple())

if result:
    print("\n✅✅✅ テスト1成功！")
else:
    print("\n⚠️  テスト1未完了")

TEST1

# ====================================================================
# テスト2: ウズベキスタンタスク
# ====================================================================
echo ""
echo -e "${BLUE}[テスト 2/2] ウズベキスタンタスク${NC}"
echo "=========================================="

if [ -f "run_uzbekistan_task.py" ]; then
    echo "実行中..."
    DISPLAY=:1 python3 run_uzbekistan_task.py
else
    echo "⚠️  run_uzbekistan_task.py が見つかりません"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ テスト完了${NC}"
echo "=========================================="


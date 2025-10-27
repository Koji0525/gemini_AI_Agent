#!/bin/bash
echo "🚀 Playwright環境を完全修復します..."

# カレントディレクトリをプロジェクトルートに
cd /workspaces/gemini_AI_Agent

echo "1. システム依存関係をインストール..."
sudo apt-get update -y
sudo apt-get install -y \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libnss3 \
    libnspr4 \
    libxss1 \
    libx11-xcb1 \
    libgtk-3-0

echo "2. Playwrightをインストール..."
pip install --upgrade playwright

echo "3. ブラウザをインストール..."
python -m playwright install chromium

echo "4. インストール確認..."
python -c "import playwright; print(f'✅ Playwrightバージョン: {playwright.__version__}')"

echo "5. テスト実行..."
python -c "
import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://httpbin.org/html')
            title = await page.title()
            await browser.close()
            print('✅ ブラウザテスト成功:', title)
            return True
    except Exception as e:
        print('❌ ブラウザテスト失敗:', e)
        return False

asyncio.run(test_browser())
"

echo "🎉 修復完了！"

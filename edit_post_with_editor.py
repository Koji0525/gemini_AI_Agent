#!/usr/bin/env python3
"""
WordPress記事編集 - wp_post_editor.py を使用
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright をインストール: pip install playwright")
    exit(1)

from wordpress.wp_post_editor import WordPressPostEditor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def edit_post():
    """wp_post_editor を使って記事を編集"""
    
    wp_url = "https://your-actual-wordpress-site.com"  # 実際のURL
    
    try:
        logger.info("=" * 80)
        logger.info("✏️ WordPress記事編集開始")
        logger.info("=" * 80)
        
        # WordPressPostEditor 初期化
        editor = WordPressPostEditor(wp_url=wp_url, sheets_manager=None)
        
        # ブラウザ起動
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 編集タスク
        task = {
            'post_id': '123',  # 編集する記事のID
            'title': '✏️ 編集されたタイトル',
            'content': '<p>この記事は wp_post_editor.py によって編集されました。</p>',
            'post_status': 'draft'
        }
        
        logger.info(f"✏️ 記事編集中: ID {task['post_id']}")
        
        # edit_post メソッドを呼び出し
        result = await editor.edit_post(page, task)
        
        logger.info("✅ 記事編集完了！")
        logger.info(f"📋 結果: {result}")
        
        await browser.close()
        await playwright.stop()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    await edit_post()

if __name__ == "__main__":
    asyncio.run(main())

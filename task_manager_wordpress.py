#!/usr/bin/env python3
"""
タスクマネージャー - wp_post_creator & wp_post_editor 統合版
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ pip install playwright")
    exit(1)

from wordpress.wp_post_creator import WordPressPostCreator
from wordpress.wp_post_editor import WordPressPostEditor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordPressTaskManager:
    """WordPress専用タスクマネージャー"""
    
    def __init__(self, wp_url: str):
        self.wp_url = wp_url
        self.creator = WordPressPostCreator(wp_url=wp_url, sheets_manager=None)
        self.editor = WordPressPostEditor(wp_url=wp_url, sheets_manager=None)
        
    async def create_draft_from_task(self, task: dict) -> dict:
        """タスクから下書き作成"""
        logger.info(f"📝 下書き作成: {task.get('title', 'Untitled')}")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            result = await self.creator.create_post(page, task)
            logger.info("✅ 下書き作成成功")
            return {'success': True, 'result': result}
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            await browser.close()
            await playwright.stop()
    
    async def edit_post_from_task(self, task: dict) -> dict:
        """タスクから記事編集"""
        logger.info(f"✏️ 記事編集: ID {task.get('post_id')}")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            result = await self.editor.edit_post(page, task)
            logger.info("✅ 記事編集成功")
            return {'success': True, 'result': result}
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            await browser.close()
            await playwright.stop()

async def test_wordpress_tasks():
    """テスト実行"""
    wp_url = "https://your-actual-wordpress-site.com"  # 実際のURLに変更
    manager = WordPressTaskManager(wp_url)
    
    # テスト1: 下書き作成
    task1 = {
        'title': f'🤖 テスト記事 {datetime.now().strftime("%H:%M:%S")}',
        'content': '<p>wp_post_creator でテスト作成</p>',
        'post_status': 'draft'
    }
    
    result1 = await manager.create_draft_from_task(task1)
    logger.info(f"結果1: {result1}")

if __name__ == "__main__":
    asyncio.run(test_wordpress_tasks())

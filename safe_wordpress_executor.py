#!/usr/bin/env python3
"""安全なWordPressタスク実行"""
import asyncio
import logging
from typing import Dict, Any, Optional

from safe_browser_manager import get_browser_controller
from wordpress.wp_post_creator import WordPressPostCreator
from wordpress.wp_post_editor import WordPressPostEditor
from config_utils import setup_optimized_logging

logger = setup_optimized_logging("safe_wp")

class SafeWordPressExecutor:
    
    def __init__(self, wp_url: str):
        self.wp_url = wp_url
        self.browser_controller = None
        self.post_creator = None
        self.post_editor = None
        logger.info(f"📋 初期化: {wp_url}")
    
    async def initialize(self):
        try:
            logger.info("🔧 環境初期化中...")
            self.browser_controller = await get_browser_controller()
            logger.info("✅ ブラウザ取得完了")
            
            self.post_creator = WordPressPostCreator(self.wp_url)
            self.post_editor = WordPressPostEditor(
                self.wp_url,
                self.browser_controller
            )
            logger.info("✅ 初期化完了")
            
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            raise
    
    async def create_draft_post(
        self,
        title: str,
        content: str,
        tags: Optional[list] = None
    ) -> Dict[str, Any]:
        try:
            logger.info(f"🆕 下書き作成: {title[:30]}...")
            
            if self.browser_controller is None:
                await self.initialize()
            
            result = await self.post_creator.create_draft_post(
                title=title,
                content=content,
                tags=tags or []
            )
            
            if result.get('success'):
                logger.info("✅ 下書き作成成功")
            else:
                logger.error(f"❌ 失敗: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            return {'success': False, 'error': str(e)}

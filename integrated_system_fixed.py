#!/usr/bin/env python3
"""完全修正版統合システム"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from safe_browser_manager import get_browser_controller, cleanup_browser
from safe_wordpress_executor import SafeWordPressExecutor
from fixed_review_agent import FixedReviewAgent
from sheets_manager import GoogleSheetsManager
from config_utils import setup_optimized_logging

logger = setup_optimized_logging("main")

class IntegratedSystemFixed:
    
    def __init__(self):
        self.wp_executor = None
        self.reviewer = None
        self.sheets_manager = None
        self.stats = {
            'executed': 0,
            'succeeded': 0,
            'failed': 0,
            'reviewed': 0
        }
    
    async def initialize(self):
        logger.info("=" * 80)
        logger.info("🚀 初期化中...")
        logger.info("=" * 80)
        
        try:
            logger.info("[1/4] ブラウザ...")
            await get_browser_controller()
            
            logger.info("[2/4] WordPress...")
            self.wp_executor = SafeWordPressExecutor(
                wp_url="https://your-site.com"
            )
            await self.wp_executor.initialize()
            
            logger.info("[3/4] レビュー...")
            self.reviewer = FixedReviewAgent()
            await self.reviewer.initialize()
            
            logger.info("[4/4] Sheets...")
            self.sheets_manager = GoogleSheetsManager(
                spreadsheet_id='YOUR_ID'
            )
            
            logger.info("✅ 初期化完了")
            
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            raise
    
    async def run_cycle(self, max_tasks: int = 3):
        logger.info("\n" + "=" * 80)
        logger.info("🔄 サイクル開始")
        logger.info("=" * 80)
        
        try:
            tasks = await self.sheets_manager.load_tasks_from_sheet()
            logger.info(f"📋 タスク数: {len(tasks)}")
            
            pending = [t for t in tasks if t.get('status') == 'pending'][:max_tasks]
            
            for task in pending:
                await self._execute_single_task(task)
                
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
    
    async def _execute_single_task(self, task: Dict[str, Any]):
        task_id = task.get('task_id', 'unknown')
        desc = task.get('description', '')
        
        logger.info(f"\n📝 タスク: {task_id}")
        self.stats['executed'] += 1
        
        try:
            # WordPress投稿
            result = await self.wp_executor.create_draft_post(
                title=f"AI投稿_{datetime.now().strftime('%Y%m%d_%H%M')}",
                content=f"<h1>{desc}</h1><p>コンテンツ</p>",
                tags=['auto']
            )
            
            if not result.get('success'):
                self.stats['failed'] += 1
                await self.sheets_manager.update_task_status(task_id, 'failed')
                return
            
            self.stats['succeeded'] += 1
            
            # レビュー
            review = await self.reviewer.review_content(
                content=str(result),
                task_description=desc
            )
            
            logger.info("✅ レビュー完了")
            self.stats['reviewed'] += 1
            
            await self.sheets_manager.update_task_status(task_id, 'reviewed')
            
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            self.stats['failed'] += 1
    
    async def cleanup(self):
        logger.info("\n🧹 クリーンアップ...")
        await cleanup_browser()
        
        logger.info("=" * 80)
        logger.info("🎉 完了")
        logger.info("=" * 80)
        logger.info(f"実行: {self.stats['executed']}")
        logger.info(f"成功: {self.stats['succeeded']}")
        logger.info(f"失敗: {self.stats['failed']}")
        logger.info(f"レビュー: {self.stats['reviewed']}")

async def main():
    system = IntegratedSystemFixed()
    try:
        await system.initialize()
        await system.run_cycle(max_tasks=3)
    finally:
        await system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

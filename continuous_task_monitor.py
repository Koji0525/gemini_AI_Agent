#!/usr/bin/env python3
"""継続監視"""
import asyncio
import logging
from datetime import datetime
from task_manager_with_sheets import TaskManagerWithSheets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def continuous_monitor(interval_minutes: int = 5):
    logger.info("🤖 継続監視開始（5分間隔）")
    
    cycle = 0
    while True:
        cycle += 1
        logger.info(f"\n🔄 サイクル {cycle} - {datetime.now()}")
        
        manager = TaskManagerWithSheets()
        if await manager.initialize():
            await manager.run_cycle()
        
        logger.info(f"💤 {interval_minutes}分待機...")
        await asyncio.sleep(interval_minutes * 60)

if __name__ == "__main__":
    asyncio.run(continuous_monitor())

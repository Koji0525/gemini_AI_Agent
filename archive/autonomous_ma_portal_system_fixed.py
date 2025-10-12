#!/usr/bin/env python3
"""
マルチエージェントポータル統合システム（修正版）
"""
import asyncio
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutonomousMAPortalSystem:
    """統合ポータルシステム"""
    
    def __init__(self):
        self.max_retries = 3
    
    async def run_multi_agent(self):
        """マルチエージェント実行"""
        import subprocess
        logger.info("🤖 マルチエージェント実行中...")
        
        result = subprocess.run(
            ['python', 'run_multi_agent.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ マルチエージェント成功")
            return True
        else:
            logger.error(f"❌ エラー: {result.stderr}")
            return False
    
    async def run(self):
        """メイン実行"""
        logger.info("=" * 80)
        logger.info("🚀 自律型マルチエージェントポータルシステム")
        logger.info("=" * 80)
        
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"\n🔄 試行 {attempt}/{self.max_retries}")
            
            success = await self.run_multi_agent()
            
            if success:
                logger.info("=" * 80)
                logger.info("🎉 システム起動成功！")
                logger.info("=" * 80)
                return True
            
            if attempt < self.max_retries:
                logger.info(f"⏳ 5秒後に再試行...")
                await asyncio.sleep(5)
        
        logger.error("❌ 最大試行回数に達しました")
        return False

async def main():
    system = AutonomousMAPortalSystem()
    await system.run()

if __name__ == "__main__":
    asyncio.run(main())

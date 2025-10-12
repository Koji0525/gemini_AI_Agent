#!/usr/bin/env python3
"""
完全統合v2：実践的タスク → エラー検出 → 自動修正
"""
import asyncio
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedAutonomousSystemV2:
    """統合自律システム v2"""
    
    def __init__(self):
        self.max_retries = 3
        self.error_log_path = Path("error_logs")
        self.error_log_path.mkdir(exist_ok=True)
    
    async def run_practical_tasks(self):
        """実践的タスクを実行"""
        logger.info("🚀 実践的タスク実行中...")
        result = subprocess.run(
            ['python', 'test_tasks_practical.py'],
            capture_output=True,
            text=True
        )
        
        logger.info(result.stdout)
        
        if result.returncode == 0:
            logger.info("✅ タスク実行成功")
            return True, None
        else:
            logger.error(f"❌ タスク実行失敗")
            logger.error(result.stderr)
            return False, result.stderr
    
    async def detect_and_fix_errors(self, error_output):
        """エラーを検出して自動修正"""
        if not error_output:
            return True
        
        logger.info("🔍 エラー検出 → 自動修正システム起動")
        
        result = subprocess.run(
            ['python', 'main_hybrid_fix.py'],
            input=error_output,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ 自動修正成功")
            return True
        else:
            logger.error("❌ 自動修正失敗")
            return False
    
    async def run_cycle(self, attempt):
        """1サイクル実行"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔄 サイクル {attempt}/{self.max_retries}")
        logger.info(f"{'='*80}")
        
        # 実践的タスク実行
        success, error = await self.run_practical_tasks()
        
        if success:
            return True
        
        # エラーがあれば自動修正
        if error:
            fixed = await self.detect_and_fix_errors(error)
            if fixed:
                # 修正後に再実行
                logger.info("🔄 修正後に再実行...")
                await asyncio.sleep(2)
                success, _ = await self.run_practical_tasks()
                return success
        
        return False
    
    async def run(self):
        """メイン実行"""
        logger.info("=" * 80)
        logger.info("🤖 統合自律型システム v2 起動")
        logger.info("=" * 80)
        
        for attempt in range(1, self.max_retries + 1):
            success = await self.run_cycle(attempt)
            
            if success:
                logger.info("\n" + "=" * 80)
                logger.info("🎉 全タスク成功！")
                logger.info("=" * 80)
                return True
            
            if attempt < self.max_retries:
                logger.info(f"⏳ 10秒後に再試行...")
                await asyncio.sleep(10)
        
        logger.error("\n" + "=" * 80)
        logger.error("❌ 最大試行回数到達")
        logger.error("=" * 80)
        return False

async def main():
    system = IntegratedAutonomousSystemV2()
    await system.run()

if __name__ == "__main__":
    asyncio.run(main())

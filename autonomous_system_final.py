#!/usr/bin/env python3
"""
完全自律エージェントシステム
1. test_tasks.py 実行
2. エラー検出
3. main_hybrid_fix.py で自動修正
4. run_multi_agent.py 実行
5. エラー検出 → 自動修正
6. 継続的に繰り返し
"""
import asyncio
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutonomousSystem:
    def __init__(self):
        self.max_retries = 3
        self.error_log = Path("error_logs")
        self.error_log.mkdir(exist_ok=True)

    async def run_test_tasks(self):
        """STEP 1: test_tasks.py 実行"""
        logger.info("=" * 80)
        logger.info("📝 STEP 1: test_tasks.py 実行")
        logger.info("=" * 80)

        result = subprocess.run(
            ['python', 'test_tasks.py'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info("✅ test_tasks.py 成功")
            return True, None
        else:
            logger.error("❌ test_tasks.py 失敗")
            return False, result.stderr

    async def run_multi_agent(self):
        """STEP 2: run_multi_agent.py 実行"""
        logger.info("=" * 80)
        logger.info("🤖 STEP 2: run_multi_agent.py 実行")
        logger.info("=" * 80)

        result = subprocess.run(
            ['python', 'run_multi_agent.py'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info("✅ run_multi_agent.py 成功")
            return True, None
        else:
            logger.error("❌ run_multi_agent.py 失敗")
            return False, result.stderr

    async def auto_fix(self, error_message: str):
        """STEP 3: main_hybrid_fix.py で自動修正"""
        logger.info("=" * 80)
        logger.info("🔧 STEP 3: 自動修正実行")
        logger.info("=" * 80)
        logger.info(f"エラー内容: {error_message[:200]}...")

        # エラーログ保存
        error_file = self.error_log / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(error_file, 'w') as f:
            f.write(error_message)

        # main_hybrid_fix.py 実行
        result = subprocess.run(
            ['python', 'main_hybrid_fix.py', '--error-file', str(error_file)],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            logger.info("✅ 自動修正成功")
            return True
        else:
            logger.warning("⚠️ 自動修正失敗 - 手動介入が必要")
            return False

    async def run_cycle(self):
        """1サイクル実行"""
        for attempt in range(1, self.max_retries + 1):
            logger.info("\n" + "=" * 80)
            logger.info(f"🔄 サイクル {attempt}/{self.max_retries}")
            logger.info("=" * 80)

            # STEP 1: test_tasks
            success, error = await self.run_test_tasks()
            if not success:
                if await self.auto_fix(error):
                    continue
                else:
                    return False

            # STEP 2: run_multi_agent
            success, error = await self.run_multi_agent()
            if not success:
                if await self.auto_fix(error):
                    continue
                else:
                    return False

            # 全て成功
            logger.info("\n" + "=" * 80)
            logger.info("🎉 全サイクル成功！")
            logger.info("=" * 80)
            return True

        logger.error("❌ 最大試行回数到達")
        return False

async def main():
    system = AutonomousSystem()
    await system.run_cycle()

if __name__ == "__main__":
    asyncio.run(main())

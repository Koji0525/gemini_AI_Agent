#!/usr/bin/env python3
"""
継続監視システム（オプション）
必要な場合のみ使用
"""
import asyncio
import logging
from datetime import datetime
from integrated_task_manager_v2 import IntegratedTaskManagerV2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def continuous_monitor(interval_minutes: int = 5):
    """継続監視"""
    logger.info("=" * 80)
    logger.info("🤖 継続監視システム起動")
    logger.info(f"   監視間隔: {interval_minutes}分")
    logger.info("   停止: Ctrl+C")
    logger.info("=" * 80)

    cycle_count = 0

    try:
        while True:
            cycle_count += 1
            logger.info(f"\n{'='*80}")
            logger.info(f"🔄 サイクル {cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'='*80}")

            manager = IntegratedTaskManagerV2()

            try:
                if await manager.initialize():
                    await manager.run_cycle()
                else:
                    logger.error("❌ 初期化失敗 - 次のサイクルで再試行")
            except Exception as e:
                logger.error(f"❌ サイクルエラー: {e}")
            finally:
                await manager.cleanup()

            logger.info(f"\n💤 次回実行まで {interval_minutes}分待機...")
            await asyncio.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        logger.info("\n🛑 停止シグナル受信 - 終了します")


if __name__ == "__main__":
    asyncio.run(continuous_monitor(interval_minutes=5))

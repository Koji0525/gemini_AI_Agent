#!/usr/bin/env python3
"""
24時間自律開発ループシステム v2.5（IntegratedOrchestrator統合版）
"""

import asyncio
import os
import logging
from datetime import datetime
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.integrated_orchestrator_v25_complete import IntegratedOrchestrator

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/autonomous_24h.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AutonomousSystem:
    """24時間自律開発システム"""

    def __init__(self):
        self.cycle_count = 0
        self.wait_minutes = int(os.getenv("WAIT_MINUTES", "60"))
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        self.max_cycles = int(os.getenv("MAX_CYCLES", "0"))

        # IntegratedOrchestrator v25 初期化
        self.orchestrator = None

        logger.info(f"⚙️ 待機時間: {self.wait_minutes}分")
        logger.info(f"📊 1日あたりの予定サイクル数: {1440 // self.wait_minutes}サイクル")

    async def initialize(self):
        """システム初期化"""
        try:
            logger.info("🔧 IntegratedOrchestrator v25 初期化中...")
            self.orchestrator = IntegratedOrchestrator()
            logger.info("✅ 初期化完了")

        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            raise

    async def execute_cycle(self):
        """1サイクルの実行（IntegratedOrchestrator v25を使用）"""
        self.cycle_count += 1
        cycle_start = datetime.now()

        logger.info("=" * 60)
        logger.info(f"🚀 サイクル #{self.cycle_count} 開始")
        logger.info("=" * 60)

        try:
            # IntegratedOrchestrator v25 の連続実行サイクルを呼び出し
            # ✅ 正しい引数: max_duration_minutes, single_cycle
            await self.orchestrator.run_continuous_cycle(
                max_duration_minutes=self.wait_minutes,  # サイクル時間
                single_cycle=True,  # 1サイクルのみ実行
            )

            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            logger.info("=" * 60)
            logger.info(f"✅ サイクル #{self.cycle_count} 完了 ({cycle_duration:.1f}秒)")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"❌ サイクル #{self.cycle_count} でエラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    async def main_loop(self):
        """メインループ"""
        logger.info("=" * 80)
        logger.info("🎯 24時間自律開発システム起動")
        logger.info(f"⏰ サイクル間隔: {self.wait_minutes}分")
        logger.info(f"🧪 テストモード: {self.test_mode}")
        if self.max_cycles > 0:
            logger.info(f"🔢 最大サイクル数: {self.max_cycles}")
        logger.info("=" * 80)

        # 初期化
        await self.initialize()

        while True:
            try:
                # サイクル実行
                success = await self.execute_cycle()

                if not success:
                    logger.warning("⚠️ サイクル失敗、5分後に再試行")
                    await asyncio.sleep(300)
                    continue

                # MAX_CYCLESチェック
                if self.max_cycles > 0 and self.cycle_count >= self.max_cycles:
                    logger.info(f"✅ 最大サイクル数({self.max_cycles})に到達")
                    break

                # 待機
                if self.test_mode:
                    logger.info("⚡ テストモード: 即座に次サイクル")
                    await asyncio.sleep(5)  # 5秒だけ待機
                else:
                    logger.info(f"⏳ 次のサイクルまで待機 ({self.wait_minutes}分)")
                    await asyncio.sleep(self.wait_minutes * 60)

            except KeyboardInterrupt:
                logger.info("🛑 ユーザーによる停止")
                break
            except Exception as e:
                logger.error(f"❌ メインループエラー: {e}")
                import traceback

                logger.error(traceback.format_exc())
                logger.info("⏳ 5分後に再試行...")
                await asyncio.sleep(300)


async def main():
    """エントリーポイント"""
    system = AutonomousSystem()
    await system.main_loop()


if __name__ == "__main__":
    # ログディレクトリ作成
    Path("logs").mkdir(exist_ok=True)

    # 実行

    # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 システム終了")

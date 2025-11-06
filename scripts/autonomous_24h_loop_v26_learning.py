#!/usr/bin/env python3
"""
24時間自律開発ループ v2.6（学習機能統合版）
"""

import asyncio
import os
import logging
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.integrated_orchestrator_v25_complete import IntegratedOrchestrator
from core_agents.error_learning_agent import ErrorLearningAgent
from browser_control.sheets_manager import GoogleSheetsManager
from configuration.config_loader import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/autonomous_24h.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AutonomousSystemV26:
    """24時間自律開発システム v2.6（学習機能付き）"""

    def __init__(self):
        self.cycle_count = 0
        self.wait_minutes = int(os.getenv("WAIT_MINUTES", "60"))
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        self.max_cycles = int(os.getenv("MAX_CYCLES", "0"))

        # 学習サイクル（6時間ごと）
        self.learning_interval = 6 * 60  # 360分
        self.last_learning_time = datetime.now()

        self.orchestrator = None
        self.learning_agent = None

        logger.info(f"⚙️ 待機時間: {self.wait_minutes}分")
        logger.info(f"🧠 学習間隔: {self.learning_interval // 60}時間")

    async def initialize(self):
        """初期化"""
        try:
            logger.info("🔧 システム初期化中...")

            # IntegratedOrchestrator
            self.orchestrator = IntegratedOrchestrator()

            # ErrorLearningAgent
            config = load_config()
            sheets = GoogleSheetsManager(config["spreadsheet_id"])
            self.learning_agent = ErrorLearningAgent(sheets)

            logger.info("✅ 初期化完了")

        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            raise

    async def execute_cycle(self):
        """1サイクル実行"""
        self.cycle_count += 1
        cycle_start = datetime.now()

        logger.info("=" * 60)
        logger.info(f"🚀 サイクル #{self.cycle_count} 開始")
        logger.info("=" * 60)

        try:
            # タスク実行
            await self.orchestrator.run_continuous_cycle(
                max_duration_minutes=self.wait_minutes, single_cycle=True
            )

            # 学習サイクルチェック
            if self._should_learn():
                await self.execute_learning()

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

    def _should_learn(self) -> bool:
        """学習サイクルを実行すべきか判定"""
        elapsed = (datetime.now() - self.last_learning_time).total_seconds()
        return elapsed >= (self.learning_interval * 60)

    async def execute_learning(self):
        """学習サイクル実行"""
        logger.info("=" * 60)
        logger.info("🧠 学習サイクル開始")
        logger.info("=" * 60)

        try:
            # エラーログ分析

            # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
            await self.learning_agent.analyze_error_logs()

            self.last_learning_time = datetime.now()

            logger.info("✅ 学習サイクル完了")

        except Exception as e:
            logger.error(f"❌ 学習エラー: {e}")

    async def main_loop(self):
        """メインループ"""
        logger.info("=" * 80)
        logger.info("🎯 24時間自律開発システム v2.6 起動")
        logger.info(f"⏰ サイクル間隔: {self.wait_minutes}分")
        logger.info(f"🧠 学習間隔: {self.learning_interval // 60}時間")
        logger.info("=" * 80)

        await self.initialize()

        while True:
            try:
                success = await self.execute_cycle()

                if not success:
                    logger.warning("⚠️ サイクル失敗、5分後に再試行")
                    await asyncio.sleep(300)
                    continue

                if self.max_cycles > 0 and self.cycle_count >= self.max_cycles:
                    logger.info(f"✅ 最大サイクル数({self.max_cycles})に到達")
                    break

                if self.test_mode:
                    logger.info("⚡ テストモード: 即座に次サイクル")
                    await asyncio.sleep(5)
                else:
                    logger.info(f"⏳ 次のサイクルまで待機 ({self.wait_minutes}分)")
                    await asyncio.sleep(self.wait_minutes * 60)

            except KeyboardInterrupt:
                logger.info("🛑 ユーザーによる停止")
                break
            except Exception as e:
                logger.error(f"❌ メインループエラー: {e}")
                await asyncio.sleep(300)


async def main():
    system = AutonomousSystemV26()
    await system.main_loop()


if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 システム終了")

#!/usr/bin/env python3
"""
🤖 24時間自律開発システム - 完全版
v24 Orchestrator + 自己修復 + 人間介入 + 自動学習
"""
import asyncio
import logging
import os
from datetime import datetime

import sys

sys.path.insert(0, ".")
from scripts.integrated_orchestrator_v24_production import IntegratedOrchestrator
from agents.self_healing.logging.decision_support_system import DecisionSupportSystem
from agents.self_healing.logging.knowledge_base_manager import KnowledgeBaseManager
from core_agents.human_interaction_agent_v02_github_api import HumanInteractionAgent
from tools.sheets_manager_v02_mapped import GoogleSheetsManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Autonomous24HSystem:
    """24時間自律開発システム"""

    def __init__(self):
        """初期化"""
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🚀 24時間自律開発システム起動")
        logger.info("   Version: v24 Production")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # コンポーネント初期化
        self.sheets = GoogleSheetsManager()
        self.knowledge_base = KnowledgeBaseManager(self.sheets)
        self.decision_support = DecisionSupportSystem(self.sheets, self.knowledge_base)
        self.human_agent = HumanInteractionAgent()

        # v24 Orchestrator初期化
        self.orchestrator = IntegratedOrchestrator(
            decision_support=self.decision_support, human_agent=self.human_agent
        )

        self.cycle_count = 0
        logger.info("✅ 全コンポーネント初期化完了")

    async def run_cycle(self):
        """1サイクル実行"""
        self.cycle_count += 1
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 サイクル {self.cycle_count} 開始 - {datetime.now()}")
        logger.info(f"{'='*60}")

        try:
            # 1. 人間の制御コマンドチェック
            control = await self.human_agent.check_control_commands()

            if control and control.get("action") == "stop":
                logger.warning("⏸️  停止指示を検出 - システム終了")
                return False

            elif control and control.get("action") == "redirect":
                logger.info(f"�� 方向変更: {control.get('message', '')}")

            # 2. タスク実行
            logger.info("🎯 タスク実行開始")
            await self.orchestrator.execute_tasks()
            logger.info("✅ タスク実行完了")

            # 3. 6時間ごとに自動学習
            if self.cycle_count % 6 == 0:
                logger.info("🤖 自動学習サイクル実行")
                await self.run_learning_cycle()

            return True

        except Exception as e:
            logger.error(f"❌ サイクル実行エラー: {e}")

            # 自己修復試行
            if self.decision_support:
                try:
                    decision = await self.decision_support.decide_action(
                        error_type=type(e).__name__,
                        error_message=str(e),
                        context={"cycle": self.cycle_count},
                    )
                    logger.info(f"🤖 自動判断: {decision.get('strategy', 'unknown')}")
                except Exception as decision_error:
                    logger.error(f"自動判断エラー: {decision_error}")

            # 重大エラーの場合は人間に通知
            if "critical" in str(e).lower() or "fatal" in str(e).lower():
                try:
                    await self.human_agent.notify_human(
                        f"🚨 重大エラー (サイクル {self.cycle_count}): {e}"
                    )
                except Exception as notify_error:
                    logger.error(f"通知エラー: {notify_error}")

            return True  # エラーでも継続

    async def run_learning_cycle(self):
        """自動学習サイクル実行"""
        try:
            from agents.self_healing.logging.self_learning_pipeline import SelfLearningPipeline

            pipeline = SelfLearningPipeline(self.sheets)
            result = await pipeline.run_learning_cycle()

            logger.info(f"✅ 学習完了:")
            logger.info(f"   - パターン学習: {result.get('patterns_learned', 0)}個")
            logger.info(f"   - ナレッジ更新: {result.get('knowledge_updated', 0)}件")

        except Exception as e:
            logger.error(f"学習サイクルエラー: {e}")

    async def run(self, max_cycles=None):
        """メインループ実行"""
        logger.info("🎬 メインループ開始")

        try:
            while True:
                # サイクル実行
                should_continue = await self.run_cycle()

                if not should_continue:
                    logger.info("🛑 停止指示により終了")
                    break

                # 最大サイクル数チェック
                if max_cycles and self.cycle_count >= max_cycles:
                    logger.info(f"✅ 最大サイクル数({max_cycles})に到達")
                    break

                # 次のサイクルまで待機（1時間）
                logger.info("⏳ 次のサイクルまで待機 (1時間)")
                await asyncio.sleep(3600)

        except KeyboardInterrupt:
            logger.info("⌨️  キーボード中断を検出")
        except Exception as e:
            logger.error(f"❌ システムエラー: {e}")
        finally:
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"🏁 システム終了 (総サイクル: {self.cycle_count})")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


async def main():
    """エントリーポイント"""
    system = Autonomous24HSystem()

    # テストモードの場合は1サイクルのみ
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    max_cycles = 1 if test_mode else None

    await system.run(max_cycles=max_cycles)


if __name__ == "__main__":
    asyncio.run(main())

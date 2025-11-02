#!/usr/bin/env python3
"""
🤖 24時間自律開発システム v25 - Complete Edition
✅ タスク完了→次タスク自動生成
✅ エラー→自動修復
✅ 学習サイクル統合
"""
import asyncio
import logging
import os
import sys

sys.path.insert(0, ".")

from utils.smart_logger import setup_smart_logging, SmartLogger

from scripts.integrated_orchestrator_v25_complete import IntegratedOrchestrator
from agents.self_healing.logging.decision_support_system import DecisionSupportSystem
from agents.self_healing.logging.knowledge_base_manager import KnowledgeBaseManager
from core_agents.human_interaction_agent_v02_github_api import HumanInteractionAgent
from tools.sheets_manager_v02_mapped import GoogleSheetsManager

logger = SmartLogger(__name__)


class Autonomous24HSystem:
    """24時間自律開発システム v25"""

    def __init__(self):
        """初期化"""
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🚀 24時間自律開発システム v25 起動")
        logger.info("   ✅ タスク完了→次タスク自動生成")
        logger.info("   ✅ エラー→自動修復提案")
        logger.info("   ✅ ナレッジベース学習統合")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # コンポーネント初期化
        self.sheets = GoogleSheetsManager()
        logger.info("✅ GoogleSheetsManager")

        self.knowledge_base = KnowledgeBaseManager(self.sheets)
        logger.info("✅ KnowledgeBaseManager")

        self.decision_support = DecisionSupportSystem(self.sheets, self.knowledge_base)
        logger.info("✅ DecisionSupportSystem")

        self.human_agent = HumanInteractionAgent(
            repo_name=os.getenv("GITHUB_REPOSITORY", "gemini_AI_Agent")
        )
        logger.info("✅ HumanInteractionAgent")

        # v25 Orchestrator初期化
        self.orchestrator = IntegratedOrchestrator(
            decision_support=self.decision_support, human_agent=self.human_agent
        )
        logger.info("✅ IntegratedOrchestrator v25")

        self.cycle_count = 0

        # テストモード判定（初期化時に保存）
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        logger.info(f"🔍 DEBUG: 待機判定 - test_mode={self.test_mode}")
        if self.test_mode:
            logger.info("⚡ テストモード有効")
        logger.info("✅ 全コンポーネント初期化完了")

    async def run_cycle(self):
        """1サイクル実行"""
        self.cycle_count += 1
        logger.info(f"{'='*60}")
        logger.info(f"🔄 サイクル {self.cycle_count} 開始")
        logger.info(f"{'='*60}")

        try:
            # 1. 人間の制御コマンドチェック
            try:
                control = await self.human_agent.check_control_commands()

                if control and control.get("action") == "stop":
                    logger.warning("⏸️  停止指示を検出")
                    return False

                elif control and control.get("action") == "redirect":
                    logger.info(f"🔄 方向変更: {control.get('message', '')}")
            except Exception as e:
                logger.warning(f"人間介入チェックエラー: {e}")

            # 2. タスク実行（IntegratedOrchestratorのrun_continuous_cycle）
            logger.info("🎯 タスク実行開始")
            logger.info(f"🔍 DEBUG: self.test_mode = {self.test_mode}")
            logger.info(f"🔍 DEBUG: cycle_count = {self.cycle_count}")
            await self.orchestrator.run_continuous_cycle(max_duration_minutes=60, single_cycle=True)
            logger.info("✅ タスク実行完了")

            # 3. 6時間ごとに自動学習
            if self.cycle_count % 6 == 0:
                logger.info("🤖 自動学習サイクル実行")
                await self.run_learning_cycle()

            return True

        except Exception as e:
            logger.error(f"❌ サイクル実行エラー: {e}")

            # 自己修復試行
            try:
                decision = self.decision_support.decide_fix_strategy(
                    {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "context": {"cycle": self.cycle_count},
                    }
                )
                logger.info(f"🤖 自動判断: {decision.get('strategy', 'unknown')}")
            except Exception as decision_error:
                logger.error(f"自動判断エラー: {decision_error}")

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
        logger.info("�� メインループ開始")

        try:
            while True:
                # サイクル実行
                should_continue = await self.run_cycle()

                if not should_continue:
                    logger.info("🛑 停止指示により終了")
                    break

                # 最大サイクル数チェック（待機前に確認）
                if max_cycles and self.cycle_count >= max_cycles:
                    logger.info(f"✅ 最大サイクル数({max_cycles})に到達")
                    break

                # 次のサイクルまで待機
                logger.info(f"🔍 DEBUG: 待機判定 - test_mode={self.test_mode}")
                if self.test_mode:
                    logger.info("⚡ テストモード: 次サイクルへ即移行")
                    # テストモードでは待機せずに次サイクルへ
                    continue
                else:
                    logger.info("⏳ 次のサイクルまで待機 (1時間)")
                    await asyncio.sleep(3600)

        except KeyboardInterrupt:
            logger.info("⌨️  キーボード中断を検出")
        except Exception as e:
            logger.error(f"❌ システムエラー: {e}")
            import traceback

            traceback.print_exc()
        finally:
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"🏁 システム終了 (総サイクル: {self.cycle_count})")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


async def main():
    """エントリーポイント"""
    # SmartLog設定（30回に1回タイムスタンプ）
    setup_smart_logging(level=logging.INFO)

    # テストモード判定（最初に定義）
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"

    # MAX_CYCLES設定（test_mode使用）
    max_cycles_env = os.getenv("MAX_CYCLES", "")
    if max_cycles_env:
        max_cycles = int(max_cycles_env)
    elif test_mode:
        max_cycles = 1  # テストモードではデフォルト1サイクル
    else:
        max_cycles = None  # 本番モードでは無限

    logger.info(f"🔧 設定: TEST_MODE={test_mode}, MAX_CYCLES={max_cycles}")

    # システム初期化
    system = Autonomous24HSystem()

    # 実行
    await system.run(max_cycles=max_cycles)


if __name__ == "__main__":
    asyncio.run(main())

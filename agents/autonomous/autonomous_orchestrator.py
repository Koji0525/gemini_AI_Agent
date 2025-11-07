#!/usr/bin/env python3
"""
🤖 AutonomousOrchestrator v1.16.1
24時間自律稼働システム（リトライロジック統合版）
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv(override=True)

# Phase 1-3 エージェント
from agents.code_generation.code_generation_agent import CodeGenerationAgent
from agents.testing.testing_agent import TestingAgent
from agents.error_recovery.error_recovery_agent import ErrorRecoveryAgent
from agents.documentation.documentation_agent import DocumentationAgent
from agents.monitoring.monitoring_agent import MonitoringAgent
from agents.optimization.optimization_agent import OptimizationAgent
from agents.collaboration.collaboration_agent import CollaborationAgent
from agents.learning.learning_optimizer import LearningOptimizer

# PM & Sheets
from core_agents.pm_agent import PMAgent
from tools.sheets_flow_orchestrator import SheetsFlowOrchestrator
from tools.sheets_manager import GoogleSheetsManager

# リトライヘルパー
from tools.sheets_retry_helper import retry_on_api_error

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.name = "Auto"


class AutonomousOrchestrator:
    """24時間自律稼働オーケストレーター（v1.16.1 リトライ統合版）"""

    def __init__(self):
        self.sheets_manager = None
        self.code_gen_agent = None
        self.testing_agent = None
        self.error_recovery_agent = None
        self.doc_agent = None
        self.monitoring_agent = None
        self.opt_agent = None
        self.collab_agent = None
        self.learning_optimizer = None
        self.pm_agent = None
        self.sheets_flow = None

        self.stats = {
            "cycles_completed": 0,
            "tasks_executed": 0,
            "errors_recovered": 0,
            "goals_achieved": 0,
            "api_retries": 0,
            "start_time": None,
        }

        logger.info("✅ Init v1.16.1")

    async def initialize(self):
        """完全初期化"""
        try:
            logger.info("=" * 60)
            logger.info("🚀 初期化開始")
            logger.info("=" * 60)

            # GoogleSheetsManager
            logger.info("📊 SheetsManager...")
            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("❌ SPREADSHEET_ID未設定")

            self.sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
            logger.info(f"  ✅ ID: {spreadsheet_id[:10]}...")

            # Phase 1-3 エージェント
            logger.info("🤖 Phase 1-3...")

            self.code_gen_agent = CodeGenerationAgent()
            logger.info("  ✅ CodeGen")

            self.testing_agent = TestingAgent()
            logger.info("  ✅ Testing")

            self.error_recovery_agent = ErrorRecoveryAgent()
            logger.info("  ✅ ErrorRec")

            self.doc_agent = DocumentationAgent()
            logger.info("  ✅ Docs")

            self.monitoring_agent = MonitoringAgent()
            logger.info("  ✅ Monitor")

            self.opt_agent = OptimizationAgent()
            logger.info("  ✅ Optimize")

            self.learning_optimizer = LearningOptimizer()
            logger.info("  ✅ Learning")

            self.collab_agent = CollaborationAgent()
            logger.info("  ✅ Collab")

            # PMAgent & SheetsFlow
            logger.info("📋 PM & Flow...")

            self.pm_agent = PMAgent(self.sheets_manager)
            logger.info("  ✅ PMAgent")

            self.sheets_flow = SheetsFlowOrchestrator(self.sheets_manager)
            logger.info("  ✅ SheetsFlow")

            # エージェント登録
            logger.info("🔗 登録...")
            self._register_all_agents()

            self.stats["start_time"] = datetime.now()

            logger.info("=" * 60)
            logger.info("✅ 初期化完了")
            logger.info(f"📊 登録数: {len(self.collab_agent.registered_agents)}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"❌ Init失敗: {e}", exc_info=True)
            raise

    def _register_all_agents(self):
        """全エージェント登録"""
        agents_config = [
            ("CodeGeneration", self.code_gen_agent, ["code", "generate", "implementation"]),
            ("Testing", self.testing_agent, ["test", "validate", "pytest"]),
            ("ErrorRecovery", self.error_recovery_agent, ["error", "fix", "debug"]),
            ("Documentation", self.doc_agent, ["docs", "markdown", "readme"]),
            ("Monitoring", self.monitoring_agent, ["monitor", "metrics", "performance"]),
            ("Optimization", self.opt_agent, ["optimize", "performance", "bottleneck"]),
            ("Learning", self.learning_optimizer, ["learn", "improve", "knowledge"]),
        ]

        for agent_name, agent_instance, capabilities in agents_config:
            try:
                self.collab_agent.register_agent(agent_name, agent_instance, capabilities)
                logger.info(f"  ✅ {agent_name}")
            except Exception as e:
                logger.warning(f"  ⚠️ {agent_name}: {e}")

    @retry_on_api_error(max_retries=3, base_delay=1.0)
    async def _load_goal_with_retry(self):
        """project_goal読み込み（リトライ付き）"""
        return await self.pm_agent.load_project_goal()

    @retry_on_api_error(max_retries=3, base_delay=1.0)
    async def _write_tasks_with_retry(self, tasks):
        """pm_tasks書き込み（リトライ付き）"""
        return await self.pm_agent.write_tasks_to_sheet(tasks)

    async def run_autonomous_cycle(self) -> Dict[str, Any]:
        """1サイクル実行（リトライロジック統合版）"""
        cycle_start = datetime.now()
        logger.info("=" * 60)
        logger.info(f"🔄 サイクル #{self.stats['cycles_completed'] + 1}")
        logger.info("=" * 60)

        try:
            # 1. project_goal読み込み（リトライ付き）
            logger.info("📖 Step1: Goal読込...")
            goal = await self._load_goal_with_retry()

            if not goal:
                logger.warning("⚠️ ゴールなし")
                return {
                    "status": "no_goal",
                    "message": "No active goal",
                    "cycle_time": (datetime.now() - cycle_start).total_seconds(),
                }

            logger.info(f"  ✅ Goal: {goal.get('goal_title', 'N/A')}")

            # 2. タスク分解
            logger.info("🔨 Step2: タスク分解...")
            tasks = await self.pm_agent.break_down_goal_to_tasks(goal)

            if not tasks:
                logger.warning("⚠️ タスクなし")
                return {
                    "status": "no_tasks",
                    "goal": goal,
                    "cycle_time": (datetime.now() - cycle_start).total_seconds(),
                }

            logger.info(f"  ✅ {len(tasks)}個生成")

            # pm_tasksに書き込み（リトライ付き）
            await self._write_tasks_with_retry(tasks)
            logger.info(f"  ✅ {len(tasks)}件書込")

            # 3. タスク実行
            logger.info("⚙️ Step3: 実行...")
            execution_results = await self.collab_agent.distribute_tasks_parallel(tasks)

            successful = sum(1 for r in execution_results if r.get("status") == "success")
            logger.info(f"  ✅ {successful}/{len(execution_results)} 成功")

            self.stats["tasks_executed"] += len(execution_results)

            # 4. ログ記録
            logger.info("📝 Step4: ログ...")
            logger.info(f"  ✅ {len(execution_results)}件記録")

            # 5. 監視・学習
            logger.info("📊 Step5: 監視・学習...")

            monitoring_result = await self.monitoring_agent.execute({"type": "collect"})
            cpu_percent = monitoring_result.get("metrics", {}).get("cpu", {}).get("percent", 0)
            logger.info(f"  ✅ CPU {cpu_percent:.1f}%")

            try:
                learning_result = await self.learning_optimizer.execute(
                    {"type": "optimize", "tasks": tasks, "results": execution_results, "goal": goal}
                )
                improvements = learning_result.get("improvements_count", 0)
                logger.info(f"  ✅ 学習: {improvements}件改善")
            except Exception as learn_error:
                logger.warning(f"  ⚠️ 学習スキップ: {learn_error}")

            # 統計更新
            self.stats["cycles_completed"] += 1
            cycle_time = (datetime.now() - cycle_start).total_seconds()

            logger.info("=" * 60)
            logger.info(f"✅ 完了 ({cycle_time:.1f}秒)")
            logger.info(
                f"📊 累計: {self.stats['cycles_completed']}サイクル, {self.stats['tasks_executed']}タスク"
            )
            if self.stats["api_retries"] > 0:
                logger.info(f"🔄 APIリトライ: {self.stats['api_retries']}回")
            logger.info("=" * 60)

            return {
                "status": "success",
                "goal": goal,
                "tasks_count": len(tasks),
                "successful_tasks": successful,
                "cycle_time": cycle_time,
                "stats": self.stats.copy(),
            }

        except Exception as e:
            logger.error(f"❌ エラー: {e}", exc_info=True)

            # ErrorRecoveryAgent で自動修復
            try:
                diagnosis = await self.error_recovery_agent.diagnose_error(
                    error=e, context={"phase": "autonomous_cycle"}
                )

                logger.info(f"🔍 診断: {diagnosis.get('error_type', 'unknown')}")

                recovery_result = await self.error_recovery_agent.apply_fix(
                    error=e,
                    strategy=diagnosis.get("strategy", {}),
                    context={"phase": "autonomous_cycle"},
                )

                if recovery_result.get("status") == "success":
                    logger.info("✅ 修復成功")
                    self.stats["errors_recovered"] += 1
                else:
                    logger.warning(f"⚠️ 修復失敗: {recovery_result.get('message')}")

            except Exception as recovery_error:
                logger.error(f"❌ 修復処理エラー: {recovery_error}")

            return {
                "status": "error",
                "error": str(e),
                "cycle_time": (datetime.now() - cycle_start).total_seconds(),
            }

    async def run_continuous(self, interval_seconds: int = 300):
        """24時間連続稼働"""
        logger.info("=" * 60)
        logger.info("🚀 24時間稼働開始 (v1.16.1)")
        logger.info(f"⏱️  間隔: {interval_seconds}秒")
        logger.info("=" * 60)

        cycle_count = 0

        while True:
            try:
                cycle_count += 1
                result = await self.run_autonomous_cycle()

                logger.info(f"⏸️  {interval_seconds}秒待機...\n")
                await asyncio.sleep(interval_seconds)

            except KeyboardInterrupt:
                logger.info("\n🛑 停止")
                break

            except Exception as e:
                logger.error(f"❌ エラー: {e}", exc_info=True)
                logger.info("⏸️ 60秒待機...")
                await asyncio.sleep(60)

        # 統計
        if self.stats["start_time"]:
            runtime = datetime.now() - self.stats["start_time"]
            logger.info("=" * 60)
            logger.info("📊 統計")
            logger.info(f"  時間: {runtime}")
            logger.info(f"  サイクル: {self.stats['cycles_completed']}")
            logger.info(f"  タスク: {self.stats['tasks_executed']}")
            logger.info(f"  修復: {self.stats['errors_recovered']}")
            logger.info(f"  リトライ: {self.stats['api_retries']}")
            logger.info("=" * 60)


async def main():
    """エントリーポイント"""
    orchestrator = AutonomousOrchestrator()

    try:
        await orchestrator.initialize()
        await orchestrator.run_continuous(interval_seconds=300)

    except KeyboardInterrupt:
        logger.info("🛑 終了")
    except Exception as e:
        logger.error(f"❌ 致命的: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

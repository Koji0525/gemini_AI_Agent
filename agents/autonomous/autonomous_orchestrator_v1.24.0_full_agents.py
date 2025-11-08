"""
AutonomousOrchestrator v1.24.0 Full Agents - ログ修正版

【v1.24.0からの変更】
✅ INFOログを完全に抑制（WARNING以上のみ表示）
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.advanced_analytics.execution_analyzer import ExecutionAnalyzer
from agents.collaboration.collaboration_agent import CollaborationAgent
from agents.monitoring.monitoring_agent import MonitoringAgent
from agents.system_observer.system_observer_v3 import SystemObserverV3
from browser_control.sheets_manager import GoogleSheetsManager
from core_agents.pm_agent import PMAgent
from core_agents.review_agent import ReviewAgent
from task_executor.task_executor_main import TaskExecutor
from tools.safe_sheets_wrapper import SafeSheetsWrapper

logger = logging.getLogger(__name__)


def configure_logging_strict():
    """ログ設定を厳密に適用（WARNING以上のみ）"""
    # ルートロガーを設定
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s:%(name)s:%(message)s",
        force=True,  # 既存の設定を上書き
    )

    # 全ての既存ロガーのレベルを変更
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # 特定のロガーを明示的に設定
    critical_loggers = [
        "tools.safe_sheets_wrapper",
        "core_agents.pm_agent",
        "task_executor.task_executor_main",
        "core_agents.review_agent",
        "agents.monitoring.monitoring_agent",
        "agents.collaboration.collaboration_agent",
        "agents.advanced_analytics.execution_analyzer",
        "agents.system_observer.system_observer_v3",
    ]

    for logger_name in critical_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


class AutonomousOrchestrator:
    """自律開発オーケストレーター v1.24.0 Full Agents"""

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.cycle_interval = int(os.getenv("CYCLE_INTERVAL", "10" if debug_mode else "180"))

        # エージェント
        self.sheets_manager = None
        self.safe_sheets = None
        self.pm_agent = None
        self.task_executor = None
        self.review_agent = None
        self.monitoring_agent = None
        self.collab_agent = None
        self.execution_analyzer = None

        # 🔭 SystemObserver v3（全エージェント監視）
        self.system_observer = None

        # 統計
        self.stats = {
            "cycles_completed": 0,
            "version": "1.24.0-full-agents",
        }

        print(f"✅ AutonomousOrchestrator v1.24.0 Full Agents 初期化")

    async def initialize(self):
        """完全初期化"""
        try:
            print("=" * 70)
            print("🚀 AutonomousOrchestrator v1.24.0 Full Agents 初期化開始")
            print("=" * 70)

            from dotenv import load_dotenv

            load_dotenv(override=True)

            # ログ設定を厳密に適用
            configure_logging_strict()

            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

            # 基盤
            print("📊 GoogleSheetsManager初期化")
            self.sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
            self.safe_sheets = SafeSheetsWrapper(self.sheets_manager)

            # 初期化後にもう一度ログレベルを設定
            configure_logging_strict()

            # エージェント
            print("🤖 エージェント初期化")
            self.pm_agent = PMAgent(self.sheets_manager)
            self.task_executor = TaskExecutor(self.sheets_manager)
            self.review_agent = ReviewAgent(self.safe_sheets)
            self.monitoring_agent = MonitoringAgent()
            self.collab_agent = CollaborationAgent()
            self.execution_analyzer = ExecutionAnalyzer(self.sheets_manager)

            # さらにもう一度ログレベルを設定（各エージェントの初期化後）
            configure_logging_strict()

            # 🔭 SystemObserver v3
            print("🔭 SystemObserver v3初期化（全エージェント監視）")
            self.system_observer = SystemObserverV3(
                monitoring_agent=self.monitoring_agent,
                execution_analyzer=self.execution_analyzer,
                collaboration_agent=self.collab_agent,
                task_executor=self.task_executor,
            )

            # 全エージェントを登録
            print("\n📋 全エージェントを登録中...")
            agent_count = self.system_observer.register_orchestrator_agents(self)

            print("=" * 70)
            print(f"✅ 全エージェント初期化完了（{agent_count}個）")
            print("🎯 統合率: 100% + 全エージェント監視")
            print("=" * 70)

            # 最終的なログレベル設定
            configure_logging_strict()

            return True

        except Exception as e:
            logger.error(f"❌ 初期化失敗: {e}")
            return False

    async def execute_autonomous_cycle(self):
        """メインの自律実行サイクル"""
        try:
            cycle_start = datetime.now()
            print("\n" + "=" * 70)
            print(f"🔄 サイクル #{self.stats['cycles_completed'] + 1} 開始")
            print("=" * 70)

            # 🔭 包括的分析
            print("\n🔭 SystemObserver v3: 全エージェント監視")
            analysis = self.system_observer.collect_comprehensive_analysis()

            # 結果表示
            snapshot = analysis["snapshot"]
            print(f"   ✅ CPU: {snapshot['resources'].get('cpu_percent', 0):.1f}%")
            print(f"   ✅ メモリ: {snapshot['resources'].get('memory_percent', 0):.1f}%")

            # エージェント詳細
            agents = snapshot["agents"]
            print(f"   👥 エージェント: {agents['total_agents']}個")
            print(f"      健全: {agents.get('healthy_agents', 0)}個")
            print(f"      警告: {agents.get('warning_agents', 0)}個")

            if analysis.get("cost"):
                print(f"   💰 コスト（時間）: ${analysis['cost']['hourly_cost']:.4f}")

            # 統計更新
            self.stats["cycles_completed"] += 1
            cycle_duration = (datetime.now() - cycle_start).total_seconds()

            print("\n" + "=" * 70)
            print(f"✅ サイクル #{self.stats['cycles_completed']} 完了")
            print(f"⏱️ 実行時間: {cycle_duration:.2f}秒")
            print("=" * 70)

        except Exception as e:
            logger.error(f"❌ サイクル実行エラー: {e}")

    async def run(self, max_cycles: int = None):
        """メインループ"""
        try:
            if not await self.initialize():
                logger.error("❌ 初期化失敗。終了します。")
                return

            print("\n" + "=" * 70)
            print("🚀 自律開発システム起動（v1.24.0 Full Agents）")
            print("=" * 70)

            cycle_count = 0
            while True:
                await self.execute_autonomous_cycle()

                cycle_count += 1
                if max_cycles and cycle_count >= max_cycles:
                    print(f"\n✅ 最大サイクル数({max_cycles})に到達。終了します。")
                    break

                if max_cycles is None or cycle_count < max_cycles:
                    print(f"\n⏳ 次のサイクルまで{self.cycle_interval}秒待機...")
                    await asyncio.sleep(self.cycle_interval)

        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")


async def main():
    parser = argparse.ArgumentParser(description="AutonomousOrchestrator v1.24.0")
    parser.add_argument("--debug", action="store_true", help="デバッグモード")
    parser.add_argument("--cycles", type=int, default=3, help="実行サイクル数")

    args = parser.parse_args()

    # ログ設定（WARNING以上のみ）
    configure_logging_strict()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 AutonomousOrchestrator v1.24.0 Full Agents")
    print("🔭 SystemObserver v3: 全エージェント監視")
    print(f"🔄 実行サイクル: {args.cycles}回")
    print("📝 ログレベル: WARNING以上のみ表示")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    orchestrator = AutonomousOrchestrator(debug_mode=args.debug)
    await orchestrator.run(max_cycles=args.cycles)


if __name__ == "__main__":
    asyncio.run(main())

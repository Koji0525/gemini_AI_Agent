"""
Phase 2 6時間テスト v2 - TaskExecutor統合版（修正版）
ObservabilityManager の実メソッドに対応
"""

import asyncio
import sys
import os
from datetime import datetime

# プロジェクトルートをPYTHONPATHに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from core_agents.pm_agent import PMAgent
from task_executor.task_executor_main import TaskExecutor
from agents.observability.observability_manager import ObservabilityManager


class AutonomousOrchestratorV2:
    """TaskExecutor統合版オーケストレーター（修正版）"""

    def __init__(self):
        print("1️⃣ コンポーネント初期化中...")

        # 既存コンポーネント
        self.sheets = GoogleSheetsManager()
        self.safe_sheets = SafeSheetsWrapper(self.sheets)
        print("   ✅ SheetsManager")

        self.pm_agent = PMAgent(sheets_manager=self.sheets)
        print("   ✅ PMAgent")

        self.observability = ObservabilityManager()
        print("   ✅ ObservabilityManager")

        # ObservabilityManager の実際のメソッドを確認
        self._check_observability_methods()

        # 新規追加: TaskExecutor
        try:
            self.task_executor = TaskExecutor(sheets_manager=self.sheets)
            print("   ✅ TaskExecutor (新規)")
        except Exception as e:
            print(f"   ⚠️ TaskExecutor 初期化失敗: {e}")
            self.task_executor = None

        print("\n✅ オーケストレーター初期化成功\n")

    def _check_observability_methods(self):
        """ObservabilityManager の利用可能メソッド確認"""
        available_methods = [
            m
            for m in dir(self.observability)
            if not m.startswith("_") and callable(getattr(self.observability, m))
        ]
        print(f"      利用可能: {', '.join(available_methods[:3])}...")

    async def execute_autonomous_cycle(self):
        """1サイクル実行"""

        print("⏳ 1サイクル実行中...")

        # ObservabilityManager の記録（安全な方法）
        try:
            # record_trace が存在する場合は使用
            if hasattr(self.observability, "record_trace"):
                # 引数なしで呼び出せるか確認
                import inspect

                sig = inspect.signature(self.observability.record_trace)
                params = list(sig.parameters.keys())

                if not params or (len(params) == 1 and params[0] == "self"):
                    # 引数なしメソッド
                    self.observability.record_trace()
                else:
                    # 引数ありの場合（実装に合わせる）
                    print("   ℹ️ ObservabilityManager: カスタムシグネチャ検出")
        except Exception as e:
            print(f"   ℹ️ ObservabilityManager 記録スキップ: {e}")

        # TaskExecutor によるタスク実行
        if self.task_executor:
            try:
                pending_tasks = self.task_executor.get_pending_tasks()

                if pending_tasks:
                    print(f"📋 pending タスク: {len(pending_tasks)}件")

                    # 最大3件実行
                    for task in pending_tasks[:3]:
                        result = await self.task_executor.execute_task(task)

                        if result["success"]:
                            print(f"   ✅ {task['title']} ({result['elapsed_time']:.2f}秒)")
                        else:
                            print(f"   ❌ {task['title']}: {result.get('error', 'Unknown')}")
                else:
                    print("📋 pending タスクなし")

            except Exception as e:
                print(f"⚠️ TaskExecutor エラー: {e}")

        print("✅ サイクル完了")

    async def run_6hour_test(self, max_hours: int = 6):
        """6時間稼働テスト"""
        print(f"🚀 {max_hours}時間稼働ループ開始...\n")

        start_time = datetime.now()
        cycle = 0

        try:
            while True:
                cycle += 1
                elapsed = (datetime.now() - start_time).total_seconds() / 3600

                if elapsed >= max_hours:
                    print(f"\n⏰ {max_hours}時間経過 - 稼働終了")
                    break

                print(f"\n{'━' * 80}")
                print(f"サイクル {cycle} (経過時間: {elapsed:.2f}時間)")
                print(f"{'━' * 80}")

                await self.execute_autonomous_cycle()

                print("⏸️  次のサイクルまで3分待機...")
                await asyncio.sleep(180)

        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")
        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
            import traceback

            traceback.print_exc()

        finally:
            # 統計出力
            print(f"\n{'=' * 80}")
            print("📊 稼働統計")
            print(f"{'=' * 80}")
            print(f"総サイクル数: {cycle}")
            print(f"稼働時間: {elapsed:.2f}時間")

            if self.task_executor:
                stats = self.task_executor.get_execution_stats()
                print(f"総タスク数: {stats.get('total_tasks', 0)}")
                print(f"成功率: {stats.get('success_rate', 0):.1f}%")
                print(f"ナレッジ活用率: {stats.get('knowledge_usage_rate', 0):.1f}%")

            print(f"{'=' * 80}")


async def main():
    orchestrator = AutonomousOrchestratorV2()
    await orchestrator.run_6hour_test(max_hours=6)


if __name__ == "__main__":
    asyncio.run(main())

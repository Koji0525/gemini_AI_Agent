#!/usr/bin/env python3
"""
🎹 Integrated Development Orchestrator v1.0
役割: 全エージェントの統合制御ハブ

連携エージェント:
1. PM Agent → 目標分解・タスク管理
2. Task Executor → タスクルーティング
3. WordPress Orchestrator → WP開発実行
4. 自己修復システム → エラー対応
5. Progress Monitor → 進捗可視化
"""
import sys

sys.path.insert(0, ".")
import asyncio
import time
import os
from datetime import datetime
from configuration.config_loader import get_config


# 既存エージェントの動的インポート
def import_existing_agents():
    """既存エージェントを動的にインポート"""
    agents = {}

    # PM Agentのインポート
    try:
        if os.path.exists("pm_agent.py"):
            import importlib.util

            spec = importlib.util.spec_from_file_location("pm_agent", "pm_agent.py")
            pm_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pm_module)
            agents["pm_agent"] = pm_module
            print("✅ PM Agent インポート成功")
    except Exception as e:
        print(f"⚠️ PM Agentインポート失敗: {e}")

    # Task Executorのインポート
    try:
        if os.path.exists("task_executor.py"):
            spec = importlib.util.spec_from_file_location("task_executor", "task_executor.py")
            te_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(te_module)
            agents["task_executor"] = te_module
            print("✅ Task Executor インポート成功")
    except Exception as e:
        print(f"⚠️ Task Executorインポート失敗: {e}")

    # WordPress Orchestratorのインポート
    try:
        if os.path.exists("agents/wordpress/specialized/wp_orchestrator.py"):
            from agents.wordpress.specialized.wp_orchestrator import WordPressOrchestrator

            agents["wp_orchestrator"] = WordPressOrchestrator
            print("✅ WordPress Orchestrator インポート成功")
    except Exception as e:
        print(f"⚠️ WordPress Orchestratorインポート失敗: {e}")

    return agents


class IntegratedOrchestrator:
    """24時間自律開発の統合制御ハブ"""

    def __init__(self):
        self.config = get_config()
        self.agents = import_existing_agents()
        self.control_flag_file = "/tmp/system_control_flag.txt"
        self.running = True

        print(f"✅ Orchestrator初期化完了")
        print(f"   利用可能なエージェント: {list(self.agents.keys())}")

    async def run_continuous_cycle(self, max_duration_minutes: int = 330):
        """
        継続的な開発サイクルを実行

        Args:
            max_duration_minutes: 最大実行時間（デフォルト5.5時間）
        """
        start_time = time.time()
        cycle_count = 0

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 24時間自律開発システム 起動")
        print(f"⏰ 最大実行時間: {max_duration_minutes}分")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        while self.running:
            cycle_count += 1
            cycle_start = time.time()

            print(f"\n{'='*60}")
            print(f"🔄 サイクル {cycle_count} 開始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")

            # 1. 制御フラグチェック
            if self._check_stop_flag():
                print("🛑 停止フラグ検出。システムを安全に停止します...")
                break

            # 2. タスク取得と実行
            try:
                tasks_executed = await self._execute_development_cycle()

                if tasks_executed == 0:
                    print("⏸️  実行可能なタスクなし。5分後に再確認...")
                    await asyncio.sleep(300)
                else:
                    print(f"✅ {tasks_executed}件のタスクを実行")

            except Exception as e:
                print(f"❌ サイクルエラー: {e}")
                print("   30秒後にリトライ...")
                await asyncio.sleep(30)

            # 3. タイムアウトチェック
            elapsed = (time.time() - start_time) / 60
            if elapsed > max_duration_minutes:
                print(f"\n⏰ {max_duration_minutes}分経過。次のCronサイクルへ引き継ぎ...")
                break

            cycle_duration = (time.time() - cycle_start) / 60
            print(f"\n✅ サイクル {cycle_count} 完了（所要時間: {cycle_duration:.1f}分）")
            print(f"⏳ 累計実行時間: {elapsed:.1f}/{max_duration_minutes}分")

            # 短時間待機
            await asyncio.sleep(60)

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🏁 開発サイクル終了（総サイクル数: {cycle_count}）")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async def _execute_development_cycle(self) -> int:
        """開発サイクルを実行し、処理したタスク数を返す"""
        tasks_count = 0

        # 既存エージェントを使ってタスクを実行
        # （実装は既存エージェントのインターフェースに合わせて調整）

        print("📋 開発サイクル実行中...")
        print("   （既存PM Agent/Task Executorとの連携を実装予定）")

        # 暫定: テストメッセージ
        await asyncio.sleep(2)

        return tasks_count

    def _check_stop_flag(self) -> bool:
        """人間からの停止フラグをチェック"""
        try:
            if not os.path.exists(self.control_flag_file):
                return False

            with open(self.control_flag_file, "r") as f:
                flag = f.read().strip()

            return flag == "STOP"
        except:
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Integrated Development Orchestrator - 24時間自律開発システム")
    parser.add_argument("--max-duration", type=int, default=330, help="最大実行時間（分）")
    parser.add_argument("--test", action="store_true", help="テストモード（5分間実行）")

    args = parser.parse_args()

    duration = 5 if args.test else args.max_duration

    orchestrator = IntegratedOrchestrator()
    asyncio.run(orchestrator.run_continuous_cycle(duration))


if __name__ == "__main__":
    main()

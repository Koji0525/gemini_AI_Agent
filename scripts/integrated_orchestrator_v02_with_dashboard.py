#!/usr/bin/env python3
"""
Integrated Orchestrator v2 - Progress Dashboard統合版
Day 5完成: 6時間ごとの自動進捗更新
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configuration.config_loader import get_config
from tools.sheets_manager import GoogleSheetsManager


class IntegratedOrchestrator:
    """24時間自律開発の統合制御ハブ - Progress Dashboard連携"""

    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        self.control_flag_path = Path("/tmp/system_control_flag.txt")
        self.cycle_count = 0
        
        print("🚀 Integrated Orchestrator v2 初期化完了")
        print("   📊 Progress Dashboard自動更新: 有効")

    async def run_continuous_cycle(self, max_duration_minutes: int = 330):
        """
        継続的なサイクル実行 (最大330分 = 5.5時間)
        6時間ごとのGitHub Actions実行に対応
        """
        print(f"\n{'='*80}")
        print(f"🔄 継続サイクル開始 (最大: {max_duration_minutes}分)")
        print(f"{'='*80}\n")

        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=max_duration_minutes)

        while datetime.now() < end_time:
            self.cycle_count += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 60

            print(f"\n{'='*80}")
            print(f"📍 サイクル {self.cycle_count} 開始")
            print(f"⏱️  経過時間: {elapsed:.1f}分 / {max_duration_minutes}分")
            print(f"{'='*80}\n")

            # 制御フラグ確認
            if self._check_stop_flag():
                print("🛑 停止フラグ検出 - サイクル終了")
                break

            # メインサイクル実行
            cycle_start = datetime.now()
            await self._run_single_cycle()
            cycle_duration = (datetime.now() - cycle_start).total_seconds() / 60

            print(f"\n✅ サイクル {self.cycle_count} 完了 ({cycle_duration:.1f}分)")
            print(f"⏳ 累計: {elapsed + cycle_duration:.1f}分 / {max_duration_minutes}分")

            # サイクル間の待機(残り時間がある場合)
            remaining = (end_time - datetime.now()).total_seconds()
            if remaining > 0:
                wait_time = min(180, remaining)  # 最大3分待機
                print(f"⏸️  次のサイクルまで {wait_time:.0f}秒待機...")
                await asyncio.sleep(wait_time)

        total_elapsed = (datetime.now() - start_time).total_seconds() / 60
        print(f"\n{'='*80}")
        print(f"🏁 継続サイクル完了")
        print(f"   総サイクル数: {self.cycle_count}")
        print(f"   総実行時間: {total_elapsed:.1f}分")
        print(f"{'='*80}\n")

    async def _run_single_cycle(self):
        """単一サイクルの実行"""
        try:
            # 1. pm_tasksからpendingタスクを取得
            print("📋 pm_tasksからタスク取得中...")
            tasks = await self._get_pending_tasks()
            
            if not tasks:
                print("ℹ️  実行可能なタスクがありません")
                
                # タスクがなくてもProgress Dashboardは更新
                await self._update_progress_dashboard()
                return

            print(f"🎯 {len(tasks)}個のpendingタスクを検出")

            # 2. 各タスクを実行
            for i, task in enumerate(tasks, 1):
                print(f"\n--- タスク {i}/{len(tasks)} ---")
                await self._execute_task(task)

            # 3. サイクル終了時にProgress Dashboard更新
            print("\n📊 Progress Dashboard更新中...")
            await self._update_progress_dashboard()

        except Exception as e:
            print(f"❌ サイクル実行エラー: {e}")
            import traceback
            traceback.print_exc()

    async def _get_pending_tasks(self):
        """pm_tasksからpendingステータスのタスクを取得"""
        try:
            data = self.sheets_manager.read_range("pm_tasks!A:Z")
            if not data or len(data) < 2:
                return []

            headers = data[0]
            status_idx = self._find_column_index(headers, ['status', 'ステータス'])
            
            pending_tasks = []
            for row in data[1:]:
                if len(row) > status_idx:
                    status = row[status_idx].lower()
                    if status == 'pending':
                        task = {
                            'task_id': row[0] if len(row) > 0 else "",
                            'goal_id': row[1] if len(row) > 1 else "",
                            'task_name': row[2] if len(row) > 2 else "",
                            'raw_row': row
                        }
                        pending_tasks.append(task)

            return pending_tasks

        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            return []

    async def _execute_task(self, task):
        """タスク実行(現状はログ出力のみ)"""
        print(f"🔧 タスク実行: {task['task_name'][:50]}...")
        
        # TODO: Task Executorへのルーティング実装
        # await self.task_executor.execute(task)
        
        # 現状は実行完了としてマーク
        print(f"✅ タスク完了: {task['task_id']}")

    async def _update_progress_dashboard(self):
        """Progress Dashboardを自動更新"""
        try:
            print("📊 Progress Dashboard更新開始...")
            
            # UnifiedProgressUpdaterをインポートして実行
            from scripts.unified_progress_updater import UnifiedProgressUpdater
            updater = UnifiedProgressUpdater()
            await updater.update_progress_dashboard()
            
            print("✅ Progress Dashboard更新完了")

        except Exception as e:
            print(f"⚠️ Progress Dashboard更新エラー: {e}")
            # エラーがあってもサイクルは継続
            import traceback
            traceback.print_exc()

    def _check_stop_flag(self):
        """停止フラグの確認"""
        try:
            if self.control_flag_path.exists():
                flag = self.control_flag_path.read_text().strip().upper()
                return flag == "STOP"
        except Exception as e:
            print(f"⚠️ 制御フラグ確認エラー: {e}")
        return False

    def _find_column_index(self, headers, possible_names):
        """列インデックスを柔軟に検索"""
        for i, header in enumerate(headers):
            if header.lower() in [name.lower() for name in possible_names]:
                return i
        return 0


def main():
    """メインエントリーポイント"""
    try:
        orchestrator = IntegratedOrchestrator()
        asyncio.run(orchestrator.run_continuous_cycle(max_duration_minutes=330))
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"\n❌ 実行エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

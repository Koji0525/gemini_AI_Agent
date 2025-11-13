#!/usr/bin/env python3
"""
タスク実行ログ分析
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.base_data_accessor import BaseDataAccessor

    class ExecutionLogAnalyzer(BaseDataAccessor):
        def analyze_logs(self):
            """実行ログを分析"""
            print("📋 タスク実行ログ分析")
            print("=" * 60)

            # 実行ログを取得
            logs = self.read_sheet_as_dicts("task_execution_log")

            print(f"実行ログ総数: {len(logs)}")

            # 最近の実行ログ（最大10件）
            recent_logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]

            print("\n📅 最近の実行ログ:")
            for log in recent_logs:
                task_id = log.get("task_id", "unknown")
                status = log.get("status", "unknown")
                timestamp = log.get("timestamp", "unknown")
                print(f"  {timestamp} - {task_id} - {status}")

            # 6_test_004の実行回数
            task_6_executions = [log for log in logs if log.get("task_id") == "6_test_004"]
            print(f"\n🔁 6_test_004の実行回数: {len(task_6_executions)}回")

            # 重複実行のパターンを分析
            task_execution_count = {}
            for log in logs:
                task_id = log.get("task_id")
                if task_id not in task_execution_count:
                    task_execution_count[task_id] = 0
                task_execution_count[task_id] += 1

            # 複数回実行されているタスク
            multiple_executions = {
                task_id: count for task_id, count in task_execution_count.items() if count > 1
            }
            if multiple_executions:
                print(f"\n⚠️ 複数回実行されているタスク:")
                for task_id, count in multiple_executions.items():
                    print(f"  {task_id}: {count}回")
            else:
                print(f"\n✅ 複数回実行されているタスクはありません")

    analyzer = ExecutionLogAnalyzer()
    analyzer.analyze_logs()

except Exception as e:
    print(f"❌ ログ分析エラー: {e}")

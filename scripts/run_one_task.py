#!/usr/bin/env python3
"""1タスク実行（最終版 v6.0 - 機能完全性保証）"""
import sys
from pathlib import Path

# 修正: parent.parent でプロジェクトルートを取得
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.task_execution.high_quality_executor_v6 import \
    HighQualityExecutorV6
from tools.google_sheets_manager import GoogleSheetsManager


def main():
    print("=" * 60)
    print("🚀 1タスク実行（最終版 v6.0 - 機能完全性保証）")
    print("=" * 60)

    try:
        # GoogleSheetsManager を使用（BaseDataAccessor の代わり）
        sheets_mgr = GoogleSheetsManager()

        # pending タスクを取得（正しいメソッド名を使用）
        all_tasks = sheets_mgr.read_pm_tasks()
        pending_tasks = [t for t in all_tasks if t.get("status") == "pending"][:1]

        if not pending_tasks:
            print("⚠️ 実行可能なタスクがありません")
            return

        task = pending_tasks[0]
        print(f"\n📋 タスク実行開始")
        print(f"   ID: {task.get('task_id', 'N/A')}")
        print(f"   内容: {task.get('description', 'N/A')[:100]}...")

        # 実行
        executor = HighQualityExecutorV6()
        result = executor.execute_task(task)

        print(f"\n✅ 実行完了")
        print(f"   ステータス: {result.get('status', 'unknown')}")
        print(f"   出力: {result.get('output_file', 'N/A')}")

    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

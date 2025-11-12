"""
実スプレッドシート操作テスト
既存のSafeSheetsWrapperを活用
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

# 環境変数読み込み
env_path = Path("/workspaces/gemini_AI_Agent/.env")
load_dotenv(dotenv_path=env_path)

from scripts.integrated.integrated_orchestrator_v31_core import IntegratedOrchestratorV31Core


async def test_real_sheets_operations():
    """実スプレッドシート操作テスト"""

    print("=" * 60)
    print("🧪 実スプレッドシート操作テスト")
    print("=" * 60)
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # オーケストレーター初期化
    print("\n【STEP 1】オーケストレーター初期化")
    try:
        orchestrator = IntegratedOrchestratorV31Core()
        print("✅ 初期化成功")
    except Exception as e:
        print(f"❌ 初期化失敗: {e}")
        return

    # sheets属性の確認
    print("\n【STEP 2】SafeSheetsWrapper確認")
    if not hasattr(orchestrator, "sheets") or orchestrator.sheets is None:
        print("❌ SafeSheetsWrapperが利用できません")
        return

    print(f"✅ SafeSheetsWrapper: {type(orchestrator.sheets).__name__}")

    # 実スプレッドシートからゴール読み込み（直接SafeSheetsWrapper使用）
    print("\n【STEP 3】実スプレッドシートからゴール読み込み")
    try:
        # SafeSheetsWrapperを直接使用
        goals = orchestrator.sheets.safe_read("project_goal!A2:C100", default=[])
        print(f"✅ ゴール読み込み成功: {len(goals)}件")

        if len(goals) > 0:
            print("\n📋 読み込まれたゴール（実データ）:")
            for i, goal in enumerate(goals[:5], 1):
                if len(goal) > 0:
                    goal_name = goal[0] if len(goal) > 0 else "(空)"
                    description = goal[1] if len(goal) > 1 else "-"
                    priority = goal[2] if len(goal) > 2 else "-"
                    print(f"   {i}. {goal_name}")
                    print(f"      説明: {description}")
                    print(f"      優先度: {priority}")
        else:
            print("⚠️ project_goalシートにゴールが登録されていません")
            print("\n📝 スプレッドシートに以下の形式でゴールを追加してください:")
            print("   A列: ゴール名")
            print("   B列: 説明")
            print("   C列: 優先度(高/中/低)")

    except Exception as e:
        print(f"❌ ゴール読み込み失敗: {e}")
        import traceback

        traceback.print_exc()
        goals = []

    # フォールバックタスク生成
    print("\n【STEP 4】フォールバックタスク生成")
    try:
        if len(goals) > 0:
            test_goals = goals[:2]
        else:
            test_goals = [
                ["Phase2完了", "6時間稼働テスト成功", "高"],
                ["統合テスト", "全システム統合確認", "高"],
            ]

        tasks = orchestrator._create_fallback_tasks(test_goals)
        print(f"✅ タスク生成: {len(tasks)}件")

        if len(tasks) > 0:
            print("\n📋 生成されたタスク:")
            for i, task in enumerate(tasks[:6], 1):
                task_name = task[0] if len(task) > 0 else "(空)"
                print(f"   {i}. {task_name}")

    except Exception as e:
        print(f"❌ タスク生成失敗: {e}")
        import traceback

        traceback.print_exc()
        tasks = []

    # タスク書き込み（実スプレッドシート）
    print("\n【STEP 5】実スプレッドシートへのタスク書き込み")
    try:
        if len(tasks) > 0:
            # SafeSheetsWrapperを直接使用してタスク書き込み
            success = orchestrator.sheets.safe_append("pm_tasks", tasks)

            if success:
                print(f"✅ タスク書き込み成功: {len(tasks)}件")
                print("   → pm_tasksシートに追記されました")
            else:
                print("⚠️ タスク書き込みに問題がありました")
        else:
            print("⚠️ 書き込むタスクがありません")

    except Exception as e:
        print(f"❌ タスク書き込み失敗: {e}")
        import traceback

        traceback.print_exc()

    # 書き込まれたタスクの確認
    print("\n【STEP 6】書き込まれたタスクの確認")
    try:
        # pm_tasksシートから読み込み
        all_tasks = orchestrator.sheets.safe_read("pm_tasks!A2:E100", default=[])
        print(f"✅ pm_tasksシート読み込み: {len(all_tasks)}件")

        if len(all_tasks) > 0:
            print("\n📋 最新のタスク（最後の5件）:")
            for i, task in enumerate(all_tasks[-5:], 1):
                if len(task) > 0:
                    task_name = task[0] if len(task) > 0 else "(空)"
                    status = task[2] if len(task) > 2 else "-"
                    print(f"   {i}. {task_name} (ステータス: {status})")

    except Exception as e:
        print(f"⚠️ タスク確認でエラー: {e}")

    # 最終レポート
    print("\n" + "=" * 60)
    print("📊 実スプレッドシート操作テスト完了!")
    print("=" * 60)
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"読み込んだゴール数: {len(goals)}")
    print(f"生成したタスク数: {len(tasks)}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_real_sheets_operations())

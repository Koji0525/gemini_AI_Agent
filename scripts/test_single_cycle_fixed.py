"""
1サイクル動作テスト (環境変数読み込み修正版)

【目的】
- ゴール読み込み
- タスク生成
- タスク書き込み
の1サイクルを実行

【実行方法】
python3 scripts/test_single_cycle_fixed.py
"""

import asyncio
import sys
import os
from datetime import datetime

# プロジェクトルート
sys.path.insert(0, "/workspaces/gemini_AI_Agent")

# 環境変数読み込み (修正版)
from pathlib import Path
from dotenv import load_dotenv

# .envファイルのパスを明示的に指定
env_path = Path("/workspaces/gemini_AI_Agent/.env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ .envファイル読み込み: {env_path}")
else:
    print(f"⚠️ .envファイルが見つかりません: {env_path}")

# 環境変数確認
spreadsheet_id = os.getenv("SPREADSHEET_ID")
if spreadsheet_id:
    print(f"✅ SPREADSHEET_ID: {spreadsheet_id[:20]}...")
else:
    print("⚠️ SPREADSHEET_ID環境変数が設定されていません")

from scripts.integrated.integrated_orchestrator_v31_core import IntegratedOrchestratorV31Core


async def test_single_cycle():
    """1サイクル動作テスト"""

    print("\n" + "=" * 60)
    print("🧪 1サイクル動作テスト")
    print("=" * 60)
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # オーケストレーター初期化
    print("\n【STEP 1】オーケストレーター初期化")
    try:
        orchestrator = IntegratedOrchestratorV31Core()
        print("✅ 初期化成功")

        # デバッグ: 属性確認
        print("\n📊 属性確認:")
        print(f"   sheets: {type(orchestrator.sheets).__name__ if orchestrator.sheets else 'None'}")
        print(
            f"   sheets_manager: {type(orchestrator.sheets_manager).__name__ if orchestrator.sheets_manager else 'None'}"
        )
        print(
            f"   pm_agent: {type(orchestrator.pm_agent).__name__ if orchestrator.pm_agent else 'None'}"
        )

    except Exception as e:
        print(f"❌ 初期化失敗: {e}")
        import traceback

        traceback.print_exc()
        return

    # ゴール読み込み
    print("\n【STEP 2】ゴール読み込み")
    try:
        goals = orchestrator._read_project_goals()
        print(f"✅ ゴール読み込み: {len(goals)}件")

        if len(goals) == 0:
            print("⚠️ ゴールが登録されていません")
            print("   デフォルトゴールを使用します")
            goals = [
                ["統合テスト", "24時間自律稼働テストの実施", "高"],
                ["Phase2完了", "6時間稼働テストの成功", "高"],
            ]
        else:
            print("\n📋 読み込まれたゴール:")
            for i, goal in enumerate(goals[:3], 1):
                if len(goal) > 0:
                    print(f"   {i}. {goal[0]}")

    except Exception as e:
        print(f"❌ ゴール読み込み失敗: {e}")
        import traceback

        traceback.print_exc()

        # フォールバック
        print("\n⚠️ デフォルトゴールを使用します")
        goals = [
            ["統合テスト", "24時間自律稼働テストの実施", "高"],
            ["Phase2完了", "6時間稼働テストの成功", "高"],
        ]

    # タスク生成
    print("\n【STEP 3】タスク生成")
    try:
        # PMAgentを使用してタスク生成
        tasks = await orchestrator._execute_with_pm_agent(goals[:2])
        print(f"✅ タスク生成: {len(tasks)}件")

        if len(tasks) > 0:
            print("\n📋 生成されたタスク:")
            for i, task in enumerate(tasks[:5], 1):
                task_name = task[0] if len(task) > 0 else "(空)"
                print(f"   {i}. {task_name}")
        else:
            print("⚠️ タスクが生成されませんでした")

    except Exception as e:
        print(f"❌ タスク生成失敗: {e}")
        import traceback

        traceback.print_exc()
        tasks = []

    # タスク書き込み
    print("\n【STEP 4】タスク書き込み")
    try:
        if len(tasks) > 0:
            success = orchestrator._write_pm_tasks(tasks)
            if success:
                print("✅ タスク書き込み成功")
            else:
                print("⚠️ タスク書き込みに問題があります")
        else:
            print("⚠️ 書き込むタスクがありません")
    except Exception as e:
        print(f"❌ タスク書き込み失敗: {e}")
        import traceback

        traceback.print_exc()

    # 最終レポート
    print("\n" + "=" * 60)
    print("📊 1サイクルテスト完了!")
    print("=" * 60)
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"ゴール数: {len(goals)}")
    print(f"生成タスク数: {len(tasks)}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_single_cycle())

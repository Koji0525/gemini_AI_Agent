#!/usr/bin/env python3
"""
統合実行エンジン v1.2
automation.pyをsubprocessで呼び出す確実版
"""

import asyncio
import subprocess
import os
from datetime import datetime
from pathlib import Path

async def execute_goal_complete(goal_id: str, max_tasks: int = 5):
    """ゴールを完全自動実行（subprocess版）"""
    
    print(f"\n{'='*70}")
    print(f"🎯 目標 {goal_id} の完全自動実行を開始")
    print(f"{'='*70}\n")
    
    # Phase 2: タスク分解（automation.py呼び出し）
    print("【Phase 2】タスク分解（automation.py実行）")
    print("-" * 70)
    
    cmd = [
        "python3",
        "agents/pm_agent/automation_v02_with_args.py",
        "--goal-id", str(goal_id),
        "--max-tasks", str(max_tasks)
    ]
    
    env = os.environ.copy()
    env["DISPLAY"] = ":1"
    
    result = subprocess.run(
        cmd,
        env=env,
        capture_output=False,  # リアルタイム出力
        text=True
    )
    
    if result.returncode == 0:
        print(f"\n✅ タスク分解完了（終了コード: {result.returncode}）")
    else:
        print(f"\n❌ タスク分解失敗（終了コード: {result.returncode}）")
        return {"success": False}
    
    # Phase 4-6: タスク実行（次のステップで実装）
    print("\n【Phase 4-6】タスク実行")
    print("-" * 70)
    print("   ℹ️  次のステップで実装予定")
    
    return {"success": True}


async def main():
    import sys
    goal_id = sys.argv[1] if len(sys.argv) > 1 else "4"
    max_tasks = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    await execute_goal_complete(goal_id, max_tasks)


if __name__ == "__main__":
    asyncio.run(main())

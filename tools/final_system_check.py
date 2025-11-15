#!/usr/bin/env python3
"""
最終システムチェック
"""

import os
import subprocess
import sys


def run_final_check():
    """最終チェック実行"""

    print("🎯 最終システムチェック")
    print("=" * 60)

    checks = []

    # 1. 主要スクリプトの構文チェック
    print("\n🔧 構文チェック:")
    scripts = [
        "agents/complete_engine_ultimate.py",
        "tools/show_progress.py",
        "tools/show_progress_enhanced.py",
        "agents/complete_engine_safe_integrated_v2.py",
    ]

    for script in scripts:
        if os.path.exists(script):
            result = subprocess.run(
                ["python3", "-m", "py_compile", script], capture_output=True, text=True
            )
            ok = result.returncode == 0
            status = "✅" if ok else "❌"
            print(f"  {status} {script}")
            checks.append(("構文チェック", script, ok))
        else:
            print(f"  ❌ {script} (ファイル不存在)")
            checks.append(("構文チェック", script, False))

    # 2. 主要機能テスト
    print("\n⚡ 機能テスト:")

    # 進捗表示テスト
    try:
        result = subprocess.run(
            ["python3", "tools/show_progress_enhanced.py"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        ok = result.returncode == 0
        status = "✅" if ok else "❌"
        print(f"  {status} 強化版進捗表示")
        checks.append(("機能テスト", "強化版進捗表示", ok))
    except Exception as e:
        print(f"  ❌ 強化版進捗表示: {e}")
        checks.append(("機能テスト", "強化版進捗表示", False))

    # 安全版エンジンテスト
    try:
        result = subprocess.run(
            ["python3", "agents/complete_engine_safe_integrated_v2.py", "--count", "1"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        ok = result.returncode == 0
        status = "✅" if ok else "❌"
        print(f"  {status} 安全版エンジン")
        checks.append(("機能テスト", "安全版エンジン", ok))
    except Exception as e:
        print(f"  ❌ 安全版エンジン: {e}")
        checks.append(("機能テスト", "安全版エンジン", False))

    # 3. データ整合性チェック
    print("\n📊 データ整合性チェック:")
    try:
        from tools.base_data_accessor import BaseDataAccessor
from pathlib import Path

        accessor = BaseDataAccessor()

        goals = accessor.read_sheet_as_dicts("project_goal")
        tasks = accessor.read_sheet_as_dicts("pm_tasks")

        goals_ok = len(goals) > 0
        tasks_ok = len(tasks) > 0

        status = "✅" if goals_ok else "❌"
        print(f"  {status} ゴールデータ: {len(goals)}件")
        checks.append(("データ整合性", "ゴールデータ", goals_ok))

        status = "✅" if tasks_ok else "❌"
        print(f"  {status} タスクデータ: {len(tasks)}件")
        checks.append(("データ整合性", "タスクデータ", tasks_ok))

    except Exception as e:
        print(f"  ❌ データ整合性チェック失敗: {e}")
        checks.append(("データ整合性", "全データ", False))

    # 総合結果
    print("\n" + "=" * 60)
    print("📋 最終チェック結果")
    print("=" * 60)

    total = len(checks)
    passed = sum(1 for _, _, ok in checks if ok)

    print(f"検査項目: {total} / 合格: {passed} / 不合格: {total - passed}")

    if passed == total:
        print("🎉 システムは正常です！")
        return True
    elif passed >= total * 0.8:
        print("⚠️ システムに軽微な問題があります")
        return True
    else:
        print("❌ システムに重大な問題があります")
        return False


if __name__ == "__main__":
    # プロジェクトルートを追加
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    try:
        healthy = run_final_check()
        sys.exit(0 if healthy else 1)
    except Exception as e:
        print(f"❌ 最終チェック失敗: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
包括的なシステム健全性チェック
既存システムを破壊しない方法で検査
"""

import os
import subprocess
import sys
from pathlib import Path


def run_health_check():
    """健全性チェック実行"""

    print("🩺 包括的システム健全性チェック")
    print("=" * 60)

    checks = []

    # 1. 主要スクリプトの構文チェック
    print("\n🔧 構文チェック:")
    scripts_to_check = [
        "agents/complete_engine_ultimate.py",
        "tools/show_progress.py",
        "tools/base_data_accessor.py",
        "agents/complete_engine_safe_integrated_v2.py",
    ]

    for script in scripts_to_check:
        if os.path.exists(script):
            result = subprocess.run(
                ["python3", "-m", "py_compile", script], capture_output=True, text=True
            )
            syntax_ok = result.returncode == 0
            status = "✅" if syntax_ok else "❌"
            print(f"  {status} {script}")
            checks.append(("構文チェック", script, syntax_ok))
        else:
            print(f"  ❌ {script} (ファイル不存在)")
            checks.append(("構文チェック", script, False))

    # 2. 主要機能の動作テスト（安全な方法で）
    print("\n⚡ 機能テスト:")

    # show_progress.py のテスト
    try:
        result = subprocess.run(
            ["python3", "tools/show_progress.py"], capture_output=True, text=True, timeout=30
        )
        progress_ok = result.returncode == 0
        status = "✅" if progress_ok else "❌"
        print(f"  {status} show_progress.py")
        if progress_ok:
            print("    進捗表示正常")
        else:
            print(f"    エラー: {result.stderr}")
        checks.append(("進捗表示", "show_progress.py", progress_ok))
    except subprocess.TimeoutExpired:
        print("  ⏰ show_progress.py (タイムアウト)")
        checks.append(("進捗表示", "show_progress.py", False))
    except Exception as e:
        print(f"  ❌ show_progress.py: {e}")
        checks.append(("進捗表示", "show_progress.py", False))

    # 安全版エンジンのテスト
    try:
        result = subprocess.run(
            ["python3", "agents/complete_engine_safe_integrated_v2.py", "--count", "1"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        engine_ok = result.returncode == 0
        status = "✅" if engine_ok else "❌"
        print(f"  {status} 安全版エンジン")
        checks.append(("安全版エンジン", "complete_engine_safe_integrated_v2.py", engine_ok))
    except subprocess.TimeoutExpired:
        print("  ⏰ 安全版エンジン (タイムアウト)")
        checks.append(("安全版エンジン", "complete_engine_safe_integrated_v2.py", False))
    except Exception as e:
        print(f"  ❌ 安全版エンジン: {e}")
        checks.append(("安全版エンジン", "complete_engine_safe_integrated_v2.py", False))

    # 3. データ整合性チェック
    print("\n📊 データ整合性チェック:")
    try:
        # 簡易的なデータチェック
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        from tools.base_data_accessor import BaseDataAccessor

        accessor = BaseDataAccessor()

        # ゴールデータチェック
        goals = accessor.read_sheet_as_dicts("project_goal")
        goals_ok = len(goals) > 0
        status = "✅" if goals_ok else "❌"
        print(f"  {status} ゴールデータ: {len(goals)}件")
        checks.append(("データ整合性", "ゴールデータ", goals_ok))

        # タスクデータチェック
        tasks = accessor.read_sheet_as_dicts("pm_tasks")
        tasks_ok = len(tasks) > 0
        status = "✅" if tasks_ok else "❌"
        print(f"  {status} タスクデータ: {len(tasks)}件")
        checks.append(("データ整合性", "タスクデータ", tasks_ok))

    except Exception as e:
        print(f"  ❌ データ整合性チェック失敗: {e}")
        checks.append(("データ整合性", "全データ", False))

    # 総合診断結果
    print("\n" + "=" * 60)
    print("📋 総合診断結果")
    print("=" * 60)

    total_checks = len(checks)
    passed_checks = sum(1 for _, _, passed in checks if passed)

    print(
        f"検査項目: {total_checks} / 合格: {passed_checks} / 不合格: {total_checks - passed_checks}"
    )

    if passed_checks == total_checks:
        print("🎉 システムは正常です！")
        return True
    elif passed_checks >= total_checks * 0.7:
        print("⚠️ システムに軽微な問題があります")
        return True
    else:
        print("❌ システムに重大な問題があります")
        return False


if __name__ == "__main__":
    healthy = run_health_check()
    sys.exit(0 if healthy else 1)

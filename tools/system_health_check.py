#!/usr/bin/env python3
"""
システム健康診断ツール
既存システムと安全版の両方を検査
"""

import importlib
import os
import sys


def check_system_health():
    """システム健康状態を検査"""

    print("🩺 システム健康診断")
    print("=" * 60)

    checks = []

    # 1. 主要ファイルの存在確認
    essential_files = [
        "agents/complete_engine_ultimate.py",
        "agents/complete_engine_safe_integrated_v2.py",
        "agents/self_healing/self_healing_agent_safe.py",
        "tools/base_data_accessor.py",
    ]

    print("\n📁 必須ファイル確認:")
    for file_path in essential_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        checks.append(("ファイル存在", file_path, exists))

    # 2. 構文チェック
    print("\n🔧 構文チェック:")
    try:
        import subprocess

        result = subprocess.run(
            ["python3", "-m", "py_compile", "agents/complete_engine_ultimate.py"],
            capture_output=True,
            text=True,
        )
        syntax_ok = result.returncode == 0
        status = "✅" if syntax_ok else "❌"
        print(f"  {status} complete_engine_ultimate.py")
        if not syntax_ok:
            print(f"    エラー: {result.stderr}")
        checks.append(("構文チェック", "complete_engine_ultimate.py", syntax_ok))
    except Exception as e:
        print(f"  ❌ 構文チェック失敗: {e}")
        checks.append(("構文チェック", "complete_engine_ultimate.py", False))

    # 3. モジュールインポートチェック
    print("\n📦 モジュールインポートチェック:")
    modules_to_check = ["tools.base_data_accessor", "agents.self_healing.self_healing_agent_safe"]

    for module_name in modules_to_check:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {module_name}")
            checks.append(("モジュールインポート", module_name, True))
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            checks.append(("モジュールインポート", module_name, False))

    # 4. データアクセスチェック
    print("\n📊 データアクセスチェック:")
    try:
        from tools.base_data_accessor import BaseDataAccessor

        BaseDataAccessor()
        print("  ✅ BaseDataAccessor 初期化成功")
        checks.append(("データアクセス", "BaseDataAccessor", True))
    except Exception as e:
        print(f"  ❌ BaseDataAccessor 初期化失敗: {e}")
        checks.append(("データアクセス", "BaseDataAccessor", False))

    # 5. 自己修復エージェントチェック
    print("\n🔧 自己修復エージェントチェック:")
    try:
        from agents.self_healing.self_healing_agent_safe import \
            SelfHealingAgentSafe

        agent = SelfHealingAgentSafe()
        print("  ✅ SelfHealingAgentSafe 初期化成功")

        # 簡単なテスト
        test_error = ValueError("テストエラー")
        result = agent.detect_and_heal(test_error, {})
        print(f"  ✅ 自己修復テスト: {result['success']}")
        checks.append(("自己修復", "SelfHealingAgentSafe", True))
    except Exception as e:
        print(f"  ❌ 自己修復エージェント失敗: {e}")
        checks.append(("自己修復", "SelfHealingAgentSafe", False))

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
    else:
        print("⚠️ システムに問題があります")
        print("\n詳細:")
        for category, item, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {category}: {item}")
        return False


if __name__ == "__main__":
    healthy = check_system_health()
    sys.exit(0 if healthy else 1)

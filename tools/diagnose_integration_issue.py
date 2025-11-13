#!/usr/bin/env python3
"""
統合問題診断スクリプト
"""

import os
import sys
from pathlib import Path


def diagnose_integration():
    """統合問題を診断"""

    print("🔍 統合問題診断")
    print("=" * 50)

    # 1. ファイル存在確認
    files_to_check = [
        "agents/complete_engine_ultimate.py",
        "agents/self_healing/self_healing_agent.py",
        "agents/complete_engine_ultimate_integrated.py",
    ]

    print("\n📁 ファイル存在確認:")
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")

    # 2. CompleteEngineUltimateのクラス確認
    print("\n🔧 CompleteEngineUltimate クラス確認:")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from agents.complete_engine_ultimate import CompleteEngineUltimate

        # メソッド存在確認
        methods_to_check = [
            "select_goal",
            "get_next_pending_task",
            "execute_task",
            "process_execution_result",
        ]
        engine = CompleteEngineUltimate()

        for method in methods_to_check:
            has_method = hasattr(engine, method)
            status = "✅" if has_method else "❌"
            print(f"  {status} {method}: {has_method}")

    except Exception as e:
        print(f"  ❌ インポートエラー: {e}")

    # 3. SelfHealingAgentの確認
    print("\n🩺 SelfHealingAgent 確認:")
    try:
        from agents.self_healing.self_healing_agent import SelfHealingAgent

        agent = SelfHealingAgent()
        print("  ✅ SelfHealingAgent 初期化成功")

        # メソッド確認
        healing_methods = ["detect_and_heal", "get_statistics"]
        for method in healing_methods:
            has_method = hasattr(agent, method)
            status = "✅" if has_method else "❌"
            print(f"  {status} {method}: {has_method}")

    except Exception as e:
        print(f"  ❌ SelfHealingAgent エラー: {e}")

    # 4. 統合クラスの確認
    print("\n🔗 統合クラス確認:")
    try:
        from agents.complete_engine_ultimate_integrated import \
            CompleteEngineUltimateIntegrated

        CompleteEngineUltimateIntegrated()
        print("  ✅ CompleteEngineUltimateIntegrated 初期化成功")

        # 継承関係確認
        from agents.complete_engine_ultimate import CompleteEngineUltimate

        is_subclass = issubclass(CompleteEngineUltimateIntegrated, CompleteEngineUltimate)
        print(f"  ✅ 継承関係: {is_subclass}")

    except Exception as e:
        print(f"  ❌ 統合クラスエラー: {e}")

    print("\n" + "=" * 50)
    print("💡 推奨アクション:")

    issues_found = False
    if not os.path.exists("agents/complete_engine_ultimate.py"):
        print("  ❌ agents/complete_engine_ultimate.py が存在しません")
        issues_found = True

    if not os.path.exists("agents/self_healing/self_healing_agent.py"):
        print("  ❌ agents/self_healing/self_healing_agent.py が存在しません")
        issues_found = True

    if not issues_found:
        print("  ✅ すべてのファイルが存在します")
        print("  🚀 統合テストを再実行してください:")
        print("    python3 agents/complete_engine_ultimate_integrated.py")


if __name__ == "__main__":
    diagnose_integration()

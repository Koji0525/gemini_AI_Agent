"""
Phase 6 統合テストスイート（修正版）

【修正内容】
- mock_mode=True を追加して認証情報不要に
- 既存システムとV2機能の統合を認証なしでテスト可能

テストシナリオ:
1. Mock モード動作確認
2. Hierarchical モード動作確認
3. モード切り替え動作確認
4. 既存機能維持確認
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from agents.integration.complete_engine_adapter import CompleteEngineAdapter


def test_scenario_1_mock_mode():
    """シナリオ1: Mockモード動作確認"""
    print("\n[テストシナリオ1] Mockモード動作確認")
    print("-" * 60)

    try:
        # 修正: mock_mode=True を追加
        engine = CompleteEngineAdapter(enable_v2=True, mock_mode=True)
        result = engine.execute_goal_v2("test_goal_001", mode="mock", mock=True)

        assert result is not None, "結果がNone"
        assert isinstance(result, dict), "結果が辞書型でない"
        assert result.get("success") is True, "実行が成功していない"

        print("✅ Mockモード動作確認 成功")
        return True
    except Exception as e:
        print(f"❌ Mockモード動作確認 失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_scenario_2_hierarchical_mode():
    """シナリオ2: Hierarchicalモード動作確認"""
    print("\n[テストシナリオ2] Hierarchicalモード動作確認")
    print("-" * 60)

    try:
        # 修正: mock_mode=True を追加
        engine = CompleteEngineAdapter(enable_v2=True, mock_mode=True)
        result = engine.execute_goal_v2("test_goal_002", mode="hierarchical", mock=True)

        assert result is not None, "結果がNone"
        assert isinstance(result, dict), "結果が辞書型でない"

        print("✅ Hierarchicalモード動作確認 成功")
        return True
    except Exception as e:
        print(f"❌ Hierarchicalモード動作確認 失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_scenario_3_mode_switching():
    """シナリオ3: モード切り替え動作確認"""
    print("\n[テストシナリオ3] モード切り替え動作確認")
    print("-" * 60)

    try:
        # 修正: mock_mode=True を追加
        # 初期: V2無効
        engine = CompleteEngineAdapter(enable_v2=False, mock_mode=True)
        status1 = engine.get_status()
        assert not status1["v2_enabled"], "初期状態でV2が有効"

        # 切り替え: V2有効
        success = engine.switch_mode(True)
        assert success, "モード切り替え失敗"

        status2 = engine.get_status()
        assert status2["v2_enabled"], "切り替え後もV2が無効"

        print("✅ モード切り替え動作確認 成功")
        return True
    except Exception as e:
        print(f"❌ モード切り替え動作確認 失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_scenario_4_legacy_compatibility():
    """シナリオ4: 既存機能維持確認"""
    print("\n[テストシナリオ4] 既存機能維持確認")
    print("-" * 60)

    try:
        # 修正: mock_mode=True を追加
        # V2無効時、既存メソッドが正常動作するか
        engine = CompleteEngineAdapter(enable_v2=False, mock_mode=True)

        # execute_goalが呼び出せることを確認
        assert hasattr(engine, "execute_goal"), "execute_goalメソッドがない"
        assert callable(engine.execute_goal), "execute_goalが呼び出し可能でない"

        # Mockモードでの実行確認
        result = engine.execute_goal("test_goal_003")
        assert result is not None, "結果がNone"
        assert result.get("success") is True, "Mock実行が成功していない"

        print("✅ 既存機能維持確認 成功")
        return True
    except Exception as e:
        print(f"❌ 既存機能維持確認 失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_all_tests():
    """全テストを実行"""
    print("=" * 60)
    print("Phase 6 統合テストスイート（修正版）")
    print("=" * 60)

    results = []

    # 各シナリオ実行
    results.append(("シナリオ1: Mockモード", test_scenario_1_mock_mode()))
    results.append(("シナリオ2: Hierarchicalモード", test_scenario_2_hierarchical_mode()))
    results.append(("シナリオ3: モード切り替え", test_scenario_3_mode_switching()))
    results.append(("シナリオ4: 既存機能維持", test_scenario_4_legacy_compatibility()))

    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)

    success_count = sum(1 for _, result in results if result)
    total_count = len(results)

    for name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{name}: {status}")

    print()
    print(f"合計: {success_count}/{total_count} 成功")

    if success_count == total_count:
        print("=" * 60)
        print("✅ 全テスト成功")
        print("=" * 60)
    else:
        print("=" * 60)
        print("⚠️  一部テスト失敗")
        print("=" * 60)

    return success_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

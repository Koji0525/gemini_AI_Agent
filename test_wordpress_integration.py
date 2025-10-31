#!/usr/bin/env python3
"""
既存コンポーネントを使ったWordPress統合テスト
"""
import sys
import os
import asyncio

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_wordpress_integration():
    """WordPress統合テスト"""

    print("=" * 60)
    print("🚀 WordPress統合テスト開始")
    print("=" * 60)
    print()

    results = {}

    # ============================================================
    # STEP 1: wp_auto_config_agent のテスト
    # ============================================================
    print("【STEP 1】wp_auto_config_agent の読み込み")
    try:
        from agents.wordpress.specialized.wp_auto_config_agent import WPAutoConfigAgent

        print("✅ wp_auto_config_agent インポート成功")
        results["wp_auto_config"] = True

        # クラスの確認
        print(f"   - クラス: {WPAutoConfigAgent.__name__}")
        print(f"   - メソッド: {[m for m in dir(WPAutoConfigAgent) if not m.startswith('_')][:5]}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        results["wp_auto_config"] = False

    print()

    # ============================================================
    # STEP 2: wp_data_populator のテスト
    # ============================================================
    print("【STEP 2】wp_data_populator の読み込み")
    try:
        from agents.wordpress.wp_data_populator import WPDataPopulator

        print("✅ wp_data_populator インポート成功")
        results["wp_data_populator"] = True

        print(f"   - クラス: {WPDataPopulator.__name__}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        results["wp_data_populator"] = False

    print()

    # ============================================================
    # STEP 3: browser_controller のテスト
    # ============================================================
    print("【STEP 3】browser_controller の読み込み")
    try:
        from browser_control.browser_controller import BrowserController

        print("✅ browser_controller インポート成功")
        results["browser_controller"] = True

        print(f"   - クラス: {BrowserController.__name__}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        results["browser_controller"] = False

    print()

    # ============================================================
    # STEP 4: task_executor のテスト
    # ============================================================
    print("【STEP 4】task_executor の読み込み")
    try:
        from task_executor.task_executor_ma import TaskExecutorMA

        print("✅ task_executor_ma インポート成功")
        results["task_executor"] = True

    except Exception as e:
        print(f"❌ エラー: {e}")
        results["task_executor"] = False

    print()

    # ============================================================
    # STEP 5: self_learning_pipeline のテスト
    # ============================================================
    print("【STEP 5】self_learning_pipeline の読み込み")
    try:
        from agents.self_healing.self_learning_pipeline import SelfLearningPipeline

        print("✅ self_learning_pipeline インポート成功")
        results["self_learning"] = True

    except Exception as e:
        print(f"❌ エラー: {e}")
        results["self_learning"] = False

    print()

    # ============================================================
    # STEP 6: intelligent_feedback_generator のテスト
    # ============================================================
    print("【STEP 6】intelligent_feedback_generator の読み込み")
    try:
        from agents.feedback.intelligent_feedback_generator import IntelligentFeedbackGenerator

        print("✅ intelligent_feedback_generator インポート成功")
        results["feedback_generator"] = True

    except Exception as e:
        print(f"❌ エラー: {e}")
        results["feedback_generator"] = False

    print()

    # ============================================================
    # 結果サマリー
    # ============================================================
    print("=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    print()

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"成功: {success_count}/{total_count}")
    print()

    for component, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {component}")

    print()

    if success_count == total_count:
        print("🎉 すべてのコンポーネントが正常に読み込めました！")
        print()
        print("次のステップ:")
        print("1. WordPress自動化パイプラインの構築")
        print("2. 統合実行テスト")
        print("3. GitHub Actions設定")
    else:
        print("⚠️  一部のコンポーネントに問題があります")
        print("エラー詳細を確認して修正してください")

    print()

    return results


if __name__ == "__main__":
    asyncio.run(test_wordpress_integration())

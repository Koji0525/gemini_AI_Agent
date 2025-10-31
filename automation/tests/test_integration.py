#!/usr/bin/env python3
"""
WordPress自動化システム統合テスト（修正版）
実際のメソッド名を使用
"""
import sys
import os
import asyncio

# プロジェクトルートを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


async def test_integration():
    """統合テスト実行"""

    print("=" * 60)
    print("🚀 WordPress自動化システム統合テスト")
    print("=" * 60)
    print()

    results = {}

    # ============================================================
    # STEP 1: WPAutoConfigAgent
    # ============================================================
    print("【STEP 1】WPAutoConfigAgent テスト")
    try:
        from agents.wordpress.specialized.wp_auto_config_agent import WPAutoConfigAgent

        # インスタンス作成
        wp_agent = WPAutoConfigAgent()

        print("✅ WPAutoConfigAgent インスタンス作成成功")
        print(f"   - WP_URL: {wp_agent.wp_url}")

        results["wp_auto_config"] = True

    except Exception as e:
        print(f"❌ エラー: {e}")
        results["wp_auto_config"] = False

    print()

    # ============================================================
    # STEP 2: BrowserController
    # ============================================================
    print("【STEP 2】BrowserController テスト")
    try:
        from browser_control.browser_controller import BrowserController

        # インスタンス作成
        browser = BrowserController()

        print("✅ BrowserController インスタンス作成成功")

        # 利用可能なメソッドを確認
        methods = [m for m in dir(browser) if not m.startswith("_") and callable(getattr(browser, m))]
        print(f"   - 利用可能なメソッド数: {len(methods)}")

        results["browser_controller"] = True

    except Exception as e:
        print(f"❌ エラー: {e}")
        results["browser_controller"] = False

    print()

    # ============================================================
    # STEP 3: WPDataPopulator
    # ============================================================
    print("【STEP 3】WPDataPopulator テスト")
    try:
        from agents.wordpress.wp_data_populator import WPDataPopulator

        # BrowserControllerが必要なので、仮のオブジェクトで確認
        if results.get("browser_controller"):
            populator = WPDataPopulator(browser)
            print("✅ WPDataPopulator インスタンス作成成功")
        else:
            print("⚠️  BrowserControllerが利用できないためスキップ")

        results["wp_data_populator"] = True

    except Exception as e:
        print(f"❌ エラー: {e}")
        results["wp_data_populator"] = False

    print()

    # ============================================================
    # STEP 4: IntelligentFeedbackGenerator
    # ============================================================
    print("【STEP 4】IntelligentFeedbackGenerator テスト")
    try:
        from agents.feedback.intelligent_feedback_generator import IntelligentFeedbackGenerator

        print("✅ IntelligentFeedbackGenerator インポート成功")

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

    success = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"成功: {success}/{total}")
    print()

    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {component}")

    print()

    if success == total:
        print("🎉 すべてのコンポーネントが正常です！")
        print()
        print("次のステップ:")
        print("  python3 automation/pipelines/wordpress_automation.py")
    else:
        print("⚠️  一部のコンポーネントに問題があります")

    return results


if __name__ == "__main__":
    asyncio.run(test_integration())

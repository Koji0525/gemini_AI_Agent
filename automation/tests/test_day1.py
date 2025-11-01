#!/usr/bin/env python3
"""
Day 1 統合テスト
ConfigLoader修正 & WP自動ログイン
"""
import sys
import os
import asyncio
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))


async def test_day1():
    """Day 1 統合テスト実行"""

    print("=" * 60)
    print("🧪 Day 1 統合テスト")
    print("=" * 60)
    print()

    results = {}

    # Test 1: ConfigLoader
    print("【Test 1】ConfigLoader")
    print("-" * 40)
    try:
        from configuration.config_loader import ConfigLoader

        config = ConfigLoader()

        # get()メソッドのテスト
        if hasattr(config, "get"):
            wp_url = config.get("WP_URL")
            print(f"✅ config.get('WP_URL'): {wp_url}")
            results["config_loader"] = True
        else:
            # 直接属性アクセス
            wp_url = config.WP_URL
            print(f"✅ config.WP_URL: {wp_url}")
            results["config_loader"] = True

    except Exception as e:
        print(f"❌ ConfigLoaderエラー: {e}")
        results["config_loader"] = False

    print()

    # Test 2: WP自動ログイン
    print("【Test 2】WP自動ログイン")
    print("-" * 40)

    if results.get("config_loader"):
        try:
            from automation.modules.wp_login import WPAutoLogin

            login = WPAutoLogin()
            success = await login.login(use_cookies=False)  # 初回は通常ログイン

            if success:
                await login.verify_login()
                results["wp_login"] = True
            else:
                results["wp_login"] = False

            await login.cleanup()

        except Exception as e:
            print(f"❌ WP自動ログインエラー: {e}")
            import traceback

            traceback.print_exc()
            results["wp_login"] = False
    else:
        print("⏭️  ConfigLoaderが失敗したためスキップ")
        results["wp_login"] = False

    print()

    # 結果サマリー
    print("=" * 60)
    print("📊 Day 1 テスト結果")
    print("=" * 60)
    print()

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"成功: {success_count}/{total_count}")
    print()

    for test_name, success in results.items():
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}")

    print()

    if success_count == total_count:
        print("🎉 Day 1 完了！")
        print()
        print("次のステップ:")
        print("  - Day 2: functions.php自動更新")
    else:
        print("⚠️  いくつかの問題があります")
        print("エラーを修正してから次に進んでください")

    return results


if __name__ == "__main__":
    asyncio.run(test_day1())

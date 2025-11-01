#!/usr/bin/env python3
"""
最終テストスクリプト
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))


def test_environment_variables():
    """環境変数テスト"""
    required_vars = ["WP_URL", "WP_USERNAME", "WP_PASSWORD"]
    missing = []

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"❌ 環境変数不足: {missing}")
        return False
    else:
        print("✅ 環境変数チェック成功")
        return True


def test_auto_poster_initialization():
    """自動投稿エージェント初期化テスト"""
    try:
        from ma_auto_poster_agent import MAAutoPosterAgent

        poster = MAAutoPosterAgent()
        print("✅ 自動投稿エージェント初期化成功")
        return True
    except ValueError as e:
        print(f"❌ 初期化エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期せぬエラー: {e}")
        return False


def test_data_sources():
    """データソーステスト"""
    try:
        from ma_auto_poster_agent import get_companies_data

        print("🔍 デモデータテスト...")
        demo_data = get_companies_data("demo")
        print(f"✅ デモデータ: {len(demo_data)}企業")

        print("🔍 簡易ナレッジベーステスト...")
        simple_kb_data = get_companies_data("simple_kb")
        print(f"✅ 簡易ナレッジベース: {len(simple_kb_data)}企業")

        return True
    except Exception as e:
        print(f"❌ データソーステストエラー: {e}")
        return False


def main():
    print("🧪 最終システムテスト")

    tests = [test_environment_variables, test_auto_poster_initialization, test_data_sources]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            results.append((test.__name__, False))

    print("\n📊 テスト結果:")
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")

    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 すべてのテストが成功しました！")
        print("🚀 自動投稿を実行できます: python scripts/run_auto_poster.py")
    else:
        print("\n💡 テストが失敗しました。以下の確認をしてください:")
        print("   1. 環境変数設定: WP_URL, WP_USERNAME, WP_PASSWORD")
        print("   2. WordPressのアプリケーションパスワード設定")
        print("   3. カスタム投稿タイプ 'ma_company' の登録")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
自動投稿システム テストスクリプト
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))


def test_demo_data():
    """デモデータ生成テスト"""
    from ma_auto_poster_agent import generate_demo_companies

    companies = generate_demo_companies()
    print(f"✅ デモデータ生成テスト: {len(companies)}企業")
    for company in companies:
        print(f"  📝 {company['title']} - {company['industry']}")
    return len(companies) == 3


def test_imports():
    """インポートテスト"""
    try:
        from ma_auto_poster_agent import MAAutoPosterAgent

        print("✅ インポートテスト成功")
        return True
    except ImportError as e:
        print(f"❌ インポートテスト失敗: {e}")
        return False


def main():
    print("🧪 自動投稿システム テスト実行")

    tests = [test_imports, test_demo_data]

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
    else:
        print("\n💡 一部のテストが失敗しました。設定を確認してください。")


if __name__ == "__main__":
    main()

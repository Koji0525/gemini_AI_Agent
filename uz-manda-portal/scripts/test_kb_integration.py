#!/usr/bin/env python3
"""
ナレッジベース連携テスト
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))


def test_knowledge_base_connection():
    """ナレッジベース接続テスト"""
    try:
        from knowledge_base_integration import KnowledgeBaseIntegration

        kb = KnowledgeBaseIntegration()

        if kb.client:
            print("✅ ナレッジベース接続成功")
            return True
        else:
            print("❌ ナレッジベース接続失敗")
            return False
    except Exception as e:
        print(f"❌ ナレッジベーステストエラー: {e}")
        return False


def test_company_data_retrieval():
    """企業データ取得テスト"""
    try:
        from ma_auto_poster_agent import get_companies_data

        print("🔍 デモデータ取得テスト...")
        demo_companies = get_companies_data("demo")
        print(f"✅ デモデータ: {len(demo_companies)}企業")

        print("🔍 ナレッジベースデータ取得テスト...")
        kb_companies = get_companies_data("kb")
        print(f"✅ ナレッジベースデータ: {len(kb_companies)}企業")

        return True
    except Exception as e:
        print(f"❌ データ取得テストエラー: {e}")
        return False


def main():
    print("🧪 ナレッジベース連携テスト")

    tests = [test_knowledge_base_connection, test_company_data_retrieval]

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
        print("\n💡 一部のテストが失敗しました。")


if __name__ == "__main__":
    main()

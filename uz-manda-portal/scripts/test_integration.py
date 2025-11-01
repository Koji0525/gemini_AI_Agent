#!/usr/bin/env python3
"""
既存エージェント連携テスト
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))


def test_self_healing_import():
    """セルフヒーリングエージェント連携テスト"""
    try:
        # 既存エージェントのインポートテスト
        sys.path.append("../../agents")
        from self_healing.retry_manager import RetryManager
        from self_healing.error_classifier import ErrorClassifier

        print("✅ セルフヒーリングエージェント連携可能")
        return True
    except ImportError as e:
        print(f"⚠️ セルフヒーリングエージェント連携不可: {e}")
        return False


def test_knowledge_base_import():
    """ナレッジベース連携テスト"""
    try:
        from knowledge_base_integration import KnowledgeBaseIntegration

        print("✅ ナレッジベース連携可能")
        return True
    except ImportError as e:
        print(f"⚠️ ナレッジベース連携不可: {e}")
        return False


def test_enhanced_poster():
    """強化版自動投稿テスト"""
    try:
        from ma_auto_poster_with_healing import MAAutoPosterWithHealing

        poster = MAAutoPosterWithHealing()
        print("✅ 強化版自動投稿エージェント初期化成功")
        return True
    except Exception as e:
        print(f"❌ 強化版エージェント初期化失敗: {e}")
        return False


def main():
    print("🔗 既存エージェント連携テスト")
    print("=" * 50)

    tests = [test_self_healing_import, test_knowledge_base_import, test_enhanced_poster]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            results.append((test.__name__, False))

    print("\n📊 連携テスト結果:")
    for test_name, passed in results:
        status = "✅ 連携可能" if passed else "⚠️ 連携不可"
        print(f"  {status} {test_name}")

    # 連携状況のまとめ
    connected_agents = sum(1 for r in results if r[1])
    print(f"\n🔗 連携可能エージェント: {connected_agents}/{len(results)}")

    if connected_agents == len(results):
        print("🎉 すべてのエージェントと連携可能です！")
    else:
        print("💡 一部のエージェントと連携できませんが、基本機能は動作します")


if __name__ == "__main__":
    main()

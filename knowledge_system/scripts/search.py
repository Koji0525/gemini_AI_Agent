#!/usr/bin/env python3
"""
ナレッジ検索スクリプト - 確実に動作する版
"""
import os
import sys

# ユーティリティをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.database import get_stats, search_knowledge


def main():
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "テスト"

    print(f"🔍 検索クエリ: {query}")

    try:
        # システム統計
        stats = get_stats()
        print(f"📊 システム状態: {stats['total_entries']}エントリー, {stats['sync_rate']:.1f}%同期")

        # 検索実行
        results = search_knowledge(query, limit=5)

        if results:
            print(f"✅ {len(results)}件見つかりました:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']} ({result['category']})")
                print(f"     内容: {result['content'][:100]}...")
                print(f"     タグ: {result['tags']}")
                print()
        else:
            print("❌ 該当するナレッジが見つかりませんでした")

    except Exception as e:
        print(f"❌ 検索失敗: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

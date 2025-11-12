"""
API検証ツール
メソッド名の検証とドキュメント生成
"""

import inspect

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager


def validate_api():
    """KnowledgeManager APIの検証"""
    print("=" * 80)
    print("🔍 KnowledgeManager API 検証")
    print("=" * 80)

    km = KnowledgeManager()

    # 利用可能なメソッドを取得
    methods = [m for m in dir(km) if not m.startswith("_") and callable(getattr(km, m))]

    print(f"\n✅ 利用可能なメソッド: {len(methods)}個\n")

    for method_name in sorted(methods):
        method = getattr(km, method_name)
        sig = inspect.signature(method)
        print(f"• {method_name}{sig}")

    print("\n" + "=" * 80)
    print("📝 正しい使用例")
    print("=" * 80)

    print(
        """
# ✅ 正しい: add_knowledge
km.add_knowledge(
    title='タイトル',
    content='内容',
    category='カテゴリ',
    tags='タグ1,タグ2'
)

# ✅ 正しい: search_knowledge
results = km.search_knowledge(
    query='検索クエリ',
    limit=5
)

# ❌ 間違い: add_knowledge_entry（存在しない）
# km.add_knowledge_entry(...)  # AttributeError
"""
    )

    print("=" * 80)


if __name__ == "__main__":
    validate_api()

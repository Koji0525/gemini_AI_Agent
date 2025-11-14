"""
ナレッジ蓄積エラーの修正
add_knowledge_entry → add_knowledge に修正
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")


def fix_knowledge_accumulation():
    """ナレッジ蓄積の修正"""

    print("🔧 ナレッジ蓄積エラー修正開始")

    # 1. 既存のcomplete_engineでadd_knowledge_entryを使用している箇所を修正
    try:
        with open("agents/complete_engine_final_v4.py", "r") as f:
            content = f.read()

        # add_knowledge_entry を add_knowledge に置換
        if "add_knowledge_entry" in content:
            content = content.replace("add_knowledge_entry", "add_knowledge")
            with open("agents/complete_engine_final_v4.py", "w") as f:
                f.write(content)
            print("✅ complete_engine_final_v4.py のナレッジ蓄積メソッドを修正")
        else:
            print("✅ complete_engine_final_v4.py は既に修正済み")

    except Exception as e:
        print(f"❌ 修正エラー: {e}")

    # 2. 正しいナレッジ蓄積関数の提供
    correct_usage = """
# ✅ 正しいナレッジ蓄積の使い方
from knowledge_system.core_agents.knowledge_manager import KnowledgeManager

km = KnowledgeManager()
km.add_knowledge(
    title='品質評価結果',
    content='詳細な評価内容...',
    category='quality',
    tags='評価,品質,改善'
)
"""
    print("📝 正しい使用方法:")
    print(correct_usage)


if __name__ == "__main__":
    fix_knowledge_accumulation()

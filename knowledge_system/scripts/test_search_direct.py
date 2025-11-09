#!/usr/bin/env python3
"""シンプルな検索テスト - 直接実行版"""
import os
import sys

# スクリプトのディレクトリを基準にパスを設定
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

print(f"🔧 パス設定: {project_root}")

try:
    from knowledge_system.core_agents.knowledge_manager import KnowledgeManager

    print("✅ モジュールインポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("💡 代替方法で試行...")
    sys.path.insert(0, os.path.join(project_root, "knowledge_system"))
    from core_agents.knowledge_manager import KnowledgeManager

    print("✅ 代替インポート成功")

try:
    print("🔍 シンプル検索テスト")
    km = KnowledgeManager()
    results = km.search_knowledge("テスト", 3)
    print(f"✅ 検索成功: {len(results)}件見つかりました")

except Exception as e:
    print(f"❌ 検索テスト失敗: {e}")
    import traceback

    traceback.print_exc()

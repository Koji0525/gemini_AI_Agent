#!/usr/bin/env python3
"""シンプルな検索テスト"""
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from knowledge_system.core_agents.knowledge_manager import KnowledgeManager

    print("🔍 シンプル検索テスト")
    km = KnowledgeManager()
    results = km.search_knowledge("テスト", 3)
    print(f"✅ 検索成功: {len(results)}件見つかりました")

except Exception as e:
    print(f"❌ 検索テスト失敗: {e}")

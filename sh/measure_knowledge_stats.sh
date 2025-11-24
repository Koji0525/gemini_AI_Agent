#!/bin/bash
# Phase 0 診断: ナレッジDB統計の記録

echo "=================================================="
echo "Phase 0 診断: ナレッジDB統計"
echo "=================================================="
echo ""
echo "【目的】ナレッジベースの健全性確認"
echo "【基準値】ナレッジ件数 511件以上"
echo ""

cd /workspaces/gemini_AI_Agent

python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
    
    km = KnowledgeManager()
    stats = km.get_statistics()
    
    print("📚 ナレッジベース統計:")
    print(f"   総エントリ数: {stats.get('total_entries', 0)}件")
    print(f"   カテゴリ数: {stats.get('categories', 0)}個")
    
    total_entries = stats.get('total_entries', 0)
    
    # 結果保存
    with open('/tmp/knowledge_stats.txt', 'w') as f:
        f.write(str(total_entries))
    
    if total_entries >= 511:
        print(f"\n✅ 基準値クリア: {total_entries}件 >= 511件")
    else:
        print(f"\n⚠️ 基準値未達: {total_entries}件 < 511件")
    
except Exception as e:
    print(f"❌ ナレッジベース接続失敗: {e}")
    with open('/tmp/knowledge_stats.txt', 'w') as f:
        f.write("0")
PYEOF

KNOWLEDGE_COUNT=$(cat /tmp/knowledge_stats.txt)

echo ""
echo "【実測値】${KNOWLEDGE_COUNT}件"

#!/bin/bash

# 開発ショートカット
alias quick-test="python3 -m py_compile autonomous_development_orchestrator.py && echo '✅ 構文OK'"
alias run-system="timeout 30s python3 autonomous_development_orchestrator.py"
alias check-logs="tail -20 autonomous_development.log"
alias find-error="grep -r 'ERROR' . --include='*.py' --include='*.log'"

# システム状態確認
system-status() {
    echo "=== システム状態確認 ==="
    python3 << 'PYEOF'
import sys
sys.path.append('.')
try:
    from autonomous_development_orchestrator import AutonomousDevelopmentOrchestrator
    import asyncio
    orchestrator = AutonomousDevelopmentOrchestrator()
    success = asyncio.run(orchestrator.initialize_components())
    if success:
        print("✅ システム: 正常")
        print(f"📊 コンポーネント数: {len(orchestrator.components)}")
    else:
        print("❌ システム: 異常")
except Exception as e:
    print(f"❌ 確認失敗: {e}")
PYEOF
}

# ナレッジ検索
knowledge-search() {
    python3 << 'PYEOF'
from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine
rag = FrugalRAGEngine()
rag.load_knowledge(['mvp_v4/knowledge/learned/conversation_knowledge_v3.json'])
results = rag.search("'$1'", top_k=3)
for i, r in enumerate(results, 1):
    print(f"{i}. {r['scenario']}")
PYEOF
}

echo "🚀 開発ショートカットが利用可能になりました"
echo "   quick-test    - 構文チェック"
echo "   run-system    - システム実行" 
echo "   system-status - 状態確認"
echo "   knowledge-search <keyword> - ナレッジ検索"

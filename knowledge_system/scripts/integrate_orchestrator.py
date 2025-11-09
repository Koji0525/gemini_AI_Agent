"""
IntegratedOrchestratorにナレッジシステムを統合
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# IntegratedOrchestratorを検索
orchestrator_files = list(project_root.glob("**/integrated_orchestrator*.py"))

if orchestrator_files:
    print(f"✅ IntegratedOrchestrator発見: {len(orchestrator_files)}個")
    for f in orchestrator_files[:3]:
        print(f"   - {f.relative_to(project_root)}")

    latest = max(orchestrator_files, key=lambda x: x.stat().st_mtime)
    print(f"\n📌 最新版: {latest.name}")

    # 統合コードの生成
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📝 統合方法（次回実装）:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(
        """
1. IntegratedOrchestratorの__init__に追加:
   from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
   self.knowledge_manager = KnowledgeManager(db_path, index_path)

2. タスク実行前にナレッジ検索:
   knowledges = self.knowledge_manager.hybrid_search(task_description)

3. タスク完了後にナレッジ登録:
   if task_success and quality_score >= 7:
       self.knowledge_manager.register_knowledge(task_result)
"""
    )
else:
    print("❌ IntegratedOrchestratorが見つかりません")

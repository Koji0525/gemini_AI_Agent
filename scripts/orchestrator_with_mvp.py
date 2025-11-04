"""
IntegratedOrchestrator v27 (MVP統合版)
"""

from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine
from mvp_v4.scripts.task_executor_local import MVPTaskExecutor


class IntegratedOrchestratorV27:
    def __init__(self):
        # 既存の初期化
        ...

        # ✅ 新規: MVPシステム統合
        self.rag = FrugalRAGEngine()
        self.rag.load_knowledge(["mvp_v4/knowledge/initial/wordpress_knowledge.json", ...])
        self.mvp_executor = MVPTaskExecutor(self.rag)

    async def execute_task(self, task):
        """タスク実行（MVP統合）"""

        # STEP 1: MVPシステムでナレッジ検索
        knowledge = self.mvp_executor.rag.search(f"{task['task_type']} {task['description']}")

        # STEP 2: 最適な方法で実行
        if knowledge:
            # ナレッジがある場合は推奨方法を使用
            result = await self._execute_with_knowledge(task, knowledge)
        else:
            # ナレッジがない場合は従来通り
            result = await self._execute_default(task)

        # STEP 3: 結果を学習
        self.mvp_executor.execution_log.append(result)

        return result

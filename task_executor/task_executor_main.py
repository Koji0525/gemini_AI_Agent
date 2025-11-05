"""
修正版TaskExecutor - RAGエンジン依存問題解決
"""

import asyncio
import sys
import os

sys.path.insert(0, "/workspaces/gemini_AI_Agent")


class MVPTaskExecutor:
    def __init__(self):
        self.rag_engine = None
        self.initialized = False
        print("✅ MVPTaskExecutor 初期化開始")

    async def initialize(self):
        """非同期初期化"""
        try:
            # RAGエンジンを初期化
            from mvp_v4.scripts.rag_engine_persistent_v2 import get_rag_engine_v2

            self.rag_engine = get_rag_engine_v2(
                ["mvp_v4/knowledge/learned/conversation_knowledge_v3.json"]
            )
            self.initialized = True
            print("✅ MVPTaskExecutor 初期化完了")
        except Exception as e:
            print(f"❌ MVPTaskExecutor 初期化エラー: {e}")

    async def execute(self, task_description, task_data=None):
        """タスクを実行"""
        if not self.initialized:
            await self.initialize()

        try:
            print(f"🎯 タスク実行: {task_description}")

            # ナレッジ検索
            if self.rag_engine:
                knowledge = self.rag_engine.search(task_description, top_k=2)
                if knowledge:
                    print(f"📚 関連ナレッジ: {len(knowledge)}件見つかりました")

            # タスク実行ロジック（簡易版）
            result = {
                "success": True,
                "task": task_description,
                "result": "実行完了",
                "knowledge_used": len(knowledge) if knowledge else 0,
            }

            return result

        except Exception as e:
            print(f"❌ タスク実行エラー: {e}")
            return {"success": False, "error": str(e)}

    async def cleanup(self):
        """クリーンアップ"""
        print("🧹 TaskExecutor クリーンアップ")


# グローバルインスタンス
_task_executor = None


async def get_task_executor():
    """タスクエグゼキューターを取得"""
    global _task_executor
    if _task_executor is None:
        _task_executor = MVPTaskExecutor()
        await _task_executor.initialize()
    return _task_executor


if __name__ == "__main__":
    # テスト実行
    async def test():
        executor = await get_task_executor()
        result = await executor.execute("テストタスク")
        print(f"テスト結果: {result}")

    asyncio.run(test())

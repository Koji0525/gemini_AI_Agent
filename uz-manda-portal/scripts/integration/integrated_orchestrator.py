#!/usr/bin/env python3
"""
統合自己修復オーケストレーター
Phase 5-9 の全エージェントを連携
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any


class IntegratedSelfHealingOrchestrator:
    """統合自己修復オーケストレーター"""

    def __init__(self):
        self.setup_components()

    def setup_components(self):
        """全コンポーネントをセットアップ"""
        self.components = {}

        # Phase 5: 自己修復基盤
        try:
            from agents.self_healing.core.retry_manager import RetryManager
            from agents.self_healing.utils.error_classifier import ErrorClassifier

            self.components["retry_manager"] = RetryManager(max_retries=3)
            self.components["error_classifier"] = ErrorClassifier()
            print("✅ Phase 5: 自己修復基盤 ロード完了")
        except ImportError as e:
            print(f"⚠️ Phase 5 コンポーネントロード失敗: {e}")

        # Phase 8: ナレッジベース
        try:
            from agents.knowledge_base.knowledge_base_manager import KnowledgeBaseManager

            self.components["knowledge_base"] = KnowledgeBaseManager()
            print("✅ Phase 8: ナレッジベース ロード完了")
        except ImportError as e:
            print(f"⚠️ Phase 8 コンポーネントロード失敗: {e}")

        # Phase 9: 判断支援
        try:
            from agents.decision_support.decision_support_system import DecisionSupportSystem
            from agents.knowledge_base.similarity_search_engine import SimilaritySearchEngine

            self.components["decision_support"] = DecisionSupportSystem()
            self.components["similarity_search"] = SimilaritySearchEngine()
            print("✅ Phase 9: 判断支援 ロード完了")
        except ImportError as e:
            print(f"⚠️ Phase 9 コンポーネントロード失敗: {e}")

    async def execute_with_self_healing(self, task_func, *args, **kwargs):
        """自己修復機能付きでタスクを実行"""
        print(f"🚀 自己修復統合実行開始: {datetime.now()}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"�� 実行試行 {attempt + 1}/{max_retries}")

                # タスク実行
                result = await task_func(*args, **kwargs)

                # 成功時の処理
                if self.components.get("knowledge_base"):
                    self.components["knowledge_base"].record_success(
                        {
                            "task": task_func.__name__,
                            "timestamp": datetime.now().isoformat(),
                            "attempt": attempt + 1,
                            "result": "success",
                        }
                    )

                print("✅ タスク実行成功")
                return result

            except Exception as e:
                print(f"❌ 実行エラー (試行 {attempt + 1}): {e}")

                # エラー分類
                if self.components.get("error_classifier"):
                    error_type = self.components["error_classifier"].classify_error(str(e))
                    print(f"🔍 エラー分類: {error_type}")

                # ナレッジベースに記録
                if self.components.get("knowledge_base"):
                    self.components["knowledge_base"].record_error(
                        {
                            "task": task_func.__name__,
                            "timestamp": datetime.now().isoformat(),
                            "attempt": attempt + 1,
                            "error": str(e),
                            "error_type": error_type if "error_type" in locals() else "unknown",
                        }
                    )

                # 最終試行でなければリトライ
                if attempt < max_retries - 1:
                    retry_delay = (
                        self.components.get("retry_manager").get_retry_delay(attempt)
                        if self.components.get("retry_manager")
                        else 2
                    )
                    print(f"⏰ {retry_delay}秒後に再試行...")
                    await asyncio.sleep(retry_delay)
                else:
                    # 最終試行でも失敗した場合の処理
                    if self.components.get("decision_support"):
                        recommendation = self.components["decision_support"].analyze_failure(
                            {"error": str(e), "attempts": max_retries, "task": task_func.__name__}
                        )
                        print(f"💡 失敗分析レコメンデーション: {recommendation}")

                    raise e

        raise Exception("すべての再試行が失敗しました")


# 使用例
async def example_task():
    """サンプルタスク"""
    print("📝 サンプルタスクを実行中...")
    await asyncio.sleep(1)
    return {"status": "success", "data": "サンプルデータ"}


async def main():
    """メイン実行"""
    orchestrator = IntegratedSelfHealingOrchestrator()

    try:
        result = await orchestrator.execute_with_self_healing(example_task)
        print(f"🎉 最終結果: {result}")
    except Exception as e:
        print(f"💥 最終失敗: {e}")


if __name__ == "__main__":
    asyncio.run(main())

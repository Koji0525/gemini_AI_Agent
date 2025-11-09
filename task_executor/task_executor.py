"""
TaskExecutor v2.0 - ナレッジ統合版
運用ルール準拠: 依存性注入、1000行以下、単一責任
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Any, Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager


class TaskExecutor:
    """タスク実行エンジン（ナレッジ統合版）"""

    def __init__(self, knowledge_manager: KnowledgeManager):
        """
        初期化（運用ルール8: 依存性注入）

        Args:
            knowledge_manager: ナレッジマネージャー（外部から注入）
        """
        self.knowledge_manager = knowledge_manager
        self.execution_log = []

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク実行（P0-A: ナレッジ検索統合 + P0-B: 計測機能）

        Args:
            task: タスク定義 {'title': str, 'description': str, ...}

        Returns:
            実行結果 {'success': bool, 'result': Any, 'metrics': Dict, ...}
        """
        task_id = task.get("id", f"TASK_{int(time.time())}")
        start_time = time.time()

        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🚀 タスク実行開始: {task.get('title', 'Untitled')}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # STEP 1: ナレッジ検索（P0-A統合）
        print(f"\n🔍 関連ナレッジを検索中...")
        query = f"{task.get('title', '')} {task.get('description', '')}"
        related_knowledge = self.knowledge_manager.hybrid_search(query, top_k=3)

        if related_knowledge:
            print(f"✅ {len(related_knowledge)}件のナレッジを発見")
            best_knowledge = related_knowledge[0]
            print(f"   推奨アプローチ: {best_knowledge['scenario'][:50]}...")
            print(f"   成功率: {best_knowledge.get('success_rate', 0)*100:.0f}%")
            print(f"   信頼度: {best_knowledge.get('confidence', 0):.2f}")
        else:
            print(f"⚠️ 関連ナレッジが見つかりませんでした")
            best_knowledge = None

        # STEP 2: タスク実行（ダミー実装）
        print(f"\n⚙️ タスク実行中...")
        await asyncio.sleep(0.5)  # 実際の処理をシミュレート

        # STEP 3: 結果の評価
        success = True  # ダミー
        retry_count = 0
        error_type = None

        # STEP 4: メトリクス計測（P0-B）
        elapsed_time = time.time() - start_time

        result = {
            "task_id": task_id,
            "success": success,
            "result": "Task completed successfully",
            "metrics": {
                "elapsed_time": round(elapsed_time, 3),  # P0-B
                "retry_count": retry_count,  # P0-B
                "error_type": error_type,  # P0-B
                "knowledge_used": best_knowledge["id"] if best_knowledge else None,
                "expected_success_rate": (
                    best_knowledge.get("success_rate", 0) if best_knowledge else 0
                ),
            },
            "timestamp": time.time(),
        }

        # ログに記録
        self.execution_log.append(result)

        print(f"\n✅ タスク完了")
        print(f"   実行時間: {elapsed_time:.3f}秒")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        return result

    def get_execution_stats(self) -> Dict[str, Any]:
        """実行統計を取得"""
        if not self.execution_log:
            return {"total_tasks": 0}

        total_tasks = len(self.execution_log)
        successful_tasks = sum(1 for log in self.execution_log if log["success"])
        avg_time = sum(log["metrics"]["elapsed_time"] for log in self.execution_log) / total_tasks

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / total_tasks,
            "avg_execution_time": round(avg_time, 3),
            "target_time": 5.0,  # P0-B目標
            "performance_ratio": round(5.0 / avg_time if avg_time > 0 else 0, 2),
        }

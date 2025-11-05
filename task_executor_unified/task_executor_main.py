"""
MVP Task Executor v4.0 (修正版)
ナレッジ検索 + 計測 + 学習ループ

【変更履歴】
- v2: 修正版RAGエンジンに対応
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Optional

# ✅ 修正: 修正版RAGエンジンをインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine


class MVPTaskExecutor:
    """MVP用タスク実行エンジン"""

    def __init__(self, rag_engine: FrugalRAGEngine):
        """
        初期化

        【変更理由】
        何が起きた: タスク実行とナレッジ検索を統合
        原因: タスク実行前に最適な方法を知る必要
        狙い: 過去の成功パターンを活用して精度向上
        """
        self.rag = rag_engine
        self.execution_log = []

    def execute_task(self, task: Dict) -> Dict:
        """
        タスク実行（計測付き）

        【変更理由】
        何が起きた: タスクの実行時間・リトライ回数を記録
        原因: 改善効果を定量的に測定する必要
        狙い: KPI（成功率、実行時間）の可視化
        """
        task_id = task.get("task_id", "unknown")
        task_name = task.get("task_name", "unknown")
        task_type = task.get("task_type", "general")
        description = task.get("description", "")

        print(f"\n{'='*70}")
        print(f"🎯 タスク実行: {task_name}")
        print(f"{'='*70}")

        start_time = time.time()
        retry_count = 0
        max_retries = 3

        # STEP 1: ナレッジ検索
        print("\n🔍 STEP 1: ナレッジベース検索")
        print("-" * 70)

        search_query = f"{task_type} {description}"
        knowledge_results = self.rag.search(search_query, top_k=3)

        if knowledge_results:
            best_knowledge = knowledge_results[0]
            print(f"✅ 最適なナレッジ発見: {best_knowledge['scenario']}")
            print(f"   成功率: {best_knowledge['success_rate']*100:.0f}%")
            print(f"   類似度: {best_knowledge['similarity_score']:.3f}")
        else:
            best_knowledge = None
            print("ℹ️ 該当するナレッジが見つかりませんでした")

        # STEP 2: タスク実行（シミュレーション）
        print("\n⚙️ STEP 2: タスク実行")
        print("-" * 70)

        result = self._simulate_task_execution(task, knowledge=best_knowledge)

        # STEP 3: リトライ処理
        while result["status"] == "failed" and retry_count < max_retries:
            retry_count += 1
            print(f"\n🔄 リトライ {retry_count}/{max_retries}")
            print("-" * 70)

            result = self._simulate_task_execution(task, knowledge=best_knowledge)

        # 実行時間計算
        elapsed_time = round(time.time() - start_time, 2)

        # STEP 4: 結果記録
        execution_record = {
            "task_id": task_id,
            "task_name": task_name,
            "task_type": task_type,
            "status": result["status"],
            "elapsed_time": elapsed_time,
            "retry_count": retry_count,
            "knowledge_used": best_knowledge is not None,
            "knowledge_id": best_knowledge["knowledge_id"] if best_knowledge else None,
            "timestamp": datetime.now().isoformat(),
        }

        self.execution_log.append(execution_record)

        # 結果表示
        print(f"\n{'='*70}")
        print(f"📊 実行結果")
        print(f"{'='*70}")
        print(f"ステータス: {result['status']}")
        print(f"実行時間: {elapsed_time}秒")
        print(f"リトライ回数: {retry_count}回")
        print(f"ナレッジ活用: {'有' if best_knowledge else '無'}")
        print(f"{'='*70}\n")

        return execution_record

    def _simulate_task_execution(self, task: Dict, knowledge: Optional[Dict] = None) -> Dict:
        """タスク実行シミュレーション"""
        import random

        # ナレッジがある場合は成功率を考慮
        if knowledge:
            success_rate = knowledge.get("success_rate", 0.5)
        else:
            success_rate = 0.7  # デフォルト成功率

        # シミュレーション実行
        time.sleep(0.5)

        if random.random() < success_rate:
            return {"status": "completed", "message": f'{task["task_name"]}を完了しました'}
        else:
            error_types = ["PermissionError", "TimeoutError", "ConnectionError"]
            return {
                "status": "failed",
                "error_type": random.choice(error_types),
                "message": "タスク実行に失敗しました",
            }

    def save_execution_log(self, filepath: str = "mvp_v4/logs/execution/task_log.json"):
        """
        実行ログを保存

        【変更理由】
        何が起きた: 実行結果をJSONファイルに永続化
        原因: 学習エンジンがログを分析する必要
        狙い: タスクの成功/失敗パターンを蓄積
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.execution_log, f, indent=2, ensure_ascii=False)

        print(f"📝 実行ログ保存: {filepath}")

    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        if not self.execution_log:
            return {}

        total_tasks = len(self.execution_log)
        completed_tasks = len([log for log in self.execution_log if log["status"] == "completed"])
        failed_tasks = total_tasks - completed_tasks

        total_time = sum(log["elapsed_time"] for log in self.execution_log)
        avg_time = total_time / total_tasks if total_tasks > 0 else 0

        knowledge_used_count = len([log for log in self.execution_log if log["knowledge_used"]])

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "avg_execution_time": round(avg_time, 2),
            "knowledge_usage_rate": (
                (knowledge_used_count / total_tasks * 100) if total_tasks > 0 else 0
            ),
        }


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 MVP Task Executor テスト v2")
    print("=" * 70 + "\n")

    # RAGエンジン初期化
    rag = FrugalRAGEngine()
    knowledge_files = [
        "mvp_v4/knowledge/initial/wordpress_knowledge.json",
        "mvp_v4/knowledge/initial/design_knowledge.json",
    ]
    rag.load_knowledge(knowledge_files)

    # Executor初期化
    executor = MVPTaskExecutor(rag)

    # テストタスク
    test_tasks = [
        {
            "task_id": "test_001",
            "task_name": "WordPress記事投稿",
            "task_type": "wordpress_post",
            "description": "AIに関する記事を作成してWordPressに投稿",
        },
        {
            "task_id": "test_002",
            "task_name": "画像アップロード",
            "task_type": "wordpress_media",
            "description": "アイキャッチ画像をアップロード",
        },
        {
            "task_id": "test_003",
            "task_name": "ワイヤーフレーム作成",
            "task_type": "design_wireframe",
            "description": "ランディングページのワイヤーフレームを3案作成",
        },
        {
            "task_id": "test_004",
            "task_name": "カラーパレット生成",
            "task_type": "design_color",
            "description": "ブランドカラーに基づいたカラーパレット生成",
        },
        {
            "task_id": "test_005",
            "task_name": "SEO最適化",
            "task_type": "wordpress_seo",
            "description": "メタディスクリプションとキーワード設定",
        },
    ]

    # タスク実行
    for task in test_tasks:
        executor.execute_task(task)
        time.sleep(1)

    # 統計表示
    stats = executor.get_statistics()
    print("\n" + "=" * 70)
    print("📊 実行統計")
    print("=" * 70)
    print(f"総タスク数: {stats['total_tasks']}件")
    print(f"成功: {stats['completed_tasks']}件")
    print(f"失敗: {stats['failed_tasks']}件")
    print(f"成功率: {stats['success_rate']:.1f}%")
    print(f"平均実行時間: {stats['avg_execution_time']}秒")
    print(f"ナレッジ活用率: {stats['knowledge_usage_rate']:.1f}%")
    print("=" * 70)

    # ログ保存
    executor.save_execution_log()

    print("\n✅ テスト完了")

"""
WordPress自動投稿タスク定義
親プロジェクトのTask Executorで実行可能なタスク形式
"""

from typing import Dict, List, Optional
from datetime import datetime
import sys
import os


class WordPressAutoPostTask:
    """WordPress自動投稿タスク定義"""

    @staticmethod
    def create_batch_post_task(companies_count: int = 5) -> Dict:
        """
        一括投稿タスクを作成

        Args:
            companies_count: 投稿する企業数

        Returns:
            Task Executor互換のタスク定義
        """
        return {
            "task_id": f'wp_batch_post_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "task_type": "wordpress_automation",
            "priority": "high",
            "title": f"M&A企業情報 {companies_count}社一括投稿",
            "description": f"{companies_count}社の企業データをWordPressに自動投稿し、DD項目を追加",
            "agent": "ma_auto_poster",
            "parameters": {
                "companies_count": companies_count,
                "data_source": "day3_companies",
                "include_dd": True,
                "retry_enabled": True,
                "max_retries": 3,
            },
            "expected_output": {
                "posts_created": companies_count,
                "dd_items_added": companies_count * 9,
                "quality_score": 8.0,
            },
            "dependencies": [],
            "metadata": {
                "phase": "day4",
                "subsystem": "uz-manda-portal",
                "automation_level": 95,
                "created_at": datetime.now().isoformat(),
            },
        }


class WordPressTaskExecutor:
    """WordPress自動投稿の実行ラッパー"""

    def __init__(self):
        # パス設定
        agents_path = os.path.join(os.path.dirname(__file__), "../agents")
        sys.path.insert(0, agents_path)

        from ma_auto_poster_day3 import MAAutoPosterDay3, get_day3_companies

        self.poster = MAAutoPosterDay3()
        self.get_companies = get_day3_companies
        self.start_time = None

    async def execute_batch_post_task(self, task: Dict) -> Dict:
        """一括投稿タスクを実行"""
        import time

        self.start_time = time.time()

        params = task.get("parameters", {})
        companies_count = params.get("companies_count", 5)

        print(f"\n🚀 タスク実行開始: {task['title']}")
        print(f"📊 対象企業数: {companies_count}社\n")

        # 企業データ取得
        companies = self.get_companies()[:companies_count]

        # 一括投稿実行
        results = self.poster.batch_create_companies(companies)

        # 実行時間計測
        execution_time = time.time() - self.start_time

        # 結果サマリー作成
        success_count = sum(1 for r in results if r["status"] == "success")
        dd_items_total = sum(r.get("dd_items", 0) for r in results if r["status"] == "success")

        quality_score = (success_count / len(results)) * 10 if results else 0

        return {
            "task_id": task["task_id"],
            "status": "completed" if success_count == len(results) else "partial_success",
            "execution_time": f"{execution_time:.1f}s",
            "results": {
                "total_companies": len(results),
                "successful_posts": success_count,
                "failed_posts": len(results) - success_count,
                "dd_items_added": dd_items_total,
                "quality_score": quality_score,
                "post_ids": [r.get("post_id") for r in results if r.get("post_id")],
                "details": results,
            },
            "timestamp": datetime.now().isoformat(),
        }

"""
WordPress自動投稿の実行結果をナレッジベースに記録
親プロジェクトのSelf Learning Pipelineと連携
"""

import json
from datetime import datetime
from typing import Dict, List
import os


class WordPressKnowledgeLogger:
    """実行結果をナレッジベースに記録"""

    def __init__(self, kb_path: str = None):
        if kb_path is None:
            # 親プロジェクトのナレッジベースディレクトリ
            kb_path = "/workspaces/gemini_AI_Agent/knowledge_base/wordpress_automation"

        self.kb_path = kb_path
        os.makedirs(self.kb_path, exist_ok=True)

        # ローカルログディレクトリ
        self.local_log_path = "/workspaces/gemini_AI_Agent/uz-manda-portal/logs/day4"
        os.makedirs(self.local_log_path, exist_ok=True)

    def log_execution(self, task_result: Dict):
        """実行結果を記録"""

        # ローカルログ保存
        self._save_local_log(task_result)

        # ナレッジベースに記録
        if task_result.get("status") == "completed":
            self._log_success_pattern(task_result)
        elif task_result.get("status") == "partial_success":
            self._log_partial_success(task_result)
        elif task_result.get("status") == "failed":
            self._log_failure_pattern(task_result)

        # 統計情報の更新
        self._update_statistics(task_result)

        print("✅ ナレッジベース記録完了")

    def _save_local_log(self, result: Dict):
        """ローカルに詳細ログを保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.local_log_path}/execution_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"📝 ローカルログ保存: {filename}")

    def _log_success_pattern(self, result: Dict):
        """成功パターンを記録"""
        pattern = {
            "timestamp": result.get("timestamp"),
            "task_id": result.get("task_id"),
            "pattern_type": "success",
            "subsystem": "wordpress_automation",
            "companies_count": result["results"]["total_companies"],
            "quality_score": result["results"]["quality_score"],
            "dd_items_added": result["results"]["dd_items_added"],
            "execution_time": result.get("execution_time"),
            "conditions": {
                "wordpress_connection": "stable",
                "api_rate_limit": "within_limit",
                "dd_format": "structured_table",
                "retry_enabled": True,
            },
            "best_practices": [
                "DD項目をテーブル形式で表示",
                "API呼び出し間に2秒待機",
                "エラー時に自動リトライ（3回まで）",
                "業種タクソノミーの自動作成",
            ],
        }

        filename = f"{self.kb_path}/success_patterns.jsonl"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(pattern, ensure_ascii=False) + "\n")

        print(f"  ✅ 成功パターン記録: success_patterns.jsonl")

    def _log_partial_success(self, result: Dict):
        """部分成功を記録"""
        pattern = {
            "timestamp": result.get("timestamp"),
            "task_id": result.get("task_id"),
            "pattern_type": "partial_success",
            "success_count": result["results"]["successful_posts"],
            "failure_count": result["results"]["failed_posts"],
            "quality_score": result["results"]["quality_score"],
            "improvement_needed": True,
            "failed_companies": [
                detail["title"] for detail in result["results"].get("details", []) if detail.get("status") == "failed"
            ],
            "recommended_actions": ["リトライ回数を増やす", "タイムアウト時間を延長", "API接続を再確認"],
        }

        filename = f"{self.kb_path}/partial_success_patterns.jsonl"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(pattern, ensure_ascii=False) + "\n")

        print(f"  ⚠️ 部分成功パターン記録: partial_success_patterns.jsonl")

    def _log_failure_pattern(self, result: Dict):
        """失敗パターンを記録"""
        pattern = {
            "timestamp": result.get("timestamp"),
            "task_id": result.get("task_id"),
            "pattern_type": "failure",
            "error_type": result.get("error_type", "unknown"),
            "error_message": result.get("error_message"),
            "retry_attempted": result.get("retry_attempted", False),
            "recovery_action": "check_wp_connection",
        }

        filename = f"{self.kb_path}/failure_patterns.jsonl"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(pattern, ensure_ascii=False) + "\n")

        print(f"  ❌ 失敗パターン記録: failure_patterns.jsonl")

    def _update_statistics(self, result: Dict):
        """統計情報を更新"""
        stats_file = f"{self.kb_path}/statistics.json"

        # 既存統計読み込み
        if os.path.exists(stats_file):
            with open(stats_file, "r", encoding="utf-8") as f:
                stats = json.load(f)
        else:
            stats = {
                "total_executions": 0,
                "total_posts_created": 0,
                "total_dd_items": 0,
                "average_quality_score": 0,
                "success_rate": 0,
                "first_execution": datetime.now().isoformat(),
                "last_execution": None,
            }

        # 統計更新
        stats["total_executions"] += 1
        stats["total_posts_created"] += result["results"].get("successful_posts", 0)
        stats["total_dd_items"] += result["results"].get("dd_items_added", 0)
        stats["last_execution"] = result.get("timestamp")

        # 平均品質スコア計算
        current_avg = stats["average_quality_score"]
        new_score = result["results"].get("quality_score", 0)
        stats["average_quality_score"] = (current_avg * (stats["total_executions"] - 1) + new_score) / stats[
            "total_executions"
        ]

        # 成功率計算
        total_attempted = result["results"]["total_companies"]
        successful = result["results"]["successful_posts"]
        if stats["total_executions"] > 0:
            stats["success_rate"] = (
                stats["total_posts_created"] / (stats["total_posts_created"] + result["results"].get("failed_posts", 0))
            ) * 100

        # 保存
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(
            f"  📊 統計更新: 実行{stats['total_executions']}回, 平均品質{stats['average_quality_score']:.1f}, 成功率{stats['success_rate']:.1f}%"
        )

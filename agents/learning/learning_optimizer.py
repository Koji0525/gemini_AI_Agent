"""
LearningOptimizer - 学習プロセスの最適化

機能:
1. 学習タイミングの動的調整
2. 効果的なパターンの優先学習
3. ナレッジベースの自動整理
4. 学習効率の最大化
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import asyncio


class LearningOptimizer:
    """学習プロセスを最適化するエージェント"""

    def __init__(
        self,
        knowledge_path: str = "mvp_v4/knowledge/learned",
        learning_interval: int = 30,  # 初期学習間隔（秒）
    ):
        """
        初期化

        Args:
            knowledge_path: ナレッジ保存先パス
            learning_interval: 学習間隔（秒）
        """
        self.knowledge_path = knowledge_path
        self.learning_interval = learning_interval
        self.min_interval = 10  # 最小間隔
        self.max_interval = 300  # 最大間隔

        self.learning_history = []
        self.pattern_effectiveness = defaultdict(lambda: {"uses": 0, "success": 0, "avg_impact": 0})
        self.last_learning_time = None

    async def analyze_knowledge_base(self) -> Dict[str, Any]:
        """
        ナレッジベースを分析

        Returns:
            分析結果
        """
        knowledge_file = f"{self.knowledge_path}/auto_registered_knowledge.json"

        if not os.path.exists(knowledge_file):
            return {"status": "empty", "total_entries": 0, "message": "ナレッジベースが空です"}

        with open(knowledge_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        knowledge_base = data.get("knowledge_base", [])

        # カテゴリ別集計
        category_counts = defaultdict(int)
        success_rates = defaultdict(list)
        tags_frequency = defaultdict(int)

        for entry in knowledge_base:
            # カテゴリ
            category = entry.get("category", "unknown")
            category_counts[category] += 1

            # 成功率
            success_rate = entry.get("success_rate", 0)
            success_rates[category].append(success_rate)

            # タグ
            tags = entry.get("metadata", {}).get("tags", [])
            for tag in tags:
                tags_frequency[tag] += 1

        # 平均成功率
        avg_success_by_category = {}
        for category, rates in success_rates.items():
            avg_success_by_category[category] = sum(rates) / len(rates) if rates else 0

        analysis = {
            "status": "analyzed",
            "total_entries": len(knowledge_base),
            "categories": dict(category_counts),
            "avg_success_by_category": avg_success_by_category,
            "top_tags": sorted(tags_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            "analyzed_at": datetime.now().isoformat(),
        }

        return analysis

    async def prioritize_learning(self, recent_events: List[Dict[str, Any]]) -> List[str]:
        """
        優先的に学習すべきパターンを決定

        Args:
            recent_events: 最近のイベントリスト

        Returns:
            優先学習パターンのリスト
        """
        priority_patterns = []

        # イベント頻度を集計
        event_frequency = defaultdict(int)
        error_patterns = defaultdict(int)

        for event in recent_events:
            event_type = event.get("type", "unknown")
            event_frequency[event_type] += 1

            # エラーイベントを特定
            if "error" in event_type.lower() or event.get("status") == "error":
                error_patterns[event_type] += 1

        # 優先順位決定ロジック
        # 1. エラーパターン（最優先）
        priority_patterns.extend(
            [
                f"error_pattern:{pattern}"
                for pattern in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)
            ]
        )

        # 2. 頻出パターン
        frequent_patterns = [
            pattern for pattern, count in event_frequency.items() if count >= 3  # 3回以上出現
        ]
        priority_patterns.extend([f"frequent:{p}" for p in frequent_patterns])

        # 3. 新規パターン（未学習）
        known_patterns = set(self.pattern_effectiveness.keys())
        new_patterns = [
            event_type for event_type in event_frequency.keys() if event_type not in known_patterns
        ]
        priority_patterns.extend([f"new:{p}" for p in new_patterns])

        return priority_patterns[:10]  # 上位10件

    def calculate_next_learning_interval(self, recent_performance: Dict[str, Any]) -> int:
        """
        次回の学習間隔を動的に調整

        Args:
            recent_performance: 最近のパフォーマンス情報

        Returns:
            次回学習までの秒数
        """
        # パフォーマンス指標
        success_rate = recent_performance.get("success_rate", 0.5)
        error_rate = recent_performance.get("error_rate", 0)
        task_velocity = recent_performance.get("task_velocity", 1.0)  # タスク/分

        # 調整係数
        if error_rate > 0.3:
            # エラー率が高い → 頻繁に学習
            adjustment = 0.5
        elif success_rate > 0.9 and task_velocity > 5:
            # 高パフォーマンス → 学習間隔を延ばす
            adjustment = 1.5
        elif success_rate < 0.7:
            # パフォーマンス低下 → 学習強化
            adjustment = 0.7
        else:
            # 通常
            adjustment = 1.0

        new_interval = int(self.learning_interval * adjustment)

        # 範囲制限
        new_interval = max(self.min_interval, min(self.max_interval, new_interval))

        self.learning_interval = new_interval

        return new_interval

    async def optimize_knowledge_base(self) -> Dict[str, Any]:
        """
        ナレッジベースを最適化（重複削除、統合、優先度付け）

        Returns:
            最適化結果
        """
        knowledge_file = f"{self.knowledge_path}/auto_registered_knowledge.json"

        if not os.path.exists(knowledge_file):
            return {"status": "skipped", "message": "ナレッジベースが存在しません"}

        with open(knowledge_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        knowledge_base = data.get("knowledge_base", [])
        original_count = len(knowledge_base)

        # 1. 重複削除（同じscenarioとcategoryの組み合わせ）
        unique_entries = {}
        for entry in knowledge_base:
            key = (entry.get("scenario", ""), entry.get("category", ""))

            # より新しいエントリを優先
            if key not in unique_entries:
                unique_entries[key] = entry
            else:
                existing_time = unique_entries[key].get("metadata", {}).get("timestamp", "")
                new_time = entry.get("metadata", {}).get("timestamp", "")
                if new_time > existing_time:
                    unique_entries[key] = entry

        deduplicated = list(unique_entries.values())

        # 2. 成功率でソート（高い順）
        sorted_entries = sorted(deduplicated, key=lambda x: x.get("success_rate", 0), reverse=True)

        # 3. 古いエントリの削除（1000件以上ある場合）
        if len(sorted_entries) > 1000:
            # 成功率の高い上位1000件を保持
            sorted_entries = sorted_entries[:1000]

        # 更新
        data["knowledge_base"] = sorted_entries
        data["total_entries"] = len(sorted_entries)
        data["last_optimized"] = datetime.now().isoformat()

        # 保存
        with open(knowledge_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        optimization_result = {
            "status": "optimized",
            "original_count": original_count,
            "deduplicated_count": len(deduplicated),
            "final_count": len(sorted_entries),
            "removed_duplicates": original_count - len(deduplicated),
            "removed_old": len(deduplicated) - len(sorted_entries),
            "optimized_at": datetime.now().isoformat(),
        }

        return optimization_result

    async def recommend_learning_focus(self) -> List[str]:
        """
        学習の焦点を推奨

        Returns:
            推奨学習トピックのリスト
        """
        analysis = await self.analyze_knowledge_base()

        if analysis["status"] == "empty":
            return ["基礎パターン", "エラーハンドリング", "タスク実行"]

        recommendations = []

        # 成功率の低いカテゴリを優先
        avg_success = analysis.get("avg_success_by_category", {})
        low_success_categories = [cat for cat, rate in avg_success.items() if rate < 70]

        if low_success_categories:
            recommendations.extend([f"改善: {cat}" for cat in low_success_categories[:3]])

        # タグの頻度から重要トピックを抽出
        top_tags = analysis.get("top_tags", [])
        if top_tags:
            recommendations.extend([f"強化: {tag}" for tag, _ in top_tags[:3]])

        return recommendations[:5]

    async def record_learning_event(self, event: Dict[str, Any]):
        """
        学習イベントを記録

        Args:
            event: 学習イベント情報
        """
        event["timestamp"] = datetime.now().isoformat()
        self.learning_history.append(event)

        # 履歴は最新100件のみ保持
        if len(self.learning_history) > 100:
            self.learning_history = self.learning_history[-100:]

        self.last_learning_time = datetime.now()

    def should_trigger_learning(self, current_performance: Dict[str, Any]) -> bool:
        """
        学習を実行すべきか判定

        Args:
            current_performance: 現在のパフォーマンス情報

        Returns:
            学習実行の可否
        """
        # 初回は必ず実行
        if self.last_learning_time is None:
            return True

        # 経過時間チェック
        elapsed = (datetime.now() - self.last_learning_time).total_seconds()

        if elapsed < self.learning_interval:
            return False

        # パフォーマンス悪化時は強制実行
        error_rate = current_performance.get("error_rate", 0)
        if error_rate > 0.3:
            return True

        return True

    async def save_knowledge(self, event: str, details: Dict[str, Any]) -> bool:
        """
        ナレッジベースに登録

        Args:
            event: イベント名
            details: 詳細情報

        Returns:
            成功/失敗
        """
        try:
            knowledge_file = f"{self.knowledge_path}/auto_registered_knowledge.json"

            # 既存データ読み込み
            if os.path.exists(knowledge_file):
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"knowledge_base": [], "total_entries": 0, "last_updated": None}

            # 新規エントリ追加
            entry = {
                "event": event,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "agent": "LearningOptimizer",
            }

            data["knowledge_base"].append(entry)
            data["total_entries"] = len(data["knowledge_base"])
            data["last_updated"] = datetime.now().isoformat()

            # 保存
            os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"❌ ナレッジ登録失敗: {e}")
            return False

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク実行（統一インターフェース）

        Args:
            task: タスク情報

        Returns:
            実行結果
        """
        task_type = task.get("type")

        if task_type == "analyze":
            # ナレッジベース分析
            result = await self.analyze_knowledge_base()
            await self.save_knowledge("knowledge_analyzed", result)
            return {"status": "success", "analysis": result}

        elif task_type == "optimize":
            # ナレッジベース最適化
            result = await self.optimize_knowledge_base()
            await self.save_knowledge("knowledge_optimized", result)
            return {"status": "success", "optimization": result}

        elif task_type == "recommend":
            # 学習推奨
            recommendations = await self.recommend_learning_focus()
            return {"status": "success", "recommendations": recommendations}

        elif task_type == "adjust_interval":
            # 学習間隔調整
            performance = task.get("performance", {})
            new_interval = self.calculate_next_learning_interval(performance)
            return {
                "status": "success",
                "new_interval": new_interval,
                "previous_interval": self.learning_interval,
            }

        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}

    def get_learning_statistics(self) -> Dict[str, Any]:
        """
        学習統計情報を取得

        Returns:
            統計情報
        """
        return {
            "current_interval": self.learning_interval,
            "min_interval": self.min_interval,
            "max_interval": self.max_interval,
            "learning_history_count": len(self.learning_history),
            "last_learning_time": (
                self.last_learning_time.isoformat() if self.last_learning_time else None
            ),
            "pattern_effectiveness_count": len(self.pattern_effectiveness),
        }

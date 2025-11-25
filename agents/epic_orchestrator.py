"""
EpicOrchestrator - Epicレベルのオーケストレーションを担当
既存のCompleteEngineと連携し、複数Epicの管理を可能にする
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# 既存システムとの互換性を維持
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.integration.progress_analyzer_v2 import ProgressAnalyzerV2
from core_agents.pm_agent_v33_epic import PMAgentV33Epic
from tools.base_data_accessor import BaseDataAccessor


class EpicOrchestrator(BaseDataAccessor):
    """Epicレベルのオーケストレーションを管理"""

    def __init__(self, sheets_manager=None):
        super().__init__(sheets_manager)
        self.pm_agent = PMAgentV33Epic(sheets_manager)
        self.progress_analyzer = ProgressAnalyzerV2()
        self.logger = logging.getLogger(__name__)

        # 実行統計
        self.stats = {"epics_processed": 0, "stories_generated": 0, "last_run": None}

    async def run_epic_cycle(self) -> Dict[str, Any]:
        """
        Epic管理サイクルの実行

        Returns:
            Dict: 実行結果の統計
        """
        try:
            self.logger.info("Epicオーケストレーションサイクル開始")
            self.stats["last_run"] = datetime.now().isoformat()

            # 1. Epicの分解とStory生成
            epic_result = await self.pm_agent.process_epics()

            # 2. 進捗分析
            progress_result = await self.analyze_epic_progress()

            # 3. リソース最適化
            optimization_result = await self.optimize_resource_allocation()

            # 統計更新
            self.stats["epics_processed"] += 1 if epic_result else 0

            result = {
                "success": epic_result and progress_result and optimization_result,
                "epic_processing": epic_result,
                "progress_analysis": progress_result,
                "resource_optimization": optimization_result,
                "timestamp": self.stats["last_run"],
                "next_scheduled_run": self._calculate_next_run(),
            }

            self.logger.info("Epicオーケストレーションサイクル完了")
            return result

        except Exception as e:
            self.logger.error(f"Epicオーケストレーション中にエラー: {e}")
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    async def analyze_epic_progress(self) -> Dict[str, Any]:
        """Epicレベルの進捗分析"""
        try:
            self.logger.info("Epic進捗分析開始")

            # 全Epicの進捗を分析
            epics = self.read_sheet_as_dicts("project_goal")
            active_epics = [e for e in epics if e.get("status") in ["active", "in_progress"]]

            progress_report = {
                "total_epics": len(active_epics),
                "epic_details": [],
                "overall_progress": 0,
                "bottlenecks": [],
                "recommendations": [],
            }

            total_progress = 0
            for epic in active_epics:
                epic_id = epic.get("id")
                epic_progress = await self._analyze_single_epic_progress(epic_id)

                progress_report["epic_details"].append(epic_progress)
                total_progress += epic_progress.get("completion_rate", 0)

                # ボトルネックの検出
                if epic_progress.get("bottleneck_detected", False):
                    progress_report["bottlenecks"].append(
                        {
                            "epic_id": epic_id,
                            "issue": epic_progress.get("bottleneck_reason", "Unknown"),
                            "severity": epic_progress.get("bottleneck_severity", "medium"),
                        }
                    )

            # 全体進捗率の計算
            if active_epics:
                progress_report["overall_progress"] = total_progress / len(active_epics)

            # 推奨アクションの生成
            progress_report["recommendations"] = await self._generate_recommendations(
                progress_report
            )

            self.logger.info(f"Epic進捗分析完了: 進捗率 {progress_report['overall_progress']:.1f}%")
            return progress_report

        except Exception as e:
            self.logger.error(f"Epic進捗分析中にエラー: {e}")
            return {"error": str(e)}

    async def _analyze_single_epic_progress(self, epic_id: str) -> Dict[str, Any]:
        """単一Epicの進捗分析"""
        try:
            # 関連するStoryを取得
            stories = self.read_sheet_as_dicts("pm_tasks")
            epic_stories = [s for s in stories if s.get("epic_id") == epic_id]

            if not epic_stories:
                return {
                    "epic_id": epic_id,
                    "completion_rate": 0,
                    "bottleneck_detected": True,
                    "bottleneck_reason": "関連Storyが見つかりません",
                    "bottleneck_severity": "high",
                }

            # 進捗率の計算
            total_stories = len(epic_stories)
            completed_stories = len([s for s in epic_stories if s.get("status") == "completed"])
            completion_rate = (completed_stories / total_stories) * 100

            # ボトルネックの検出
            bottleneck_detected = completion_rate < 50 and total_stories > 5
            bottleneck_reason = "進捗が50%未満でボトルネックの可能性" if bottleneck_detected else ""

            return {
                "epic_id": epic_id,
                "total_stories": total_stories,
                "completed_stories": completed_stories,
                "completion_rate": completion_rate,
                "bottleneck_detected": bottleneck_detected,
                "bottleneck_reason": bottleneck_reason,
                "bottleneck_severity": "medium" if bottleneck_detected else "none",
            }

        except Exception as e:
            self.logger.error(f"単一Epic進捗分析エラー {epic_id}: {e}")
            return {
                "epic_id": epic_id,
                "error": str(e),
                "completion_rate": 0,
                "bottleneck_detected": True,
            }

    async def _generate_recommendations(self, progress_report: Dict[str, Any]) -> List[str]:
        """進捗分析に基づく推奨アクションを生成"""
        recommendations = []

        # ボトルネックに対する推奨
        for bottleneck in progress_report.get("bottlenecks", []):
            if bottleneck["severity"] == "high":
                recommendations.append(
                    f"高優先度ボトルネック: Epic {bottleneck['epic_id']} - {bottleneck['issue']}"
                )

        # 全体進捗に基づく推奨
        overall_progress = progress_report.get("overall_progress", 0)
        if overall_progress < 30:
            recommendations.append(
                "全体進捗が遅延しています。リソース配分の見直しを検討してください"
            )
        elif overall_progress > 80:
            recommendations.append("順調に進捗しています。次のEpicの準備を開始できます")

        # Story数に基づく推奨
        total_epics = progress_report.get("total_epics", 0)
        if total_epics > 3:
            recommendations.append("同時実行Epic数が多いため、優先度付けを強化してください")

        return recommendations

    async def optimize_resource_allocation(self) -> Dict[str, Any]:
        """リソース配分の最適化"""
        try:
            self.logger.info("リソース配分最適化開始")

            # 現在のリソース使用状況の分析
            resource_usage = await self._analyze_resource_usage()

            # 最適化提案の生成
            optimization_suggestions = await self._generate_optimization_suggestions(resource_usage)

            result = {
                "current_usage": resource_usage,
                "suggestions": optimization_suggestions,
                "estimated_improvement": self._estimate_improvement(optimization_suggestions),
            }

            self.logger.info("リソース配分最適化完了")
            return result

        except Exception as e:
            self.logger.error(f"リソース最適化中にエラー: {e}")
            return {"error": str(e)}

    async def _analyze_resource_usage(self) -> Dict[str, Any]:
        """現在のリソース使用状況を分析"""
        # 簡易的な実装 - 実際にはシステムメトリクスを使用
        return {
            "cpu_usage": "medium",  # low, medium, high
            "memory_usage": "medium",
            "concurrent_epics": 2,
            "concurrent_stories": 5,
            "api_usage": "low",
        }

    async def _generate_optimization_suggestions(self, resource_usage: Dict[str, Any]) -> List[str]:
        """リソース最適化の提案を生成"""
        suggestions = []

        if resource_usage.get("concurrent_epics", 0) > 3:
            suggestions.append("同時実行Epic数を3以下に制限することを推奨")

        if resource_usage.get("concurrent_stories", 0) > 10:
            suggestions.append("同時実行Story数を10以下に制限することを推奨")

        if resource_usage.get("api_usage") == "high":
            suggestions.append("API使用率が高いため、バッチ処理の導入を検討")

        if not suggestions:
            suggestions.append("現在のリソース配分は最適です")

        return suggestions

    def _estimate_improvement(self, suggestions: List[str]) -> str:
        """最適化による改善効果の見積もり"""
        if len(suggestions) == 1 and "最適です" in suggestions[0]:
            return "現状維持"

        improvement_mapping = {
            "Epic数": "10-20%の効率改善",
            "Story数": "5-15%の実行時間短縮",
            "API使用率": "15-25%のコスト削減",
        }

        for key in improvement_mapping:
            if any(key in suggestion for suggestion in suggestions):
                return improvement_mapping[key]

        return "5-10%の総合改善"

    def _calculate_next_run(self) -> str:
        """次回実行時刻の計算"""
        next_run = datetime.now().timestamp() + 3600  # 1時間後
        return datetime.fromtimestamp(next_run).isoformat()

    async def get_orchestration_status(self) -> Dict[str, Any]:
        """オーケストレーションの現在の状態を取得"""
        return {
            "stats": self.stats,
            "is_healthy": await self._health_check(),
            "recommended_actions": await self._get_recommended_actions(),
        }

    async def _health_check(self) -> bool:
        """システム健全性チェック"""
        try:
            # 基本的なコンポーネントが動作しているか確認
            epics = self.read_sheet_as_dicts("project_goal")
            stories = self.read_sheet_as_dicts("pm_tasks")

            return len(epics) > 0 and len(stories) > 0
        except Exception:
            return False

    async def _get_recommended_actions(self) -> List[str]:
        """推奨アクションの取得"""
        return [
            "定期的なEpic進捗分析の実行",
            "リソース使用率の監視",
            "ボトルネックの早期検出と対応",
        ]


# テスト用の実行コード
async def main():
    """テスト実行"""
    logging.basicConfig(level=logging.INFO)

    # EpicOrchestratorのインスタンス化
    orchestrator = EpicOrchestrator()

    # オーケストレーションサイクルの実行
    result = await orchestrator.run_epic_cycle()

    print("🎯 Epicオーケストレーション結果:")
    print(f"✅ 成功: {result.get('success', False)}")
    print(f"📊 Epic処理: {result.get('epic_processing', False)}")
    print(f"📈 進捗分析: {result.get('progress_analysis', {})}")
    print(f"⚡ リソース最適化: {result.get('resource_optimization', {})}")

    # 現在の状態も表示
    status = await orchestrator.get_orchestration_status()
    print(f"🩺 健全性: {status.get('is_healthy', False)}")
    print(f"📋 推奨アクション: {status.get('recommended_actions', [])}")


if __name__ == "__main__":
    asyncio.run(main())

"""
IntelligenceCoordinator - Phase 4.1統合コーディネーター

【役割】
3つのインテリジェンスモジュールを統合し、包括的な故障分析を提供

【統合モジュール】
1. FailurePatternDetector: パターン検出
2. RootCauseAnalyzer: 根本原因分析
3. AgentAttributionSystem: 責任特定
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.intelligence.agent_attribution_system import \
    AgentAttributionSystem
from agents.observability.intelligence.failure_pattern_detector import \
    FailurePatternDetector
from agents.observability.intelligence.root_cause_analyzer import \
    RootCauseAnalyzer
from agents.observability.observability_manager import \
    get_observability_manager


class IntelligenceCoordinator:
    """インテリジェンス統合コーディネーター"""

    def __init__(self):
        self.obs_manager = get_observability_manager()
        self.pattern_detector = FailurePatternDetector()
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.attribution_system = AgentAttributionSystem()

        print("✅ IntelligenceCoordinator初期化完了")

    def perform_comprehensive_failure_analysis(
        self, failure_trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        包括的な故障分析

        Args:
            failure_trace_id: 特定の失敗トレースID（省略時は最新のエラーを分析）

        Returns:
            統合分析結果
        """
        try:
            analysis_start = datetime.now()

            # 最新のエラートレースを取得（指定がない場合）
            if not failure_trace_id:
                all_traces = self.obs_manager.search_traces(limit=100)
                error_traces = [t for t in all_traces if t.get("status") == "error"]

                if not error_traces:
                    return {
                        "status": "no_errors",
                        "message": "分析対象のエラーが見つかりません",
                        "suggestion": "システムは正常に動作しています",
                    }

                failure_trace_id = error_traces[0].get("trace_id")

            print(f"\n🔍 包括的故障分析開始: {failure_trace_id}")

            # 1. パターン検出
            print("   [1/4] パターン検出中...")
            patterns = self.pattern_detector.detect_failure_patterns()

            # 2. 根本原因分析
            print("   [2/4] 根本原因分析中...")
            root_cause = self.root_cause_analyzer.analyze_failure_chain(failure_trace_id)

            # 3. 責任特定
            print("   [3/4] 責任エージェント特定中...")
            attribution = self.attribution_system.attribute_failure_to_agent(failure_trace_id)

            # 4. トレンド分析
            print("   [4/4] トレンド分析中...")
            trends = self.pattern_detector.analyze_failure_trends()

            # 統合レポート生成
            analysis_duration = (datetime.now() - analysis_start).total_seconds()

            report = {
                "analysis_id": f"comprehensive-{datetime.now().timestamp()}",
                "analyzed_trace_id": failure_trace_id,
                "analysis_duration_seconds": round(analysis_duration, 2),
                # パターン検出結果
                "pattern_analysis": {
                    "total_errors": patterns.get("total_errors", 0),
                    "detected_patterns": len(patterns.get("patterns_detected", [])),
                    "classification_rate": patterns.get("classification_rate", 0),
                    "top_patterns": patterns.get("patterns_detected", [])[:3],
                },
                # 根本原因分析結果
                "root_cause_analysis": {
                    "root_cause_operation": root_cause.get("root_cause", {}).get(
                        "root_cause_operation", "unknown"
                    ),
                    "confidence": root_cause.get("root_cause", {}).get("confidence", 0),
                    "impact_severity": root_cause.get("impact_assessment", {}).get(
                        "impact_severity", "unknown"
                    ),
                    "affected_operations": root_cause.get("impact_assessment", {}).get(
                        "affected_operations_count", 0
                    ),
                },
                # 責任特定結果
                "agent_attribution": {
                    "responsible_agent": attribution.get("responsible_agent", "unknown"),
                    "confidence_score": attribution.get("confidence_score", 0),
                    "recommended_actions": attribution.get("recommended_actions", [])[:2],
                },
                # トレンド情報
                "trend_analysis": {
                    "peak_error_hour": trends.get("peak_error_hour"),
                    "recurring_pattern_count": len(trends.get("recurring_patterns", [])),
                },
                # 総合評価
                "summary": self._generate_summary(patterns, root_cause, attribution),
                "timestamp": datetime.now().isoformat(),
            }

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": report["analysis_id"],
                    "operation_name": "intelligence.comprehensive_analysis",
                    "status": "success",
                    "duration_ms": int(analysis_duration * 1000),
                    "analyzed_trace_id": failure_trace_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return report

        except Exception as e:
            return {"error": str(e)}

    def _generate_summary(
        self, patterns: Dict[str, Any], root_cause: Dict[str, Any], attribution: Dict[str, Any]
    ) -> str:
        """統合サマリーの生成"""

        responsible_agent = attribution.get("responsible_agent", "unknown")
        confidence = attribution.get("confidence_score", 0)
        root_op = root_cause.get("root_cause", {}).get("root_cause_operation", "unknown")

        if confidence > 0.7:
            confidence_desc = "高い確信度で"
        elif confidence > 0.4:
            confidence_desc = "中程度の確信度で"
        else:
            confidence_desc = "低い確信度で"

        summary = (
            f"{confidence_desc}{responsible_agent}が責任エージェントと特定されました。"
            f"根本原因は{root_op}のオペレーションです。"
        )

        # 推奨アクションを追加
        actions = attribution.get("recommended_actions", [])
        if actions:
            summary += f" 推奨アクション: {actions[0].get('action', '調査が必要')}"

        return summary

    def generate_intelligence_dashboard(self) -> Dict[str, Any]:
        """
        インテリジェンスダッシュボードデータの生成

        Returns:
            ダッシュボード表示用のデータ
        """
        try:
            # 各モジュールからデータを収集
            patterns = self.pattern_detector.detect_failure_patterns()
            trends = self.pattern_detector.analyze_failure_trends()
            attribution_report = self.attribution_system.generate_attribution_report()

            dashboard = {
                "system_health": {
                    "total_errors": patterns.get("total_errors", 0),
                    "classification_rate": patterns.get("classification_rate", 0),
                    "peak_error_time": trends.get("peak_error_hour", "不明"),
                },
                "pattern_insights": {
                    "detected_patterns": len(patterns.get("patterns_detected", [])),
                    "top_patterns": [
                        {
                            "name": p.get("pattern_name"),
                            "count": p.get("occurrence_count"),
                            "severity": p.get("severity"),
                        }
                        for p in patterns.get("patterns_detected", [])[:5]
                    ],
                },
                "agent_performance": {
                    "agent_ranking": attribution_report.get("agent_ranking", [])[:5],
                    "most_failing_agent": (
                        attribution_report.get("agent_ranking", [{}])[0].get("agent", "なし")
                        if attribution_report.get("agent_ranking")
                        else "なし"
                    ),
                },
                "recommendations": self._generate_recommendations(
                    patterns, trends, attribution_report
                ),
                "dashboard_timestamp": datetime.now().isoformat(),
            }

            return dashboard

        except Exception as e:
            return {"error": str(e)}

    def _generate_recommendations(
        self, patterns: Dict[str, Any], trends: Dict[str, Any], attribution_report: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """推奨事項の生成"""

        recommendations = []

        # パターンベースの推奨
        if patterns.get("total_errors", 0) > 10:
            recommendations.append(
                {
                    "type": "pattern",
                    "priority": "high",
                    "message": "エラー数が多いため、システム全体の見直しを推奨",
                }
            )

        # トレンドベースの推奨
        if trends.get("recurring_patterns"):
            recommendations.append(
                {
                    "type": "trend",
                    "priority": "medium",
                    "message": "再発パターンが検出されました。根本的な修正が必要です",
                }
            )

        # エージェントベースの推奨
        agent_ranking = attribution_report.get("agent_ranking", [])
        if agent_ranking and agent_ranking[0].get("failure_count", 0) > 5:
            worst_agent = agent_ranking[0].get("agent", "不明")
            recommendations.append(
                {
                    "type": "agent",
                    "priority": "high",
                    "message": f"{worst_agent}の改善を最優先で実施してください",
                }
            )

        return recommendations


if __name__ == "__main__":
    print("🧪 IntelligenceCoordinator テスト")

    coordinator = IntelligenceCoordinator()

    # テスト1: ダッシュボードデータ生成
    print("\n【テスト1: ダッシュボードデータ生成】")
    dashboard = coordinator.generate_intelligence_dashboard()
    print(f"システム健全性:")
    print(f"  総エラー数: {dashboard.get('system_health', {}).get('total_errors', 0)}")
    print(f"  分類率: {dashboard.get('system_health', {}).get('classification_rate', 0):.1%}")
    print(f"推奨事項: {len(dashboard.get('recommendations', []))}件")

    # テスト2: 包括的故障分析（エラーがある場合のみ）
    print("\n【テスト2: 包括的故障分析】")
    analysis = coordinator.perform_comprehensive_failure_analysis()

    if analysis.get("status") == "no_errors":
        print(f"✅ {analysis.get('message')}")
    elif "error" in analysis:
        print(f"⚠️ エラー: {analysis.get('error')}")
    else:
        print(f"分析完了:")
        print(
            f"  責任エージェント: {analysis.get('agent_attribution', {}).get('responsible_agent', 'unknown')}"
        )
        print(f"  信頼度: {analysis.get('agent_attribution', {}).get('confidence_score', 0):.1%}")
        print(f"  サマリー: {analysis.get('summary', '不明')}")

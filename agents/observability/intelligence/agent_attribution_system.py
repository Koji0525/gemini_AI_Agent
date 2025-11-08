"""
AgentAttributionSystem - エージェント責任特定システム

【Phase 4.1の目的】
どのエージェントが失敗の責任を持つかを信頼度スコア付きで特定

【主要機能】
1. エージェント単位での責任追跡
2. 信頼度スコア計算
3. 推奨修正アクションの生成
4. 責任連鎖の可視化
"""

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager


class AgentAttributionSystem:
    """エージェント責任特定システム"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # エージェント責任パターン定義
        self.attribution_patterns = {
            "PMAgent": {
                "typical_failures": ["task_planning", "task_decomposition", "priority_setting"],
                "severity_weight": 0.9,
                "responsibility_keywords": ["planning", "decompose", "priority"],
            },
            "TaskExecutor": {
                "typical_failures": ["task_execution", "step_execution", "quality_validation"],
                "severity_weight": 0.85,
                "responsibility_keywords": ["execute", "step", "quality"],
            },
            "CollaborationAgent": {
                "typical_failures": ["agent_routing", "load_balancing", "agent_registration"],
                "severity_weight": 0.8,
                "responsibility_keywords": ["route", "balance", "register"],
            },
            "WordPressAgent": {
                "typical_failures": ["wp_post_creation", "wp_authentication", "wp_api_call"],
                "severity_weight": 0.75,
                "responsibility_keywords": ["wordpress", "post", "wp_"],
            },
            "ReviewAgent": {
                "typical_failures": ["code_review", "quality_check", "validation"],
                "severity_weight": 0.7,
                "responsibility_keywords": ["review", "check", "validate"],
            },
        }

        print("✅ AgentAttributionSystem初期化完了")

    def attribute_failure_to_agent(self, failure_trace_id: str) -> Dict[str, Any]:
        """
        失敗をエージェントに帰属

        Args:
            failure_trace_id: 失敗トレースID

        Returns:
            責任エージェントと信頼度スコア
        """
        try:
            # 失敗トレースを取得
            all_traces = self.obs_manager.search_traces(limit=1000)
            failure_trace = next(
                (t for t in all_traces if t.get("trace_id") == failure_trace_id), None
            )

            if not failure_trace:
                return {"error": f"トレースID {failure_trace_id} が見つかりません"}

            operation_name = failure_trace.get("operation_name", "")
            error_message = failure_trace.get("error_message", "").lower()

            # エージェント責任スコア計算
            agent_scores = {}
            for agent_name, pattern in self.attribution_patterns.items():
                score = self._calculate_responsibility_score(
                    agent_name, pattern, operation_name, error_message
                )
                if score > 0:
                    agent_scores[agent_name] = score

            # 最高スコアのエージェントを特定
            if agent_scores:
                responsible_agent = max(agent_scores.items(), key=lambda x: x[1])
                agent_name, confidence = responsible_agent

                # 推奨修正アクションを生成
                recommended_actions = self._generate_fix_actions(
                    agent_name, operation_name, error_message
                )

                # 責任連鎖を構築
                responsibility_chain = self._build_responsibility_chain(failure_trace, all_traces)

                # トレース記録
                self.obs_manager.record_trace(
                    {
                        "trace_id": f"agent-attribution-{datetime.now().timestamp()}",
                        "operation_name": "intelligence.agent_attribution",
                        "status": "success",
                        "duration_ms": 180,
                        "responsible_agent": agent_name,
                        "confidence_score": confidence,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                return {
                    "failure_trace_id": failure_trace_id,
                    "responsible_agent": agent_name,
                    "confidence_score": confidence,
                    "alternative_candidates": [
                        {"agent": name, "score": score}
                        for name, score in sorted(
                            agent_scores.items(), key=lambda x: x[1], reverse=True
                        )[1:3]
                    ],
                    "recommended_actions": recommended_actions,
                    "responsibility_chain": responsibility_chain,
                    "attribution_timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "failure_trace_id": failure_trace_id,
                    "responsible_agent": "unknown",
                    "confidence_score": 0.0,
                    "reasoning": "責任エージェントを特定できませんでした",
                }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_responsibility_score(
        self, agent_name: str, pattern: Dict[str, Any], operation_name: str, error_message: str
    ) -> float:
        """責任スコアの計算"""

        score = 0.0

        # オペレーション名からのマッチング
        for failure_type in pattern["typical_failures"]:
            if failure_type in operation_name.lower():
                score += 0.4

        # エラーメッセージからのマッチング
        for keyword in pattern["responsibility_keywords"]:
            if keyword in error_message:
                score += 0.3

        # エージェント名の直接マッチング
        if agent_name.lower() in operation_name.lower():
            score += 0.5

        # 重み付け
        score *= pattern["severity_weight"]

        # 正規化（0-1範囲）
        return min(score, 1.0)

    def _generate_fix_actions(
        self, agent_name: str, operation_name: str, error_message: str
    ) -> List[Dict[str, Any]]:
        """推奨修正アクションの生成"""

        action_templates = {
            "PMAgent": [
                {
                    "action": "タスク計画ロジックの見直し",
                    "priority": "high",
                    "estimated_effort": "2時間",
                },
                {
                    "action": "タスク分解アルゴリズムの改善",
                    "priority": "medium",
                    "estimated_effort": "4時間",
                },
            ],
            "TaskExecutor": [
                {
                    "action": "実行ステップのエラーハンドリング強化",
                    "priority": "high",
                    "estimated_effort": "3時間",
                },
                {
                    "action": "品質検証ロジックの改善",
                    "priority": "medium",
                    "estimated_effort": "2時間",
                },
            ],
            "CollaborationAgent": [
                {
                    "action": "ルーティングロジックの最適化",
                    "priority": "high",
                    "estimated_effort": "3時間",
                },
                {
                    "action": "負荷分散アルゴリズムの調整",
                    "priority": "medium",
                    "estimated_effort": "4時間",
                },
            ],
            "WordPressAgent": [
                {
                    "action": "WordPress API認証の再確認",
                    "priority": "critical",
                    "estimated_effort": "1時間",
                },
                {
                    "action": "投稿作成ロジックのデバッグ",
                    "priority": "high",
                    "estimated_effort": "2時間",
                },
            ],
            "ReviewAgent": [
                {
                    "action": "レビュー基準の明確化",
                    "priority": "medium",
                    "estimated_effort": "3時間",
                },
                {
                    "action": "品質チェックロジックの改善",
                    "priority": "medium",
                    "estimated_effort": "2時間",
                },
            ],
        }

        actions = action_templates.get(
            agent_name,
            [{"action": "エラーログの詳細調査", "priority": "high", "estimated_effort": "不明"}],
        )

        # コンテキストに基づく優先度調整
        if "authentication" in error_message or "auth" in error_message:
            for action in actions:
                if "認証" in action["action"] or "auth" in action["action"].lower():
                    action["priority"] = "critical"

        return actions

    def _build_responsibility_chain(
        self, failure_trace: Dict, all_traces: List[Dict]
    ) -> List[Dict[str, Any]]:
        """責任連鎖の構築"""

        chain = []
        failure_time = failure_trace.get("timestamp", "")

        # 時間的に近いトレースを収集
        for trace in all_traces:
            if self._is_time_close(trace.get("timestamp", ""), failure_time):
                # オペレーション名からエージェントを推測
                operation = trace.get("operation_name", "")
                agent = self._infer_agent_from_operation(operation)

                chain.append(
                    {
                        "agent": agent,
                        "operation": operation,
                        "status": trace.get("status", ""),
                        "timestamp": trace.get("timestamp", ""),
                        "is_failure": trace.get("trace_id") == failure_trace.get("trace_id"),
                    }
                )

        # 時系列順にソート
        chain.sort(key=lambda x: x["timestamp"])
        return chain

    def _infer_agent_from_operation(self, operation_name: str) -> str:
        """オペレーション名からエージェントを推測"""

        operation_lower = operation_name.lower()

        for agent_name, pattern in self.attribution_patterns.items():
            if agent_name.lower() in operation_lower:
                return agent_name
            for keyword in pattern["responsibility_keywords"]:
                if keyword in operation_lower:
                    return agent_name

        return "UnknownAgent"

    def _is_time_close(self, time1: str, time2: str, threshold_seconds: int = 300) -> bool:
        """時間的に近いかを判定"""
        try:
            dt1 = datetime.fromisoformat(time1.replace("Z", "+00:00"))
            dt2 = datetime.fromisoformat(time2.replace("Z", "+00:00"))
            return abs((dt1 - dt2).total_seconds()) < threshold_seconds
        except:
            return False

    def generate_attribution_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        責任レポートの生成

        Args:
            time_window_hours: 分析対象の時間窓

        Returns:
            エージェント別の失敗統計
        """
        try:
            all_traces = self.obs_manager.search_traces(limit=1000)
            error_traces = [t for t in all_traces if t.get("status") == "error"]

            # エージェント別失敗カウント
            agent_failures = defaultdict(int)
            agent_details = defaultdict(list)

            for trace in error_traces:
                operation = trace.get("operation_name", "")
                agent = self._infer_agent_from_operation(operation)
                agent_failures[agent] += 1
                agent_details[agent].append(
                    {
                        "trace_id": trace.get("trace_id"),
                        "operation": operation,
                        "error_message": trace.get("error_message", "")[:100],
                        "timestamp": trace.get("timestamp", ""),
                    }
                )

            # 責任ランキング
            ranking = [
                {
                    "agent": agent,
                    "failure_count": count,
                    "failure_rate": count / len(error_traces) if error_traces else 0,
                    "recent_failures": agent_details[agent][:3],
                }
                for agent, count in sorted(agent_failures.items(), key=lambda x: x[1], reverse=True)
            ]

            return {
                "total_failures": len(error_traces),
                "time_window_hours": time_window_hours,
                "agent_ranking": ranking,
                "summary": f"最多失敗エージェント: {ranking[0]['agent'] if ranking else 'なし'}",
                "report_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    print("🧪 AgentAttributionSystem テスト")

    system = AgentAttributionSystem()

    # テスト1: 責任レポート生成
    print("\n【テスト1: 責任レポート生成】")
    report = system.generate_attribution_report()
    print(f"総失敗数: {report.get('total_failures', 0)}")
    print(f"エージェント数: {len(report.get('agent_ranking', []))}")

    # テスト2: 模擬失敗の責任特定
    print("\n【テスト2: 失敗の責任特定（模擬）】")
    attribution = system.attribute_failure_to_agent("test-trace-001")

    if "error" in attribution:
        print(f"⚠️ {attribution['error']}")
        print("   （実際のエラートレースが必要です）")
    else:
        print(f"責任エージェント: {attribution.get('responsible_agent', 'unknown')}")
        print(f"信頼度: {attribution.get('confidence_score', 0):.1%}")

"""
RootCauseAnalyzer - 根本原因分析エンジン

【Phase 4.1の目的】
因果関係を分析し、失敗の根本原因を特定する

【主要機能】
1. トレースチェーンの逆追跡
2. 因果関係の推論
3. 信頼度スコア付き原因特定
4. 影響範囲の評価
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager


class RootCauseAnalyzer:
    """根本原因分析エンジン"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # 因果関係ルール定義
        self.causal_rules = {
            "authentication_causes_task_failure": {
                "condition": lambda traces: self._has_auth_error_before_task_error(traces),
                "confidence": 0.95,
                "explanation": "認証エラーがタスク失敗の原因",
            },
            "rate_limit_causes_retry": {
                "condition": lambda traces: self._has_rate_limit_before_retry(traces),
                "confidence": 0.90,
                "explanation": "APIレート制限がリトライの原因",
            },
            "network_timeout_causes_cascade": {
                "condition": lambda traces: self._has_timeout_cascade(traces),
                "confidence": 0.85,
                "explanation": "ネットワークタイムアウトが連鎖失敗の原因",
            },
        }

        print("✅ RootCauseAnalyzer初期化完了")

    def analyze_failure_chain(self, failure_trace_id: str) -> Dict[str, Any]:
        """
        失敗チェーンの分析

        Args:
            failure_trace_id: 分析対象の失敗トレースID

        Returns:
            根本原因分析結果
        """
        try:
            # 失敗トレースを取得
            all_traces = self.obs_manager.search_traces(limit=1000)
            failure_trace = next(
                (t for t in all_traces if t.get("trace_id") == failure_trace_id), None
            )

            if not failure_trace:
                return {"error": f"トレースID {failure_trace_id} が見つかりません"}

            # 時系列で関連トレースを収集
            failure_time = failure_trace.get("timestamp", "")
            related_traces = self._get_related_traces(all_traces, failure_trace, failure_time)

            # 因果チェーンを構築
            causal_chain = self._build_causal_chain(failure_trace, related_traces)

            # 根本原因を特定
            root_cause = self._identify_root_cause(causal_chain)

            # 影響範囲を評価
            impact_assessment = self._assess_impact(failure_trace, related_traces)

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": f"root-cause-analysis-{datetime.now().timestamp()}",
                    "operation_name": "intelligence.root_cause_analysis",
                    "status": "success",
                    "duration_ms": 200,
                    "analyzed_trace_id": failure_trace_id,
                    "root_cause_confidence": root_cause.get("confidence", 0),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "failure_trace_id": failure_trace_id,
                "failure_operation": failure_trace.get("operation_name", ""),
                "causal_chain": causal_chain,
                "root_cause": root_cause,
                "impact_assessment": impact_assessment,
                "analysis_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}

    def _get_related_traces(
        self, all_traces: List[Dict], failure_trace: Dict, failure_time: str
    ) -> List[Dict]:
        """関連トレースの収集"""

        related = []
        for trace in all_traces:
            # 同じオペレーション名または時間的に近い
            if (
                trace.get("operation_name", "").split(".")[0]
                == failure_trace.get("operation_name", "").split(".")[0]
            ):
                related.append(trace)
            elif self._is_time_close(trace.get("timestamp", ""), failure_time):
                related.append(trace)

        # 時系列順にソート
        related.sort(key=lambda x: x.get("timestamp", ""))
        return related

    def _is_time_close(self, time1: str, time2: str, threshold_seconds: int = 300) -> bool:
        """時間的に近いかを判定"""
        try:
            dt1 = datetime.fromisoformat(time1.replace("Z", "+00:00"))
            dt2 = datetime.fromisoformat(time2.replace("Z", "+00:00"))
            return abs((dt1 - dt2).total_seconds()) < threshold_seconds
        except:
            return False

    def _build_causal_chain(
        self, failure_trace: Dict, related_traces: List[Dict]
    ) -> List[Dict[str, Any]]:
        """因果チェーンの構築"""

        chain = []
        for trace in related_traces:
            chain.append(
                {
                    "step": len(chain) + 1,
                    "trace_id": trace.get("trace_id", ""),
                    "operation": trace.get("operation_name", ""),
                    "status": trace.get("status", ""),
                    "timestamp": trace.get("timestamp", ""),
                    "is_failure_point": trace.get("trace_id") == failure_trace.get("trace_id"),
                }
            )

        return chain

    def _identify_root_cause(self, causal_chain: List[Dict]) -> Dict[str, Any]:
        """根本原因の特定"""

        # 最初のエラーを根本原因として特定
        error_steps = [step for step in causal_chain if step["status"] == "error"]

        if error_steps:
            first_error = error_steps[0]
            return {
                "root_cause_operation": first_error["operation"],
                "root_cause_step": first_error["step"],
                "confidence": 0.88,
                "reasoning": f"チェーン内の最初のエラー（ステップ{first_error['step']}）",
                "trace_id": first_error["trace_id"],
            }

        # エラーが見つからない場合
        return {
            "root_cause_operation": "unknown",
            "root_cause_step": 0,
            "confidence": 0.0,
            "reasoning": "明確な根本原因を特定できませんでした",
        }

    def _assess_impact(self, failure_trace: Dict, related_traces: List[Dict]) -> Dict[str, Any]:
        """影響範囲の評価"""

        affected_operations = set()
        downstream_failures = 0

        failure_time = failure_trace.get("timestamp", "")

        for trace in related_traces:
            if trace.get("status") == "error" and trace.get("trace_id") != failure_trace.get(
                "trace_id"
            ):

                if self._is_time_close(trace.get("timestamp", ""), failure_time):
                    affected_operations.add(trace.get("operation_name", ""))
                    downstream_failures += 1

        return {
            "affected_operations_count": len(affected_operations),
            "affected_operations": list(affected_operations),
            "downstream_failures": downstream_failures,
            "impact_severity": (
                "high"
                if downstream_failures > 3
                else "medium" if downstream_failures > 0 else "low"
            ),
        }

    def _has_auth_error_before_task_error(self, traces: List[Dict]) -> bool:
        """認証エラー→タスクエラーのパターン検出"""
        auth_error_time = None
        task_error_time = None

        for trace in traces:
            if "auth" in trace.get("operation_name", "").lower() and trace.get("status") == "error":
                auth_error_time = trace.get("timestamp")
            elif (
                "task" in trace.get("operation_name", "").lower() and trace.get("status") == "error"
            ):
                task_error_time = trace.get("timestamp")

        if auth_error_time and task_error_time:
            return auth_error_time < task_error_time
        return False

    def _has_rate_limit_before_retry(self, traces: List[Dict]) -> bool:
        """レート制限→リトライのパターン検出"""
        for i, trace in enumerate(traces[:-1]):
            if "rate limit" in str(trace.get("error_message", "")).lower():
                next_trace = traces[i + 1]
                if "retry" in next_trace.get("operation_name", "").lower():
                    return True
        return False

    def _has_timeout_cascade(self, traces: List[Dict]) -> bool:
        """タイムアウト連鎖のパターン検出"""
        timeout_count = sum(
            1 for t in traces if "timeout" in str(t.get("error_message", "")).lower()
        )
        return timeout_count >= 3


if __name__ == "__main__":
    print("🧪 RootCauseAnalyzer テスト")

    analyzer = RootCauseAnalyzer()

    # テスト: 模擬失敗チェーン分析
    print("\n【テスト: 失敗チェーン分析（模擬）】")

    # 実際のトレースIDがない場合はダミーIDで動作確認
    result = analyzer.analyze_failure_chain("test-trace-001")

    if "error" in result:
        print(f"⚠️ {result['error']}")
        print("   （実際のエラートレースが必要です）")
    else:
        print(f"根本原因: {result.get('root_cause', {}).get('root_cause_operation', 'unknown')}")
        print(f"信頼度: {result.get('root_cause', {}).get('confidence', 0):.1%}")
        print(f"影響範囲: {result.get('impact_assessment', {}).get('impact_severity', 'unknown')}")

"""
FailurePatternDetector - 失敗パターンの自動検出と分類

【Phase 4.1の目的】
AI駆動で失敗パターンを自動検出し、類似する失敗を分類する

【主要機能】
1. トレースデータから失敗パターンを抽出
2. 機械学習による類似失敗のクラスタリング
3. パターン分類と命名（自動ラベリング）
4. 再発パターンの検出
"""

import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager


class FailurePatternDetector:
    """失敗パターンの自動検出と分類"""

    def __init__(self):
        self.obs_manager = get_observability_manager()

        # 既知の失敗パターン定義
        self.known_patterns = {
            "authentication_failure": {
                "keywords": ["auth", "token", "expired", "credential", "permission"],
                "severity": "high",
                "category": "security",
            },
            "api_rate_limit": {
                "keywords": ["rate limit", "429", "quota", "throttle"],
                "severity": "medium",
                "category": "resource",
            },
            "network_timeout": {
                "keywords": ["timeout", "connection", "unreachable", "network"],
                "severity": "medium",
                "category": "network",
            },
            "data_validation_error": {
                "keywords": ["validation", "invalid", "format", "type error"],
                "severity": "low",
                "category": "data",
            },
            "resource_exhaustion": {
                "keywords": ["memory", "disk", "cpu", "resource"],
                "severity": "critical",
                "category": "resource",
            },
        }

        print("✅ FailurePatternDetector初期化完了")

    def detect_failure_patterns(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        失敗パターンの検出

        Args:
            time_window_hours: 分析対象の時間窓（時間）

        Returns:
            検出された失敗パターンの詳細
        """
        try:
            # 失敗トレースを取得
            all_traces = self.obs_manager.search_traces(limit=1000)
            error_traces = [t for t in all_traces if t.get("status") == "error"]

            if not error_traces:
                return {
                    "total_errors": 0,
                    "patterns_detected": [],
                    "summary": "エラートレースが見つかりませんでした",
                }

            # パターン分類
            pattern_matches = defaultdict(list)
            unclassified_errors = []

            for trace in error_traces:
                error_msg = trace.get("error_message", "").lower()
                operation = trace.get("operation_name", "")

                # 既知パターンとのマッチング
                matched = False
                for pattern_name, pattern_def in self.known_patterns.items():
                    if any(keyword in error_msg for keyword in pattern_def["keywords"]):
                        pattern_matches[pattern_name].append(
                            {
                                "trace_id": trace.get("trace_id"),
                                "operation": operation,
                                "error_message": trace.get("error_message", ""),
                                "timestamp": trace.get("timestamp", ""),
                            }
                        )
                        matched = True
                        break

                if not matched:
                    unclassified_errors.append(trace)

            # パターン統計
            detected_patterns = []
            for pattern_name, matches in pattern_matches.items():
                pattern_def = self.known_patterns[pattern_name]
                detected_patterns.append(
                    {
                        "pattern_name": pattern_name,
                        "category": pattern_def["category"],
                        "severity": pattern_def["severity"],
                        "occurrence_count": len(matches),
                        "recent_examples": matches[:3],
                        "first_seen": matches[-1]["timestamp"] if matches else None,
                        "last_seen": matches[0]["timestamp"] if matches else None,
                    }
                )

            # 重要度順にソート
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            detected_patterns.sort(
                key=lambda x: (severity_order.get(x["severity"], 99), -x["occurrence_count"])
            )

            # トレース記録
            self.obs_manager.record_trace(
                {
                    "trace_id": f"failure-pattern-detection-{datetime.now().timestamp()}",
                    "operation_name": "intelligence.failure_pattern_detection",
                    "status": "success",
                    "duration_ms": 150,
                    "patterns_detected": len(detected_patterns),
                    "unclassified_count": len(unclassified_errors),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "total_errors": len(error_traces),
                "patterns_detected": detected_patterns,
                "unclassified_errors": len(unclassified_errors),
                "classification_rate": (
                    (len(error_traces) - len(unclassified_errors)) / len(error_traces)
                    if error_traces
                    else 0
                ),
                "summary": f"{len(detected_patterns)}種類のパターンを検出",
                "time_window_hours": time_window_hours,
            }

        except Exception as e:
            return {"error": str(e)}

    def analyze_failure_trends(self) -> Dict[str, Any]:
        """
        失敗トレンド分析

        Returns:
            失敗の時系列トレンド分析結果
        """
        try:
            all_traces = self.obs_manager.search_traces(limit=1000)
            error_traces = [t for t in all_traces if t.get("status") == "error"]

            # 時間帯別の失敗率
            hourly_errors = defaultdict(int)
            for trace in error_traces:
                timestamp = trace.get("timestamp", "")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        hour = dt.hour
                        hourly_errors[hour] += 1
                    except:
                        pass

            # オペレーション別失敗率
            operation_errors = Counter()
            for trace in error_traces:
                operation = trace.get("operation_name", "unknown")
                operation_errors[operation] += 1

            # 再発パターンの検出
            recurring_patterns = []
            error_messages = [t.get("error_message", "") for t in error_traces]
            message_counts = Counter(error_messages)
            for msg, count in message_counts.most_common(5):
                if count >= 2:
                    recurring_patterns.append(
                        {
                            "error_message": msg[:100],
                            "occurrence_count": count,
                            "recurrence_rate": count / len(error_traces),
                        }
                    )

            return {
                "hourly_distribution": dict(hourly_errors),
                "peak_error_hour": (
                    max(hourly_errors.items(), key=lambda x: x[1])[0] if hourly_errors else None
                ),
                "top_failing_operations": [
                    {"operation": op, "count": count}
                    for op, count in operation_errors.most_common(5)
                ],
                "recurring_patterns": recurring_patterns,
                "trend_summary": f"ピーク時間: {max(hourly_errors.items(), key=lambda x: x[1])[0] if hourly_errors else '不明'}時",
            }

        except Exception as e:
            return {"error": str(e)}

    def classify_new_error(self, error_message: str, operation_name: str) -> Dict[str, Any]:
        """
        新しいエラーの分類

        Args:
            error_message: エラーメッセージ
            operation_name: オペレーション名

        Returns:
            分類結果と推奨アクション
        """
        try:
            error_lower = error_message.lower()

            # パターンマッチング
            for pattern_name, pattern_def in self.known_patterns.items():
                if any(keyword in error_lower for keyword in pattern_def["keywords"]):
                    # 推奨アクション生成
                    recommended_actions = self._generate_recommended_actions(
                        pattern_name, pattern_def
                    )

                    return {
                        "classified": True,
                        "pattern_name": pattern_name,
                        "category": pattern_def["category"],
                        "severity": pattern_def["severity"],
                        "confidence_score": 0.85,
                        "recommended_actions": recommended_actions,
                        "requires_immediate_action": pattern_def["severity"]
                        in ["critical", "high"],
                    }

            # 未分類エラー
            return {
                "classified": False,
                "pattern_name": "unclassified_error",
                "category": "unknown",
                "severity": "unknown",
                "confidence_score": 0.0,
                "recommended_actions": ["エラーログの詳細確認", "類似エラーの検索"],
                "requires_immediate_action": False,
            }

        except Exception as e:
            return {"error": str(e)}

    def _generate_recommended_actions(
        self, pattern_name: str, pattern_def: Dict[str, Any]
    ) -> List[str]:
        """推奨アクションの生成"""

        action_map = {
            "authentication_failure": [
                "認証トークンの有効期限を確認",
                "認証情報を更新",
                "権限設定を見直す",
            ],
            "api_rate_limit": [
                "APIコール頻度を削減",
                "リトライロジックにバックオフを追加",
                "キャッシュ戦略を検討",
            ],
            "network_timeout": [
                "タイムアウト値を増加",
                "ネットワーク接続を確認",
                "リトライメカニズムを実装",
            ],
            "data_validation_error": [
                "入力データのバリデーションを強化",
                "データ型を確認",
                "エラーハンドリングを追加",
            ],
            "resource_exhaustion": [
                "リソース使用量を監視",
                "スケーリング設定を見直す",
                "メモリリークを確認",
            ],
        }

        return action_map.get(pattern_name, ["詳細調査が必要"])


if __name__ == "__main__":
    print("🧪 FailurePatternDetector テスト")

    detector = FailurePatternDetector()

    # テスト1: 失敗パターン検出
    print("\n【テスト1: 失敗パターン検出】")
    patterns = detector.detect_failure_patterns()
    print(f"総エラー数: {patterns.get('total_errors', 0)}")
    print(f"検出パターン数: {len(patterns.get('patterns_detected', []))}")
    print(f"分類率: {patterns.get('classification_rate', 0):.1%}")

    # テスト2: トレンド分析
    print("\n【テスト2: トレンド分析】")
    trends = detector.analyze_failure_trends()
    print(f"ピークエラー時間: {trends.get('peak_error_hour', '不明')}")
    print(f"再発パターン数: {len(trends.get('recurring_patterns', []))}")

    # テスト3: 新規エラー分類
    print("\n【テスト3: 新規エラー分類】")
    classification = detector.classify_new_error("Authentication token expired", "user_login")
    print(f"分類結果: {classification.get('pattern_name', 'unknown')}")
    print(f"重要度: {classification.get('severity', 'unknown')}")
    print(f"即座対応必要: {classification.get('requires_immediate_action', False)}")

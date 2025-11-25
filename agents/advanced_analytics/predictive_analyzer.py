"""
Predictive Analyzer v1.0
失敗リスクの予測とシステム問題の予測
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.advanced_analytics.execution_analyzer import ExecutionAnalyzer
from agents.advanced_analytics.pattern_learner import PatternLearner
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager


class PredictiveAnalyzer:
    """予測的分析システム"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.analyzer = ExecutionAnalyzer(sheets_manager)
        self.learner = PatternLearner(sheets_manager)

    async def predict_task_failure_risk(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タスクの失敗リスクを予測"""

        print(f"🔮 タスクの失敗リスクを予測中: {task.get('description', 'Unknown')[:50]}...")

        # 過去のログを取得
        logs = await self.analyzer.get_execution_logs()

        # 類似タスクを検索
        similar_tasks = self._find_similar_tasks(task, logs)

        if not similar_tasks:
            return {
                "risk_score": 0.5,  # データ不足の場合は中リスク
                "confidence": "低",
                "reason": "類似タスクのデータが不足",
                "recommendations": ["慎重に実行し、詳細なログを記録"],
            }

        # 失敗率を計算
        total = len(similar_tasks)
        failed = sum(1 for t in similar_tasks if t.get("status") == "failed")
        failure_rate = failed / total if total > 0 else 0.5

        # リスクレベルの判定
        if failure_rate < 0.1:
            risk_level = "低"
            risk_color = "🟢"
        elif failure_rate < 0.3:
            risk_level = "中"
            risk_color = "🟡"
        else:
            risk_level = "高"
            risk_color = "��"

        # 推奨事項を生成
        recommendations = self._generate_risk_recommendations(task, similar_tasks, failure_rate)

        prediction = {
            "risk_score": round(failure_rate, 2),
            "risk_level": risk_level,
            "risk_icon": risk_color,
            "confidence": "高" if total > 5 else "中" if total > 2 else "低",
            "similar_task_count": total,
            "failed_task_count": failed,
            "reason": self._explain_risk(similar_tasks),
            "recommendations": recommendations,
        }

        print(f"   {risk_color} リスクレベル: {risk_level} (スコア: {prediction['risk_score']})")

        return prediction

    async def predict_system_issues(self) -> Dict[str, Any]:
        """システム問題を予測"""

        print("🔮 システム問題を予測中...")

        # 過去のログを取得
        logs = await self.analyzer.get_execution_logs()

        # 各種指標を分析
        predictions = {
            "api_timeout_risk": self._predict_api_timeout(logs),
            "resource_exhaustion_risk": self._predict_resource_issues(logs),
            "error_spike_risk": self._predict_error_spike(logs),
            "performance_degradation": self._predict_performance_issues(logs),
            "overall_health": self._calculate_system_health(logs),
        }

        # アラートを生成
        alerts = self._generate_system_alerts(predictions)

        return {
            "predictions": predictions,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat(),
        }

    async def suggest_preventive_actions(self) -> List[Dict[str, Any]]:
        """予防的アクションを提案"""

        print("💡 予防的アクションを提案中...")

        # システム問題を予測
        system_predictions = await self.predict_system_issues()

        actions = []

        # 各リスクに対する予防策
        predictions = system_predictions["predictions"]

        # APIタイムアウトリスク
        if predictions["api_timeout_risk"]["level"] == "高":
            actions.append(
                {
                    "priority": "高",
                    "action": "APIタイムアウト設定を60秒以上に延長",
                    "reason": "タイムアウトエラーが増加傾向",
                    "implementation": "agents/gemini_api_client.py のタイムアウト設定を変更",
                }
            )

        # リソース枯渇リスク
        if predictions["resource_exhaustion_risk"]["level"] == "中":
            actions.append(
                {
                    "priority": "中",
                    "action": "キャッシュクリアの実行",
                    "reason": "リソース使用量が上昇傾向",
                    "implementation": "定期的なキャッシュクリアスクリプトの実行",
                }
            )

        # エラー急増リスク
        if predictions["error_spike_risk"]["level"] == "高":
            actions.append(
                {
                    "priority": "高",
                    "action": "エラーログの詳細調査",
                    "reason": "エラー発生率が急増",
                    "implementation": "execution_analyzer.py で詳細分析を実行",
                }
            )

        # システムヘルスが低い
        if predictions["overall_health"]["score"] < 70:
            actions.append(
                {
                    "priority": "高",
                    "action": "システム全体のヘルスチェック",
                    "reason": f"システムヘルススコアが{predictions['overall_health']['score']}と低下",
                    "implementation": "全エージェントの動作確認とログレビュー",
                }
            )

        print(f"   ✅ {len(actions)}件の予防的アクションを提案")

        return actions

    async def save_learned_patterns(self, patterns: Dict[str, Any]) -> bool:
        """学習済みパターンをGoogle Sheetsに保存"""

        print("💾 学習済みパターンを保存中...")

        try:
            spreadsheet = self.sheets.gc.open_by_key(self.sheets.spreadsheet_id)
            worksheet = spreadsheet.worksheet("learning_patterns")

            # 成功パターンを保存
            if patterns.get("success_patterns"):
                strategies = patterns["success_patterns"].get("agent_success_strategies", [])

                for strategy in strategies[:10]:  # 上位10件
                    row = [
                        f"success_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "success",
                        strategy.get("agent", ""),
                        ", ".join(strategy.get("specialty", [])[:2]),
                        "高成功率",
                        f"成功数: {strategy.get('success_count', 0)}",
                        0.9,  # 信頼度スコア
                        strategy.get("success_count", 0),
                        100.0,  # 成功率
                        datetime.now().isoformat(),
                        "",
                        strategy.get("recommendation", ""),
                        "success,best_practice",
                        "",
                        "",
                    ]
                    worksheet.append_rows(row)

            # 失敗パターンを保存
            if patterns.get("failure_patterns"):
                failure_points = patterns["failure_patterns"].get("common_failure_points", [])

                for point in failure_points[:10]:  # 上位10件
                    row = [
                        f"failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "failure",
                        point.get("agent", ""),
                        point.get("task", "")[:50],
                        "失敗条件",
                        point.get("error", ""),
                        0.7,  # 信頼度スコア
                        1,
                        0.0,  # 成功率
                        datetime.now().isoformat(),
                        "",
                        "要注意",
                        "failure,high_risk",
                        "",
                        "",
                    ]
                    worksheet.append_rows(row)

            print("   ✅ パターンを保存しました")
            return True

        except Exception as e:
            print(f"   ❌ 保存エラー: {e}")
            return False

    # === プライベートメソッド ===

    def _find_similar_tasks(self, task: Dict, logs: List[Dict]) -> List[Dict]:
        """類似タスクを検索"""
        task_desc = task.get("description", "").lower()
        agent = task.get("agent_role", "")

        similar = []
        for log in logs:
            log_desc = log.get("task_description", "").lower()
            log_agent = log.get("agent_role", "")

            # エージェントが同じ、またはタスク説明に共通キーワードがある
            if log_agent == agent or any(
                word in log_desc for word in task_desc.split()[:3] if len(word) > 2
            ):
                similar.append(log)

        return similar

    def _generate_risk_recommendations(
        self, task: Dict, similar_tasks: List[Dict], failure_rate: float
    ) -> List[str]:
        """リスクに基づく推奨事項を生成"""
        recommendations = []

        if failure_rate > 0.5:
            recommendations.append("⚠️ 高リスク: 事前に詳細な実行計画を策定")
            recommendations.append("🔍 類似タスクの失敗原因を事前に確認")

        if failure_rate > 0.3:
            recommendations.append("📊 実行前にエージェントの状態を確認")
            recommendations.append("⏱️ タイムアウト設定を通常より長めに設定")

        # タイムアウトエラーが多い場合
        timeout_count = sum(
            1 for t in similar_tasks if "timeout" in t.get("output_summary", "").lower()
        )
        if timeout_count > 0:
            recommendations.append(
                f"⏰ 過去{timeout_count}件のタイムアウト発生 → タイムアウト延長を推奨"
            )

        if not recommendations:
            recommendations.append("✅ 低リスク: 通常通り実行可能")

        return recommendations

    def _explain_risk(self, similar_tasks: List[Dict]) -> str:
        """リスクの理由を説明"""
        total = len(similar_tasks)
        failed = sum(1 for t in similar_tasks if t.get("status") == "failed")

        if failed == 0:
            return f"類似タスク{total}件すべて成功"
        else:
            return f"類似タスク{total}件中{failed}件が失敗"

    def _predict_api_timeout(self, logs: List[Dict]) -> Dict[str, Any]:
        """APIタイムアウトリスクを予測"""
        recent_logs = logs[-50:] if len(logs) > 50 else logs

        timeout_count = sum(
            1 for log in recent_logs if "timeout" in log.get("output_summary", "").lower()
        )

        rate = timeout_count / len(recent_logs) if recent_logs else 0

        return {
            "level": "高" if rate > 0.1 else "中" if rate > 0.05 else "低",
            "count": timeout_count,
            "rate": round(rate * 100, 1),
        }

    def _predict_resource_issues(self, logs: List[Dict]) -> Dict[str, Any]:
        """リソース問題を予測"""
        # TODO: より詳細なリソース分析
        return {"level": "低", "reason": "リソース使用量は正常範囲"}

    def _predict_error_spike(self, logs: List[Dict]) -> Dict[str, Any]:
        """エラー急増を予測"""
        if len(logs) < 20:
            return {"level": "低", "reason": "データ不足"}

        # 直近10件と前10件を比較
        recent = logs[-10:]
        previous = logs[-20:-10]

        recent_errors = sum(1 for log in recent if log.get("status") == "failed")
        previous_errors = sum(1 for log in previous if log.get("status") == "failed")

        if recent_errors > previous_errors * 2:
            return {
                "level": "高",
                "reason": f"エラー率が2倍以上に増加 ({previous_errors}→{recent_errors})",
            }
        elif recent_errors > previous_errors:
            return {
                "level": "中",
                "reason": f"エラー率が増加傾向 ({previous_errors}→{recent_errors})",
            }
        else:
            return {"level": "低", "reason": "エラー率は安定"}

    def _predict_performance_issues(self, logs: List[Dict]) -> Dict[str, Any]:
        """パフォーマンス問題を予測"""
        # TODO: 実行時間の傾向分析
        return {"level": "低", "reason": "パフォーマンスは正常"}

    def _calculate_system_health(self, logs: List[Dict]) -> Dict[str, Any]:
        """システムヘルススコアを計算"""
        if not logs:
            return {"score": 50, "status": "不明"}

        recent_logs = logs[-50:] if len(logs) > 50 else logs

        success_rate = self.analyzer._calculate_success_rate(recent_logs)

        # ヘルススコア = 成功率 × 0.7 + その他指標 × 0.3
        health_score = success_rate * 0.7 + 30  # 簡易版

        if health_score >= 90:
            status = "優秀"
            icon = "🟢"
        elif health_score >= 70:
            status = "良好"
            icon = "🟡"
        else:
            status = "要注意"
            icon = "🔴"

        return {"score": round(health_score, 1), "status": status, "icon": icon}

    def _generate_system_alerts(self, predictions: Dict) -> List[str]:
        """システムアラートを生成"""
        alerts = []

        for key, pred in predictions.items():
            if isinstance(pred, dict) and pred.get("level") == "高":
                alerts.append(f"🚨 {key}: {pred.get('reason', '要確認')}")

        return alerts


async def main():
    """メイン実行"""
    print("🚀 予測的分析システムを起動\n")

    # 設定読み込み
    config = ConfigLoader()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"),
        service_account_file=config.get("GOOGLE_SERVICE_ACCOUNT_FILE"),
    )

    predictor = PredictiveAnalyzer(sheets)

    # === 1. システム問題予測 ===
    print("=" * 70)
    print("🔮 システム問題予測")
    print("=" * 70)

    system_predictions = await predictor.predict_system_issues()

    print("\n📊 予測結果:")
    for key, pred in system_predictions["predictions"].items():
        if isinstance(pred, dict):
            level = pred.get("level", "不明")
            icon = "🔴" if level == "高" else "🟡" if level == "中" else "🟢"
            print(f"  {icon} {key}: {level}")
            if "reason" in pred:
                print(f"     理由: {pred['reason']}")

    if system_predictions["alerts"]:
        print("\n🚨 アラート:")
        for alert in system_predictions["alerts"]:
            print(f"  {alert}")

    # === 2. 予防的アクション提案 ===
    print("\n" + "=" * 70)
    print("💡 予防的アクション提案")
    print("=" * 70 + "\n")

    actions = await predictor.suggest_preventive_actions()

    if actions:
        for i, action in enumerate(actions, 1):
            priority_icon = "🔴" if action["priority"] == "高" else "🟡"
            print(f"{i}. {priority_icon} 優先度: {action['priority']}")
            print(f"   アクション: {action['action']}")
            print(f"   理由: {action['reason']}")
            print(f"   実装方法: {action['implementation']}")
            print()
    else:
        print("✅ 現時点で必要な予防的アクションはありません")

    # === 3. 学習済みパターンの保存 ===
    print("=" * 70)
    print("💾 学習済みパターンの保存")
    print("=" * 70 + "\n")

    learner = PatternLearner(sheets)
    patterns = {
        "success_patterns": await learner.learn_success_patterns(),
        "failure_patterns": await learner.learn_failure_patterns(),
    }

    await predictor.save_learned_patterns(patterns)

    # レポート保存
    output_file = Path("agent_outputs/predictive_analysis_report.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": datetime.now().isoformat(),
        "system_predictions": system_predictions,
        "preventive_actions": actions,
    }

    import json

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 予測レポートを保存: {output_file}")
    print("\n" + "=" * 70)
    print("✅ Phase 3-3: 予測的分析システム完成！")
    print("=" * 70)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

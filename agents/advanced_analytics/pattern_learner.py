"""
Pattern Learner v1.0
成功パターンと失敗パターンの学習
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader
from agents.advanced_analytics.execution_analyzer import ExecutionAnalyzer


class PatternLearner:
    """成功パターンと失敗パターンの学習"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.analyzer = ExecutionAnalyzer(sheets_manager)

    async def learn_success_patterns(self) -> Dict[str, Any]:
        """成功パターンの学習"""
        print("📚 成功パターンを学習中...")

        # 実行ログを取得
        logs = await self.analyzer.get_execution_logs()

        # 成功したタスクのみ抽出
        success_logs = [log for log in logs if log.get("status") == "completed"]

        if not success_logs:
            print("⚠️ 成功したタスクが見つかりません")
            return {}

        print(f"✅ {len(success_logs)}件の成功タスクを分析")

        patterns = {
            "agent_success_strategies": self._learn_agent_strategies(success_logs),
            "optimal_task_sequences": self._learn_task_sequences(success_logs),
            "effective_parameters": self._learn_effective_parameters(success_logs),
            "best_practices": self._generate_best_practices(success_logs),
        }

        return patterns

    async def learn_failure_patterns(self) -> Dict[str, Any]:
        """失敗パターンの学習"""
        print("📚 失敗パターンを学習中...")

        # 実行ログを取得
        logs = await self.analyzer.get_execution_logs()

        # 失敗したタスクのみ抽出
        failed_logs = [log for log in logs if log.get("status") == "failed"]

        if not failed_logs:
            print("✅ 失敗したタスクがありません（素晴らしい！）")
            return {}

        print(f"⚠️ {len(failed_logs)}件の失敗タスクを分析")

        patterns = {
            "common_failure_points": self._identify_failure_points(failed_logs),
            "error_precursors": self._identify_error_precursors(logs, failed_logs),
            "avoidance_strategies": self._generate_avoidance_strategies(failed_logs),
            "recovery_methods": self._learn_recovery_methods(logs, failed_logs),
        }

        return patterns

    def _learn_agent_strategies(self, success_logs: List[Dict]) -> List[Dict]:
        """エージェント別の成功戦略を学習"""
        agent_strategies = defaultdict(lambda: {"total_success": 0, "common_tasks": [], "typical_duration": []})

        for log in success_logs:
            agent = log.get("agent_role", "Unknown")
            task_desc = log.get("task_description", "")

            agent_strategies[agent]["total_success"] += 1
            agent_strategies[agent]["common_tasks"].append(task_desc)

        # 各エージェントの得意分野を抽出
        strategies = []
        for agent, data in agent_strategies.items():
            # よく実行するタスクのキーワードを抽出
            task_keywords = self._extract_keywords(data["common_tasks"])

            strategies.append(
                {
                    "agent": agent,
                    "success_count": data["total_success"],
                    "specialty": task_keywords[:3],  # 上位3つのキーワード
                    "recommendation": f"{agent}は{', '.join(task_keywords[:2])}に最適",
                }
            )

        return sorted(strategies, key=lambda x: x["success_count"], reverse=True)

    def _learn_task_sequences(self, success_logs: List[Dict]) -> List[Dict]:
        """最適なタスク実行順序を学習"""
        # TODO: タスクの実行順序を分析
        return []

    def _learn_effective_parameters(self, success_logs: List[Dict]) -> Dict[str, Any]:
        """効果的なパラメータを学習"""
        # TODO: 成功したタスクのパラメータを分析
        return {}

    def _generate_best_practices(self, success_logs: List[Dict]) -> List[str]:
        """ベストプラクティスの生成"""
        practices = []

        # エージェント使用に関する推奨
        agent_perf = self.analyzer._analyze_agent_performance(success_logs)
        if agent_perf:
            best_agents = [a for a in agent_perf if a["success_rate"] == 100]
            if best_agents:
                practices.append(
                    f"✅ {', '.join([a['agent'] for a in best_agents[:3]])} エージェントは100%の成功率を維持"
                )

        # タスク量に関する推奨
        total_tasks = len(success_logs)
        if total_tasks > 100:
            practices.append("✅ 大量タスク（100+）の処理が安定して動作")

        return practices

    def _identify_failure_points(self, failed_logs: List[Dict]) -> List[Dict]:
        """失敗しやすいポイントを特定"""
        failure_points = []

        for log in failed_logs:
            failure_points.append(
                {
                    "task": log.get("task_description", "Unknown")[:50],
                    "agent": log.get("agent_role", "Unknown"),
                    "error": log.get("output_summary", "Unknown")[:50],
                    "risk_level": "高",
                }
            )

        return failure_points

    def _identify_error_precursors(self, all_logs: List[Dict], failed_logs: List[Dict]) -> List[str]:
        """エラーの前兆シグナルを特定"""
        # TODO: エラー前のパターンを分析
        return []

    def _generate_avoidance_strategies(self, failed_logs: List[Dict]) -> List[str]:
        """回避策を生成"""
        strategies = []

        # タイムアウトエラーに対する回避策
        timeout_errors = [log for log in failed_logs if "timeout" in log.get("output_summary", "").lower()]
        if timeout_errors:
            strategies.append("⚠️ タイムアウト対策: APIタイムアウト設定を60秒以上に延長を推奨")

        return strategies

    def _learn_recovery_methods(self, all_logs: List[Dict], failed_logs: List[Dict]) -> List[str]:
        """リカバリ方法を学習"""
        # TODO: 失敗後の成功パターンを分析
        return []

    def _extract_keywords(self, texts: List[str]) -> List[str]:
        """テキストからキーワードを抽出"""
        # 簡易的なキーワード抽出
        word_counts = defaultdict(int)

        # ストップワード
        stop_words = {"を", "の", "は", "に", "で", "と", "が", "する", "作成", "実行"}

        for text in texts:
            words = text.split()
            for word in words:
                if len(word) > 1 and word not in stop_words:
                    word_counts[word] += 1

        # 頻度順にソート
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

        return [word for word, count in sorted_words[:10]]

    async def generate_learning_report(self) -> Dict[str, Any]:
        """学習レポートの生成"""
        print("\n" + "=" * 70)
        print("🎓 パターン学習レポート")
        print("=" * 70)

        # 成功パターンを学習
        success_patterns = await self.learn_success_patterns()

        # 失敗パターンを学習
        failure_patterns = await self.learn_failure_patterns()

        report = {
            "timestamp": datetime.now().isoformat(),
            "success_patterns": success_patterns,
            "failure_patterns": failure_patterns,
            "recommendations": self._generate_recommendations(success_patterns, failure_patterns),
        }

        # レポート表示
        self._print_learning_report(report)

        return report

    def _generate_recommendations(self, success_patterns: Dict, failure_patterns: Dict) -> List[str]:
        """推奨事項の生成"""
        recommendations = []

        # 成功パターンに基づく推奨
        if success_patterns.get("agent_success_strategies"):
            strategies = success_patterns["agent_success_strategies"]
            if strategies:
                top_agent = strategies[0]
                recommendations.append(f"💡 {top_agent['agent']}エージェントを優先的に使用することを推奨")

        # 失敗パターンに基づく推奨
        if failure_patterns.get("avoidance_strategies"):
            recommendations.extend(failure_patterns["avoidance_strategies"])

        return recommendations

    def _print_learning_report(self, report: Dict):
        """学習レポートを表示"""
        print("\n📊 成功パターン:")

        strategies = report["success_patterns"].get("agent_success_strategies", [])
        for strategy in strategies[:5]:
            print(f"  🤖 {strategy['agent']}")
            print(f"     成功数: {strategy['success_count']}")
            print(f"     得意分野: {', '.join(strategy['specialty'][:2])}")
            print(f"     推奨: {strategy['recommendation']}")

        best_practices = report["success_patterns"].get("best_practices", [])
        if best_practices:
            print("\n✅ ベストプラクティス:")
            for practice in best_practices:
                print(f"  {practice}")

        print("\n⚠️ 失敗パターン:")
        failure_points = report["failure_patterns"].get("common_failure_points", [])
        if failure_points:
            for point in failure_points[:5]:
                print(f"  ❌ {point['task']}")
                print(f"     エージェント: {point['agent']}")
                print(f"     エラー: {point['error']}")
        else:
            print("  なし（素晴らしい！）")

        print("\n💡 推奨事項:")
        for rec in report["recommendations"]:
            print(f"  {rec}")

        print("\n" + "=" * 70)


async def main():
    """メイン実行"""
    print("🚀 パターン学習システムを起動\n")

    # 設定読み込み
    config = ConfigLoader()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"), service_account_file=config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )

    # パターン学習実行
    learner = PatternLearner(sheets)
    report = await learner.generate_learning_report()

    # レポート保存
    output_file = Path("agent_outputs/pattern_learning_report.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    import json

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 学習レポートを保存: {output_file}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

"""
Execution Analyzer v1.3
実行データの高度な分析（初期化修正版）
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader


class ExecutionAnalyzer:
    """実行データの高度な分析"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager

    async def get_execution_logs(self) -> List[Dict]:
        """task_execution_logからデータを取得"""
        try:
            # GoogleSheetsManagerのクライアントを確保
            self.sheets._ensure_client()

            # スプレッドシートを開く
            spreadsheet = self.sheets.gc.open_by_key(self.sheets.spreadsheet_id)

            # task_execution_logシートを取得
            try:
                worksheet = spreadsheet.worksheet("task_execution_log")
            except Exception as e:
                print(f"⚠️ task_execution_logシートが見つかりません: {e}")
                return []

            # 全データを取得
            all_values = worksheet.get_all_records()

            print(f"✅ {len(all_values)}件のログを取得")

            return all_values

        except Exception as e:
            print(f"❌ ログ取得エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    async def analyze_execution_patterns(self, days: int = 30) -> Dict[str, Any]:
        """実行パターンの分析"""

        print(f"📊 過去{days}日間の実行データを分析中...")

        # task_execution_logから全データ取得
        logs = await self.get_execution_logs()

        if not logs:
            print("⚠️ 実行ログが見つかりません")
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "common_errors": [],
                "agent_performance": [],
                "bottlenecks": [],
                "insights": [],
            }

        # 分析結果
        analysis = {
            "total_executions": len(logs),
            "success_rate": self._calculate_success_rate(logs),
            "average_execution_time": self._calculate_avg_time(logs),
            "common_errors": self._identify_common_errors(logs),
            "agent_performance": self._analyze_agent_performance(logs),
            "bottlenecks": self._identify_bottlenecks(logs),
            "insights": self._generate_insights(logs),
        }

        return analysis

    def _calculate_success_rate(self, logs: List[Dict]) -> float:
        """成功率の計算"""
        if not logs:
            return 0.0

        completed = sum(1 for log in logs if log.get("status") == "completed")
        return (completed / len(logs)) * 100

    def _calculate_avg_time(self, logs: List[Dict]) -> float:
        """平均実行時間の計算"""
        # TODO: タイムスタンプから計算
        return 0.0

    def _identify_common_errors(self, logs: List[Dict]) -> List[Dict]:
        """よくあるエラーの特定"""
        error_counts = Counter()

        failed_logs = [log for log in logs if log.get("status") == "failed"]

        for log in failed_logs:
            error_summary = log.get("output_summary", "Unknown Error")
            # エラーの最初の50文字を使用
            error_key = error_summary[:50] if error_summary else "Unknown"
            error_counts[error_key] += 1

        if not failed_logs:
            return []

        # 頻度順にソート
        return [
            {"error_type": error, "count": count, "percentage": round((count / len(failed_logs) * 100), 1)}
            for error, count in error_counts.most_common(10)
        ]

    def _analyze_agent_performance(self, logs: List[Dict]) -> List[Dict]:
        """エージェント別のパフォーマンス分析"""
        agent_stats = {}

        for log in logs:
            agent = log.get("agent_role", "Unknown")

            if agent not in agent_stats:
                agent_stats[agent] = {"total": 0, "completed": 0, "failed": 0}

            agent_stats[agent]["total"] += 1

            status = log.get("status")
            if status == "completed":
                agent_stats[agent]["completed"] += 1
            elif status == "failed":
                agent_stats[agent]["failed"] += 1

        # 成功率を計算
        result = []
        for agent, stats in agent_stats.items():
            success_rate = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            result.append(
                {
                    "agent": agent,
                    "total_tasks": stats["total"],
                    "success_rate": round(success_rate, 1),
                    "completed": stats["completed"],
                    "failed": stats["failed"],
                }
            )

        # 成功率でソート
        result.sort(key=lambda x: x["success_rate"], reverse=True)

        return result

    def _identify_bottlenecks(self, logs: List[Dict]) -> List[Dict]:
        """ボトルネックの特定"""
        # タスクの説明から頻繁に失敗するタスクタイプを特定
        failed_tasks = [log for log in logs if log.get("status") == "failed"]

        if not failed_tasks:
            return []

        task_types = Counter()
        for log in failed_tasks:
            task_desc = log.get("task_description", "Unknown")
            # タスクタイプを抽出（最初の単語など）
            task_type = task_desc.split()[0] if task_desc else "Unknown"
            task_types[task_type] += 1

        return [
            {
                "task_type": task_type,
                "failure_count": count,
                "risk_level": "高" if count > 5 else "中" if count > 2 else "低",
            }
            for task_type, count in task_types.most_common(5)
        ]

    def _generate_insights(self, logs: List[Dict]) -> List[str]:
        """洞察の生成"""
        insights = []

        # 成功率に基づく洞察
        success_rate = self._calculate_success_rate(logs)
        if success_rate >= 90:
            insights.append("✅ システムは非常に安定しています（成功率90%以上）")
        elif success_rate >= 70:
            insights.append("⚠️ システムは概ね安定していますが改善の余地があります")
        else:
            insights.append("🔴 システムの安定性に問題があります（成功率70%未満）")

        # エラーに基づく洞察
        errors = self._identify_common_errors(logs)
        if errors:
            top_error = errors[0]
            insights.append(f"📊 最も頻繁なエラー: {top_error['error_type'][:30]}... ({top_error['count']}回)")

        # エージェントパフォーマンスに基づく洞察
        agent_perf = self._analyze_agent_performance(logs)
        if agent_perf:
            best_agent = agent_perf[0]
            if len(agent_perf) > 1:
                worst_agent = agent_perf[-1]
                insights.append(f"🏆 最高パフォーマンス: {best_agent['agent']} ({best_agent['success_rate']:.1f}%)")
                if worst_agent["success_rate"] < 50:
                    insights.append(f"⚠️ 改善が必要: {worst_agent['agent']} ({worst_agent['success_rate']:.1f}%)")
            else:
                insights.append(f"🏆 パフォーマンス: {best_agent['agent']} ({best_agent['success_rate']:.1f}%)")

        return insights

    def print_analysis_report(self, analysis: Dict[str, Any]):
        """分析レポートを見やすく表示"""
        print("\n" + "=" * 70)
        print("📊 実行データ分析レポート")
        print("=" * 70)

        print(f"\n📈 総合統計:")
        print(f"  総実行数: {analysis['total_executions']}件")
        print(f"  成功率: {analysis['success_rate']:.1f}%")
        print(f"  平均実行時間: {analysis['average_execution_time']:.1f}秒")

        if analysis["common_errors"]:
            print(f"\n🔍 よくあるエラー:")
            for i, error in enumerate(analysis["common_errors"][:5], 1):
                print(f"  {i}. {error['error_type'][:50]}")
                print(f"     発生回数: {error['count']}回 ({error['percentage']:.1f}%)")
        else:
            print(f"\n🔍 よくあるエラー: なし（全て成功）")

        if analysis["agent_performance"]:
            print(f"\n🤖 エージェント別パフォーマンス:")
            for agent in analysis["agent_performance"][:5]:
                icon = "✅" if agent["success_rate"] >= 80 else "⚠️" if agent["success_rate"] >= 50 else "❌"
                print(f"  {icon} {agent['agent']}")
                print(f"     タスク数: {agent['total_tasks']}, 成功率: {agent['success_rate']:.1f}%")

        if analysis["bottlenecks"]:
            print(f"\n🎯 ボトルネック:")
            for bottleneck in analysis["bottlenecks"][:5]:
                print(
                    f"  - {bottleneck['task_type']}: {bottleneck['failure_count']}回失敗 (リスク: {bottleneck['risk_level']})"
                )

        print(f"\n💡 洞察:")
        for insight in analysis["insights"]:
            print(f"  {insight}")

        print("\n" + "=" * 70)


# テスト実行
async def main():
    print("🚀 実行データ分析を開始します\n")

    # ConfigLoaderから設定を読み込み
    config = ConfigLoader()

    # 正しい初期化方法
    spreadsheet_id = config.get("SPREADSHEET_ID")
    service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")

    print(f"📋 設定確認:")
    print(f"  SPREADSHEET_ID: {spreadsheet_id}")
    print(f"  SERVICE_ACCOUNT_FILE: {service_account_file}")
    print()

    # GoogleSheetsManagerを正しく初期化
    sheets = GoogleSheetsManager(spreadsheet_id=spreadsheet_id, service_account_file=service_account_file)

    analyzer = ExecutionAnalyzer(sheets)
    analysis = await analyzer.analyze_execution_patterns(days=30)

    # レポート表示
    analyzer.print_analysis_report(analysis)

    # 結果をJSONで保存
    output_file = Path("agent_outputs/execution_analysis_report.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    import json

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(f"\n💾 詳細レポートを保存: {output_file}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

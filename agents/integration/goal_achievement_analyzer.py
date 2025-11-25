#!/usr/bin/env python3
"""
ゴール達成状況分析エージェント

**機能**:
- project_goalの目標とtask_execution_logの実行結果を比較
- 目標達成に不足している要素を特定
- 実行品質の分析（低スコアタスクの検出）
- 次のアクションの推奨
"""
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager


class GoalAchievementAnalyzer:
    """ゴール達成状況を分析するエージェント"""

    def __init__(self):
        """初期化"""
        self.sheets_mgr = GoogleSheetsManager()
        self.quality_threshold_low = 60  # 60点以下は低品質
        self.quality_threshold_high = 80  # 80点以上は高品質

    def analyze_all_goals(self) -> List[Dict]:
        """
        全ゴールの達成状況を分析

        Returns:
            各ゴールの分析結果のリスト
        """
        print(f"\n{'='*80}")
        print(f"📊 ゴール達成状況分析開始")
        print(f"{'='*80}")

        try:
            # ゴール一覧を取得
            goals = self.sheets_mgr.read_project_goals()

            if not goals:
                print("⚠️ ゴールが見つかりません")
                return []

            print(f"✅ {len(goals)}個のゴールを分析します\n")

            analyses = []
            for goal in goals:
                goal_id = goal.get("goal_id")
                if goal_id:
                    analysis = self.analyze_single_goal(goal_id)
                    analyses.append(analysis)

            # サマリー表示
            self._print_overall_summary(analyses)

            return analyses

        except Exception as e:
            print(f"❌ 分析エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    def analyze_single_goal(self, goal_id: str) -> Dict:
        """
        単一ゴールの達成状況を詳細分析

        Args:
            goal_id: 分析対象のゴールID

        Returns:
            分析結果の辞書
        """
        try:
            # ゴール情報取得
            goals = self.sheets_mgr.read_project_goals()
            goal = next((g for g in goals if str(g.get("goal_id")) == str(goal_id)), None)

            if not goal:
                return {"error": f"Goal {goal_id} not found"}

            # タスク情報取得
            all_tasks = self.sheets_mgr.read_pm_tasks()
            goal_tasks = [t for t in all_tasks if str(t.get("parent_goal_id")) == str(goal_id)]

            # 実行ログ取得
            execution_logs = self.sheets_mgr.read_task_execution_logs()
            goal_logs = [
                log
                for log in execution_logs
                if any(str(log.get("task_id")) == str(t.get("task_id")) for t in goal_tasks)
            ]

            # 進捗計算
            progress = self._calculate_progress(goal_tasks)

            # 品質分析
            quality_analysis = self._analyze_quality(goal_logs)

            # 不足要素の特定
            missing_elements = self._identify_missing_elements(goal, goal_tasks, goal_logs)

            # 推奨アクション生成
            recommendations = self._generate_recommendations(
                goal, progress, quality_analysis, missing_elements
            )

            analysis = {
                "goal_id": goal_id,
                "goal_description": goal.get("goal_description", "N/A")[:100],
                "status": goal.get("status", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "progress": progress,
                "quality_analysis": quality_analysis,
                "missing_elements": missing_elements,
                "recommendations": recommendations,
                "achievement_score": self._calculate_achievement_score(progress, quality_analysis),
            }

            self._print_goal_analysis(analysis)

            return analysis

        except Exception as e:
            print(f"❌ ゴール{goal_id}の分析エラー: {e}")
            import traceback

            traceback.print_exc()
            return {"goal_id": goal_id, "error": str(e)}

    def _calculate_progress(self, tasks: List[Dict]) -> Dict:
        """進捗状況を計算"""
        if not tasks:
            return {"total": 0, "completed": 0, "in_progress": 0, "pending": 0, "percentage": 0.0}

        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
        pending = sum(1 for t in tasks if t.get("status") == "pending")

        percentage = (completed / total * 100) if total > 0 else 0

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "percentage": round(percentage, 1),
        }

    def _analyze_quality(self, execution_logs: List[Dict]) -> Dict:
        """実行品質を分析"""
        if not execution_logs:
            return {
                "avg_score": 0,
                "low_quality_count": 0,
                "high_quality_count": 0,
                "quality_distribution": {},
            }

        # スコアを抽出（文字列 "60/100" を数値に変換）
        scores = []
        for log in execution_logs:
            score_str = log.get("quality_score", "0/100")
            try:
                if isinstance(score_str, str) and "/" in score_str:
                    score = float(score_str.split("/")[0])
                    scores.append(score)
            except:
                continue

        if not scores:
            return {
                "avg_score": 0,
                "low_quality_count": 0,
                "high_quality_count": 0,
                "quality_distribution": {},
            }

        avg_score = sum(scores) / len(scores)
        low_quality = sum(1 for s in scores if s < self.quality_threshold_low)
        high_quality = sum(1 for s in scores if s >= self.quality_threshold_high)

        # 品質分布
        distribution = {
            "excellent": sum(1 for s in scores if s >= 90),
            "good": sum(1 for s in scores if 80 <= s < 90),
            "acceptable": sum(1 for s in scores if 60 <= s < 80),
            "poor": sum(1 for s in scores if s < 60),
        }

        return {
            "avg_score": round(avg_score, 1),
            "low_quality_count": low_quality,
            "high_quality_count": high_quality,
            "quality_distribution": distribution,
            "total_executions": len(scores),
        }

    def _identify_missing_elements(
        self, goal: Dict, tasks: List[Dict], logs: List[Dict]
    ) -> List[Dict]:
        """不足要素を特定"""
        missing = []

        # 1. pendingタスクの確認
        pending_tasks = [t for t in tasks if t.get("status") == "pending"]
        if pending_tasks:
            missing.append(
                {
                    "type": "pending_tasks",
                    "count": len(pending_tasks),
                    "severity": "medium",
                    "description": f"{len(pending_tasks)}個の未実行タスクが残っています",
                }
            )

        # 2. 低品質実行の確認
        low_quality_logs = []
        for log in logs:
            score_str = log.get("quality_score", "0/100")
            try:
                if isinstance(score_str, str) and "/" in score_str:
                    score = float(score_str.split("/")[0])
                    if score < self.quality_threshold_low:
                        low_quality_logs.append(log)
            except:
                continue

        if low_quality_logs:
            missing.append(
                {
                    "type": "low_quality_executions",
                    "count": len(low_quality_logs),
                    "severity": "high",
                    "description": f"{len(low_quality_logs)}個のタスクが低品質（60点未満）です",
                    "task_ids": [log.get("task_id") for log in low_quality_logs[:5]],
                }
            )

        # 3. テストタスクの有無確認
        test_tasks = [
            t
            for t in tasks
            if "test" in str(t.get("description", "")).lower()
            or "テスト" in str(t.get("description", ""))
        ]

        if not test_tasks:
            missing.append(
                {
                    "type": "missing_tests",
                    "count": 0,
                    "severity": "medium",
                    "description": "テストタスクが定義されていません",
                }
            )

        # 4. ドキュメントタスクの有無確認
        doc_tasks = [
            t
            for t in tasks
            if "document" in str(t.get("description", "")).lower()
            or "ドキュメント" in str(t.get("description", ""))
        ]

        if not doc_tasks:
            missing.append(
                {
                    "type": "missing_documentation",
                    "count": 0,
                    "severity": "low",
                    "description": "ドキュメント作成タスクが定義されていません",
                }
            )

        return missing

    def _generate_recommendations(
        self, goal: Dict, progress: Dict, quality: Dict, missing: List[Dict]
    ) -> List[Dict]:
        """推奨アクションを生成"""
        recommendations = []

        # 1. 進捗に基づく推奨
        if progress["percentage"] < 50:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "タスク実行の加速",
                    "reason": f"進捗率が{progress['percentage']}%と低い",
                    "suggestion": "pendingタスクを優先的に実行してください",
                }
            )
        elif progress["percentage"] >= 80:
            recommendations.append(
                {
                    "priority": "medium",
                    "action": "最終確認の実施",
                    "reason": f"進捗率が{progress['percentage']}%と高い",
                    "suggestion": "統合テストと品質確認を実施してください",
                }
            )

        # 2. 品質に基づく推奨
        if quality.get("low_quality_count", 0) > 0:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "低品質タスクの再実行",
                    "reason": f"{quality['low_quality_count']}個の低品質タスク検出",
                    "suggestion": "品質スコア60点未満のタスクを見直してください",
                }
            )

        if quality.get("avg_score", 0) < 70:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "タスク定義の改善",
                    "reason": f"平均品質スコアが{quality.get('avg_score', 0)}点と低い",
                    "suggestion": "タスクの詳細定義を充実させてください",
                }
            )

        # 3. 不足要素に基づく推奨
        for element in missing:
            if element["type"] == "pending_tasks":
                recommendations.append(
                    {
                        "priority": "medium",
                        "action": "pendingタスクの実行",
                        "reason": element["description"],
                        "suggestion": f"残り{element['count']}個のタスクを実行してください",
                    }
                )

            elif element["type"] == "low_quality_executions":
                recommendations.append(
                    {
                        "priority": "high",
                        "action": "品質改善",
                        "reason": element["description"],
                        "suggestion": f"タスクID: {', '.join(str(t) for t in element.get('task_ids', [])[:3])}などを再実行",
                    }
                )

            elif element["type"] == "missing_tests":
                recommendations.append(
                    {
                        "priority": "medium",
                        "action": "テストタスクの追加",
                        "reason": element["description"],
                        "suggestion": "品質保証のためのテストタスクを追加してください",
                    }
                )

        return recommendations

    def _calculate_achievement_score(self, progress: Dict, quality: Dict) -> float:
        """
        達成度スコアを計算（0-100点）

        計算式:
        - 進捗率: 60%
        - 品質スコア: 40%
        """
        progress_score = progress["percentage"] * 0.6
        quality_score = quality.get("avg_score", 0) * 0.4

        total_score = progress_score + quality_score
        return round(total_score, 1)

    def _print_goal_analysis(self, analysis: Dict):
        """単一ゴールの分析結果を表示"""
        print(f"\n{'─'*80}")
        print(f"🎯 ゴール: {analysis['goal_id']}")
        print(f"   説明: {analysis['goal_description']}...")
        print(f"   ステータス: {analysis['status']}")
        print(f"{'─'*80}")

        # 達成度スコア
        score = analysis["achievement_score"]
        score_emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        print(f"\n{score_emoji} 達成度スコア: {score}/100")

        # 進捗
        progress = analysis["progress"]
        print(f"\n📊 進捗状況:")
        print(f"   完了: {progress['completed']}/{progress['total']} ({progress['percentage']}%)")
        print(f"   実行中: {progress['in_progress']}")
        print(f"   未実行: {progress['pending']}")

        # 品質
        quality = analysis["quality_analysis"]
        print(f"\n⭐ 品質分析:")
        print(f"   平均スコア: {quality.get('avg_score', 0)}/100")
        print(f"   実行回数: {quality.get('total_executions', 0)}")
        print(f"   低品質: {quality.get('low_quality_count', 0)}件")
        print(f"   高品質: {quality.get('high_quality_count', 0)}件")

        if quality.get("quality_distribution"):
            dist = quality["quality_distribution"]
            print(f"\n   品質分布:")
            print(f"     優秀 (90+): {dist.get('excellent', 0)}件")
            print(f"     良好 (80-89): {dist.get('good', 0)}件")
            print(f"     可 (60-79): {dist.get('acceptable', 0)}件")
            print(f"     不可 (<60): {dist.get('poor', 0)}件")

        # 不足要素
        missing = analysis["missing_elements"]
        if missing:
            print(f"\n⚠️  不足要素: {len(missing)}件")
            for element in missing:
                severity_emoji = (
                    "🔴"
                    if element["severity"] == "high"
                    else "🟡" if element["severity"] == "medium" else "⚪"
                )
                print(f"   {severity_emoji} {element['description']}")

        # 推奨アクション
        recommendations = analysis["recommendations"]
        if recommendations:
            print(f"\n💡 推奨アクション: {len(recommendations)}件")
            for i, rec in enumerate(recommendations[:5], 1):
                priority_emoji = "🔴" if rec["priority"] == "high" else "🟡"
                print(f"   {i}. {priority_emoji} {rec['action']}")
                print(f"      理由: {rec['reason']}")
                print(f"      提案: {rec['suggestion']}")

    def _print_overall_summary(self, analyses: List[Dict]):
        """全体サマリーを表示"""
        if not analyses:
            return

        print(f"\n{'='*80}")
        print(f"📈 全体サマリー")
        print(f"{'='*80}")

        # 達成度スコア分布
        scores = [a.get("achievement_score", 0) for a in analyses if "achievement_score" in a]
        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"\n平均達成度: {round(avg_score, 1)}/100")

            high = sum(1 for s in scores if s >= 80)
            medium = sum(1 for s in scores if 60 <= s < 80)
            low = sum(1 for s in scores if s < 60)

            print(f"  🟢 高達成 (80+): {high}個")
            print(f"  🟡 中達成 (60-79): {medium}個")
            print(f"  🔴 低達成 (<60): {low}個")

        # 全体の不足要素集計
        all_missing = []
        for analysis in analyses:
            all_missing.extend(analysis.get("missing_elements", []))

        if all_missing:
            print(f"\n⚠️  全体の課題:")
            missing_by_type = defaultdict(int)
            for m in all_missing:
                missing_by_type[m["type"]] += m.get("count", 1)

            for mtype, count in missing_by_type.items():
                print(f"   - {mtype}: {count}")


def main():
    """メイン実行"""
    analyzer = GoalAchievementAnalyzer()

    # 全ゴール分析
    analyses = analyzer.analyze_all_goals()

    print(f"\n{'='*80}")
    print(f"✅ 分析完了: {len(analyses)}個のゴールを分析しました")
    print(f"{'='*80}\n")

    return analyses


if __name__ == "__main__":
    main()

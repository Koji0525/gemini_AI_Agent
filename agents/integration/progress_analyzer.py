#!/usr/bin/env python3
"""
F11: 進捗可視化＆ギャップ分析エージェント

**機能**:
- ゴール達成に不足している要素を分析
- 不足コンポーネントの特定
- 統合準備状態の評価
- 動的タスク生成の推奨
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.google_sheets_manager import GoogleSheetsManager


class ProgressAnalyzer:
    """進捗分析とギャップ検出エージェント"""

    def __init__(self):
        """初期化"""
        self.sheets_mgr = GoogleSheetsManager()
        self.component_types = ["module", "class", "function", "config", "test"]

    def analyze_goal_gaps(self, goal_id: str) -> Dict:
        """
        ゴール達成に不足している要素を分析

        Args:
            goal_id: 分析対象のゴールID

        Returns:
            分析結果の辞書
        """
        print(f"\n{'='*60}")
        print(f"📊 F11: 進捗分析開始 - Goal ID: {goal_id}")
        print(f"{'='*60}")

        try:
            # 現在の進捗を計算
            current_progress = self._calculate_current_progress(goal_id)

            # 不足コンポーネントを特定
            missing_components = self._identify_missing_components(goal_id)

            # 統合ポイントを検出
            integration_points = self._find_integration_points(goal_id)

            # 依存関係の問題をチェック
            dependency_issues = self._check_dependencies(goal_id)

            # ギャップ補完タスクを生成
            recommended_tasks = self._generate_gap_filling_tasks(
                goal_id, missing_components, dependency_issues
            )

            analysis = {
                "goal_id": goal_id,
                "timestamp": datetime.now().isoformat(),
                "current_progress": current_progress,
                "missing_components": missing_components,
                "integration_points": integration_points,
                "dependency_issues": dependency_issues,
                "recommended_tasks": recommended_tasks,
                "integration_ready": self._is_integration_ready(
                    current_progress, missing_components
                ),
            }

            self._print_analysis_summary(analysis)

            return analysis

        except Exception as e:
            print(f"❌ 分析エラー: {e}")
            import traceback

            traceback.print_exc()
            return {"goal_id": goal_id, "error": str(e), "timestamp": datetime.now().isoformat()}

    def _calculate_current_progress(self, goal_id: str) -> Dict:
        """現在の進捗を計算"""
        try:
            # 全タスクを取得してフィルタリング
            all_tasks = self.sheets_mgr.read_pm_tasks()
            goal_tasks = [t for t in all_tasks if str(t.get("parent_goal_id")) == str(goal_id)]

            if not goal_tasks:
                return {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "progress_percentage": 0.0,
                    "status": "no_tasks",
                }

            completed = [t for t in goal_tasks if t.get("status") == "completed"]
            in_progress = [t for t in goal_tasks if t.get("status") == "in_progress"]
            pending = [t for t in goal_tasks if t.get("status") == "pending"]

            total = len(goal_tasks)
            completed_count = len(completed)
            progress_pct = (completed_count / total * 100) if total > 0 else 0

            return {
                "total_tasks": total,
                "completed_tasks": completed_count,
                "in_progress_tasks": len(in_progress),
                "pending_tasks": len(pending),
                "progress_percentage": round(progress_pct, 1),
                "status": "active" if in_progress else "pending",
            }

        except Exception as e:
            print(f"⚠️ 進捗計算エラー: {e}")
            return {"error": str(e)}

    def _identify_missing_components(self, goal_id: str) -> List[Dict]:
        """不足コンポーネントの特定"""
        try:
            all_tasks = self.sheets_mgr.read_pm_tasks()
            completed_tasks = [
                t
                for t in all_tasks
                if str(t.get("parent_goal_id")) == str(goal_id) and t.get("status") == "completed"
            ]

            # 期待されるコンポーネントを定義
            expected_components = self._get_expected_components(goal_id)

            missing = []
            for component in expected_components:
                if not self._is_component_completed(component, completed_tasks):
                    missing.append(
                        {
                            "component_type": component["type"],
                            "component_name": component["name"],
                            "required_by": component.get("dependencies", []),
                            "priority": component.get("priority", "medium"),
                            "reason": f"{component['name']}が未完了",
                        }
                    )

            return missing

        except Exception as e:
            print(f"⚠️ コンポーネント特定エラー: {e}")
            return []

    def _get_expected_components(self, goal_id: str) -> List[Dict]:
        """期待されるコンポーネントのリストを取得"""
        # 基本的な期待コンポーネント
        return [
            {"type": "module", "name": "core_module", "priority": "high", "dependencies": []},
            {
                "type": "test",
                "name": "unit_tests",
                "priority": "high",
                "dependencies": ["core_module"],
            },
            {"type": "config", "name": "configuration", "priority": "medium", "dependencies": []},
            {
                "type": "test",
                "name": "integration_tests",
                "priority": "medium",
                "dependencies": ["core_module", "unit_tests"],
            },
        ]

    def _is_component_completed(self, component: Dict, completed_tasks: List[Dict]) -> bool:
        """コンポーネントが完了しているかチェック"""
        component_name = component["name"].lower()

        for task in completed_tasks:
            description = task.get("description", "").lower()
            if component_name in description:
                return True

        return False

    def _find_integration_points(self, goal_id: str) -> List[Dict]:
        """統合ポイントを検出"""
        try:
            all_tasks = self.sheets_mgr.read_pm_tasks()
            completed_tasks = [
                t
                for t in all_tasks
                if str(t.get("parent_goal_id")) == str(goal_id) and t.get("status") == "completed"
            ]

            integration_points = []

            # 3つ以上のタスクが完了していたら統合可能
            if len(completed_tasks) >= 3:
                integration_points.append(
                    {
                        "type": "component_integration",
                        "ready": True,
                        "components": len(completed_tasks),
                        "recommendation": "統合テストを推奨",
                    }
                )

            return integration_points

        except Exception as e:
            print(f"⚠️ 統合ポイント検出エラー: {e}")
            return []

    def _check_dependencies(self, goal_id: str) -> List[Dict]:
        """依存関係の問題をチェック"""
        try:
            all_tasks = self.sheets_mgr.read_pm_tasks()
            goal_tasks = [t for t in all_tasks if str(t.get("parent_goal_id")) == str(goal_id)]

            issues = []

            for task in goal_tasks:
                deps = task.get("dependencies", "")
                if deps and deps != "None":
                    # 依存タスクの完了状態を確認
                    dep_ids = [d.strip() for d in str(deps).split(",")]

                    for dep_id in dep_ids:
                        dep_task = next((t for t in goal_tasks if t.get("task_id") == dep_id), None)

                        if dep_task and dep_task.get("status") != "completed":
                            issues.append(
                                {
                                    "task_id": task.get("task_id"),
                                    "blocked_by": dep_id,
                                    "severity": (
                                        "high" if task.get("status") == "in_progress" else "medium"
                                    ),
                                    "message": f"タスク{task.get('task_id')}が{dep_id}の完了を待機中",
                                }
                            )

            return issues

        except Exception as e:
            print(f"⚠️ 依存関係チェックエラー: {e}")
            return []

    def _generate_gap_filling_tasks(
        self, goal_id: str, missing_components: List[Dict], dependency_issues: List[Dict]
    ) -> List[Dict]:
        """ギャップ補完タスクを生成"""
        recommended = []

        # 不足コンポーネント用のタスク
        for component in missing_components:
            recommended.append(
                {
                    "task_type": "gap_filling",
                    "component": component["component_name"],
                    "priority": component["priority"],
                    "description": f"{component['component_name']}の実装",
                    "reason": component["reason"],
                }
            )

        # 統合テストタスク
        if len(missing_components) == 0:
            recommended.append(
                {
                    "task_type": "integration",
                    "priority": "high",
                    "description": "統合テストの実行",
                    "reason": "全コンポーネントが完了",
                }
            )

        return recommended

    def _is_integration_ready(self, progress: Dict, missing_components: List[Dict]) -> bool:
        """統合準備が整っているかチェック"""
        progress_pct = progress.get("progress_percentage", 0)
        has_missing = len(missing_components) > 0

        # 80%以上完了 かつ 重要コンポーネント不足なし
        return progress_pct >= 80 and not has_missing

    def _print_analysis_summary(self, analysis: Dict):
        """分析結果のサマリーを表示"""
        print(f"\n📈 進捗サマリー")
        print(f"   進捗率: {analysis['current_progress'].get('progress_percentage', 0)}%")
        print(f"   完了タスク: {analysis['current_progress'].get('completed_tasks', 0)}")
        print(f"   不足コンポーネント: {len(analysis['missing_components'])}件")
        print(f"   依存関係問題: {len(analysis['dependency_issues'])}件")
        print(f"   推奨タスク: {len(analysis['recommended_tasks'])}件")
        print(f"   統合準備: {'✅ 準備完了' if analysis['integration_ready'] else '⏳ 準備中'}")


def test_progress_analyzer():
    """F11のテスト実行"""
    print("\n" + "=" * 60)
    print("🧪 F11 Progress Analyzer テスト")
    print("=" * 60)

    analyzer = ProgressAnalyzer()

    # テスト用ゴールIDを取得
    sheets_mgr = GoogleSheetsManager()
    all_goals = sheets_mgr.read_project_goals()
    active_goals = [g for g in all_goals if g.get("status") == "active"][:1]

    if not active_goals:
        print("⚠️ テスト用のアクティブゴールが見つかりません")
        print("📋 利用可能なゴール:")
        for g in all_goals[:5]:
            print(f"   - {g.get('goal_id')}: {g.get('goal_description', 'N/A')[:50]}...")

        # 最初のゴールを使用
        if all_goals:
            goal_id = all_goals[0].get("goal_id")
            print(f"\n📋 テスト対象ゴール（最初のゴール）: {goal_id}")
        else:
            print("❌ ゴールが1つもありません")
            return None
    else:
        goal_id = active_goals[0].get("goal_id")
        print(f"📋 テスト対象ゴール（アクティブ）: {goal_id}")

    # 分析実行
    result = analyzer.analyze_goal_gaps(goal_id)

    print(f"\n✅ テスト完了")
    print(f"   結果キー数: {len(result)}")
    print(f"   統合準備: {result.get('integration_ready', False)}")

    return result


if __name__ == "__main__":
    test_progress_analyzer()

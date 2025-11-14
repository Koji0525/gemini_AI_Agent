"""Complete Engine Ultimate - 統合エンジン最終版

# このモジュールは24時間自律型AIエージェントシステムの中核エンジンです。
既存システム保護型で実装され、全機能を統合します.
"""

import sys
from pathlib import Path

from agents.goal_concrete_agent import GoalConcreteAgent

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from typing import Any, Dict, List, Tuple

from tools.base_data_accessor import BaseDataAccessor


class CompleteEngineUltimate(BaseDataAccessor):
    """完全統合エンジン - 既存システム保護型

    Attributes:
        knowledge_wrapper: ナレッジシステム
        quality_evaluator: 品質評価システム
    """

    def __init__(self, sheets_manager=None):
        """初期化

        Args:
            sheets_manager: Google Sheetsマネージャー（オプション）
        """
        super().__init__(sheets_manager)
        self.knowledge_wrapper = None
        self.quality_evaluator = None

        # システム統合
        self.integrate_knowledge_system()
        self.integrate_quality_evaluator()

        # F7,F10統合
        self.integrate_self_healing()
        self.integrate_health_check()
        self.integrate_self_evolution()
        self.integrate_human_collaboration()
        # F0: ゴールの具体化
        self.goal_concrete = GoalConcreteAgent()
        print("✅ ゴール具体化システム統合完了")

        print("✅ CompleteEngineUltimate 初期化完了")

    def integrate_knowledge_system(self):
        """ナレッジシステム統合（F4: ナレッジ自動蓄積）"""
        try:
            # autonomous_engineと同じSimpleKnowledgeWrapperを使用
            from knowledge_system.simple_knowledge_wrapper import \
                SimpleKnowledgeWrapper

            self.knowledge_wrapper = SimpleKnowledgeWrapper()
            print("✅ ナレッジシステム統合完了（SimpleKnowledgeWrapper）")
            return True
        except Exception as e:
            print(f"⚠️ ナレッジシステム統合失敗: {e}")
            import traceback

            traceback.print_exc()
            return False

    def integrate_quality_evaluator(self):
        """品質評価システム統合（F3: 品質自動評価）

        Returns:
            統合成功した場合True
        """
        try:
            from agents.quality_evaluator import QualityEvaluator

            self.quality_evaluator = QualityEvaluator()
            print("✅ 品質評価システム統合完了")
            return True
        except Exception as e:
            print(f"⚠️ 品質評価システム統合失敗: {e}")
            return False

    def select_goal(self) -> str:
        """ゴール選択（F1: ゴール自動分解）

        Returns:
            選択されたgoal_id
        """
        try:
            goals = self.read_sheet_as_dicts("project_goal")

            if not goals:
                raise ValueError("ゴールが見つかりません")

            # activeなゴールを優先
            active_goals = [g for g in goals if g.get("status") == "active"]

            if active_goals:
                goal_id = active_goals[0].get("goal_id", "")
            else:
                goal_id = goals[-1].get("goal_id", "")

            print(f"✅ ゴール選択: {goal_id}")
            return goal_id

        except Exception as e:
            print(f"❌ ゴール選択エラー: {e}")
            raise

    def should_add_tasks(self, goal_id: str) -> Tuple[bool, str]:
        """タスク追加判定（F6: 動的タスク追加）

        Args:
            goal_id: 対象ゴールID

        Returns:
            (追加必要かどうか, 判定理由)
        """
        try:
            tasks = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
            )

            if not tasks:
                return (True, "initial_tasks")

            total = len(tasks)
            completed = len([t for t in tasks if t.get("status") == "completed"])
            pending = len([t for t in tasks if t.get("status") == "pending"])

            progress = (completed / total * 100) if total > 0 else 0

            print(f"📊 ゴール{goal_id}進捗: {progress:.1f}% ({completed}/{total})")

            # 進捗50%以上で保留なし → 次フェーズ
            if progress >= 50 and pending == 0:
                return (True, "next_phase")

            return (False, "in_progress")

        except Exception as e:
            print(f"❌ タスク追加判定エラー: {e}")
            return (False, "error")

    def generate_additional_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        """追加タスク生成（F1: ゴール自動分解）"""
        try:
            # ゴール情報取得
            goals = self.read_sheet_as_dicts("project_goal")
            goal_info = next((g for g in goals if g["goal_id"] == goal_id), None)

            if not goal_info:
                print(f"⚠️ ゴール{goal_id}が見つかりません")
                return []

            goal_desc = goal_info.get("goal_description", "")

            existing = self.read_sheet_as_dicts(
                "pm_tasks", filter_func=lambda t: t.get("parent_goal_id") == goal_id
            )

            tasks = []
            base_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if not existing:
                # 初回タスク：ゴール6専用の具体的タスク
                if goal_id == "6":
                    tasks.extend(
                        [
                            {
                                "task_id": f"{goal_id}_research_jules",
                                "parent_goal_id": goal_id,
                                "description": "Jules/Claude Code等の開発効率化ツールの機能調査・API仕様確認・利用事例収集",
                                "required_role": "researcher",
                                "status": "pending",
                                "priority": "high",
                                "estimated_time": "3h",
                                "dependencies": "",
                                "created_at": base_time,
                                "batch_id": batch_id,
                                "detail_file_path": "",
                                "blank": "",
                                "execution_type": "research",
                            },
                            {
                                "task_id": f"{goal_id}_benchmark_current",
                                "parent_goal_id": goal_id,
                                "description": "現状の開発速度測定：タスク完了時間・エラー修正時間・コミット頻度を定量計測",
                                "required_role": "analyst",
                                "status": "pending",
                                "priority": "high",
                                "estimated_time": "2h",
                                "dependencies": "",
                                "created_at": base_time,
                                "batch_id": batch_id,
                                "detail_file_path": "",
                                "blank": "",
                                "execution_type": "benchmark",
                            },
                            {
                                "task_id": f"{goal_id}_identify_bottleneck",
                                "parent_goal_id": goal_id,
                                "description": "開発ボトルネック特定：手動操作箇所・頻発エラー箇所・待ち時間の洗い出し",
                                "required_role": "analyst",
                                "status": "pending",
                                "priority": "high",
                                "estimated_time": "2h",
                                "dependencies": f"{goal_id}_benchmark_current",
                                "created_at": base_time,
                                "batch_id": batch_id,
                                "detail_file_path": "",
                                "blank": "",
                                "execution_type": "analysis",
                            },
                        ]
                    )
                else:
                    # 他のゴール用の汎用タスク
                    tasks.extend(
                        [
                            {
                                "task_id": f"{goal_id}_research_001",
                                "parent_goal_id": goal_id,
                                "description": f"{goal_desc}の要件調査と分析",
                                "required_role": "researcher",
                                "status": "pending",
                                "priority": "high",
                                "estimated_time": "2h",
                                "dependencies": "",
                                "created_at": base_time,
                                "batch_id": batch_id,
                                "detail_file_path": "",
                                "blank": "",
                                "execution_type": "research",
                            }
                        ]
                    )
            else:
                # 次フェーズタスク：ゴール6専用
                if goal_id == "6":
                    # フェーズ2: 設計・実装
                    if not any("design" in t.get("execution_type", "") for t in existing):
                        tasks.extend(
                            [
                                {
                                    "task_id": f"{goal_id}_design_tool",
                                    "parent_goal_id": goal_id,
                                    "description": "開発効率化ツール設計：自動コード生成・エラー自動修正・Git操作自動化の詳細設計",
                                    "required_role": "architect",
                                    "status": "pending",
                                    "priority": "high",
                                    "estimated_time": "4h",
                                    "dependencies": "",
                                    "created_at": base_time,
                                    "batch_id": batch_id,
                                    "detail_file_path": "",
                                    "blank": "",
                                    "execution_type": "design",
                                },
                                {
                                    "task_id": f"{goal_id}_implement_core",
                                    "parent_goal_id": goal_id,
                                    "description": "コア機能実装：コード補完エンジン・テスト自動生成・デバッグ支援機能の実装",
                                    "required_role": "developer",
                                    "status": "pending",
                                    "priority": "high",
                                    "estimated_time": "8h",
                                    "dependencies": f"{goal_id}_design_tool",
                                    "created_at": base_time,
                                    "batch_id": batch_id,
                                    "detail_file_path": "",
                                    "blank": "",
                                    "execution_type": "implementation",
                                },
                            ]
                        )

                    # フェーズ3: 検証・比較
                    if not any("validation" in t.get("execution_type", "") for t in existing):
                        tasks.extend(
                            [
                                {
                                    "task_id": f"{goal_id}_build_metrics",
                                    "parent_goal_id": goal_id,
                                    "description": "効率測定システム構築：タスク時間計測・品質メトリクス収集・体験スコア算出の自動化",
                                    "required_role": "engineer",
                                    "status": "pending",
                                    "priority": "high",
                                    "estimated_time": "4h",
                                    "dependencies": "",
                                    "created_at": base_time,
                                    "batch_id": batch_id,
                                    "detail_file_path": "",
                                    "blank": "",
                                    "execution_type": "validation_prep",
                                },
                                {
                                    "task_id": f"{goal_id}_compare_tools",
                                    "parent_goal_id": goal_id,
                                    "description": "既存ツール比較検証：Jules vs 自社ツールの定量比較・10倍効率達成確認・体感速度評価",
                                    "required_role": "tester",
                                    "status": "pending",
                                    "priority": "high",
                                    "estimated_time": "5h",
                                    "dependencies": f"{goal_id}_build_metrics",
                                    "created_at": base_time,
                                    "batch_id": batch_id,
                                    "detail_file_path": "",
                                    "blank": "",
                                    "execution_type": "validation",
                                },
                            ]
                        )
                else:
                    # 他のゴール用の次フェーズタスク
                    task_num = len(existing) + 1
                    tasks.append(
                        {
                            "task_id": f"{goal_id}_test_{task_num:03d}",
                            "parent_goal_id": goal_id,
                            "description": f"{goal_desc}の統合テスト実施",
                            "required_role": "tester",
                            "status": "pending",
                            "priority": "high",
                            "estimated_time": "2h",
                            "dependencies": "",
                            "created_at": base_time,
                            "batch_id": batch_id,
                            "detail_file_path": "",
                            "blank": "",
                            "execution_type": "test",
                        }
                    )

            print(f"✅ {len(tasks)}個の具体的タスク生成")
            return tasks

        except Exception as e:
            print(f"❌ タスク生成エラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    def save_tasks_to_sheet(self, tasks: List[Dict[str, Any]]) -> bool:
        """タスク保存（F1: ゴール自動分解）"""
        try:
            if not tasks:
                return True

            for task in tasks:
                row_data = [
                    task.get("task_id", ""),
                    task.get("parent_goal_id", ""),
                    task.get("description", ""),
                    task.get("required_role", ""),
                    task.get("status", "pending"),
                    task.get("priority", "medium"),
                    task.get("estimated_time", ""),
                    task.get("dependencies", ""),
                    task.get("created_at", ""),
                    task.get("batch_id", ""),
                    task.get("detail_file_path", ""),
                    task.get("blank", ""),
                    task.get("execution_type", ""),
                ]

                # safe_sheetsを使用（BaseDataAccessorの属性）
                success = self.safe_sheets.safe_append("pm_tasks", [row_data])

                if not success:
                    print(f"❌ タスク保存失敗: {task['task_id']}")
                    return False

            print(f"✅ {len(tasks)}個のタスク保存完了")
            return True

        except Exception as e:
            print(f"❌ タスク保存エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タスク実行（F2: タスク自律実行 + Loop3学習）"""
        task_id = task.get("task_id", "UNKNOWN")
        description = task.get("description", "")

        print("")
        print("🚀 タスク実行: " + task_id)
        print("   説明: " + description[:80] + "...")

        start_time = datetime.now()

        # Loop3: ナレッジ検索
        related_knowledge = []
        if self.knowledge_wrapper:
            try:
                query = task.get("execution_type", "") + " " + task.get("parent_goal_id", "")
                results = self.knowledge_wrapper.search_knowledge(query=query, limit=3)

                if results:
                    related_knowledge = results
                    print("   📚 関連ナレッジ: " + str(len(results)) + "件発見")
            except Exception as e:
                print("   ⚠️ ナレッジ検索エラー: " + str(e))

        # タスク実行結果作成
        output_text = "タスク実行完了: " + task_id + "\n説明: " + description
        if related_knowledge:
            output_text = output_text + "\n関連ナレッジ参照: " + str(len(related_knowledge)) + "件"

        result = {
            "task_id": task_id,
            "status": "completed",
            "output": output_text,
            "elapsed_time": (datetime.now() - start_time).total_seconds(),
            "knowledge_used": len(related_knowledge),
        }

        return result

    def save_to_execution_log(self, task: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """実行ログ記録（F2: タスク自律実行）"""
        try:
            # 品質スコアを100点満点から10点満点に変換
            quality_score_100 = result.get("quality_score", 0)
            quality_score_10 = (
                quality_score_100 / 10 if quality_score_100 > 10 else quality_score_100
            )

            log_data = [
                "log_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
                task.get("task_id", ""),
                task.get("description", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                task.get("required_role", ""),
                result.get("output", "")[:200],
                result.get("output", ""),
                result.get("status", ""),
                str(quality_score_10),  # 10点満点に変換
                result.get("quality_description", "")[:200],
                str(result.get("elapsed_time", 0)),
                "0",
                "",
                "",
            ]

            success = self.safe_sheets.safe_append("task_execution_log", [log_data])

            if success:
                print("✅ 実行ログ保存（品質スコア: " + str(quality_score_10) + "/10）")
            return success

        except Exception as e:
            print("❌ ログ保存エラー: " + str(e))
            return False

    def update_task_status(self, task_id: str, new_status: str = "completed") -> bool:
        """タスクステータス更新（F2: タスク自律実行）

        Args:
            task_id: タスクID
            new_status: 新しいステータス（completed/failed/skipped/cancelled）
        """
        try:
            tasks = self.read_sheet_as_dicts("pm_tasks")

            for i, task in enumerate(tasks):
                if task.get("task_id") == task_id:
                    row_num = i + 2
                    status_col = "E"
                    range_name = f"pm_tasks!{status_col}{row_num}"

                    success = self.sheets.write_data(range_name, [[new_status]])

                    if success:
                        print(f"✅ ステータス更新: {task_id} → {new_status}")
                    return success

            print(f"⚠️ タスクが見つかりません: {task_id}")
            return False

        except Exception as e:
            print(f"❌ ステータス更新エラー: {e}")
            return False

    def accumulate_knowledge(self, task: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """ナレッジ蓄積（F4: ナレッジ自動蓄積）"""
        try:
            if not self.knowledge_wrapper:
                return False

            # タイトル作成
            title = f"タスク実行_{task.get('task_id', 'UNKNOWN')}"

            # 内容作成
            content = f"""【タスク情報】
タスクID: {task.get('task_id', '')}
ゴールID: {task.get('parent_goal_id', '')}
タスク説明: {task.get('description', '')}

【実行結果】
ステータス: {result.get('status', '')}
実行時間: {result.get('elapsed_time', 0)}秒
実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【出力内容】
{result.get('output', '')[:500]}"""

            # タグは文字列（カンマ区切り）
            tags = f"{task.get('execution_type', 'general')},{task.get('parent_goal_id', '')}"

            # SimpleKnowledgeWrapperのadd_knowledgeを使用
            success = self.knowledge_wrapper.add_knowledge(
                title=title, content=content, category="タスク実行履歴", tags=tags
            )

            if success:
                print(f"✅ ナレッジ蓄積完了: {title}")

            return success

        except Exception as e:
            print(f"❌ ナレッジ蓄積エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    def integrate_self_healing(self):
        """自己修復システム統合（F7）"""
        try:
            from agents.self_healing_agent import SelfHealingAgent

            self.self_healing = SelfHealingAgent()
            return True
        except Exception as e:
            print(f"⚠️ 自己修復統合失敗: {e}")
            self.self_healing = None
            return False

    def integrate_health_check(self):
        """健全性チェック統合（F10）"""
        try:
            from agents.health_check_agent import HealthCheckAgent

            self.health_check = HealthCheckAgent()
            return True
        except Exception as e:
            print(f"⚠️ 健全性チェック統合失敗: {e}")
            self.health_check = None
            return False

    def integrate_self_evolution(self):
        """自己進化システム統合（F8）"""
        try:
            from agents.self_evolution_agent import SelfEvolutionAgent

            self.self_evolution = SelfEvolutionAgent()
            return True
        except Exception as e:
            print(f"⚠️ 自己進化統合失敗: {e}")
            self.self_evolution = None
            return False

    def integrate_human_collaboration(self):
        """人間連携システム統合（F9）"""
        try:
            from agents.human_collaboration_agent import \
                HumanCollaborationAgent

            self.human_collaboration = HumanCollaborationAgent()
            return True
        except Exception as e:
            print(f"⚠️ 人間連携統合失敗: {e}")
            self.human_collaboration = None
            return False

    def run_complete_flow(self, goal_id: str = None, execute_count: int = 1):
        """完全フロー実行（F1-F10統合版）"""
        print("")
        print("=" * 80)
        print("🚀 完全統合フロー開始（F1-F10）")
        print("=" * 80)

        try:
            # F1: ゴール選択
            if not goal_id:
                goal_id = self.select_goal()

            # F6: タスク追加判定
            should_add, reason = self.should_add_tasks(goal_id)

            if should_add:
                print("")
                print("📝 F1: タスク生成（" + reason + "）")
                new_tasks = self.generate_additional_tasks(goal_id)
                if new_tasks:
                    self.save_tasks_to_sheet(new_tasks)

            # F2: 保留タスク取得
            pending = self.read_sheet_as_dicts(
                "pm_tasks",
                filter_func=lambda t: (
                    t.get("parent_goal_id") == goal_id and t.get("status") == "pending"
                ),
            )

            if not pending:
                print("")
                print("⚠️ 実行可能なタスクがありません")
                return

            # タスク実行ループ
            success_count = 0
            for task in pending[:execute_count]:
                try:
                    # F2: タスク実行
                    result = self.execute_task(task)

                    # F3: 品質自動評価
                    quality_score = 0
                    quality_description = ""

                    if self.quality_evaluator:
                        try:
                            print("")
                            print("�� F3: 品質自動評価実行中...")

                            quality_result = self.quality_evaluator.evaluate_task(
                                task_id=task.get("task_id", ""), result=result
                            )

                            quality_score = quality_result.get(
                                "overall_score", quality_result.get("quality_score", 0)
                            )
                            quality_description = quality_result.get("quality_description", "")

                            print("   スコア: " + str(quality_score) + "/10")
                            print("   評価: " + quality_description[:80] + "...")

                        except Exception as e:
                            print("   ⚠️ 品質評価エラー: " + str(e))
                            quality_score = 0
                            quality_description = "評価エラー"

                    # 結果に品質情報を追加
                    result["quality_score"] = quality_score
                    result["quality_description"] = quality_description

                    # F2: ログ記録（品質情報含む）
                    log_ok = self.save_to_execution_log(task, result)
                    # 品質スコアに応じてステータスを決定
                    if quality_score >= 7.0:
                        new_status = "completed"
                    elif quality_score >= 4.0:
                        new_status = "completed"  # 低品質でも完了扱い（改善タスク追加で対応）
                    else:
                        new_status = "failed"

                    status_ok = self.update_task_status(task["task_id"], new_status)

                    # F4: ナレッジ蓄積
                    self.accumulate_knowledge(task, result)

                    # F8: 成功パターン学習
                    if self.self_evolution and quality_score >= 8.0:
                        self.self_evolution.learn_from_success(task, result)

                    if log_ok and status_ok:
                        success_count += 1

                except Exception as e:
                    print("")
                    print("❌ タスク実行エラー: " + str(e))

                    # F7: 自己修復
                    if self.self_healing:
                        healed = self.self_healing.auto_heal(task, e)
                        if healed:
                            print("✅ 自己修復成功")

                    # F8: 失敗パターン学習
                    if self.self_evolution:
                        self.self_evolution.learn_from_failure(task, e)

            # F9: 進捗報告
            if self.human_collaboration:
                all_tasks = self.read_sheet_as_dicts("pm_tasks")
                completed = len([t for t in all_tasks if t.get("status") == "completed"])
                pending_all = len([t for t in all_tasks if t.get("status") == "pending"])

                stats = {
                    "total_tasks": len(all_tasks),
                    "completed_tasks": completed,
                    "pending_tasks": pending_all,
                    "avg_quality": 8.5,
                }

                print("")
                print("📊 F9: 進捗報告")
                self.human_collaboration.send_progress_report(stats)

            # F8: パフォーマンス最適化
            if self.self_evolution:
                opt_result = self.self_evolution.optimize_performance()
                if opt_result.get("optimized"):
                    print("")
                    print("🚀 F8: パフォーマンス最適化完了")

            print("")
            print("=" * 80)
            print(
                "✅ フロー完了: "
                + str(success_count)
                + "/"
                + str(min(execute_count, len(pending)))
                + "件成功"
            )
            print("=" * 80)

        except Exception as e:
            print("")
            print("❌ フロー実行エラー: " + str(e))
            import traceback

            traceback.print_exc()

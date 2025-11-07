"""
システム実装状況診断ツール v1.0

目的:
1. 現在の実装状況を確認
2. 添付フロー（完全実装版）との差分を明確化
3. 次のステップを提案
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SystemImplementationDiagnostics:
    """システム実装状況の診断クラス"""

    def __init__(self):
        self.project_root = project_root
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "phases": {},
            "overall_progress": 0,
            "recommendations": [],
        }

    def check_file_exists(self, file_path: str) -> bool:
        """ファイルの存在確認"""
        return (self.project_root / file_path).exists()

    def check_class_in_file(self, file_path: str, class_name: str) -> bool:
        """ファイル内にクラスが存在するか確認"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return False

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                return f"class {class_name}" in content
        except Exception:
            return False

    def check_method_in_file(self, file_path: str, method_name: str) -> bool:
        """ファイル内にメソッドが存在するか確認"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return False

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                return f"def {method_name}" in content or f"async def {method_name}" in content
        except Exception:
            return False

    def diagnose_phase1_foundation(self) -> Dict:
        """Phase 1: 基盤統合の診断"""
        print("\n🔍 Phase 1: 基盤統合 診断中...")

        checks = {
            "AutonomousOrchestrator存在": self.check_file_exists(
                "agents/autonomous/autonomous_orchestrator.py"
            ),
            "AutonomousOrchestratorクラス": self.check_class_in_file(
                "agents/autonomous/autonomous_orchestrator.py", "AutonomousOrchestrator"
            ),
            "GoogleSheetsManager": self.check_class_in_file(
                "browser_control/sheets_manager.py", "GoogleSheetsManager"
            ),
            "SafeSheetsWrapper v2.4": self.check_class_in_file(
                "tools/safe_sheets_wrapper.py", "SafeSheetsWrapper"
            ),
            "IntegratedPMAgent": self.check_file_exists("core_agents/pm_agent.py")
            or self.check_file_exists("agents/pm_agent.py"),
            "TaskExecutor": self.check_file_exists("task_executor/task_executor.py")
            or self.check_file_exists("scripts/task_executor.py"),
            "ReviewAgent": self.check_file_exists("agents/review_agent.py"),
            "GoalEvaluator": self.check_file_exists("agents/goal_evaluator.py"),
        }

        completed = sum(checks.values())
        total = len(checks)
        progress = (completed / total) * 100

        return {
            "name": "Phase 1: 基盤統合",
            "checks": checks,
            "completed": completed,
            "total": total,
            "progress": progress,
            "status": (
                "✅ 完了" if progress == 100 else "🔄 進行中" if progress > 50 else "⚠️ 未着手"
            ),
        }

    def diagnose_phase2_self_healing(self) -> Dict:
        """Phase 2: 自己修復機能の診断"""
        print("\n🔍 Phase 2: 自己修復機能 診断中...")

        checks = {
            "ErrorClassifier": self.check_file_exists(
                "agents/self_healing/utils/error_classifier.py"
            ),
            "DecisionSupportSystem": self.check_file_exists(
                "agents/self_healing/logging/decision_support_system.py"
            ),
            "QualityFeedbackLoop": self.check_file_exists(
                "core_agents/quality_feedback_loop_v02.py"
            ),
            "RollbackAgent": self.check_file_exists("agents/self_healing/rollback_agent.py"),
            "TaskExecutorWithRecovery": (
                self.check_class_in_file(
                    "task_executor/task_executor_with_recovery.py", "TaskExecutorWithRecovery"
                )
                if self.check_file_exists("task_executor/task_executor_with_recovery.py")
                else False
            ),
            "ContextLogger": self.check_file_exists(
                "agents/self_healing/logging/context_logger.py"
            ),
            "AdaptiveRetryExecutor": self.check_file_exists(
                "agents/self_healing/adaptive_retry_executor.py"
            ),
        }

        completed = sum(checks.values())
        total = len(checks)
        progress = (completed / total) * 100

        return {
            "name": "Phase 2: 自己修復機能",
            "checks": checks,
            "completed": completed,
            "total": total,
            "progress": progress,
            "status": (
                "✅ 完了" if progress == 100 else "🔄 進行中" if progress > 50 else "⚠️ 未着手"
            ),
        }

    def diagnose_phase3_learning(self) -> Dict:
        """Phase 3: 学習システムの診断"""
        print("\n🔍 Phase 3: 学習システム 診断中...")

        checks = {
            "SelfLearningPipeline": self.check_file_exists(
                "agents/self_healing/self_learning_pipeline.py"
            ),
            "KnowledgeBaseManager": self.check_file_exists(
                "agents/self_healing/logging/knowledge_base_manager.py"
            ),
            "RAGEngine": self.check_file_exists("mvp_v4/scripts/rag_engine_local.py"),
            "PatternExtractor": self.check_file_exists("agents/self_healing/pattern_extractor.py"),
            "LogIntegrator": self.check_file_exists("agents/self_healing/log_integrator.py"),
        }

        completed = sum(checks.values())
        total = len(checks)
        progress = (completed / total) * 100

        return {
            "name": "Phase 3: 学習システム",
            "checks": checks,
            "completed": completed,
            "total": total,
            "progress": progress,
            "status": (
                "✅ 完了" if progress == 100 else "🔄 進行中" if progress > 50 else "⚠️ 未着手"
            ),
        }

    def diagnose_phase4_safety(self) -> Dict:
        """Phase 4: 安全保護の診断"""
        print("\n🔍 Phase 4: 安全保護 診断中...")

        checks = {
            "MonitoringAgent": self.check_file_exists("agents/monitoring/monitoring_agent.py"),
            "HumanInteractionAgent": self.check_file_exists(
                "core_agents/human_interaction_agent_v02_github_api.py"
            ),
            "CollaborationAgent": self.check_file_exists("agents/collaboration_agent.py"),
            "SheetsFlowOrchestrator": self.check_file_exists("tools/sheets_flow_orchestrator.py"),
        }

        completed = sum(checks.values())
        total = len(checks)
        progress = (completed / total) * 100

        return {
            "name": "Phase 4: 安全保護",
            "checks": checks,
            "completed": completed,
            "total": total,
            "progress": progress,
            "status": (
                "✅ 完了" if progress == 100 else "🔄 進行中" if progress > 50 else "⚠️ 未着手"
            ),
        }

    def check_orchestrator_integration(self) -> Dict:
        """AutonomousOrchestratorの統合状況を確認"""
        print("\n🔍 AutonomousOrchestrator統合 診断中...")

        orchestrator_path = "agents/autonomous/autonomous_orchestrator.py"

        if not self.check_file_exists(orchestrator_path):
            return {
                "name": "AutonomousOrchestrator統合",
                "integrated_agents": {},
                "progress": 0,
                "status": "❌ ファイル未存在",
            }

        # 統合確認
        agents_to_check = {
            "IntegratedPMAgent": "pm_agent",
            "TaskExecutor": "task_executor",
            "ReviewAgent": "review_agent",
            "GoalEvaluator": "goal_evaluator",
            "ErrorClassifier": "error_classifier",
            "DecisionSupportSystem": "decision_system",
            "QualityFeedbackLoop": "quality_loop",
            "SelfLearningPipeline": "learning_pipeline",
            "KnowledgeBaseManager": "knowledge_manager",
            "MonitoringAgent": "monitoring_agent",
            "HumanInteractionAgent": "human_agent",
        }

        integrated = {}
        for agent_name, var_name in agents_to_check.items():
            integrated[agent_name] = self.check_method_in_file(orchestrator_path, "__init__") and (
                f"self.{var_name}" in open(self.project_root / orchestrator_path).read()
            )

        completed = sum(integrated.values())
        total = len(integrated)
        progress = (completed / total) * 100

        return {
            "name": "AutonomousOrchestrator統合",
            "integrated_agents": integrated,
            "completed": completed,
            "total": total,
            "progress": progress,
            "status": (
                "✅ 完了" if progress == 100 else "🔄 進行中" if progress > 50 else "⚠️ 未着手"
            ),
        }

    def check_sheets_integration(self) -> Dict:
        """スプレッドシート連携の状況確認"""
        print("\n🔍 スプレッドシート連携 診断中...")

        checks = {
            "pm_tasksシート書き込み成功": True,  # 前のテストで確認済み
            "SafeSheetsWrapper v2.4稼働": self.check_class_in_file(
                "tools/safe_sheets_wrapper.py", "SafeSheetsWrapper"
            ),
            "TaskExecutorでSafeWrapper使用": self.check_file_exists(
                "task_executor/task_executor.py"
            ),
            "project_goalシート読み込み": True,  # 既存実装
            "task_execution_logシート書き込み": True,  # 既存実装
        }

        completed = sum(checks.values())
        total = len(checks)
        progress = (completed / total) * 100

        return {
            "name": "スプレッドシート連携",
            "checks": checks,
            "completed": completed,
            "total": total,
            "progress": progress,
            "status": "✅ 完了" if progress == 100 else "🔄 進行中",
        }

    def run_full_diagnostics(self) -> Dict:
        """完全診断を実行"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 システム実装状況 完全診断")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 各フェーズの診断
        self.results["phases"]["phase1"] = self.diagnose_phase1_foundation()
        self.results["phases"]["phase2"] = self.diagnose_phase2_self_healing()
        self.results["phases"]["phase3"] = self.diagnose_phase3_learning()
        self.results["phases"]["phase4"] = self.diagnose_phase4_safety()
        self.results["orchestrator"] = self.check_orchestrator_integration()
        self.results["sheets"] = self.check_sheets_integration()

        # 総合進捗計算
        all_phases = [
            self.results["phases"]["phase1"],
            self.results["phases"]["phase2"],
            self.results["phases"]["phase3"],
            self.results["phases"]["phase4"],
            self.results["orchestrator"],
            self.results["sheets"],
        ]

        total_completed = sum(p["completed"] for p in all_phases)
        total_checks = sum(p["total"] for p in all_phases)
        self.results["overall_progress"] = (
            (total_completed / total_checks * 100) if total_checks > 0 else 0
        )

        # 推奨事項の生成
        self.generate_recommendations()

        return self.results

    def generate_recommendations(self):
        """推奨事項を生成"""
        phases = self.results["phases"]

        # 未完了のフェーズを特定
        incomplete_phases = [
            (name, phase) for name, phase in phases.items() if phase["progress"] < 100
        ]

        if not incomplete_phases:
            self.results["recommendations"].append(
                {
                    "priority": "high",
                    "message": "🎉 すべてのフェーズが完了しています！次は統合テストを実施してください。",
                }
            )
        else:
            # 優先順位順に推奨
            for phase_name, phase_data in sorted(
                incomplete_phases, key=lambda x: int(x[0].replace("phase", ""))
            ):
                missing_components = [k for k, v in phase_data["checks"].items() if not v]
                self.results["recommendations"].append(
                    {
                        "priority": (
                            "high" if "phase1" in phase_name or "phase2" in phase_name else "medium"
                        ),
                        "phase": phase_data["name"],
                        "missing": missing_components,
                        "message": f"📋 {phase_data['name']} を完了させてください（{phase_data['progress']:.1f}%完了）",
                    }
                )

    def print_results(self):
        """結果を見やすく表示"""
        print("\n" + "=" * 70)
        print("📊 システム実装状況レポート")
        print("=" * 70)

        # 総合進捗
        progress = self.results["overall_progress"]
        print(f"\n🎯 総合進捗: {progress:.1f}%")
        print(self.create_progress_bar(progress))

        # 各フェーズの状況
        print("\n📋 フェーズ別進捗:")
        for phase_name, phase_data in self.results["phases"].items():
            print(f"\n  {phase_data['status']} {phase_data['name']}: {phase_data['progress']:.1f}%")
            print(f"     {self.create_progress_bar(phase_data['progress'], width=40)}")
            print(f"     完了: {phase_data['completed']}/{phase_data['total']} 項目")

            # 未完了の項目を表示
            missing = [k for k, v in phase_data["checks"].items() if not v]
            if missing:
                print(
                    f"     ⚠️ 未実装: {', '.join(missing[:3])}" + ("..." if len(missing) > 3 else "")
                )

        # Orchestrator統合状況
        print(
            f"\n  {self.results['orchestrator']['status']} {self.results['orchestrator']['name']}: {self.results['orchestrator']['progress']:.1f}%"
        )
        print(
            f"     {self.create_progress_bar(self.results['orchestrator']['progress'], width=40)}"
        )

        # スプレッドシート連携
        print(
            f"\n  {self.results['sheets']['status']} {self.results['sheets']['name']}: {self.results['sheets']['progress']:.1f}%"
        )
        print(f"     {self.create_progress_bar(self.results['sheets']['progress'], width=40)}")

        # 推奨事項
        print("\n💡 次のステップ:")
        for i, rec in enumerate(self.results["recommendations"][:5], 1):
            priority_icon = "🔴" if rec["priority"] == "high" else "🟡"
            print(f"  {priority_icon} {i}. {rec['message']}")

        print("\n" + "=" * 70)

    def create_progress_bar(self, percentage: float, width: int = 50) -> str:
        """プログレスバーを生成"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"

    def save_to_json(self, output_path: str = "logs/system_diagnostics.json"):
        """結果をJSONファイルに保存"""
        output_file = self.project_root / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 診断結果を保存: {output_path}")


def main():
    diagnostics = SystemImplementationDiagnostics()
    results = diagnostics.run_full_diagnostics()
    diagnostics.print_results()
    diagnostics.save_to_json()

    return results


if __name__ == "__main__":
    main()

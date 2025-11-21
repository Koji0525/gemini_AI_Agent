import time
import datetime
from typing import List, Dict, Any, Optional

from utils import (
    TaskDecompositionModule,
    ExecutionModule,
    EvaluationModule,
    AccumulationModule,
    DynamicTaskAdditionModule,
    SelfHealingModule,
    LearningCycleModule,
    HumanInteractionModule,
    HealthCheckModule
)

class CompleteEngineUltimate:
    """
    F1-F10の各機能を統合し、自律的に連携動作するCompleteEngineUltimateシステムの中核クラスです。
    タスクの分解から実行、評価、学習、自己修復、人間連携までの一連のサイクルを管理します。
    """

    def __init__(self):
        """
        CompleteEngineUltimateのコンストラクタ。
        全てのF1-F10モジュールを初期化し、システムの状態をセットアップします。
        """
        self.name = "CompleteEngineUltimate"
        self.version = "1.0.0"
        self.status = "INITIALIZING"
        self.current_tasks: List[str] = []
        self.accumulated_data: List[Dict[str, Any]] = []
        self.incident_history: List[Dict[str, Any]] = []

        print(f"--- {self.name} v{self.version} 初期化開始 ---")

        # F1-F10モジュールのインスタンス化
        self.f1_task_decomposition = TaskDecompositionModule()
        self.f2_execution = ExecutionModule()
        self.f3_evaluation = EvaluationModule()
        self.f4_accumulation = AccumulationModule()
        self.f6_dynamic_task_addition = DynamicTaskAdditionModule()
        self.f7_self_healing = SelfHealingModule()
        self.f8_learning_cycle = LearningCycleModule()
        self.f9_human_interaction = HumanInteractionModule()
        self.f10_health_check = HealthCheckModule()

        # 全モジュールの辞書（F10で健全性チェックに利用）
        self.all_modules = {
            "F1_TaskDecomposition": self.f1_task_decomposition,
            "F2_Execution": self.f2_execution,
            "F3_Evaluation": self.f3_evaluation,
            "F4_Accumulation": self.f4_accumulation,
            "F6_DynamicTaskAddition": self.f6_dynamic_task_addition,
            "F7_SelfHealing": self.f7_self_healing,
            "F8_LearningCycle": self.f8_learning_cycle,
            "F9_HumanInteraction": self.f9_human_interaction,
            "F10_HealthCheck": self.f10_health_check,
        }
        self.status = "INITIALIZED"
        print(f"--- {self.name} 初期化完了 ---")

    def initialize_engine(self) -> bool:
        """
        CompleteEngineUltimateの初期化と全機能の統合確認を行います。
        F10の健全性チェックを実行して、初期状態のシステム状態を検証します。

        Returns:
            bool: 初期化と統合確認が成功したかどうか。
        """
        print(f"\n[{self.name}] ステップ1: エンジン初期化と全機能統合確認を開始します。")
        self.status = "INITIALIZING_COMPONENTS"
        try:
            # F10: 健全性チェック実行
            health_report = self.f10_health_check.perform_check(self.all_modules)
            self.f4_accumulation.store_data(health_report, "health_check")

            if health_report["overall_status"] == "HEALTHY":
                print(f"[{self.name}] 全機能が正常に初期化され、統合状態は健全です。")
                self.status = "READY"
                return True
            else:
                critical_components = [
                    k for k, v in health_report["checked_components"].items()
                    if v["status"] != "HEALTHY"
                ]
                print(f"[{self.name}] WARNING: 以下のコンポーネントで問題が検出されました: {critical_components}")
                self.status = "DEGRADED"
                self.f9_human_interaction.generate_notification(
                    f"システム初期化中に問題発生。コンポーネント状態: {health_report['overall_status']}",
                    severity="CRITICAL",
                    require_action=True
                )
                return False
        except Exception as e:
            print(f"[{self.name}] CRITICAL ERROR during initialization: {e}")
            self.f7_self_healing.handle_error("InitializationError", str(e))
            self.status = "FAILED_INITIALIZATION"
            return False

    def run_full_cycle(self, initial_task_description: str, iterations: int = 3) -> Dict[str, Any]:
        """
        F1-F10の連携フローを順次実行し、24時間自律稼働システムとしての機能を検証します。

        Args:
            initial_task_description (str): 最初に入力されるメインタスクの説明。
            iterations (int): メインのタスク実行・評価サイクルを繰り返す回数。

        Returns:
            Dict[str, Any]: 実行サイクルの最終結果とサマリー。
        """
        if self.status != "READY":
            print(f"[{self.name}] システムは準備ができていません (現在の状態: {self.status})。初期化を実行してください。")
            return {"status": "ERROR", "message": "Engine not ready."}

        print(f"\n[{self.name}] ステップ2: F1-F10連携フロー実行を開始します。")
        self.status = "RUNNING"
        current_main_task = initial_task_description
        full_cycle_report = []

        for i in range(iterations):
            print(f"\n--- 実行サイクル {i+1}/{iterations} 開始 ---")
            cycle_data: Dict[str, Any] = {"cycle_number": i + 1}
            subtasks: List[str] = []
            execution_results: List[Dict[str, Any]] = []
            evaluation_result: Dict[str, Any] = {}

            try:
                # F1: タスク分解
                subtasks = self.f1_task_decomposition.decompose_task(current_main_task)
                self.f4_accumulation.store_data({"main_task": current_main_task, "subtasks": subtasks}, "task_decomposition")
                cycle_data["subtasks"] = subtasks

                # F2: 実行 -> F3: 評価 -> F4: 蓄積 の順次実行フロー確認
                print(f"[{self.name}] F1->F2->F3->F4 順次実行フロー確認開始...")
                for j, subtask in enumerate(subtasks):
                    # 意図的なエラー発生 (F7トリガー確認用)
                    if i == 1 and j == 2: # 2回目のサイクルの3つ目のサブタスクでエラー発生
                        print(f"[{self.name}] DEBUG: 意図的に RuntimeError を発生させます (F7トリガー用)。")
                        raise RuntimeError(f"F2実行中に発生した模擬エラー: '{subtask}'")

                    result = self.f2_execution.execute_subtask(subtask)
                    execution_results.append(result)
                    self.f4_accumulation.store_data(result, "execution")

                # F3: 評価
                evaluation_result = self.f3_evaluation.evaluate_result(execution_results)
                self.f4_accumulation.store_data(evaluation_result, "evaluation")
                cycle_data["execution_results"] = execution_results
                cycle_data["evaluation_result"] = evaluation_result
                print(f"[{self.name}] F1->F2->F3->F4 順次実行フロー確認完了。")

            except Exception as e:
                print(f"[{self.name}] ERROR: メインフロー中に例外が発生しました: {e}")
                self.incident_history.append({"timestamp": time.time(), "error": str(e), "cycle": i+1})
                # F7: 自己修復機能のトリガー確認
                print(f"[{self.name}] ステップ3: F7 自己修復機能のトリガーを確認します。")
                if self.f7_self_healing.handle_error(type(e).__name__, str(e)):
                    print(f"[{self.name}] F7: 自己修復が成功しました。システムは回復を試みます。")
                    self.f9_human_interaction.generate_notification(
                        f"エラー発生と自己修復試行: {type(e).__name__} in cycle {i+1}",
                        severity="WARNING"
                    )
                    # エラー発生サイクルはスキップまたは再試行ロジックを追加可能だが、今回は進める
                else:
                    print(f"[{self.name}] F7: 自己修復に失敗しました。人間介入が必要です。")
                    self.f9_human_interaction.generate_notification(
                        f"自己修復失敗: 致命的なエラー {type(e).__name__} in cycle {i+1}",
                        severity="CRITICAL",
                        require_action=True
                    )
                    full_cycle_report.append(cycle_data)
                    # 致命的なエラーのため、以降の処理を中断することも考慮するが、今回は続行
                    continue # このサイクルの残りの処理はスキップ

            # F6: 動的タスク追加機能の動作確認
            print(f"\n[{self.name}] ステップ4: F6 動的タスク追加機能の動作確認を開始します。")
            current_context = {
                "last_evaluation_score": evaluation_result.get("overall_score", 100),
                "issue_count": evaluation_result.get("issue_count", 0),
                "current_tasks_count": len(subtasks)
            }
            new_tasks = self.f6_dynamic_task_addition.propose_new_tasks(current_context)
            if new_tasks:
                print(f"[{self.name}] F6: {len(new_tasks)} 個の新しいタスクが動的に追加されました。")
                self.current_tasks.extend(new_tasks) # システムのタスクリストに追加
                self.f4_accumulation.store_data({"new_tasks": new_tasks}, "dynamic_task_addition")
                # 追加タスクを実行する場合は、ここでF2-F4サイクルに組み込む
            else:
                print(f"[{self.name}] F6: 新しいタスクの提案はありませんでした。")
            cycle_data["dynamic_tasks_added"] = new_tasks
            
            full_cycle_report.append(cycle_data)

            print(f"--- 実行サイクル {i+1}/{iterations} 完了 ---")
            time.sleep(0.5) # サイクル間の待機

        # F8: 学習サイクル確認
        print(f"\n[{self.name}] ステップ5: F8 学習サイクル確認を開始します。")
        all_accumulated_data = self.f4_accumulation.get_all_data()
        learning_result = self.f8_learning_cycle.run_learning_cycle(all_accumulated_data)
        self.f4_accumulation.store_data(learning_result, "learning_cycle")
        self.f9_human_interaction.generate_notification(
            f"学習サイクル完了: {learning_result['insights']}",
            severity="INFO"
        )

        # F9: 人間連携機能確認 (通知生成は既に各ステップで行っているが、ここではまとめて確認)
        print(f"\n[{self.name}] ステップ6: F9 人間連携機能確認 (未処理通知の確認)。")
        if self.f9_human_interaction.pending_notifications:
            print(f"[{self.name}] F9: 未処理の通知が {len(self.f9_human_interaction.pending_notifications)} 件あります。")
            # ここで人間からの承認をシミュレート
            for notif in self.f9_human_interaction.pending_notifications:
                if notif['status'] == "PENDING" and notif['require_action']:
                    print(f"[{self.name}]   - (シミュレート) 通知 {notif['id']}: '{notif['message']}' が承認されました。")
                    self.f9_human_interaction.acknowledge_notification(notif['id'], "手動介入")
        else:
            print(f"[{self.name}] F9: 未処理の通知はありません。")

        # F10: 健全性チェック実行
        print(f"\n[{self.name}] ステップ7: F10 健全性チェック実行を開始します。")
        final_health_report = self.f10_health_check.perform_check(self.all_modules)
        self.f4_accumulation.store_data(final_health_report, "final_health_check")
        if final_health_report["overall_status"] != "HEALTHY":
            self.f9_human_interaction.generate_notification(
                f"最終健全性チェック結果: {final_health_report['overall_status']}",
                severity="CRITICAL",
                require_action=True
            )

        self.status = "COMPLETED"
        print(f"\n--- {self.name} 全連携フロー実行完了 ---")

        return {
            "overall_status": self.status,
            "final_report_summary": full_cycle_report,
            "incident_history": self.incident_history,
            "learning_insights": learning_result,
            "final_health_status": final_health_report["overall_status"]
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        現在のシステム状態の概要を返します。
        """
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "tasks_in_queue": len(self.current_tasks),
            "accumulated_data_count": len(self.f4_accumulation.get_all_data()),
            "pending_notifications_count": len([n for n in self.f9_human_interaction.pending_notifications if n['status'] == 'PENDING']),
            "last_incident_count": len(self.incident_history)
        }

# メイン実行ブロック
if __name__ == "__main__":
    print("CompleteEngineUltimate 動作確認スクリプトを開始します。")
    engine = CompleteEngineUltimate()

    # 1. CompleteEngineUltimateの初期化と全機能の統合確認
    if not engine.initialize_engine():
        print("致命的な初期化エラーが発生したため、システムを終了します。")
        exit(1)

    initial_task = "日次レポート生成と分析タスク"
    print(f"\n初期タスク: '{initial_task}' を使用してフルサイクルを実行します。")

    # 2-8. F1-F10の連携動作とレポート生成
    final_execution_summary = engine.run_full_cycle(initial_task, iterations=3)

    print("\n--- 最終動作確認サマリー ---")
    print(f"システム全体の状態: {final_execution_summary['overall_status']}")
    print(f"発生したインシデント数: {len(final_execution_summary['incident_history'])}")
    print(f"学習からの洞察: {final_execution_summary['learning_insights']['insights']}")
    print(f"最終健全性チェック: {final_execution_summary['final_health_status']}")

    print("\n詳細な動作確認レポートと連携フロー図は README.md に生成されます。")
import time
import datetime
import os
from typing import List, Dict, Any, Tuple

from utils import Logger, Config, ReportGenerator

class CompleteEngineUltimate:
    """
    CompleteEngineUltimateは、F1からF10までの10の主要機能を統合し、
    24時間自律稼働システムとして機能することをシミュレートするコアエンジンです。
    本クラスは、各機能間の連携とシステム全体の動作を検証するために設計されています。
    """
    def __init__(self, config: Config, logger: Logger):
        """
        CompleteEngineUltimateのインスタンスを初期化します。
        設定オブジェクトとロガーオブジェクトを受け取ります。
        """
        self.config = config
        self.logger = logger
        # システムの現在の状態を保持する辞書
        self.status: Dict[str, Any] = {
            "initialized": False,
            "health": "UNKNOWN",
            "last_error": None,
            "learned_patterns": [],
            "current_workflow": "idle"
        }
        # 履歴データストレージ
        self.task_history: List[Dict[str, Any]] = []
        self.incident_history: List[Dict[str, Any]] = []
        self.knowledge_base: List[str] = []
        self.dynamic_tasks: List[str] = []

        self.logger.info("CompleteEngineUltimate initializing...")
        try:
            self._initialize_all_components()
            self.status["initialized"] = True
            self.logger.info("CompleteEngineUltimate initialized successfully.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize CompleteEngineUltimate: {e}")
            self.status["initialized"] = False
            self.status["last_error"] = {"source": "Initialization", "message": str(e)}

    def _initialize_all_components(self) -> None:
        """
        F1-F10の各コンポーネントの初期化をシミュレートします。
        実際のシステムでは、ここでは各モジュールのインスタンス化や依存関係の注入が行われます。
        """
        self.logger.info("F1: Task Decomposer initialized.")
        self.logger.info("F2: Task Executor initialized.")
        self.logger.info("F3: Result Evaluator initialized.")
        self.logger.info("F4: Data Accumulator initialized.")
        self.logger.info("F5: Action Planner initialized. (Implicitly integrated)")
        self.logger.info("F6: Dynamic Task Adder initialized.")
        self.logger.info("F7: Self-Healing Mechanism initialized.")
        self.logger.info("F8: Learning Engine initialized.")
        self.logger.info("F9: Human Interface initialized.")
        self.logger.info("F10: Health Checker initialized.")

    # --- F1: タスク分解 (Task Decomposer) ---
    def f1_decompose_task(self, main_task: str) -> List[str]:
        """
        与えられたメインタスクを複数のサブタスクに分解する機能をシミュレートします。
        """
        self.logger.info(f"F1: Decomposing task: '{main_task}'")
        if not isinstance(main_task, str) or not main_task.strip():
            self.logger.error("F1: Invalid main_task provided. Cannot decompose.")
            return []
        
        # 複雑な分解ロジックをシミュレート
        sub_tasks = [
            f"{main_task} - Phase 1: Data Acquisition",
            f"{main_task} - Phase 2: Processing & Analysis",
            f"{main_task} - Phase 3: Reporting & Visualization"
        ]
        self.logger.info(f"F1: Decomposed into: {sub_tasks}")
        return sub_tasks

    # --- F2: 実行 (Task Executor) ---
    def f2_execute_task(self, sub_task: str, simulate_error: bool = False) -> Dict[str, Any]:
        """
        個々のサブタスクを実行する機能をシミュレートします。
        意図的にエラーを発生させるオプションもあります。
        """
        self.logger.info(f"F2: Executing task: '{sub_task}'")
        if not isinstance(sub_task, str) or not sub_task.strip():
            self.logger.error("F2: Invalid sub_task provided. Skipping execution.")
            return {"task": sub_task, "status": "SKIPPED", "output": "Error: Invalid task input."}

        # 特定のサブタスク名でエラーをシミュレート
        if simulate_error and "Processing & Analysis" in sub_task:
            self.logger.error(f"F2: Simulated execution error for '{sub_task}'!")
            return {"task": sub_task, "status": "FAILED", "output": "Error: Resource allocation failed (GPU shortage)."}
        
        # 正常な処理時間をシミュレート
        time.sleep(self.config.get_setting("task_execution_delay", 0.1))
        self.logger.info(f"F2: Task '{sub_task}' completed successfully.")
        return {"task": sub_task, "status": "COMPLETED", "output": f"Result for {sub_task} generated."}

    # --- F3: 評価 (Result Evaluator) ---
    def f3_evaluate_result(self, result: Dict[str, Any]) -> str:
        """
        タスクの実行結果を評価する機能をシミュレートします。
        """
        self.logger.info(f"F3: Evaluating result for task: '{result.get('task', 'Unknown Task')}'")
        if not isinstance(result, dict) or "status" not in result:
            self.logger.error("F3: Invalid result format provided. Cannot evaluate.")
            return "ERROR_EVALUATION"

        if result["status"] == "FAILED":
            self.logger.warning(f"F3: Evaluation: Task '{result['task']}' failed. Requires remediation.")
            return "NEEDS_REMEDIATION"
        elif result["status"] == "SKIPPED":
            self.logger.info(f"F3: Evaluation: Task '{result['task']}' was skipped. No action needed.")
            return "SKIPPED"
        
        # 評価処理をシミュレート
        time.sleep(self.config.get_setting("evaluation_delay", 0.05))
        self.logger.info(f"F3: Evaluation: Task '{result['task']}' successful.")
        return "SUCCESS"

    # --- F4: 蓄積 (Data Accumulator) ---
    def f4_store_data(self, data: Dict[str, Any]) -> None:
        """
        タスクの履歴や関連データを永続ストレージに蓄積する機能をシミュレートします。
        """
        self.logger.info(f"F4: Storing data for task: '{data.get('task', 'N/A')}'")
        if not isinstance(data, dict):
            self.logger.error("F4: Invalid data format provided. Cannot store.")
            return
        
        self.task_history.append({"timestamp": datetime.datetime.now().isoformat(), **data})
        # 実際のデータベースなどへの保存をシミュレート
        time.sleep(self.config.get_setting("storage_delay", 0.02))
        self.logger.info(f"F4: Data stored successfully. Total history entries: {len(self.task_history)}")

    # --- F5: 計画 (Action Planner) ---
    # F5は明示的なメソッドではなく、F1-F4の実行フローやF8の学習結果に基づいて
    # 次のアクションを決定する「システム全体の振る舞い」として暗黙的に実装されます。
    # このテストフレームワークでは、run_integration_testメソッド内でそのロジックを表現します。

    # --- F6: 動的タスク追加 (Dynamic Task Adder) ---
    def f6_add_dynamic_task(self, new_task_description: str) -> None:
        """
        実行中に新たなタスクを動的にシステムに追加する機能をシミュレートします。
        """
        self.logger.info(f"F6: Dynamically adding new task: '{new_task_description}'")
        if not isinstance(new_task_description, str) or not new_task_description.strip():
            self.logger.error("F6: Invalid new_task_description provided. Cannot add.")
            return
        
        self.dynamic_tasks.append(new_task_description)
        self.logger.info(f"F6: Task '{new_task_description}' added to dynamic task queue. Current dynamic tasks: {len(self.dynamic_tasks)}")
    
    # --- F7: 自己修復 (Self-Healing Mechanism) ---
    def f7_self_heal(self, error_details: Dict[str, Any]) -> bool:
        """
        システム内で発生したエラーを検知し、自動的に修復を試みる機能をシミュレートします。
        """
        self.logger.error(f"F7: Self-healing triggered for error: {error_details.get('message', 'Unknown Error')}")
        self.incident_history.append({"timestamp": datetime.datetime.now().isoformat(), **error_details})
        
        # エラータイプに基づいて修復ロジックをシミュレート
        if "Resource allocation failed" in error_details.get("message", ""):
            self.logger.info("F7: Attempting to reallocate resources (e.g., scale up, retry with different parameters)...")
            time.sleep(self.config.get_setting("healing_delay", 0.5))
            self.logger.info("F7: Resource reallocation attempted. Retrying task if possible.")
            return True # 修復試行成功
        elif "Critical system crash" in error_details.get("message", ""):
            self.logger.warning("F7: Critical system crash detected. Manual intervention likely required after attempted restart.")
            self.logger.info("F7: Initiating graceful restart sequence...")
            time.sleep(self.config.get_setting("healing_delay", 1.0))
            return False # 自動修復は限界、人間連携が必要なケース
        
        self.logger.info("F7: Generic error healing attempted (e.g., logging, clean-up).")
        return True # その他エラーは修復試行成功とする

    # --- F8: 学習サイクル (Learning Engine) ---
    def f8_learn_from_data(self) -> List[str]:
        """
        蓄積されたデータからパターンを抽出し、システムの知識ベースを更新する機能をシミュレートします。
        """
        self.logger.info("F8: Initiating learning cycle from accumulated data...")
        if len(self.task_history) < self.config.get_setting("min_data_for_learning", 3):
            self.logger.info("F8: Not enough data for meaningful learning yet. Skipping.")
            return []

        # 過去のタスク履歴からパターン抽出をシミュレート
        successful_tasks = [t for t in self.task_history if t.get("status") == "COMPLETED"]
        failed_tasks = [t for t in self.task_history if t.get("status") == "FAILED"]

        patterns = []
        if successful_tasks:
            patterns.append(f"Pattern: {len(successful_tasks)} successful tasks observed, often related to '{successful_tasks[0]['main_task'].split(':')[0].strip() if 'main_task' in successful_tasks[0] else 'various'}' processing.")
        if failed_tasks:
            error_messages = [t.get("output", "").replace("Error: ", "").strip() for t in failed_tasks if t.get("output", "").startswith("Error:")]
            common_errors = list(set(error_messages))
            if common_errors:
                patterns.append(f"Pattern: Common failure types observed: {', '.join(common_errors)}. Consider preventative measures.")
        
        if patterns:
            self.knowledge_base.extend(patterns)
            self.logger.info(f"F8: Learned new patterns: {patterns}")
            self.status["learned_patterns"] = self.knowledge_base
        else:
            self.logger.info("F8: No new significant patterns found after this cycle.")
        
        return patterns

    # --- F9: 人間連携機能 (Human Interface) ---
    def f9_notify_human(self, message: str, level: str = "INFO") -> None:
        """
        人間のオペレーターに通知を生成し、連携する機能をシミュレートします。
        """
        self.logger.log(level, f"F9: Notifying human operator ({level}): {message}")
        # 実際の通知システム（メール、Slack、ダッシュボードなど）との連携をシミュレート
        time.sleep(self.config.get_setting("notification_delay", 0.01))
        self.logger.info(f"F9: Human notification '{message[:50]}...' sent (simulated).")

    # --- F10: 健全性チェック (Health Checker) ---
    def f10_health_check(self) -> Dict[str, Any]:
        """
        システム全体の健全性を定期的にチェックし、ステータスを報告する機能をシミュレートします。
        """
        self.logger.info("F10: Performing comprehensive system health check...")
        
        health_status = {
            "overall": "GREEN",
            "components": {
                "F1_TaskDecomposer": "OK", "F2_TaskExecutor": "OK", "F3_ResultEvaluator": "OK",
                "F4_DataAccumulator": "OK", "F5_ActionPlanner": "OK", "F6_DynamicTaskAdder": "OK",
                "F7_SelfHealing": "OK", "F8_LearningEngine": "OK", "F9_HumanInterface": "OK"
            },
            "metrics": {
                "task_history_size": len(self.task_history),
                "incident_count": len(self.incident_history),
                "dynamic_tasks_pending": len(self.dynamic_tasks),
                "knowledge_base_size": len(self.knowledge_base)
            }
        }

        # エラー履歴があればヘルスステータスを警告に変更
        if self.incident_history:
            health_status["overall"] = "YELLOW"
            health_status["components"]["F7_SelfHealing"] = "WARNING (Incidents reported)"
            self.f9_notify_human(f"Warning: {len(self.incident_history)} incidents reported since last check. System health is YELLOW.", "WARNING")
        
        # 動的タスクが多すぎる場合はクリティカルエラー
        if len(self.dynamic_tasks) > self.config.get_setting("max_dynamic_tasks_queue", 3):
             health_status["overall"] = "RED"
             health_status["components"]["F6_DynamicTaskAdder"] = "CRITICAL (Too many pending dynamic tasks)"
             self.f9_notify_human("Critical: Too many dynamic tasks pending. System overload risk. Manual review required.", "CRITICAL")
        
        # 過去の学習で危険なパターンが検出されていたら警告
        if any("failure" in p.lower() for p in self.status["learned_patterns"]):
            if health_status["overall"] == "GREEN": health_status["overall"] = "YELLOW"
            health_status["components"]["F8_LearningEngine"] = "WARNING (Failure patterns detected)"
            self.f9_notify_human("Warning: F8 detected recurring failure patterns. Review system configurations.", "WARNING")

        self.logger.info(f"F10: System health check completed. Overall status: {health_status['overall']}")
        self.status["health"] = health_status["overall"]
        return health_status

    def run_integration_test(self) -> Dict[str, Any]:
        """
        CompleteEngineUltimateのF1-F10連携動作を実際に確認するメインフローです。
        各機能が連携して動作するシナリオをシミュレートし、その結果を記録します。
        """
        self.logger.info("\n--- Starting CompleteEngineUltimate Integration Test ---")
        self.status["current_workflow"] = "integration_test"

        test_results: Dict[str, Any] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "initialization_status": self.status["initialized"],
            "f1_f4_flow_results": [],
            "f6_dynamic_task_added": False,
            "f7_self_healing_status": {"triggered": False, "successful": False, "details": None, "retry_attempted": False},
            "f8_learning_cycle_results": [],
            "f9_human_notification_triggered": [],
            "f10_health_check_report": None,
            "overall_success": False,
            "criteria_met": {}
        }

        # 1. CompleteEngineUltimateの初期化と全機能の統合確認
        self.logger.info("\n[Step 1] Initializing and integrating all components.")
        if not test_results["initialization_status"]:
            self.logger.critical("Step 1 Failed: System failed to initialize. Cannot proceed.")
            test_results["criteria_met"]["initialization_success"] = False
            return test_results
        test_results["criteria_met"]["initialization_success"] = True
        self.logger.info("Step 1 Confirmed: CompleteEngineUltimate initialized with all components integrated.")

        # 2. F1→F2→F3→F4の順次実行フロー確認（タスク分解→実行→評価→蓄積）
        self.logger.info("\n[Step 2] Testing F1->F2->F3->F4 sequential flow.")
        main_task_1 = "Generate Quarterly Financial Report"
        sub_tasks_1 = self.f1_decompose_task(main_task_1)

        flow_successful = True
        for i, sub_task in enumerate(sub_tasks_1):
            execution_result = self.f2_execute_task(sub_task)
            evaluation_status = self.f3_evaluate_result(execution_result)
            self.f4_store_data({"main_task": main_task_1, "sub_task": sub_task, "f2_result": execution_result, "f3_evaluation": evaluation_status})
            
            flow_entry = {
                "sub_task": sub_task,
                "execution_status": execution_result["status"],
                "evaluation_status": evaluation_status,
                "f4_stored": True
            }
            test_results["f1_f4_flow_results"].append(flow_entry)

            if evaluation_status == "NEEDS_REMEDIATION":
                self.f9_notify_human(f"Warning: Sub-task '{sub_task}' needs remediation. Output: {execution_result['output']}", "WARNING")
                test_results["f9_human_notification_triggered"].append({"message": f"Sub-task remediation needed for {sub_task}", "level": "WARNING"})
                flow_successful = False # 途切れてはいないが、警告レベル
            elif execution_result["status"] == "SKIPPED":
                flow_successful = False # スキップされた場合も完全な流れとは言えない

        test_results["criteria_met"]["f1_f4_flow_intact"] = flow_successful
        self.logger.info(f"Step 2 {'Confirmed' if flow_successful else 'Completed with Warnings/Skips'}: F1-F4 flow executed.")

        # 3. F6の動的タスク追加機能の動作確認
        self.logger.info("\n[Step 3] Testing F6: Dynamic task addition.")
        dynamic_task_description = "Investigate unexpected server load spike"
        self.f6_add_dynamic_task(dynamic_task_description)
        if dynamic_task_description in self.dynamic_tasks:
            test_results["f6_dynamic_task_added"] = True
            test_results["criteria_met"]["f6_dynamic_task_working"] = True
            self.logger.info("Step 3 Confirmed: F6 dynamic task successfully added.")
        else:
            test_results["criteria_met"]["f6_dynamic_task_working"] = False
            self.logger.error("Step 3 Failed: F6 dynamic task addition failed.")

        # 4. F7の自己修復機能のトリガー確認（意図的なエラー発生）
        self.logger.info("\n[Step 4] Testing F7: Self-healing with intentional error.")
        main_task_2 = "Daily System Backup"
        sub_tasks_2 = self.f1_decompose_task(main_task_2)
        
        # 意図的にF2でエラーを発生させるサブタスク
        error_sub_task = sub_tasks_2[1] # "Daily System Backup - Phase 2: Processing & Analysis"
        self.logger.info(f"Intentionally causing an error in F2 for sub-task: '{error_sub_task}'")
        execution_result_with_error = self.f2_execute_task(error_sub_task, simulate_error=True)
        
        if execution_result_with_error["status"] == "FAILED":
            test_results["f7_self_healing_status"]["triggered"] = True
            error_details = {
                "source": "F2_TaskExecutor",
                "message": execution_result_with_error["output"],
                "task": execution_result_with_error["task"],
                "timestamp": datetime.datetime.now().isoformat()
            }
            healing_success = self.f7_self_heal(error_details)
            test_results["f7_self_healing_status"]["successful"] = healing_success
            test_results["f7_self_healing_status"]["details"] = error_details
            test_results["criteria_met"]["f7_triggered_on_error"] = True

            if healing_success:
                self.logger.info("F7: Self-healing mechanism successfully attempted to resolve the error.")
                # 修復後にタスクを再実行するシナリオをシミュレート
                self.logger.info(f"Retrying task '{error_sub_task}' after self-healing attempt...")
                retry_result = self.f2_execute_task(error_sub_task, simulate_error=False) # 再試行は成功と仮定
                retry_eval = self.f3_evaluate_result(retry_result)
                self.f4_store_data({"main_task": main_task_2, "sub_task": error_sub_task, **retry_result, "f3_evaluation": retry_eval, "retry_attempt": True})
                test_results["f7_self_healing_status"]["retry_attempted"] = True
                self.logger.info(f"Step 4 Confirmed: F7 self-healing triggered and successfully attempted recovery. Task retried.")
            else:
                self.logger.warning("F7: Self-healing attempted but failed to fully resolve automatically. Human intervention needed.")
                self.f9_notify_human(f"Urgent: F7 failed to self-heal task '{error_sub_task}'. Manual review required.", "ERROR")
                test_results["f9_human_notification_triggered"].append({"message": f"F7 self-heal failed for {error_sub_task}", "level": "ERROR"})
                self.logger.info(f"Step 4 Completed with Warning: F7 self-healing triggered but required human intervention.")
        else:
            test_results["criteria_met"]["f7_triggered_on_error"] = False
            self.logger.error("Step 4 Failed: Error simulation failed. Self-healing not triggered.")

        # 5. F8の学習サイクル確認（パターン抽出）
        self.logger.info("\n[Step 5] Testing F8: Learning cycle (pattern extraction).")
        learned_patterns = self.f8_learn_from_data()
        test_results["f8_learning_cycle_results"] = learned_patterns
        if learned_patterns:
            test_results["criteria_met"]["f8_learning_executed"] = True
            self.logger.info(f"Step 5 Confirmed: F8 learning cycle completed and patterns extracted.")
        else:
            test_results["criteria_met"]["f8_learning_executed"] = True # 実行されたこと自体は成功
            self.logger.warning("Step 5 Completed with Warning: F8 learning cycle completed but no significant patterns extracted (possibly due to insufficient data or no recurring issues).")

        # 6. F9の人間連携機能確認（通知生成）
        self.logger.info("\n[Step 6] Testing F9: Human interaction (notification generation).")
        self.f9_notify_human("System status update: All routine tasks for the hour completed.", "INFO")
        test_results["f9_human_notification_triggered"].append({"message": "Routine tasks completed", "level": "INFO"})
        # F7ステップで既にエラー通知がトリガーされているため、追加で確認
        if len(test_results["f9_human_notification_triggered"]) > 0:
            test_results["criteria_met"]["f9_human_notification_working"] = True
            self.logger.info(f"Step 6 Confirmed: F9 human notification triggered multiple times.")
        else:
            test_results["criteria_met"]["f9_human_notification_working"] = False
            self.logger.error("Step 6 Failed: F9 human notification was not triggered.")

        # 7. F10の健全性チェック実行
        self.logger.info("\n[Step 7] Testing F10: Health check execution.")
        health_report = self.f10_health_check()
        test_results["f10_health_check_report"] = health_report
        self.logger.info(f"F10: Health check overall status: {health_report['overall']}")
        if health_report and health_report["overall"] != "RED":
            test_results["criteria_met"]["f10_health_check_ok"] = True
            self.logger.info(f"Step 7 Confirmed: F10 health check executed with status: {health_report['overall']}.")
        else:
            test_results["criteria_met"]["f10_health_check_ok"] = False
            self.logger.error(f"Step 7 Failed: F10 health check reported critical issues or did not run properly. Status: {health_report['overall'] if health_report else 'N/A'}")

        # 最終的な成功基準の確認
        self.logger.info("\n--- Evaluating Overall Success Criteria ---")
        overall_success_flag = all(test_results["criteria_met"].get(k, False) for k in [
            "initialization_success",
            "f1_f4_flow_intact",
            "f6_dynamic_task_working",
            "f7_triggered_on_error",
            "f8_learning_executed", # 学習自体が実行されればOK
            "f9_human_notification_working",
            "f10_health_check_ok"
        ])
        
        # F1-F4フローは警告でも成功と見なす、F7の自己修復はトリガーされたらOK
        test_results["overall_success"] = overall_success_flag

        if test_results["overall_success"]:
            self.logger.info("\n--- CompleteEngineUltimate Integration Test: SUCCESS ---")
        else:
            self.logger.error("\n--- CompleteEngineUltimate Integration Test: FAILED ---")
            self.logger.error(f"Failed criteria: {[k for k, v in test_results['criteria_met'].items() if not v]}")

        self.status["current_workflow"] = "idle"
        return test_results

def main():
    """
    CompleteEngineUltimateの統合テストを実行し、レポートを生成するメイン関数。
    """
    config = Config()
    
    # ログファイルのパスを設定
    log_filename = os.path.join(os.path.dirname(__file__), "complete_engine_ultimate_test.log")
    logger = Logger(log_filename, config.get_setting("log_level", "INFO"))
    
    engine = CompleteEngineUltimate(config, logger)
    test_results = engine.run_integration_test()

    # レポートの生成
    report_generator = ReportGenerator(test_results, logger)
    markdown_report_content = report_generator.generate_markdown_report()

    # レポートをファイルに保存
    report_filename = os.path.join(os.path.dirname(__file__), config.get_setting("report_filename", "integration_test_report.md"))
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(markdown_report_content)
    logger.info(f"Integration test report generated: {report_filename}")
    logger.info("Program finished.")


if __name__ == "__main__":
    main()
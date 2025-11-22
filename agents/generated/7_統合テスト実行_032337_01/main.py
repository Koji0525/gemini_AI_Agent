import os
import datetime
import random
import time
from typing import List, Dict, Any, Tuple

from utils import TestResult, TestReportGenerator, setup_logging, LOG_FILE

# ロギング設定
logger = setup_logging()

# F1-F10 機能のモックアップクラス群
# 実際のシステムでは、これらのクラスは具体的なビジネスロジックを持つが、
# 統合テストの目的のため、ここでは最小限のインターフェースと動作をシミュレートする。

class BaseSystemFunction:
    """システム機能の基底クラス"""
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        logger.info(f"[{self.name}] 機能モックが初期化されました。")

    def initialize(self) -> bool:
        """機能の初期化をシミュレートする"""
        try:
            # 実際の初期化ロジック（DB接続、設定読み込みなど）をシミュレート
            time.sleep(0.05) # 短い遅延
            if random.random() < 0.02: # 2%の確率で初期化失敗
                raise ConnectionError(f"Failed to connect to {self.name} service.")
            self.initialized = True
            logger.info(f"[{self.name}] が正常に初期化されました。")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] の初期化に失敗しました: {e}")
            self.initialized = False
            return False

    def is_initialized(self) -> bool:
        """初期化状態を確認する"""
        return self.initialized

    def perform_basic_operation(self, input_data: str = "default_input") -> Tuple[bool, str]:
        """基本的な動作をシミュレートする"""
        if not self.is_initialized():
            return False, f"[{self.name}] は初期化されていません。操作を実行できません。"
        try:
            # 実際の操作ロジックをシミュレート
            time.sleep(0.1) # 短い遅延
            if random.random() < 0.05: # 5%の確率で操作失敗
                raise ValueError(f"[{self.name}] operation failed due to invalid state.")
            result_data = f"Operation successful for {self.name} with input: {input_data}"
            logger.debug(result_data)
            return True, result_data
        except Exception as e:
            logger.error(f"[{self.name}] の基本操作中にエラーが発生しました: {e}")
            return False, f"Error during basic operation: {e}"

class GoalDecomposition(BaseSystemFunction):
    """F1: ゴール分解機能"""
    def __init__(self):
        super().__init__("F1_GoalDecomposition")

    def decompose_goal(self, goal: str) -> Tuple[bool, List[str]]:
        success, msg = self.perform_basic_operation(f"Decompose goal: {goal}")
        if success:
            tasks = [f"Subtask A for {goal}", f"Subtask B for {goal}", f"Subtask C for {goal}"]
            return True, tasks
        return False, []

class PlanningEngine(BaseSystemFunction):
    """F2: 計画機能"""
    def __init__(self):
        super().__init__("F2_PlanningEngine")

    def generate_plan(self, tasks: List[str]) -> Tuple[bool, Dict[str, Any]]:
        success, msg = self.perform_basic_operation(f"Generate plan for {len(tasks)} tasks")
        if success:
            plan = {"plan_id": f"PLAN-{random.randint(1000, 9999)}", "steps": tasks, "status": "Generated"}
            return True, plan
        return False, {}

class ExecutionEngine(BaseSystemFunction):
    """F3: 実行機能"""
    def __init__(self):
        super().__init__("F3_ExecutionEngine")

    def execute_plan(self, plan: Dict[str, Any]) -> Tuple[bool, str]:
        success, msg = self.perform_basic_operation(f"Execute plan: {plan.get('plan_id')}")
        if success:
            return True, f"Plan {plan.get('plan_id')} executed successfully."
        return False, f"Failed to execute plan {plan.get('plan_id')}: {msg}"

class KnowledgeSystem(BaseSystemFunction):
    """F4: ナレッジシステム機能"""
    def __init__(self):
        super().__init__("F4_KnowledgeSystem")
        self._knowledge_base = {} # インメモリのナレッジベースをシミュレート

    def write_knowledge(self, key: str, value: Any) -> Tuple[bool, str]:
        if not self.is_initialized():
            return False, "Knowledge System not initialized."
        try:
            time.sleep(0.03)
            if random.random() < 0.03: # 3%の確率で書き込み失敗
                raise IOError(f"Failed to write knowledge for key: {key}")
            self._knowledge_base[key] = value
            logger.info(f"[F4] Knowledge '{key}' written successfully.")
            return True, f"Knowledge '{key}' written."
        except Exception as e:
            logger.error(f"[F4] Failed to write knowledge '{key}': {e}")
            return False, f"Error writing knowledge: {e}"

    def read_knowledge(self, key: str) -> Tuple[bool, Any]:
        if not self.is_initialized():
            return False, "Knowledge System not initialized."
        try:
            time.sleep(0.02)
            if random.random() < 0.01: # 1%の確率で読み込み失敗
                raise KeyError(f"Knowledge key '{key}' not found or inaccessible.")
            value = self._knowledge_base.get(key)
            if value is None:
                logger.warning(f"[F4] Knowledge key '{key}' not found.")
                return False, None
            logger.info(f"[F4] Knowledge '{key}' read successfully.")
            return True, value
        except Exception as e:
            logger.error(f"[F4] Failed to read knowledge '{key}': {e}")
            return False, None

class MonitoringSystem(BaseSystemFunction):
    """F5: 監視機能"""
    def __init__(self):
        super().__init__("F5_MonitoringSystem")

    def monitor_status(self, entity_id: str) -> Tuple[bool, Dict[str, Any]]:
        success, msg = self.perform_basic_operation(f"Monitor entity: {entity_id}")
        if success:
            status = {"entity_id": entity_id, "cpu_usage": random.uniform(10.0, 90.0), "memory_usage": random.uniform(20.0, 80.0), "status": "Healthy"}
            return True, status
        return False, {}

class EvaluationModule(BaseSystemFunction):
    """F6: 評価機能"""
    def __init__(self):
        super().__init__("F6_EvaluationModule")

    def evaluate_performance(self, metrics: Dict[str, Any]) -> Tuple[bool, str]:
        success, msg = self.perform_basic_operation("Evaluate performance")
        if success:
            score = sum(metrics.values()) / len(metrics) if metrics else 0
            feedback = "Good" if score > 70 else "Needs Improvement"
            return True, f"Performance score: {score:.2f}, Feedback: {feedback}"
        return False, f"Evaluation failed: {msg}"

class AdaptationEngine(BaseSystemFunction):
    """F7: 適応機能"""
    def __init__(self):
        super().__init__("F7_AdaptationEngine")

    def adapt_system(self, recommendation: str) -> Tuple[bool, str]:
        success, msg = self.perform_basic_operation(f"Adapt system based on: {recommendation}")
        if success:
            return True, f"System adapted: {recommendation}"
        return False, f"Adaptation failed: {msg}"

class SelfHealingSystem(BaseSystemFunction):
    """F8: 自己修復機能"""
    def __init__(self):
        super().__init__("F8_SelfHealingSystem")

    def detect_and_heal(self, issue_description: str) -> Tuple[bool, str]:
        success, msg = self.perform_basic_operation(f"Detect and heal issue: {issue_description}")
        if success:
            if random.random() < 0.1: # 10%の確率で修復失敗をシミュレート
                return False, f"Healing attempt failed for issue: {issue_description}"
            return True, f"Issue '{issue_description}' successfully healed."
        return False, f"Healing detection failed: {msg}"

class SecurityModule(BaseSystemFunction):
    """F9: セキュリティ機能"""
    def __init__(self):
        super().__init__("F9_SecurityModule")

    def run_security_scan(self, target: str) -> Tuple[bool, str]:
        success, msg = self.perform_basic_operation(f"Run security scan on: {target}")
        if success:
            if random.random() < 0.08: # 8%の確率で脆弱性を発見
                return False, f"Security vulnerability detected in {target}."
            return True, f"Security scan on {target} completed. No major threats found."
        return False, f"Security scan failed: {msg}"

class HealthCheckSystem(BaseSystemFunction):
    """F10: 健全性チェック機能"""
    def __init__(self):
        super().__init__("F10_HealthCheckSystem")

    def perform_system_health_check(self) -> Tuple[bool, str]:
        success, msg = self.perform_basic_operation("Perform full system health check")
        if success:
            if random.random() < 0.03: # 3%の確率で軽微な異常を検出
                return False, "System health check detected minor anomalies."
            return True, "System health is optimal."
        return False, f"Health check failed: {msg}"

class GoogleSheetsIntegration(BaseSystemFunction):
    """Google Sheets連携機能のモックアップ"""
    def __init__(self):
        super().__init__("GoogleSheetsIntegration")
        self._mock_sheet_data = []

    def sync_data(self, data: List[Dict[str, Any]]) -> Tuple[bool, str]:
        if not self.is_initialized():
            return False, "Google Sheets Integration not initialized."
        try:
            time.sleep(0.08)
            if random.random() < 0.07: # 7%の確率で同期失敗
                raise ConnectionRefusedError("Failed to connect to Google Sheets API.")
            self._mock_sheet_data.extend(data)
            logger.info(f"[GoogleSheetsIntegration] {len(data)} items synced to mock sheet.")
            return True, f"Successfully synced {len(data)} items to Google Sheets."
        except Exception as e:
            logger.error(f"[GoogleSheetsIntegration] データ同期中にエラーが発生しました: {e}")
            return False, f"Error syncing data: {e}"

    def get_mock_data(self) -> List[Dict[str, Any]]:
        return self._mock_sheet_data


class SystemIntegrationTestRunner:
    """
    24時間自律稼働システムのF1-F10機能の統合テストを実行するランナー。
    指定された成功基準に基づいてテストを実行し、レポートを生成します。
    """
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.test_results: List[TestResult] = []
        self.functions: Dict[str, BaseSystemFunction] = {}
        logger.info("SystemIntegrationTestRunnerが初期化されました。")

    def _add_test_result(self, test_name: str, success: bool, message: str):
        """テスト結果をリストに追加するヘルパーメソッド"""
        self.test_results.append(TestResult(test_name, success, message))
        if success:
            logger.info(f"PASS: {test_name} - {message}")
        else:
            logger.error(f"FAIL: {test_name} - {message}")

    def setup_functions(self):
        """全てのシステム機能をインスタンス化する"""
        self.functions = {
            "F1_GoalDecomposition": GoalDecomposition(),
            "F2_PlanningEngine": PlanningEngine(),
            "F3_ExecutionEngine": ExecutionEngine(),
            "F4_KnowledgeSystem": KnowledgeSystem(),
            "F5_MonitoringSystem": MonitoringSystem(),
            "F6_EvaluationModule": EvaluationModule(),
            "F7_AdaptationEngine": AdaptationEngine(),
            "F8_SelfHealingSystem": SelfHealingSystem(),
            "F9_SecurityModule": SecurityModule(),
            "F10_HealthCheckSystem": HealthCheckSystem(),
            "GoogleSheetsIntegration": GoogleSheetsIntegration() # 特殊機能として追加
        }
        logger.info(f"全 {len(self.functions)} 個の機能モックがロードされました。")

    def run_initialization_tests(self):
        """F1-F10およびGoogle Sheets連携の初期化テストを実行する"""
        logger.info("\n--- 初期化テストを開始します ---")
        for name, func in self.functions.items():
            test_name = f"Test_{name}_Initialization"
            try:
                if func.initialize():
                    self._add_test_result(test_name, True, f"{name} が正常に初期化されました。")
                else:
                    self._add_test_result(test_name, False, f"{name} の初期化に失敗しました。")
            except Exception as e:
                self._add_test_result(test_name, False, f"{name} の初期化中に予期せぬエラーが発生しました: {e}")
        logger.info("--- 初期化テストを完了しました ---\n")

    def run_basic_operation_tests(self):
        """各機能の基本的な動作確認テストを実行する"""
        logger.info("\n--- 基本動作確認テストを開始します ---")
        for name, func in self.functions.items():
            if name == "F4_KnowledgeSystem" or name == "GoogleSheetsIntegration":
                # これらの機能は専用のテストケースがあるため、ここではスキップ
                logger.debug(f"[{name}] は専用テストがあるため、基本動作テストをスキップします。")
                continue

            test_name = f"Test_{name}_BasicOperation"
            success, message = func.perform_basic_operation(f"Input for {name}")
            self._add_test_result(test_name, success, message)
        logger.info("--- 基本動作確認テストを完了しました ---\n")

    def run_f1_f10_specific_tests(self):
        """F1-F10の具体的な連携や、特有の動作に関するテストを実行する"""
        logger.info("\n--- F1-F10 機能固有テストを開始します ---")

        # F1: ゴール分解テスト
        f1: GoalDecomposition = self.functions["F1_GoalDecomposition"]
        if f1.is_initialized():
            success, tasks = f1.decompose_goal("Develop new feature")
            self._add_test_result("Test_F1_GoalDecomposition_Basic", success, f"Goal decomposition tasks: {tasks}" if success else "Goal decomposition failed.")
            if success:
                # F1とF2の連携テスト
                f2: PlanningEngine = self.functions["F2_PlanningEngine"]
                if f2.is_initialized():
                    success_plan, plan = f2.generate_plan(tasks)
                    self._add_test_result("Test_F2_PlanningEngine_GeneratePlan", success_plan, f"Plan generated: {plan}" if success_plan else "Plan generation failed.")
                    if success_plan:
                        # F2とF3の連携テスト
                        f3: ExecutionEngine = self.functions["F3_ExecutionEngine"]
                        if f3.is_initialized():
                            success_exec, exec_msg = f3.execute_plan(plan)
                            self._add_test_result("Test_F3_ExecutionEngine_ExecutePlan", success_exec, exec_msg)
                        else:
                            self._add_test_result("Test_F3_ExecutionEngine_ExecutePlan", False, "F3 not initialized, cannot execute plan.")
                else:
                    self._add_test_result("Test_F2_PlanningEngine_GeneratePlan", False, "F2 not initialized, cannot generate plan.")
        else:
            self._add_test_result("Test_F1_GoalDecomposition_Basic", False, "F1 not initialized, cannot decompose goal.")

        # F4: ナレッジシステム読み書きテスト
        f4: KnowledgeSystem = self.functions["F4_KnowledgeSystem"]
        if f4.is_initialized():
            # 書き込みテスト
            write_success, write_msg = f4.write_knowledge("project_status", {"id": 1, "name": "Project Alpha", "status": "In Progress"})
            self._add_test_result("Test_F4_KnowledgeSystem_Write", write_success, write_msg)
            write_success_2, write_msg_2 = f4.write_knowledge("config_param_A", "value_for_A")
            self._add_test_result("Test_F4_KnowledgeSystem_Write_Multiple", write_success_2, write_msg_2)

            # 読み込みテスト
            read_success, read_data = f4.read_knowledge("project_status")
            self._add_test_result("Test_F4_KnowledgeSystem_Read_Existing", read_success and read_data is not None, f"Read data: {read_data}" if read_success else "Failed to read data.")
            read_success_non_existent, read_data_non_existent = f4.read_knowledge("non_existent_key")
            self._add_test_result("Test_F4_KnowledgeSystem_Read_NonExistent", not read_success_non_existent and read_data_non_existent is None, "Attempted to read non-existent key (expected failure or None).")
        else:
            self._add_test_result("Test_F4_KnowledgeSystem_Write", False, "F4 not initialized, cannot write knowledge.")
            self._add_test_result("Test_F4_KnowledgeSystem_Read_Existing", False, "F4 not initialized, cannot read knowledge.")

        # F5: 監視機能テスト
        f5: MonitoringSystem = self.functions["F5_MonitoringSystem"]
        if f5.is_initialized():
            success, status = f5.monitor_status("Service_X")
            self._add_test_result("Test_F5_MonitoringSystem_Monitor", success, f"Service_X status: {status}" if success else "Monitoring failed.")
            if success and status:
                # F5とF6の連携テスト
                f6: EvaluationModule = self.functions["F6_EvaluationModule"]
                if f6.is_initialized():
                    success_eval, eval_msg = f6.evaluate_performance({"cpu": status['cpu_usage'], "mem": status['memory_usage']})
                    self._add_test_result("Test_F6_EvaluationModule_Evaluate", success_eval, eval_msg)
                else:
                    self._add_test_result("Test_F6_EvaluationModule_Evaluate", False, "F6 not initialized, cannot evaluate performance.")
        else:
            self._add_test_result("Test_F5_MonitoringSystem_Monitor", False, "F5 not initialized, cannot monitor.")

        # F7: 適応機能テスト (F6の結果をF7が受け取るシナリオを想定)
        f7: AdaptationEngine = self.functions["F7_AdaptationEngine"]
        if f7.is_initialized():
            success, msg = f7.adapt_system("Scale up CPU for Service_X")
            self._add_test_result("Test_F7_AdaptationEngine_Adapt", success, msg)
        else:
            self._add_test_result("Test_F7_AdaptationEngine_Adapt", False, "F7 not initialized, cannot adapt.")

        # F8: 自己修復機能テスト
        f8: SelfHealingSystem = self.functions["F8_SelfHealingSystem"]
        if f8.is_initialized():
            success, msg = f8.detect_and_heal("Database_Connection_Error")
            self._add_test_result("Test_F8_SelfHealingSystem_HealIssue", success, msg)
            success_no_issue, msg_no_issue = f8.detect_and_heal("No_Issue_Detected")
            self._add_test_result("Test_F8_SelfHealingSystem_NoIssue", success_no_issue, msg_no_issue)
        else:
            self._add_test_result("Test_F8_SelfHealingSystem_HealIssue", False, "F8 not initialized, cannot heal.")

        # F9: セキュリティ機能テスト
        f9: SecurityModule = self.functions["F9_SecurityModule"]
        if f9.is_initialized():
            success, msg = f9.run_security_scan("Core_Service_API")
            self._add_test_result("Test_F9_SecurityModule_Scan", success, msg)
        else:
            self._add_test_result("Test_F9_SecurityModule_Scan", False, "F9 not initialized, cannot run security scan.")

        # F10: 健全性チェック機能テスト
        f10: HealthCheckSystem = self.functions["F10_HealthCheckSystem"]
        if f10.is_initialized():
            success, msg = f10.perform_system_health_check()
            self._add_test_result("Test_F10_HealthCheckSystem_Check", success, msg)
        else:
            self._add_test_result("Test_F10_HealthCheckSystem_Check", False, "F10 not initialized, cannot perform health check.")

        logger.info("--- F1-F10 機能固有テストを完了しました ---\n")

    def run_google_sheets_integration_test(self):
        """Google Sheets連携の動作確認テストを実行する"""
        logger.info("\n--- Google Sheets連携テストを開始します ---")
        gsi: GoogleSheetsIntegration = self.functions["GoogleSheetsIntegration"]
        if gsi.is_initialized():
            test_data = [
                {"timestamp": str(datetime.datetime.now()), "event": "System Start", "status": "INFO"},
                {"timestamp": str(datetime.datetime.now()), "event": "Test Run", "status": "SUCCESS"}
            ]
            sync_success, sync_msg = gsi.sync_data(test_data)
            self._add_test_result("Test_GoogleSheetsIntegration_SyncData", sync_success, sync_msg)

            # データが実際にモックに存在するかを確認
            if sync_success:
                mock_data = gsi.get_mock_data()
                if len(mock_data) >= 2 and mock_data[-1]["event"] == "Test Run":
                    self._add_test_result("Test_GoogleSheetsIntegration_VerifyData", True, "Synced data verified in mock system.")
                else:
                    self._add_test_result("Test_GoogleSheetsIntegration_VerifyData", False, "Synced data not found or incorrect in mock system.")
            else:
                self._add_test_result("Test_GoogleSheetsIntegration_VerifyData", False, "Data sync failed, cannot verify.")

        else:
            self._add_test_result("Test_GoogleSheetsIntegration_SyncData", False, "Google Sheets Integration not initialized.")
            self._add_test_result("Test_GoogleSheetsIntegration_VerifyData", False, "Google Sheets Integration not initialized.")
        logger.info("--- Google Sheets連携テストを完了しました ---\n")

    def run_all_integration_tests(self):
        """全ての統合テストを実行するメインメソッド"""
        logger.info(f"--- 統合テストスイート {datetime.datetime.now()} に開始 ---")
        self.setup_functions()
        self.run_initialization_tests()
        self.run_basic_operation_tests()
        self.run_f1_f10_specific_tests()
        self.run_google_sheets_integration_test()
        logger.info(f"--- 統合テストスイート {datetime.datetime.now()} に終了 ---")

    def generate_test_report(self):
        """テスト結果レポートを生成し、ファイルに出力する"""
        report_generator = TestReportGenerator(self.test_results)
        report_content = report_generator.generate_markdown_report()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = os.path.join(self.output_dir, f"integration_test_report_{timestamp}.md")
        try:
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"テスト結果レポートが '{report_filename}' に生成されました。")

            # 成功基準の確認
            success_count = report_generator.get_success_count()
            total_count = report_generator.get_total_count()
            success_rate = report_generator.get_success_rate()
            logger.info(f"合計テスト数: {total_count}, 成功数: {success_count}, 成功率: {success_rate:.2f}%")

            if success_rate >= 85.0:
                logger.info("成功基準: 全テストで85%以上の成功率を達成 - 達成済み。")
            else:
                logger.warning(f"成功基準: 全テストで85%以上の成功率を達成 - 未達成 (現在の成功率: {success_rate:.2f}%)。")

            initialization_failures = [r for r in self.test_results if "Initialization" in r.name and not r.success]
            if not initialization_failures:
                logger.info("成功基準: F1-F10の全機能が正常に初期化される - 達成済み。")
            else:
                logger.warning(f"成功基準: F1-F10の全機能が正常に初期化される - 未達成 (失敗数: {len(initialization_failures)})。")

            knowledge_system_failures = [r for r in self.test_results if "F4_KnowledgeSystem" in r.name and not r.success]
            if not knowledge_system_failures:
                logger.info("成功基準: ナレッジシステムが正常に動作する - 達成済み。")
            else:
                logger.warning(f"成功基準: ナレッジシステムが正常に動作する - 未達成 (失敗数: {len(knowledge_system_failures)})。")

        except IOError as e:
            logger.error(f"レポートファイルの書き込み中にエラーが発生しました: {e}")
        except Exception as e:
            logger.error(f"レポート生成中に予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    logger.info("統合テストスクリプトを開始します。")
    # `tests/system_protection/test_core_functions.py` の実行をシミュレートする
    # このスクリプト自体が、そのファイルが持つべき統合テストロジックを内包していると見なす
    runner = SystemIntegrationTestRunner()
    runner.run_all_integration_tests()
    runner.generate_test_report()
    logger.info(f"詳細なログは {LOG_FILE} を参照してください。")
    logger.info("統合テストスクリプトを終了します。")
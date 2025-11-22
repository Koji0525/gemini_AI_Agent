import os
import time
import json
import logging
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import datetime

# Assuming utils.py is in the same directory or accessible via sys.path
from utils import TestHistoryManager, analyze_test_stability, TestResult, simulate_test_run, run_test_with_retries, StaticCodeAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlakyTestDetector:
    """
    フラッキーテストを自動的に検出し、修正戦略を提案または適用するエンジン。
    テスト実行履歴の統計分析と、必要に応じた複数回実行による再現性確認を行う。
    """
    DEFAULT_CONFIG = {
        "db_path": "test_history.db",
        "flaky_threshold_failure_rate": 0.3, # 過去5回中2回以上失敗 (2/5 = 0.4) とすると、0.3はもっと低い頻度でも検出
        "flaky_threshold_min_runs": 5, # 検出のために必要な最小実行回数
        "rerun_confirmation_count": 3, # フラッキー判定後に再現性確認のために再実行する回数
        "rerun_failure_threshold": 1, # 再実行で何回失敗したらフラッキーと確定するか
        "duration_variance_threshold": 0.5, # 実行時間の標準偏差が平均の0.5倍を超えると異常とみなす
        "static_analysis_enabled": True
    }

    def __init__(self, config_path: str = None):
        """
        FlakyTestDetectorの初期化。
        設定ファイルがあればそれをロードし、なければデフォルト設定を使用する。
        """
        self.config = self.DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self.config.update(user_config)
                logger.info(f"Configuration loaded from {config_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse config file {config_path}: {e}. Using default configuration.")
            except Exception as e:
                logger.error(f"An unexpected error occurred while loading config file {config_path}: {e}. Using default configuration.")
        else:
            logger.info("No configuration file provided or found. Using default configuration.")

        self.history_manager = TestHistoryManager(self.config["db_path"])
        self.static_analyzer = StaticCodeAnalyzer()
        logger.info(f"Initialized FlakyTestDetector with DB: {self.config['db_path']}")

    def _determine_flakiness_candidate(self, test_id: str) -> Dict[str, Any]:
        """
        テスト実行履歴に基づいてフラッキーテストの候補を判定する。
        統計分析により、不安定なテストを特定する。
        """
        history = self.history_manager.get_test_history(test_id)
        if not history:
            return {"is_candidate": False, "reason": "No history available."}

        num_runs = len(history)
        if num_runs < self.config["flaky_threshold_min_runs"]:
            return {"is_candidate": False, "reason": f"Insufficient history ({num_runs}/{self.config['flaky_threshold_min_runs']} runs)."}

        analysis_results = analyze_test_stability(history)
        failure_rate = analysis_results["failure_rate"]
        duration_std_dev_ratio = analysis_results["duration_std_dev_ratio"]
        common_errors = analysis_results["common_errors"]

        reasons = []
        is_candidate = False

        if failure_rate > self.config["flaky_threshold_failure_rate"]:
            reasons.append(f"High failure rate ({failure_rate:.2f} > {self.config['flaky_threshold_failure_rate']:.2f}).")
            is_candidate = True

        if duration_std_dev_ratio > self.config["duration_variance_threshold"]:
            reasons.append(f"High duration variance ({duration_std_dev_ratio:.2f} > {self.config['duration_variance_threshold']:.2f}).")
            is_candidate = True

        if len(common_errors) > 0:
            reasons.append(f"Recurring error patterns: {', '.join([f'{err["message"]} ({err["count"]})' for err in common_errors])}.")

        # 静的解析による追加の候補判定
        if self.config["static_analysis_enabled"] and not is_candidate:
            # ここではテストIDからテストファイルパスを仮定する必要がある
            # 実際にはpytestのitem.nodeidなどからパスを取得する
            test_file_path = f"tests/{test_id.split('::')[0]}.py" # 仮のパス
            static_analysis_findings = self.static_analyzer.analyze_test_file(test_file_path)
            if static_analysis_findings:
                reasons.append(f"Static analysis found potential non-deterministic elements: {', '.join(static_analysis_findings)}.")
                is_candidate = True
        
        return {
            "is_candidate": is_candidate,
            "reason": "; ".join(reasons) if reasons else "No specific issues found.",
            "metrics": {
                "num_runs": num_runs,
                "failure_rate": failure_rate,
                "avg_duration": analysis_results["avg_duration"],
                "duration_std_dev": analysis_results["duration_std_dev"],
                "duration_std_dev_ratio": duration_std_dev_ratio,
                "common_errors": common_errors
            }
        }

    def _confirm_flakiness_by_rerun(self, test_id: str, test_function_ref: Any) -> bool:
        """
        フラッキーテスト候補を複数回再実行し、実際に不安定であることを確認する。
        """
        logger.info(f"Confirming flakiness for {test_id} by re-running {self.config['rerun_confirmation_count']} times.")
        
        # 実際にはpytestのテスト関数を直接実行するロジックが必要だが、ここではsimulate_test_runを使用
        # test_function_refはテスト実行ロジックへの参照を想定
        
        failures = 0
        successful_runs = []
        failed_runs = []

        for i in range(self.config["rerun_confirmation_count"]):
            logger.debug(f"Re-run attempt {i+1}/{self.config['rerun_confirmation_count']} for {test_id}...")
            # ここではsimulate_test_runを呼び出すが、実際にはpytest.run_test_item()のようなAPIを使う
            # test_function_refはテストを識別し、実行するための情報を含むオブジェクトを想定
            # For demonstration, simulate a test run. A real implementation would execute the actual test.
            # We'll simulate a random outcome for demonstration purposes to mimic flakiness.
            
            # The actual test execution would look something like:
            # result = self._run_single_test_item(test_id) # This would interact with pytest
            
            # For this design document, we simulate a run outcome
            # Simulating flakiness for demonstration: fail 30% of the time, pass 70%
            is_passed_simulation = (i % 2 == 0 and failures < self.config["rerun_failure_threshold"]) or (failures >= self.config["rerun_failure_threshold"])
            result = simulate_test_run(test_id, min_duration=0.1, max_duration=1.0, failure_probability=0.3 if is_passed_simulation else 0.05)
            
            self.history_manager.record_test_result(test_id, result.passed, result.duration, result.error_message)

            if not result.passed:
                failures += 1
                failed_runs.append(result)
                logger.warning(f"  {test_id} failed on re-run {i+1} with error: {result.error_message}")
            else:
                successful_runs.append(result)
                logger.debug(f"  {test_id} passed on re-run {i+1}.")

        if failures >= self.config["rerun_failure_threshold"]:
            logger.warning(f"Test '{test_id}' confirmed as flaky: {failures} failures in {self.config['rerun_confirmation_count']} re-runs.")
            return True
        else:
            logger.info(f"Test '{test_id}' appears stable after {self.config['rerun_confirmation_count']} re-runs ({failures} failures).")
            return False

    def suggest_remediation(self, test_id: str, flakiness_details: Dict[str, Any]) -> List[str]:
        """
        検出されたフラッキーテストに対して、修正戦略を提案する。
        """
        suggestions = []
        suggestions.append(f"Test '{test_id}' is identified as flaky due to: {flakiness_details['reason']}")
        suggestions.append("--- Remediation Suggestions ---")

        # 失敗率が高い場合
        if flakiness_details['metrics']['failure_rate'] > self.config["flaky_threshold_failure_rate"]:
            suggestions.append("- Investigate common error patterns: Look into the recurring error messages to find root causes.")
            for error in flakiness_details['metrics']['common_errors']:
                suggestions.append(f"  - Error: '{error['message']}' occurred {error['count']} times.")
            suggestions.append("- Add a retry mechanism: Implement `pytest-rerunfailures` or similar for transient failures.")

        # 実行時間の分散が大きい場合
        if flakiness_details['metrics']['duration_std_dev_ratio'] > self.config["duration_variance_threshold"]:
            suggestions.append("- Add appropriate wait times (e.g., `WebDriverWait` for UI tests, `time.sleep` with caution): Ensure elements are ready or operations complete.")
            suggestions.append("- Refactor test setup/teardown: Ensure consistent test environment and data state.")

        # 静的解析の検出結果に基づく提案
        if "Static analysis found potential" in flakiness_details['reason']:
             suggestions.append("- Review code for non-deterministic elements: Check for reliance on system time, uncontrolled randomness, or race conditions in parallel tests.")
             suggestions.append("- Use mocks/stubs: Isolate external dependencies (APIs, databases) to ensure deterministic test outcomes.")
             suggestions.append("- Improve test data management: Use consistent, isolated test data for each run.")
             suggestions.append("- Optimize test order (if dependencies exist): Although tests should be independent, sometimes subtle state leakage occurs.")

        suggestions.append("--- End of Suggestions ---")
        return suggestions

    def run_flaky_detection_cycle(self, all_test_ids_to_check: List[str], test_function_map: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        テストスイート全体に対してフラッキーテスト検出サイクルを実行する。
        """
        logger.info("Starting flaky test detection cycle...")
        flaky_tests_detected: List[Dict[str, Any]] = []
        remediation_plans: List[str] = []

        all_known_test_ids = self.history_manager.get_all_test_ids()
        
        # In a real scenario, all_test_ids_to_check would come from pytest's collection phase.
        # For this design, we'll combine known history and provided test IDs.
        unique_test_ids = list(set(all_test_ids_to_check + all_known_test_ids))

        for test_id in unique_test_ids:
            logger.info(f"Analyzing test: {test_id}")
            detection_result = self._determine_flakiness_candidate(test_id)

            if detection_result["is_candidate"]:
                logger.warning(f"Test '{test_id}' is a flaky candidate: {detection_result['reason']}")
                
                # Assume test_function_map provides a way to get the actual test function reference
                test_func_ref = test_function_map.get(test_id)
                if test_func_ref:
                    if self._confirm_flakiness_by_rerun(test_id, test_func_ref):
                        flaky_tests_detected.append({
                            "test_id": test_id,
                            "detection_details": detection_result,
                            "confirmed_flaky": True
                        })
                        suggestions = self.suggest_remediation(test_id, detection_result)
                        remediation_plans.extend(suggestions)
                        logger.warning(f"Confirmed flaky test '{test_id}'. Remediation plan generated.")
                    else:
                        logger.info(f"Test '{test_id}' initially flagged but stable on re-run. Monitor closely.")
                else:
                    logger.warning(f"Test function reference for '{test_id}' not found. Cannot re-run for confirmation.")
                    flaky_tests_detected.append({
                            "test_id": test_id,
                            "detection_details": detection_result,
                            "confirmed_flaky": False, # Could not confirm due to missing ref
                            "reason_unconfirmed": "Test function reference not available for re-run."
                        })
            else:
                logger.debug(f"Test '{test_id}' appears stable: {detection_result['reason']}")

        logger.info("Flaky test detection cycle completed.")
        return flaky_tests_detected, remediation_plans


class TestAutomationEngine:
    """
    既存のテスト自動化エンジンを模擬し、FlakyTestDetectorとの統合を示すクラス。
    実際にはpytestのようなテストフレームワークと連携する。
    """
    def __init__(self, db_path: str = "test_history.db"):
        self.history_manager = TestHistoryManager(db_path)
        self.flaky_detector = FlakyTestDetector()
        self.registered_tests: Dict[str, Any] = {} # {test_id: test_function_ref}

    def register_test(self, test_id: str, test_func_ref: Any):
        """テストを登録する（実際にはpytestのテストディスカバリで自動的に行われる）"""
        self.registered_tests[test_id] = test_func_ref

    def execute_test_suite(self, suite_name: str = "default_suite") -> List[TestResult]:
        """
        テストスイートの実行をシミュレートし、結果を履歴マネージャーに記録する。
        """
        logger.info(f"Executing test suite: {suite_name}")
        results: List[TestResult] = []
        for test_id, _ in self.registered_tests.items():
            # 実際にはpytest.main([test_id]) のような呼び出し
            # ここではsimulate_test_runを使って結果を生成
            passed = True if hash(test_id + datetime.now().strftime('%H%M')) % 10 < 7 else False # Simulate some failures
            duration = 0.1 + (hash(test_id) % 100) / 100.0
            error_message = None
            if not passed:
                error_message = f"Simulated failure for {test_id}"
            
            result = TestResult(test_id, passed, duration, error_message, datetime.now())
            self.history_manager.record_test_result(test_id, passed, duration, error_message)
            results.append(result)
            logger.info(f"  Test '{test_id}': {'PASSED' if passed else 'FAILED'} in {duration:.2f}s")
        logger.info(f"Test suite '{suite_name}' execution completed.")
        return results

    def run_flaky_detection_and_report(self):
        """
        テスト実行後にフラッキーテスト検出を実行し、レポートを生成する。
        """
        logger.info("\n--- Starting Flaky Test Detection Phase ---")
        all_test_ids = list(self.registered_tests.keys())
        flaky_tests, remediation_plans = self.flaky_detector.run_flaky_detection_cycle(all_test_ids, self.registered_tests)

        if flaky_tests:
            logger.warning("\n--- Flaky Tests Detected ---")
            for ft in flaky_tests:
                logger.warning(f"  Test ID: {ft['test_id']}")
                logger.warning(f"    Reason: {ft['detection_details']['reason']}")
                if not ft.get('confirmed_flaky', False):
                    logger.warning(f"    NOTE: Flakiness could not be confirmed by re-run. Reason: {ft.get('reason_unconfirmed', 'Unknown')}")
            
            logger.info("\n--- Remediation Plans ---")
            for plan in remediation_plans:
                logger.info(plan)
        else:
            logger.info("\nNo flaky tests detected in this cycle.")
        logger.info("--- Flaky Test Detection Phase Completed ---\n")

def example_test_func_a():
    """Example test function A (for simulation reference)"""
    pass

def example_test_func_b():
    """Example test function B (for simulation reference)"""
    pass

def example_test_func_c():
    """Example test function C (for simulation reference) - potentially flaky"""
    pass

if __name__ == "__main__":
    # シミュレーション用のテストIDとテスト関数参照を準備
    # 実際にはpytestの収集フェーズからこれらの情報が提供される
    simulated_test_function_map = {
        "test_module_a.py::test_example_a": example_test_func_a,
        "test_module_a.py::test_example_b": example_test_func_b,
        "test_module_b.py::test_example_c": example_test_func_c,
        "test_module_c.py::test_flaky_case": example_test_func_a, # Assume this one is often flaky
        "test_module_c.py::test_stable_case": example_test_func_b,
    }

    # テスト自動化エンジンのインスタンス化
    engine = TestAutomationEngine(db_path="flaky_test_data.db")

    # テストをエンジンに登録
    for test_id, func_ref in simulated_test_function_map.items():
        engine.register_test(test_id, func_ref)

    # 複数回テストスイートを実行し、履歴データを蓄積する
    # フラッキーテストを検出するためには十分な履歴が必要
    logger.info("--- Running test suites to build history ---")
    for i in range(7): # 7回実行して履歴を作成
        logger.info(f"\n===== Test Suite Run {i+1} =====")
        engine.execute_test_suite()
        time.sleep(1) # 少し間隔を空ける

    # フラッキーテストの検出とレポート生成
    engine.run_flaky_detection_and_report()

    # 静的解析のデモンストレーション (別途、テストファイルが存在することを前提)
    # utils.pyのStaticCodeAnalyzerが実際にはテストファイルのコードを読み込む
    static_analyzer = StaticCodeAnalyzer()
    print("\n--- Static Analysis Demonstration ---")
    
    # 実際にはテストコードのパスを渡す
    mock_test_code_path = "mock_test_file.py"
    with open(mock_test_code_path, "w", encoding="utf-8") as f:
        f.write("""
import time
import random
import pytest

def test_time_dependent():
    # This test relies on time.sleep, which can be a source of flakiness if timings are tight.
    time.sleep(0.1)
    assert True

def test_random_behavior():
    # This test relies on random, making its outcome non-deterministic.
    if random.randint(0, 1) == 0:
        pytest.fail("Simulated random failure")
    assert True

_shared_state = []

def test_uses_shared_state_a():
    _shared_state.append(1)
    assert len(_shared_state) > 0

def test_uses_shared_state_b():
    # This test modifies/depends on shared state from another test
    assert len(_shared_state) == 1 # This might fail if test_uses_shared_state_a runs after it
    _shared_state.clear()
        """)
    
    findings = static_analyzer.analyze_test_file(mock_test_code_path)
    print(f"Static analysis findings for '{mock_test_code_path}': {findings}")
    os.remove(mock_test_code_path) # クリーンアップ
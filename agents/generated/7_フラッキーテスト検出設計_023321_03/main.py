import os
import time
import json
import logging
from typing import List, Dict, Any, Optional

from utils import analyze_test_stability, SQLiteManager, TestResult
from collections import defaultdict

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlakyTestDetector:
    """
    テスト自動化エンジンに統合され、フラッキーテストを検出・修正するための主要ロジックを管理するクラス。

    テスト実行履歴を分析し、統計的に不安定なテストを識別。
    識別されたテストに対して修正戦略を提案または適用する。
    """

    DEFAULT_DB_PATH = os.path.join(os.getcwd(), "test_results.db")
    DEFAULT_FLAKY_THRESHOLD_PASS_RATE = 0.85 # 成功率が85%未満をフラッキー候補とする
    DEFAULT_FLAKY_THRESHOLD_DURATION_VARIANCE_FACTOR = 0.5 # 平均実行時間に対する分散の割合
    DEFAULT_MIN_HISTORY_FOR_ANALYSIS = 10 # 分析に必要な最小実行回数

    def __init__(self, db_path: str = DEFAULT_DB_PATH, config: Optional[Dict[str, Any]] = None):
        """
        FlakyTestDetectorのコンストラクタ。

        Args:
            db_path (str): テスト結果を保存するSQLiteデータベースのパス。
            config (Optional[Dict[str, Any]]): 検出と修正のための設定オプション。
                - 'flaky_threshold_pass_rate': 成功率の閾値 (例: 0.85)
                - 'flaky_threshold_duration_variance_factor': 実行時間の分散の閾値 (例: 0.5)
                - 'min_history_for_analysis': 分析に必要な最小履歴数 (例: 10)
                - 'max_retries_for_flaky_detection': フラッキー検出のための再実行回数 (例: 3)
                - 'wait_time_on_retry_ms': リトライ時の待機時間（ミリ秒） (例: 500)
        """
        self.db_path = db_path
        self.db_manager = SQLiteManager(db_path)
        self.config = {
            "flaky_threshold_pass_rate": self.DEFAULT_FLAKY_THRESHOLD_PASS_RATE,
            "flaky_threshold_duration_variance_factor": self.DEFAULT_FLAKY_THRESHOLD_DURATION_VARIANCE_FACTOR,
            "min_history_for_analysis": self.DEFAULT_MIN_HISTORY_FOR_ANALYSIS,
            "max_retries_for_flaky_detection": 3,
            "wait_time_on_retry_ms": 200, # default 200ms
            "lookback_period_days": 30 # 過去30日間のデータを分析対象とする
        }
        if config:
            self.config.update(config)

        self.db_manager.create_table()
        logger.info(f"FlakyTestDetector initialized with DB: {self.db_path}")

    def record_test_result(self, test_id: str, status: str, duration: float, error_message: Optional[str] = None):
        """
        単一のテスト実行結果をデータベースに記録する。

        Args:
            test_id (str): テストの一意な識別子。
            status (str): テストの結果 ('passed', 'failed', 'skipped', 'error'など)。
            duration (float): テストの実行時間（秒）。
            error_message (Optional[str]): テストが失敗した場合のエラーメッセージ。
        """
        try:
            self.db_manager.insert_result(test_id, status, duration, error_message)
            logger.debug(f"Recorded result for {test_id}: {status} in {duration:.2f}s")
        except Exception as e:
            logger.error(f"Failed to record test result for {test_id}: {e}")

    def detect_flaky_tests(self, lookback_period_days: Optional[int] = None) -> Dict[str, Any]:
        """
        データベースに記録された履歴データに基づいて、フラッキーテストを検出する。

        Args:
            lookback_period_days (Optional[int]): 過去N日間のデータを分析対象とする。
                                                Noneの場合、設定値（デフォルト30日）を使用。

        Returns:
            Dict[str, Any]: 検出されたフラッキーテストとそれに関連する情報。
                           例: {'flaky_tests': [{'test_id': '...', 'reason': '...'}], 'analysis_summary': {...}}
        """
        period = lookback_period_days if lookback_period_days is not None else self.config['lookback_period_days']
        all_results = self.db_manager.get_results_since(period_days=period)
        
        if not all_results:
            logger.info(f"No test results found in the last {period} days for analysis.")
            return {'flaky_tests': [], 'analysis_summary': {'message': 'No data for analysis.'}}

        # test_idごとに結果をグループ化
        grouped_results: Dict[str, List[TestResult]] = defaultdict(list)
        for res in all_results:
            grouped_results[res.test_id].append(res)

        flaky_tests_detected: List[Dict[str, Any]] = []
        analysis_summary: Dict[str, Any] = {'total_tests_analyzed': 0, 'tests_with_insufficient_history': 0}

        for test_id, results_list in grouped_results.items():
            analysis_summary['total_tests_analyzed'] += 1
            if len(results_list) < self.config['min_history_for_analysis']:
                analysis_summary['tests_with_insufficient_history'] += 1
                logger.debug(f"Skipping {test_id}: insufficient history ({len(results_list)} < {self.config['min_history_for_analysis']})")
                continue

            metrics = analyze_test_stability(results_list)
            is_flaky = False
            reasons = []

            if metrics['pass_rate'] < self.config['flaky_threshold_pass_rate']:
                is_flaky = True
                reasons.append(f"Low pass rate ({metrics['pass_rate']:.2f} < {self.config['flaky_threshold_pass_rate']:.2f})")
            
            # 実行時間の分散をチェック（十分なデータがある場合のみ）
            if metrics['avg_duration'] > 0 and metrics['duration_std_dev'] is not None and len(results_list) > 1:
                variance_ratio = metrics['duration_std_dev'] / metrics['avg_duration']
                if variance_ratio > self.config['flaky_threshold_duration_variance_factor']:
                    is_flaky = True
                    reasons.append(f"High duration variance (std_dev/avg = {variance_ratio:.2f} > {self.config['flaky_threshold_duration_variance_factor']:.2f})")

            if is_flaky:
                flaky_tests_detected.append({
                    'test_id': test_id,
                    'reason': ", ".join(reasons),
                    'metrics': metrics
                })
                logger.warning(f"Detected flaky test: {test_id} - Reasons: {', '.join(reasons)}")
            else:
                logger.debug(f"Test {test_id} appears stable. Metrics: {json.dumps(metrics)}")
        
        analysis_summary['detected_flaky_count'] = len(flaky_tests_detected)
        logger.info(f"Flaky test detection complete. Found {len(flaky_tests_detected)} flaky tests.")
        return {'flaky_tests': flaky_tests_detected, 'analysis_summary': analysis_summary}

    def run_with_flaky_detection_retries(self, test_runner_func, test_id: str, *args, **kwargs) -> Dict[str, Any]:
        """
        指定されたテスト関数を複数回実行し、その結果を記録する。
        これは、検出アルゴリズムの「テストの複数回実行による再現性確認」の部分をサポートする。
        実際のテスト実行は外部のtest_runner_funcに委譲される。

        Args:
            test_runner_func (callable): 実際のテストを実行する関数。
                                         シグネチャは `(test_id, *args, **kwargs)` で、
                                         結果として `{'status': 'passed'/'failed', 'duration': float, 'error_message': str}`
                                         のような辞書を返すことを期待する。
            test_id (str): 実行するテストの識別子。
            *args, **kwargs: test_runner_funcに渡される追加引数。

        Returns:
            Dict[str, Any]: 最終的なテスト結果と、リトライ回数、全実行結果のリスト。
        """
        max_retries = self.config['max_retries_for_flaky_detection']
        wait_time_ms = self.config['wait_time_on_retry_ms']
        
        all_run_results = []
        final_status = 'failed'
        final_duration = 0.0
        final_error = "Test could not pass after retries."

        logger.info(f"Running test '{test_id}' with up to {max_retries + 1} attempts for flakiness detection.")

        for attempt in range(max_retries + 1):
            start_time = time.perf_counter()
            run_result = {'status': 'error', 'duration': 0.0, 'error_message': f"Attempt {attempt + 1} failed before execution."}
            try:
                # 実際のテスト実行はtest_runner_funcに委譲
                run_result = test_runner_func(test_id, *args, **kwargs)
                if not isinstance(run_result, dict) or 'status' not in run_result or 'duration' not in run_result:
                    raise ValueError("test_runner_func must return a dict with 'status' and 'duration'.")
            except Exception as e:
                run_result['status'] = 'error'
                run_result['duration'] = time.perf_counter() - start_time
                run_result['error_message'] = f"Exception during test execution: {e}"
                logger.error(f"Error executing test '{test_id}' (attempt {attempt + 1}): {e}")
            
            self.record_test_result(test_id, run_result['status'], run_result['duration'], run_result.get('error_message'))
            all_run_results.append(run_result)

            if run_result['status'] == 'passed':
                final_status = 'passed'
                final_duration = run_result['duration']
                final_error = None
                logger.info(f"Test '{test_id}' passed on attempt {attempt + 1}.")
                break
            else:
                logger.warning(f"Test '{test_id}' failed on attempt {attempt + 1}. Status: {run_result['status']}, Error: {run_result.get('error_message', 'N/A')}")
                if attempt < max_retries:
                    time.sleep(wait_time_ms / 1000.0) # ミリ秒を秒に変換
                    logger.info(f"Retrying test '{test_id}' after {wait_time_ms}ms...")

        # 最終的な結果を判断（最後の実行結果が最も重要だが、成功した場合はそれを優先）
        if final_status == 'failed':
            last_result = all_run_results[-1]
            final_status = last_result['status']
            final_duration = last_result['duration']
            final_error = last_result.get('error_message', "Failed after all retries.")

        return {
            'test_id': test_id,
            'status': final_status,
            'duration': final_duration,
            'error_message': final_error,
            'attempts': len(all_run_results),
            'all_run_results': all_run_results
        }
    
    def suggest_fix_strategies(self, flaky_test_info: Dict[str, Any]) -> List[str]:
        """
        検出されたフラッキーテストに対して、一般的な修正戦略を提案する。

        Args:
            flaky_test_info (Dict[str, Any]): detect_flaky_testsから返された単一のフラッキーテスト情報。
                                             例: {'test_id': '...', 'reason': '...', 'metrics': {...}}

        Returns:
            List[str]: 提案される修正戦略のリスト。
        """
        suggestions = []
        test_id = flaky_test_info['test_id']
        metrics = flaky_test_info['metrics']
        reason = flaky_test_info['reason']

        logger.info(f"Suggesting fixes for flaky test: {test_id} (Reason: {reason})")

        # 成功率が低い場合
        if metrics['pass_rate'] < self.config['flaky_threshold_pass_rate']:
            suggestions.append(f"Pass rate ({metrics['pass_rate']:.2f}) is low. Consider the following:")
            suggestions.append("- Investigate non-deterministic elements: e.g., time dependencies, random numbers, external service availability.")
            suggestions.append("- Add more robust assertions and error handling.")
            suggestions.append("- Implement retries within the test itself for transient failures (e.g., database connection issues).")
            suggestions.append("- Ensure proper teardown/setup to avoid state leakage between tests.")
        
        # 実行時間の分散が大きい場合
        if 'High duration variance' in reason:
             suggestions.append(f"High duration variance (std_dev/avg = {metrics['duration_std_dev'] / metrics['avg_duration']:.2f}) suggests performance instability or race conditions.")
             suggestions.append("- Add explicit waits (e.g., `WebDriverWait` for UI tests, polling for async operations) instead of fixed `time.sleep()`.")
             suggestions.append("- Profile the test to identify performance bottlenecks or unpredictable delays.")
             suggestions.append("- Isolate external dependencies using mocks/stubs to reduce network/I/O latency variations.")
             suggestions.append("- Review for potential race conditions or deadlocks, especially in concurrent code.")

        # 一般的な提案
        suggestions.append("- Review the test for any shared mutable state that might be affecting other tests or being affected by them.")
        suggestions.append("- Use dependency injection to mock external services (APIs, databases) for deterministic results.")
        suggestions.append("- Ensure the test environment is consistent and isolated for each run.")
        suggestions.append("- If this is an integration/E2E test, consider breaking it down into smaller, more focused unit tests.")
        suggestions.append("- Re-evaluate the test's scope and purpose. Is it testing too much at once?")

        return suggestions

    def get_flaky_test_status_report(self, num_recent_runs: int = 20) -> Dict[str, Any]:
        """
        現在認識されているフラッキーテストのリストと、最近の実行状況に関するレポートを生成する。

        Args:
            num_recent_runs (int): 各テストについて取得する最近の実行履歴の数。

        Returns:
            Dict[str, Any]: フラッキーテストのステータスレポート。
        """
        flaky_detection_results = self.detect_flaky_tests()
        flaky_tests_list = flaky_detection_results['flaky_tests']
        
        report: Dict[str, Any] = {
            "timestamp": time.time(),
            "total_flaky_tests_detected": len(flaky_tests_list),
            "flaky_tests_details": []
        }

        for flaky_test in flaky_tests_list:
            test_id = flaky_test['test_id']
            recent_results = self.db_manager.get_results(test_id, limit=num_recent_runs)
            recent_statuses = [r.status for r in recent_results]
            
            recent_pass_count = recent_statuses.count('passed')
            recent_fail_count = len([s for s in recent_statuses if s not in ['passed', 'skipped']])
            recent_pass_rate = recent_pass_count / len(recent_statuses) if recent_statuses else 0.0

            details = {
                "test_id": test_id,
                "reason_for_flakiness": flaky_test['reason'],
                "metrics_at_detection": flaky_test['metrics'],
                "recent_history": {
                    "last_n_runs": num_recent_runs,
                    "total_runs_in_history": len(recent_results),
                    "pass_count": recent_pass_count,
                    "fail_count": recent_fail_count,
                    "recent_pass_rate": f"{recent_pass_rate:.2f}",
                    "statuses_summary": recent_statuses # 全てのステータスのリスト
                },
                "suggested_fix_strategies": self.suggest_fix_strategies(flaky_test)
            }
            report['flaky_tests_details'].append(details)
        
        return report

# 既存のtest_automation_engine.pyへの統合イメージ:
# 例えば、TestAutomationEngineクラスのrun_testsメソッド内で、
# FlakyTestDetectorを初期化し、各テストの実行前後に記録・検出ロジックを呼び出す。
#
# class TestAutomationEngine:
#     def __init__(self, ...):
#         self.flaky_detector = FlakyTestDetector(db_path="test_results.db", config={...})
#         # ... 他の初期化
#
#     def _run_single_test_logic(self, test_id, test_function, *args, **kwargs):
#         # ここで実際のpytestなどの実行を模倣
#         # 例: pytest.main([test_id, '--collect-only']) などでテスト情報を取得後、
#         # pytest.main([test_id]) で実行するイメージ
#         # この例ではモックとして関数を直接実行
#         start_time = time.perf_counter()
#         try:
#             # ここが実際のテストランナーの呼び出しになる
#             # 例: result = subprocess.run(['pytest', test_id], capture_output=True, text=True)
#             # run_result = parse_pytest_output(result)
#             
#             # モック関数を呼び出す
#             status, error = test_function(*args, **kwargs)
#             run_result = {'status': status, 'error_message': error}
#             if status == 'passed':
#                 run_result['duration'] = time.perf_counter() - start_time
#             else:
#                 run_result['duration'] = time.perf_counter() - start_time + 0.1 # 失敗は少し長くかかるとして
#         except Exception as e:
#             run_result = {'status': 'error', 'duration': time.perf_counter() - start_time, 'error_message': str(e)}
#
#         return run_result
#
#     def run_tests(self, test_list: List[str]):
#         logger.info("Starting test run with flaky detection.")
#         all_results = []
#         for test_id in test_list:
#             # ここで実際のテスト実行ロジック (例: pytestの呼び出し) をラップ
#             # _run_single_test_logic は test_runner_func のシグネチャに合わせる必要がある
#             # そのためには、test_idを受け取り、テストを実行し、Dictを返すように調整する
#             
#             # 仮のテスト実行関数 (実際のテストロジックの代わりに使う)
#             def mock_test_runner(current_test_id, *inner_args, **inner_kwargs):
#                 # ここで本来はpytestなどを呼び出す
#                 # print(f"Mock running test: {current_test_id}")
#                 if "flaky_test_A" in current_test_id and time.time() % 3 != 0: # 3回に1回は成功
#                     return {'status': 'passed', 'duration': 0.5 + random.random()/2, 'error_message': None}
#                 elif "flaky_test_B" in current_test_id and random.random() < 0.3: # 30%の確率で失敗
#                     return {'status': 'failed', 'duration': 1.0 + random.random(), 'error_message': 'Random failure in test B'}
#                 elif "stable_test_C" in current_test_id:
#                     return {'status': 'passed', 'duration': 0.2 + random.random()/5, 'error_message': None}
#                 else:
#                     return {'status': 'passed', 'duration': 0.3 + random.random()/3, 'error_message': None}
#
#             # フラッキーテスト検出のためのリトライロジックを適用してテストを実行
#             result_with_retries = self.flaky_detector.run_with_flaky_detection_retries(
#                 mock_test_runner, test_id
#             )
#             all_results.append(result_with_retries)
#             logger.info(f"Final result for {test_id}: {result_with_retries['status']} (Attempts: {result_with_retries['attempts']})")
#         
#         logger.info("All tests executed. Running flaky detection analysis...")
#         flaky_report = self.flaky_detector.detect_flaky_tests()
#         logger.info(f"Flaky Test Detection Report: {json.dumps(flaky_report, indent=2)}")
#
#         # フラッキーと判断されたテストに対して修正戦略をログに出力
#         for flaky_test in flaky_report.get('flaky_tests', []):
#             suggestions = self.flaky_detector.suggest_fix_strategies(flaky_test)
#             logger.warning(f"\n--- Suggested fixes for {flaky_test['test_id']} ---")
#             for s in suggestions:
#                 logger.warning(f"  - {s}")
#             logger.warning("-----------------------------------\n")
#
#         return all_results, flaky_report
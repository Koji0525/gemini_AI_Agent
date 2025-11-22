import random
import time
import datetime
from typing import Dict, List, Any, Tuple
from utils import TestHistoryDB, calculate_stability_metrics, is_potentially_flaky

class FlakyTestDetector:
    """
    フラッキーテストを自動的に検出し、修正戦略を提案または適用するクラス。
    テスト実行履歴の統計分析と複数回実行による再現性確認を組み合わせてフラッキーテストを特定します。
    """

    def __init__(self, db_path: str = "test_history.db", config: Dict[str, Any] = None):
        """
        FlakyTestDetectorの初期化。

        Args:
            db_path (str): テスト履歴を保存するSQLiteデータベースファイルのパス。
            config (Dict[str, Any], optional): 検出アルゴリズムの設定。
        """
        self.db = TestHistoryDB(db_path)
        self.config = {
            "history_lookback_limit": 10,                 # 統計分析に用いる過去の実行履歴数
            "min_history_runs_for_initial_check": 3,      # 初期チェックに必要な最小履歴数
            "flaky_failure_rate_threshold": 80.0,         # 成功率がこの値未満の場合、"疑わしい"とマーク (例: 80%未満 = 20%以上の失敗率)
            "flaky_duration_stddev_ratio_threshold": 0.3, # 実行時間の標準偏差が平均のこの割合を超える場合、"疑わしい"とマーク (例: 30%)
            "rerun_attempts_for_flaky_confirmation": 3,   # 疑わしいテストを再実行する回数
            "rerun_failure_threshold": 1,                 # 再実行のうち、これ以上失敗すればフラッキーと確定
            "max_auto_retries_on_flaky": 2,               # フラッキーと判定されたテストに対する最大自動リトライ回数
            "retry_delay_seconds": 0.5,                   # リトライ間の待機時間
            "simulate_test_pass_rate_map": {},            # シミュレーション用のテストIDごとの成功率 (例: {"test_flaky_login": 0.5})
            "simulate_test_duration_map": {},             # シミュレーション用のテストIDごとの平均実行時間 (例: {"test_flaky_login": (0.1, 0.05)})
        }
        if config:
            self.config.update(config)
        
        # utils.pyの判定関数に渡す設定を更新
        self.config_for_utils = {
            "min_history_runs": self.config["min_history_runs_for_initial_check"],
            "flaky_failure_rate_threshold": self.config["flaky_failure_rate_threshold"],
            "flaky_duration_stddev_ratio_threshold": self.config["flaky_duration_stddev_ratio_threshold"]
        }
        print(f"FlakyTestDetector initialized with config: {self.config}")

    def record_test_result(self, test_id: str, status: str, duration: float, error_message: str = None, additional_info: Dict[str, Any] = None):
        """
        テスト実行結果をデータベースに記録します。

        Args:
            test_id (str): テストを一意に識別するID。
            status (str): テスト結果 ('PASS', 'FAIL', 'ERROR')。
            duration (float): テスト実行時間（秒）。
            error_message (str, optional): 失敗時のエラーメッセージ。
            additional_info (Dict[str, Any], optional): その他の情報（辞書形式）。
        """
        self.db.insert_result(test_id, status, duration, error_message, additional_info)
        print(f"Recorded: {test_id} - {status} in {duration:.2f}s")

    def _simulate_single_test_run(self, test_id: str) -> Dict[str, Any]:
        """
        単一のテスト実行をシミュレートします。
        設定された成功率と実行時間に基づいて結果を生成します。
        実際のテストランナー (pytestなど) がテストを実行し、その結果を返すことを想定しています。

        Args:
            test_id (str): シミュレートするテストのID。

        Returns:
            Dict[str, Any]: シミュレーションされたテスト結果 ('status', 'duration', 'error_message')。
        """
        pass_rate = self.config["simulate_test_pass_rate_map"].get(test_id, 0.95) # デフォルトは95%成功
        avg_duration, std_duration = self.config["simulate_test_duration_map"].get(test_id, (0.2, 0.05)) # デフォルト平均0.2秒, 標準偏差0.05秒

        status = "PASS"
        error_message = None
        
        if random.random() > pass_rate:
            status = "FAIL"
            error_message = f"Simulated failure for {test_id}: Randomly failed."
            if test_id.startswith("test_flaky_"):
                error_message = f"Simulated flaky failure for {test_id}: Intermittent issue."

        # 実行時間は正規分布に従うとして乱数生成
        duration = max(0.01, random.gauss(avg_duration, std_duration))
        time.sleep(duration * 0.1) # シミュレーションなので少し待機

        return {"status": status, "duration": duration, "error_message": error_message}

    def _execute_test_with_retries(self, test_id: str, max_retries: int) -> Dict[str, Any]:
        """
        テストを実行し、失敗した場合は指定された回数リトライを試みます。
        ここではシミュレーションされたテスト実行を使用します。

        Args:
            test_id (str): 実行するテストのID。
            max_retries (int): 最大リトライ回数。

        Returns:
            Dict[str, Any]: 最終的なテスト結果。リトライ後の成功を含む。
        """
        attempt = 0
        latest_result = {}
        while attempt <= max_retries:
            print(f"  Attempt {attempt + 1}/{max_retries + 1} for test '{test_id}'...")
            result = self._simulate_single_test_run(test_id)
            self.record_test_result(test_id, result["status"], result["duration"], result["error_message"], {"attempt": attempt + 1})
            
            latest_result = result
            if result["status"] == "PASS":
                print(f"  Test '{test_id}' PASSED on attempt {attempt + 1}.")
                return result # 成功したら即座に終了

            print(f"  Test '{test_id}' FAILED on attempt {attempt + 1}. Retrying...")
            attempt += 1
            if attempt <= max_retries:
                time.sleep(self.config["retry_delay_seconds"]) # リトライ間の待機

        return latest_result # 全てのリトライが失敗した場合、最後の結果を返す

    def detect_flaky_tests(self) -> List[Dict[str, Any]]:
        """
        データベースに記録された履歴に基づいてフラッキーテストを検出します。
        検出フロー:
        1. 全テストIDを取得。
        2. 各テストIDについて、過去N回の履歴を取得し、安定性メトリクスを計算。
        3. メトリクスに基づき、潜在的にフラッキーなテストを識別 (閾値判定)。
        4. 潜在的にフラッキーなテストを複数回再実行し、再現性を確認。
        5. 再実行の結果、一定回数以上失敗すればフラッキーと確定。

        Returns:
            List[Dict[str, Any]]: 検出されたフラッキーテストのリスト。各辞書はテストID、理由、推奨修正戦略を含む。
        """
        print("\n--- Starting Flaky Test Detection ---")
        all_test_ids = self.db.get_all_test_ids()
        potentially_flaky_tests: Dict[str, Dict[str, Any]] = {}

        # ステップ1: 統計分析による潜在的フラッキーテストの特定
        for test_id in all_test_ids:
            history = self.db.get_test_history(test_id, self.config["history_lookback_limit"])
            if not history or len(history) < self.config["min_history_runs_for_initial_check"]:
                # print(f"Skipping {test_id}: Not enough history ({len(history)} runs).")
                continue

            metrics = calculate_stability_metrics(history)
            is_flaky, reason = is_potentially_flaky(metrics, self.config_for_utils)
            
            if is_flaky:
                potentially_flaky_tests[test_id] = {
                    "reason_statistical": reason,
                    "metrics": metrics,
                    "last_status": history[0]['status'] # 最新の実行結果
                }
                print(f"  [Potential Flaky] {test_id}: {reason} (Pass rate: {metrics['pass_rate']:.2f}%)")
        
        # ステップ2: 疑わしいテストの複数回再実行による再現性確認
        flaky_tests_confirmed: List[Dict[str, Any]] = []
        for test_id, data in potentially_flaky_tests.items():
            print(f"\n  Checking reproducibility for '{test_id}' (Statistical reason: {data['reason_statistical']})...")
            failures_in_rerun = 0
            rerun_results = []
            
            for i in range(self.config["rerun_attempts_for_flaky_confirmation"]):
                sim_result = self._simulate_single_test_run(test_id) # シミュレーションで再実行
                rerun_results.append(sim_result)
                if sim_result["status"] != "PASS":
                    failures_in_rerun += 1
                print(f"    Rerun attempt {i+1}: {sim_result['status']} in {sim_result['duration']:.2f}s")
                # 実際のテスト環境では、ここでテスト結果をDBに記録するか、メモリに一時保持して後でまとめて記録する
                # 今回は検出の文脈なので、DBには記録しない (検出目的の再実行のため)
                time.sleep(0.config["retry_delay_seconds"] / 2) # 短めの待機

            if failures_in_rerun >= self.config["rerun_failure_threshold"]:
                flaky_tests_confirmed.append({
                    "test_id": test_id,
                    "reason": f"統計的に不安定 ({data['reason_statistical']}) かつ、再実行 {self.config['rerun_attempts_for_flaky_confirmation']} 回中 {failures_in_rerun} 回失敗。",
                    "metrics": data["metrics"],
                    "suggested_actions": self._suggest_flaky_test_actions(test_id)
                })
                print(f"  [CONFIRMED FLAKY] {test_id}: Confirmed due to {failures_in_rerun} failures in {self.config['rerun_attempts_for_flaky_confirmation']} reruns.")
            else:
                print(f"  [NOT FLAKY] {test_id}: Passed enough times during reruns. (Failures: {failures_in_rerun})")

        print("\n--- Flaky Test Detection Completed ---")
        return flaky_tests_confirmed

    def _suggest_flaky_test_actions(self, test_id: str) -> List[str]:
        """
        フラッキーテストに対して推奨される修正戦略を生成します。
        このメソッドは、検出されたテストの特性に応じて具体的なアドバイスを提供できます。
        現状では一般的なアドバイスを提供します。

        Args:
            test_id (str): フラッキーと判定されたテストのID。

        Returns:
            List[str]: 推奨される修正戦略のリスト。
        """
        actions = [
            "テストを分離し、外部依存をモック/スタブで排除することを検討してください。",
            "非同期処理や外部APIコールを含む場合、適切な待機メカニズム (Explicit Wait) を実装してください。",
            "テストのセットアップ/ティアダウンが他のテストに影響を与えていないか確認してください。",
            "並行実行時に競合状態が発生していないか、同期メカニズムを確認してください。",
            f"CI/CDパイプラインで自動リトライ ({self.config['max_auto_retries_on_flaky']}回まで) を適用することを検討してください。",
            "テストの実行環境 (OS, ネットワーク, サービスバージョン) が一貫しているか確認してください。",
        ]
        if "timeout" in test_id.lower() or "sleep" in test_id.lower(): # 例としてテストIDから推測
             actions.insert(1, "テスト内のsleep()を明示的な待機に置き換えることを強く推奨します。")
        return actions

class TestAutomationEngine:
    """
    既存のテスト自動化エンジンをシミュレートするクラス。
    FlakyTestDetectorと連携し、テスト実行、結果記録、フラッキー検出、
    そして必要に応じたリトライ戦略を適用します。
    """
    def __init__(self, detector: FlakyTestDetector, test_list: List[str]):
        """
        エンジンの初期化。

        Args:
            detector (FlakyTestDetector): フラッキーテスト検出器のインスタンス。
            test_list (List[str]): このエンジンが実行するテストのリスト。
        """
        self.detector = detector
        self.test_list = test_list
        self.latest_test_results: Dict[str, Dict[str, Any]] = {}
        print("\nTestAutomationEngine initialized.")

    def run_all_tests(self):
        """
        全ての登録されたテストを実行し、結果をFlakyTestDetectorに記録します。
        フラッキーテストが検出された場合、自動リトライ戦略を適用します。
        """
        print("\n--- Starting Test Suite Execution ---")
        self.latest_test_results = {}
        for test_id in self.test_list:
            print(f"\nRunning test: {test_id}")
            # まずは通常実行 (検出ロジックは実行後に適用)
            initial_result = self.detector._simulate_single_test_run(test_id)
            self.detector.record_test_result(test_id, initial_result["status"], initial_result["duration"], initial_result["error_message"])
            self.latest_test_results[test_id] = initial_result

        print("\n--- Initial Test Suite Execution Completed ---")
        
        # フラッキーテストの検出
        flaky_tests = self.detector.detect_flaky_tests()
        
        if flaky_tests:
            print("\n--- Detected Flaky Tests, Applying Auto-Retries ---")
            for flaky_test in flaky_tests:
                test_id = flaky_test["test_id"]
                print(f"\n  Flaky Test: {test_id}. Applying auto-retries...")
                
                # フラッキーと判定されたテストに対してリトライ戦略を適用
                # ここでは detector._execute_test_with_retries を使用
                final_result_after_retries = self.detector._execute_test_with_retries(
                    test_id, self.detector.config["max_auto_retries_on_flaky"]
                )
                self.latest_test_results[test_id] = final_result_after_retries
                print(f"  Final status for {test_id} after retries: {final_result_after_retries['status']}")
                
                print(f"  Suggested Actions for {test_id}:")
                for action in flaky_test["suggested_actions"]:
                    print(f"    - {action}")
        else:
            print("\n--- No Flaky Tests Detected ---")

        print("\n--- Test Automation Engine Run Finished ---")
        
        # 最終的な結果のサマリー
        print("\n--- Final Test Summary ---")
        pass_count = sum(1 for r in self.latest_test_results.values() if r["status"] == "PASS")
        fail_count = sum(1 for r in self.latest_test_results.values() if r["status"] == "FAIL")
        error_count = sum(1 for r in self.latest_test_results.values() if r["status"] == "ERROR")
        total_count = len(self.latest_test_results)

        print(f"Total Tests: {total_count}, Passed: {pass_count}, Failed: {fail_count}, Errored: {error_count}")
        for test_id, result in self.latest_test_results.items():
            print(f"  {test_id}: {result['status']} ({result['duration']:.2f}s)")


if __name__ == "__main__":
    # シミュレーション用のテスト設定
    simulation_config = {
        "simulate_test_pass_rate_map": {
            "test_stable_login": 0.99, # ほぼ成功
            "test_flaky_db_connection": 0.6, # 60%しか成功しないフラッキーテスト
            "test_intermittent_api_call": 0.7, # 70%成功、API依存
            "test_slow_ui_load": 0.9, # 90%成功、たまにタイムアウトするテスト
            "test_perf_critical_feature": 0.95, # 95%成功だが、たまに実行時間が変動する
        },
        "simulate_test_duration_map": {
            "test_stable_login": (0.1, 0.01),
            "test_flaky_db_connection": (0.5, 0.2), # 実行時間も変動
            "test_intermittent_api_call": (0.8, 0.1),
            "test_slow_ui_load": (1.5, 0.5), # 長い時間と大きな変動
            "test_perf_critical_feature": (0.3, 0.1), # 短い時間だが標準偏差が相対的に高め
        },
        "history_lookback_limit": 10,
        "min_history_runs_for_initial_check": 3,
        "flaky_failure_rate_threshold": 90.0, # 成功率が90%未満で疑わしい
        "rerun_attempts_for_flaky_confirmation": 3,
        "rerun_failure_threshold": 1, # 再実行3回中1回でも失敗したらフラッキー確定
        "max_auto_retries_on_flaky": 2, # フラッキーと判定されたら2回まで自動リトライ
        "retry_delay_seconds": 0.2, # リトライ間の待機時間
    }

    # FlakyTestDetectorを初期化 (インメモリDBを使用)
    detector = FlakyTestDetector(db_path=":memory:", config=simulation_config)

    # 複数回テストスイートを実行し、履歴を蓄積
    test_suite = ["test_stable_login", "test_flaky_db_connection", "test_intermittent_api_call", "test_slow_ui_load", "test_perf_critical_feature"]
    
    print("\n----- Populating Test History (5 runs) -----")
    for _ in range(5): # テスト履歴を5回分蓄積
        print(f"\n--- History Run {_ + 1} ---")
        for test_id in test_suite:
            result = detector._simulate_single_test_run(test_id)
            detector.record_test_result(test_id, result["status"], result["duration"], result["error_message"])
        time.sleep(0.1) # 連続実行を防ぐための短い待機

    # テスト自動化エンジンを初期化し、実行
    engine = TestAutomationEngine(detector, test_suite)
    engine.run_all_tests()

    # DB接続を閉じる
    detector.db.close()
import subprocess
import json
import datetime
import os
import time
from typing import List, Dict, Any, Optional

from utils import TestHistoryManager, analyze_test_stability, generate_pytest_rerun_options, generate_sleep_suggestion

class FlakkyTestDetector:
    """
    テスト自動化エンジンに組み込まれ、フラッキーテスト（結果が不安定なテスト）を自動的に検出し、
    その修正戦略を提案、あるいは一部自動適用するロジックを提供するメインクラス。

    目的: テストスイートの信頼性を高め、誤検出による開発効率の低下を防ぐ。
    """

    def __init__(self, db_path: str = 'test_history.db', config: Optional[Dict[str, Any]] = None):
        """
        FlakkyTestDetectorの初期化。

        Args:
            db_path (str): テスト実行履歴を保存するSQLiteデータベースファイルのパス。
            config (Optional[Dict[str, Any]]): 検出と修正のカスタム設定。
                - history_based_min_runs (int): 履歴ベース検出のための最小実行回数。
                - history_based_failure_threshold (float): 履歴ベース検出の失敗率閾値 (0.0-1.0)。
                - rerun_based_num_reruns (int): 再実行ベース検出のためのテスト再実行回数。
                - rerun_based_failure_threshold (float): 再実行ベース検出の失敗率閾値 (0.0-1.0)。
                - pytest_path (str): pytest実行コマンドのパス (例: "pytest" or "/usr/local/bin/pytest")。
                - default_test_suite_path (str): デフォルトのテストスイートパス (例: "./tests")。
                - json_report_file (str): pytestのJSONレポート出力ファイル名。
        """
        self.history_manager = TestHistoryManager(db_path)
        self.config = {
            "history_based_min_runs": 10,
            "history_based_failure_threshold": 0.2,  # 過去10回中2回以上失敗 (20%以上の失敗率)
            "rerun_based_num_reruns": 5,
            "rerun_based_failure_threshold": 0.4,    # 5回中2回以上失敗 (40%以上の失敗率)
            "pytest_path": "pytest",                 # pytest実行コマンド
            "default_test_suite_path": "./tests",    # デフォルトのテストスイートパス
            "json_report_file": "pytest_report.json" # pytestのJSONレポート出力ファイル名
        }
        if config:
            self.config.update(config)

        self.flaky_tests_identified: Dict[str, Dict[str, Any]] = {}
        print(f"FlakkyTestDetector initialized with DB: {db_path} and config: {self.config}")

    def _execute_pytest_command(self, test_path: str, options: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        pytestコマンドを実行し、結果をパースする内部ヘルパーメソッド。
        pytest-json-reportプラグインに依存します。

        Args:
            test_path (str): 実行するテストファイルのパスまたはテストID。
            options (Optional[List[str]]): pytestに追加するオプション。

        Returns:
            Dict[str, Any]: pytestの実行結果。
                - success (bool): pytestプロセスが成功したか。
                - tests (List[Dict[str, Any]]): 各テストの結果のリスト。
                - stdout (str): 標準出力。
                - stderr (str): 標準エラー出力。
        """
        json_report_path = self.config["json_report_file"]
        command = [self.config["pytest_path"], f"--json-report-file={json_report_path}", test_path]
        if options:
            command.extend(options)

        print(f"Executing pytest command: {' '.join(command)}")
        try:
            # subprocess.runは、コマンドを実行し、終了するまで待機する
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            
            # JSONレポートファイルから結果を読み込む
            report_data = {}
            if os.path.exists(json_report_path):
                try:
                    with open(json_report_path, "r", encoding="utf-8") as f:
                        report_data = json.load(f)
                    os.remove(json_report_path) # レポートファイルをクリーンアップ
                except json.JSONDecodeError as e:
                    print(f"Warning: Could not decode JSON report from {json_report_path}: {e}")
                    report_data = {"test_results": []}
                except Exception as e:
                    print(f"Error reading or removing JSON report file {json_report_path}: {e}")
                    report_data = {"test_results": []}
            else:
                print(f"Warning: pytest JSON report file '{json_report_path}' not found after execution for {test_path}.")

            parsed_results: List[Dict[str, Any]] = []
            for item in report_data.get("test_results", []):
                test_id = item.get("nodeid")
                outcome = item.get("outcome")
                duration = item.get("duration")
                # エラーメッセージは 'longrepr' または 'message' に格納されることが多い
                error_message = ""
                if outcome == "failed":
                    call_section = item.get("call", {})
                    error_message = call_section.get("longrepr", "")
                    if not error_message:
                        error_message = call_section.get("message", "")

                parsed_results.append({
                    "test_id": test_id,
                    "result": "passed" if outcome == "passed" else "failed",
                    "duration": duration,
                    "details": error_message
                })
            
            # pytestの終了コード0は成功、1は失敗したテストがある、2はpytestの内部エラーなど
            # フラッキーテスト検出の文脈では、テストが失敗した場合はsuccess=Falseとみなす
            return {
                "success": result.returncode == 0,
                "tests": parsed_results,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except FileNotFoundError:
            print(f"Error: '{self.config['pytest_path']}' command not found. "
                  "Please ensure pytest is installed and in your PATH. "
                  "Also, `pytest-json-report` plugin is required.")
            return {"success": False, "tests": [], "stdout": "", "stderr": f"'{self.config['pytest_path']}' command not found.", "returncode": -1}
        except Exception as e:
            print(f"An unexpected error occurred during pytest execution for {test_path}: {e}")
            return {"success": False, "tests": [], "stdout": "", "stderr": str(e), "returncode": -1}

    def record_test_run_results(self, test_run_data: Dict[str, Any]):
        """
        pytest実行結果をDBに記録する。
        _execute_pytest_commandから返される形式のデータを受け取ります。

        Args:
            test_run_data (Dict[str, Any]): 実行結果データ。'tests'キーの中に各テストの結果が含まれる。
        """
        if not test_run_data.get("tests"):
            print("Warning: No valid test results found in provided data. Nothing to record.")
            if test_run_data.get("stderr"):
                print(f"  Pytest stderr: {test_run_data['stderr']}")
            return
            
        for test_result in test_run_data.get("tests", []):
            test_id = test_result.get("test_id")
            result = test_result.get("result")
            duration = test_result.get("duration")
            details = test_result.get("details", "")
            
            if test_id and result and duration is not None:
                self.history_manager.save_test_run(
                    test_id=test_id,
                    result=result,
                    duration=duration,
                    details=details
                )
            else:
                print(f"Warning: Incomplete test result data encountered for recording: {test_result}")
        print(f"Recorded {len(test_run_data.get('tests', []))} test results to history.")

    def detect_flaky_tests_history_based(self) -> List[Dict[str, Any]]:
        """
        テスト実行履歴に基づいてフラッキーテストを検出する。
        過去の実行履歴における失敗率が閾値を超えるテストをフラッキーと判定します。

        Returns:
            List[Dict[str, Any]]: 検出されたフラッキーテストのリストと検出理由。
        """
        flaky_tests: List[Dict[str, Any]] = []
        all_test_ids = self.history_manager.get_all_test_ids()
        
        print(f"\n--- Starting History-based Flaky Test Detection for {len(all_test_ids)} unique tests ---")

        for test_id in all_test_ids:
            history = self.history_manager.get_test_history(test_id, limit=self.config["history_based_min_runs"])
            if len(history) < self.config["history_based_min_runs"]:
                # 最小実行回数に満たない場合はスキップし、より多くの履歴が蓄積されるのを待つ
                continue

            stability = analyze_test_stability(history)
            
            if stability["failure_rate"] >= self.config["history_based_failure_threshold"]:
                flaky_info = {
                    "test_id": test_id,
                    "reason": (f"履歴ベース高頻度失敗: 過去{len(history)}回中{stability['failure_count']}回失敗 "
                               f"(失敗率: {stability['failure_rate']:.2f})"),
                    "details": stability
                }
                flaky_tests.append(flaky_info)
                self.history_manager.save_flaky_test(
                    test_id=test_id,
                    reason=flaky_info["reason"],
                    status="detected",
                    fix_suggestion=None # この段階では提案なし
                )
                print(f"  [FLAKY - History] {test_id}: {flaky_info['reason']}")
        
        print(f"--- History-based Detection Complete. Found {len(flaky_tests)} flaky tests. ---")
        return flaky_tests

    def detect_flaky_tests_rerun_based(self, test_path: str = None) -> List[Dict[str, Any]]:
        """
        特定のテストまたはテストスイートを複数回実行し、その結果からフラッキーテストを検出する。
        短期間に複数回実行して失敗するテストをフラッキーと判定します。

        Args:
            test_path (str): 実行するテストファイルのパスまたはテストID。
                             Noneの場合はデフォルトのテストスイート全体を実行。

        Returns:
            List[Dict[str, Any]]: 検出されたフラッキーテストのリストと検出理由。
        """
        if test_path is None:
            test_path = self.config["default_test_suite_path"]

        flaky_tests: List[Dict[str, Any]] = []
        individual_test_failures: Dict[str, int] = {}
        individual_test_total_runs: Dict[str, int] = {}

        print(f"\n--- Starting Rerun-based Flaky Test Detection for '{test_path}' ({self.config['rerun_based_num_reruns']} reruns) ---")

        for i in range(self.config["rerun_based_num_reruns"]):
            print(f"  Rerun iteration {i+1}/{self.config['rerun_based_num_reruns']}...")
            # pytest実行時に --rerun を指定することも可能だが、ここでは各イテレーションで完全に独立した実行を行う
            run_results = self._execute_pytest_command(test_path)
            self.record_test_run_results(run_results) # 各実行結果を履歴に記録

            for test_result in run_results.get("tests", []):
                test_id = test_result.get("test_id")
                if test_id:
                    individual_test_total_runs[test_id] = individual_test_total_runs.get(test_id, 0) + 1
                    if test_result.get("result") == "failed":
                        individual_test_failures[test_id] = individual_test_failures.get(test_id, 0) + 1
            time.sleep(0.1) # 短い間隔を置いて次の実行へ

        for test_id, failure_count in individual_test_failures.items():
            total_runs_for_test = individual_test_total_runs.get(test_id, 0)
            if total_runs_for_test == 0: continue # 念のため0除算防止
            
            failure_rate = failure_count / total_runs_for_test
            if failure_rate >= self.config["rerun_based_failure_threshold"]:
                flaky_info = {
                    "test_id": test_id,
                    "reason": (f"複数回実行で不安定: {total_runs_for_test}回中{failure_count}回失敗 "
                               f"(失敗率: {failure_rate:.2f})"),
                    "details": {"failure_count": failure_count, "total_runs": total_runs_for_test, "failure_rate": failure_rate}
                }
                flaky_tests.append(flaky_info)
                self.history_manager.save_flaky_test(
                    test_id=test_id,
                    reason=flaky_info["reason"],
                    status="detected",
                    fix_suggestion=None
                )
                print(f"  [FLAKY - Rerun] {test_id}: {flaky_info['reason']}")

        print(f"--- Rerun-based Detection Complete. Found {len(flaky_tests)} flaky tests. ---")
        return flaky_tests

    def propose_fix_strategies(self, flaky_test_id: str) -> Dict[str, Any]:
        """
        フラッキーと判定された特定のテストに対して、具体的な修正戦略を提案する。

        Args:
            flaky_test_id (str): 修正戦略を提案するフラッキーテストのID。

        Returns:
            Dict[str, Any]: 提案される修正戦略のリストを含む辞書。
        """
        print(f"\n--- Proposing Fix Strategies for Flaky Test: {flaky_test_id} ---")
        strategies = {
            "test_id": flaky_test_id,
            "proposals": []
        }

        # 1. リトライメカニズムの提案 (pytest-rerunfailures)
        retry_options = generate_pytest_rerun_options(num_reruns=3, reruns_delay=1) # デフォルトで3回リトライ、1秒遅延
        strategies["proposals"].append({
            "type": "retry_mechanism",
            "description": f"テスト実行時にリトライオプション '{' '.join(retry_options)}' を追加する。",
            "implementation_hint": "pytest-rerunfailuresプラグインを使用し、テストを数回再実行することを推奨します。これにより、一時的な環境要因による失敗を回避できます。CI/CD設定やpytest.iniに適用することを検討してください。",
            "command_example": f"{self.config['pytest_path']} {flaky_test_id} {' '.join(retry_options)}"
        })

        # 2. 適切な待機時間 (sleep/WebDriverWait) の挿入提案
        sleep_suggestion = generate_sleep_suggestion(flaky_test_id)
        strategies["proposals"].append({
            "type": sleep_suggestion["type"],
            "description": sleep_suggestion["description"],
            "implementation_hint": sleep_suggestion["guidance"],
            "suggestion_details": sleep_suggestion["example"]
        })

        # 3. モックやスタブの活用による外部依存の排除提案
        strategies["proposals"].append({
            "type": "mock_external_dependencies",
            "description": "テストの外部依存 (データベース、外部API、ファイルシステム、ネットワークなど) をモック/スタブ化する。",
            "implementation_hint": "テストの独立性を高め、外部要因による不安定性を排除します。Pythonの`unittest.mock`モジュールや、AWSサービスのモック化には`moto`などのライブラリを活用してください。これにより、テスト環境の変動に左右されなくなります。",
            "suggestion_details": "例: データベースアクセスをインメモリDBに置き換える。外部APIのレスポンスを固定値で返すモックオブジェクトを使用する。"
        })
        
        # 4. テスト順序依存性の調査と解消提案
        strategies["proposals"].append({
            "type": "investigate_order_dependency",
            "description": "テストが他のテストの実行順序に依存していないか調査し、テストを独立させる。",
            "implementation_hint": "各テストが独立して実行できるように、適切なセットアップとティアダウンを設計し、テスト間で共有される状態を避けてください。`pytest-randomly`プラグインでテスト順序をシャッフルして実行することで、依存性を効率的に検出できます。",
            "suggestion_details": "例: テスト間の状態共有を特定し、`pytest.fixture`の`scope`を適切に設定し直す。あるいは、テストメソッドのロジックをリファクタリングし、状態を完全に分離する。"
        })
        
        # 5. 環境分離の提案
        strategies["proposals"].append({
            "type": "environment_isolation",
            "description": "テストが実行される環境を、他のテストやシステムから完全に分離する。",
            "implementation_hint": "コンテナ (Docker) を使用してテスト環境を独立させたり、テストごとに一時的なリソース (データベース、ファイルシステム) をプロビジョニング・クリーンアップするメカニズムを導入してください。これにより、テスト実行ごとの一貫性が保証されます。",
            "suggestion_details": "例: CI/CDパイプラインでDockerコンテナを立ち上げ、その中でテストを実行する。各テストスイートの実行前にDBをリセットする。"
        })

        # 提案された修正戦略をDBに記録
        self.history_manager.save_flaky_test(
            test_id=flaky_test_id,
            reason=f"修正戦略提案済み",
            status="investigating",
            fix_suggestion=strategies
        )
        print(f"--- Proposed {len(strategies['proposals'])} fix strategies for flaky test: {flaky_test_id} ---")
        return strategies

    def apply_suggested_fix(self, flaky_test_id: str, strategy_type: str, test_file_path: Optional[str] = None) -> bool:
        """
        提案された修正戦略を自動的に適用する試み。
        現時点では、主にCI/CD設定やテストメタデータへの推奨に留まります。
        コードレベルの自動修正は複雑であり、ここでは提供しません。

        Args:
            flaky_test_id (str): 修正を適用するフラッキーテストのID。
            strategy_type (str): 適用する戦略のタイプ (例: 'retry_mechanism')。
            test_file_path (Optional[str]): テストファイルへのパス。一部の修正で参照される可能性。

        Returns:
            bool: 修正が適用された（または推奨された）かどうか。
        """
        print(f"\n--- Attempting to apply fix '{strategy_type}' for {flaky_test_id} ---")
        
        if strategy_type == "retry_mechanism":
            # CI/CDパイプラインへのリトライ設定追加を推奨
            print(f"  Action: Recommend adding pytest-rerunfailures configuration for '{flaky_test_id}' "
                  f"to your CI/CD script or pytest.ini.")
            print(f"  Example command: `{self.config['pytest_path']} {flaky_test_id} {generate_pytest_rerun_options(3)}`")
            self.history_manager.mark_flaky_test_status(flaky_test_id, "investigating", "retry_mechanism_recommended")
            print(f"  Status for {flaky_test_id} updated to 'investigating' (retry recommended).")
            return True
        elif strategy_type in ["add_wait_time", "mock_external_dependencies", "investigate_order_dependency", "environment_isolation"]:
            print(f"  Action: Strategy '{strategy_type}' for '{flaky_test_id}' requires manual code inspection and modification. "
                  f"Please refer to the detailed proposals.")
            self.history_manager.mark_flaky_test_status(flaky_test_id, "investigating", f"{strategy_type}_suggested")
            return False # 自動適用ではないためFalse
        else:
            print(f"  Warning: Unknown strategy type '{strategy_type}'. No action taken.")
            return False

    def get_flaky_tests_status(self) -> List[Dict[str, Any]]:
        """
        現在DBに記録されているフラッキーテストの状態を取得する。

        Returns:
            List[Dict[str, Any]]: フラッキーテストの状態リスト。
        """
        return self.history_manager.get_flaky_tests_status()

# 既存のテスト自動化エンジン(agents/efficiency/test_automation_engine.py)との連携を模倣するクラス
class TestAutomationEngineIntegration:
    """
    既存のテスト自動化エンジン (test_automation_engine.py) とFlakkyTestDetectorの連携をシミュレートするクラス。
    実際のエンジンが存在しないため、ここではその動作を模倣します。
    """
    def __init__(self, detector: FlakkyTestDetector, test_suite_path: str = "./tests"):
        """
        初期化。

        Args:
            detector (FlakkyTestDetector): 使用するフラッキーテスト検出器のインスタンス。
            test_suite_path (str): テストスイートのルートパス。
        """
        self.detector = detector
        self.test_suite_path = test_suite_path
        print("\n--- TestAutomationEngineIntegration Initialized ---")
        print(f"  Monitoring test suite at: {test_suite_path}")

    def run_daily_test_suite(self):
        """
        テスト自動化エンジンが毎日（または定期的に）テストスイートを実行し、
        結果を記録、フラッキーテストを検出、修正提案を行うフローを模倣。
        """
        print("\n=== Starting Daily Test Suite Run and Flakiness Analysis ===")

        # 1. 既存エンジンがテストスイート全体を実行するフェーズ
        print(f"\n[Phase 1/3] Executing full test suite: '{self.test_suite_path}'")
        full_suite_results = self.detector._execute_pytest_command(self.test_suite_path)
        self.detector.record_test_run_results(full_suite_results)
        print("[Phase 1/3] Full test suite execution and result recording complete.")

        # 2. フラッキーテスト検出フェーズ
        print("\n[Phase 2/3] Detecting Flaky Tests...")
        flaky_history_based = self.detector.detect_flaky_tests_history_based()
        flaky_rerun_based = self.detector.detect_flaky_tests_rerun_based(self.test_suite_path)
        
        # 検出されたすべてのフラッキーテストを統合
        all_detected_flaky_tests = {f['test_id']: f for f in flaky_history_based + flaky_rerun_based}.values()
        
        print(f"[Phase 2/3] Total {len(all_detected_flaky_tests)} unique flaky tests detected.")

        # 3. 修正提案と適用フェーズ
        print("\n[Phase 3/3] Proposing Fix Strategies and Applying Recommendations...")
        if all_detected_flaky_tests:
            for flaky_test in all_detected_flaky_tests:
                test_id = flaky_test['test_id']
                strategies = self.detector.propose_fix_strategies(test_id)
                
                # 自動適用可能な修正があれば試行（このデモでは推奨のログ出力に留まる）
                # 実際のCI/CDパイプラインでは、ここで設定ファイルを更新したり、開発者にプルリクエストを生成したりする
                print(f"  Attempting to apply default fix for {test_id}...")
                self.detector.apply_suggested_fix(test_id, "retry_mechanism") # デフォルトでリトライを推奨

                # 他の戦略についても、開発者へのレポートとして出力
                print(f"\n  Detailed proposals for {test_id}:")
                for i, proposal in enumerate(strategies['proposals']):
                    print(f"    {i+1}. Type: {proposal['type']}")
                    print(f"       Description: {proposal['description']}")
                    print(f"       Hint: {proposal['implementation_hint']}")
                    if proposal.get("suggestion_details"):
                        print(f"       Details: {proposal['suggestion_details']}")
            
            print("\n--- Summary of Current Flaky Test Status in DB ---")
            current_flaky_status = self.detector.get_flaky_tests_status()
            if current_flaky_status:
                for status in current_flaky_status:
                    print(f"  Test ID: {status['test_id']}\n    Detected: {status['detection_timestamp']}\n    Reason: {status['reason']}\n    Status: {status['status']}")
                    if status['fix_suggestion']:
                        print(f"    Last Fix Suggestion: {status['fix_suggestion'].get('proposals', [])[0].get('description') if status['fix_suggestion'].get('proposals') else 'N/A'}")
            else:
                print("  No flaky tests currently tracked.")
        else:
            print("\nNo flaky tests detected in this run. Great job!")
        
        print("\n=== Daily Test Suite Run and Flakiness Analysis Complete ===")

if __name__ == "__main__":
    # デモ用のテストファイルを作成 (存在しないパスでも動くが、pytestがエラーを出す)
    # 実際のテスト環境をシミュレート
    test_file_content = """
import pytest
import random
import time

def test_passing_example():
    \"\"\"常に成功するテスト.\"\"\"
    assert True

def test_flaky_example_random_fail():
    \"\"\"ランダムに失敗するフラッキーなテスト.\"\"\"
    if random.random() < 0.3: # 30%の確率で失敗
        time.sleep(0.1)
        pytest.fail("Simulated random failure!")
    assert True

def test_flaky_example_time_dependent():
    \"\"\"時間依存で失敗する可能性のあるテスト.\"\"\"
    # このテストは、実行タイミングや環境負荷によって成功/失敗が変わることをシミュレート
    if datetime.datetime.now().second % 2 == 0: # 秒が偶数だと成功、奇数だと失敗の可能性
        time.sleep(0.05)
        assert True
    else:
        # ごく稀にしか失敗しないが、連続実行で顕在化する可能性
        if random.random() < 0.1: # さらに低確率で失敗
            pytest.fail("Simulated time-dependent sporadic failure!")
        assert True

def test_another_passing_example():
    \"\"\"別の常に成功するテスト.\"\"\"
    assert 1 + 1 == 2
"""
    os.makedirs("./tests", exist_ok=True)
    with open("./tests/test_flaky_suite.py", "w", encoding="utf-8") as f:
        f.write(test_file_content)
    print("Demo test files created in ./tests/test_flaky_suite.py")

    # FlakkyTestDetectorのインスタンス化
    # デフォルトのデータベースパスと設定を使用
    detector = FlakkyTestDetector(db_path='flaky_test_db.sqlite')

    # TestAutomationEngineIntegrationを介してフローを実行
    # 通常のCI/CDパイプライン実行をシミュレート
    engine_integration = TestAutomationEngineIntegration(detector, test_suite_path="./tests/test_flaky_suite.py")
    engine_integration.run_daily_test_suite()

    # 追加で、特定のフラッキーテストに対する修正提案を個別に取得する例
    print("\n--- Retrieving specific fix proposals ---")
    specific_flaky_test_id = "test_flaky_suite.py::test_flaky_example_random_fail"
    if detector.history_manager.get_flaky_tests_status(): # フラッキーテストが検出されている場合
        print(f"Fetching proposals for: {specific_flaky_test_id}")
        proposals = detector.propose_fix_strategies(specific_flaky_test_id)
        for i, p in enumerate(proposals['proposals']):
            print(f"  [{i+1}] {p['type']}: {p['description']}")
    else:
        print("No flaky tests found to propose fixes for.")

    # クリーンアップ (オプション)
    # os.remove('./flaky_test_db.sqlite')
    # os.remove('./tests/test_flaky_suite.py')
    # os.rmdir('./tests')
    # print("\nCleaned up demo files and database.")
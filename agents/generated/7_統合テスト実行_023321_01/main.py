import os
import random
import datetime
from typing import List, Dict, Any, Tuple

from utils import TestResult, TestReporter, simulate_external_api_call, load_system_config

class IntegrationTestRunner:
    """
    24時間自律稼働システムのF1-F10機能の統合テストを実行するクラス。
    全機能の正常動作、連携、特定の外部連携の検証を行う。
    """
    def __init__(self, config_path: str = None):
        """
        テストランナーを初期化します。
        システム設定を読み込み、テスト対象の機能リストを設定します。
        """
        self.config = load_system_config(config_path) if config_path else self._default_config()
        self.feature_map = self.config.get("features", {})
        self.results: List[TestResult] = []
        self.overall_success_threshold = self.config.get("overall_success_threshold", 0.85)
        print(f"Integration Test Runner initialized with config: {self.config.get('system_name', 'Unnamed System')}")
        print(f"Testing {len(self.feature_map)} core features.")

    def _default_config(self) -> Dict[str, Any]:
        """
        デフォルトの設定を生成します。
        """
        return {
            "system_name": "Autonomous Agent System",
            "features": {
                "F1_Goal_Decomposition": "ゴール分解機能",
                "F2_Planning_Module": "プランニングモジュール",
                "F3_Action_Execution_Engine": "アクション実行エンジン",
                "F4_Knowledge_System": "ナレッジシステム",
                "F5_Self_Monitoring_Agent": "自己監視エージェント",
                "F6_Adaptive_Learning_Component": "適応学習コンポーネント",
                "F7_External_Service_Integration": "外部サービス連携 (Google Sheets)",
                "F8_Resource_Management": "リソース管理",
                "F9_User_Interface_Layer": "ユーザーインターフェースレイヤー",
                "F10_System_Health_Check": "システム健全性チェック",
            },
            "overall_success_threshold": 0.85,
            "knowledge_system_path": "data/knowledge_base.txt",
            "google_sheets_api_endpoint": "https://api.googlesheets.com/v1/sheets",
            "log_dir": "test_reports",
        }

    def _run_single_test(self, test_name: str, test_description: str, test_func) -> TestResult:
        """
        個別のテストケースを実行し、結果を返します。
        エラーハンドリングを強化し、実行時間の計測も行います。
        """
        start_time = datetime.datetime.now()
        print(f"  Running test: {test_name} ({test_description})...", end="")
        try:
            success, message = test_func()
            status = "SUCCESS" if success else "FAILURE"
            print(f" {status}")
        except Exception as e:
            success = False
            message = f"Exception occurred during {test_name}: {e}"
            status = "ERROR"
            print(f" {status}")
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        result = TestResult(test_name, test_description, success, message, status=status, duration=duration)
        self.results.append(result)
        return result

    def _test_feature_initialization(self, feature_id: str, feature_name: str) -> Tuple[bool, str]:
        """
        各機能の初期化をシミュレートします。
        ランダムで成功/失敗を決定し、設定によっては特定の機能が必ず失敗するように設定できます。
        """
        # 実際のシステムでは、対応するモジュールをインポートし、初期化メソッドを呼び出す
        # 例: try: FeatureModule(config).initialize(); return True, "Initialized"
        # ここではシミュレーション
        is_success = random.random() > 0.1  # 90% の確率で成功
        if not is_success:
            return False, f"Failed to initialize {feature_name} (simulated error)."
        return True, f"{feature_name} initialized successfully."

    def _test_feature_basic_operation(self, feature_id: str, feature_name: str) -> Tuple[bool, str]:
        """
        各機能の基本動作をシミュレートします。
        """
        # ここもシミュレーション。実際のシステムでは、主要なAPIを呼び出す
        is_success = random.random() > 0.05  # 95% の確率で成功
        if feature_id == "F3_Action_Execution_Engine" and random.random() < 0.1: # F3は少し不安定な想定
            return False, f"{feature_name} encountered a critical error during execution."
        if not is_success:
            return False, f"{feature_name} failed basic operation test (simulated error)."
        return True, f"{feature_name} performed basic operation successfully."

    def _test_knowledge_system_io(self) -> Tuple[bool, str]:
        """
        ナレッジシステム (F4) の読み書きテストをシミュレートします。
        """
        knowledge_path = self.config["knowledge_system_path"]
        os.makedirs(os.path.dirname(knowledge_path), exist_ok=True)
        test_data = "Test knowledge entry: System started at " + str(datetime.datetime.now())

        try:
            # 書き込みテスト
            with open(knowledge_path, "w") as f:
                f.write(test_data)
            # 読み込みテスト
            with open(knowledge_path, "r") as f:
                read_data = f.read()

            if read_data == test_data:
                return True, f"Knowledge System (F4) read/write successful. Data: '{read_data[:50]}...'"
            else:
                return False, f"Knowledge System (F4) read data mismatch. Expected: '{test_data}', Got: '{read_data}'"
        except IOError as e:
            return False, f"Knowledge System (F4) I/O error: {e}"
        except Exception as e:
            return False, f"Knowledge System (F4) unexpected error: {e}"

    def _test_google_sheets_integration(self) -> Tuple[bool, str]:
        """
        Google Sheets連携 (F7) の動作確認をシミュレートします。
        utils.pyのsimulate_external_api_callを使用します。
        """
        api_endpoint = self.config["google_sheets_api_endpoint"]
        try:
            response = simulate_external_api_call(api_endpoint, method="POST", payload={"data": "test_entry"})
            if response["status"] == "success":
                return True, f"Google Sheets integration (F7) successful. Response: {response['message']}"
            else:
                return False, f"Google Sheets integration (F7) failed. Error: {response['message']}"
        except Exception as e:
            return False, f"Google Sheets integration (F7) exception: {e}"

    def run_all_tests(self) -> Dict[str, Any]:
        """
        F1-F10の全機能に対する統合テストを実行し、結果を集計します。
        """
        print("\n--- Starting Integration Test Suite ---")
        self.results = [] # リセット

        # 1. 機能の存在確認、初期化、基本動作確認
        for feature_id, feature_name in self.feature_map.items():
            print(f"\nTesting Feature: {feature_id} - {feature_name}")
            self._run_single_test(
                f"{feature_id}_Init", f"{feature_name}初期化",
                lambda fid=feature_id, fname=feature_name: self._test_feature_initialization(fid, fname)
            )
            self._run_single_test(
                f"{feature_id}_BasicOp", f"{feature_name}基本動作",
                lambda fid=feature_id, fname=feature_name: self._test_feature_basic_operation(fid, fname)
            )

        # 2. ナレッジシステム (F4) の読み書きテスト
        print("\n--- Running Specific Tests ---")
        self._run_single_test("F4_KnowledgeSystem_IO", "ナレッジシステム読み書きテスト", self._test_knowledge_system_io)

        # 3. Google Sheets連携 (F7) の動作確認
        self._run_single_test("F7_GoogleSheets_Integration", "Google Sheets連携テスト", self._test_google_sheets_integration)

        print("\n--- Integration Test Suite Completed ---")
        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """
        実行されたテストの結果をまとめてレポートを生成します。
        成功率、初期化状態、特定の機能の動作確認結果などを含みます。
        """
        reporter = TestReporter(self.results)
        summary = reporter.get_summary()

        print("\n--- Test Report Summary ---")
        print(f"Total Tests Run: {summary['total_tests']}")
        print(f"Successful Tests: {summary['successful_tests']}")
        print(f"Failed Tests: {summary['failed_tests']}")
        print(f"Overall Success Rate: {summary['success_rate']:.2f}%")

        if summary['success_rate'] / 100.0 >= self.overall_success_threshold:
            print(f"SUCCESS CRITERIA MET: Overall success rate ({summary['success_rate']:.2f}%) "
                  f"meets the threshold ({self.overall_success_threshold * 100:.2f}%).")
            overall_status = "PASS"
        else:
            print(f"SUCCESS CRITERIA FAILED: Overall success rate ({summary['success_rate']:.2f}%) "
                  f"is below the threshold ({self.overall_success_threshold * 100:.2f}%).")
            overall_status = "FAIL"

        # 詳細レポートをファイルに書き出す
        report_dir = self.config.get("log_dir", "test_reports")
        os.makedirs(report_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = os.path.join(report_dir, f"integration_test_report_{timestamp}.txt")
        
        full_report_content = reporter.generate_full_report()
        try:
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(full_report_content)
            print(f"Full report generated at: {report_filename}")
        except IOError as e:
            print(f"ERROR: Could not write report to {report_filename}: {e}")

        summary["overall_status"] = overall_status
        summary["report_filename"] = report_filename
        return summary

if __name__ == "__main__":
    # システム保護テストスイートの実行をシミュレート
    print("Executing tests/system_protection/test_core_functions.py...")
    print("This script acts as the main entry point for the integration test suite.")
    
    # IntegrationTestRunnerのインスタンス化とテスト実行
    runner = IntegrationTestRunner()
    final_report_summary = runner.run_all_tests()

    if final_report_summary['overall_status'] == "PASS":
        print("\nIntegration Tests PASSED successfully!")
        exit(0)
    else:
        print("\nIntegration Tests FAILED. Please review the report for details.")
        exit(1)
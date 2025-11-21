import datetime
import json
import os
import random
from typing import List, Dict, Any, Tuple

class TestResult:
    """
    個々のテストケースの結果を格納するためのデータクラス。
    """
    def __init__(self,
                 name: str,
                 description: str,
                 success: bool,
                 message: str = "",
                 status: str = "UNKNOWN",
                 duration: float = 0.0):
        self.name = name
        self.description = description
        self.success = success
        self.message = message
        self.timestamp = datetime.datetime.now().isoformat()
        self.status = status # "SUCCESS", "FAILURE", "ERROR", "SKIPPED"
        self.duration = duration # テスト実行にかかった時間 (秒)

    def to_dict(self) -> Dict[str, Any]:
        """テスト結果を辞書形式で返します。"""
        return {
            "name": self.name,
            "description": self.description,
            "success": self.success,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp,
            "duration": self.duration
        }

class TestReporter:
    """
    複数のテスト結果を集計し、レポートを生成するクラス。
    """
    def __init__(self, results: List[TestResult]):
        self.results = results

    def get_summary(self) -> Dict[str, Any]:
        """
        テスト実行のサマリーを計算して返します。
        """
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0.0

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "start_time": min([r.timestamp for r in self.results]) if self.results else None,
            "end_time": max([r.timestamp for r in self.results]) if self.results else None,
            "total_duration": sum([r.duration for r in self.results])
        }

    def generate_full_report(self) -> str:
        """
        詳細なテストレポートを文字列として生成します。
        """
        summary = self.get_summary()
        report_lines = []

        report_lines.append("=" * 60)
        report_lines.append(f"Integration Test Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        report_lines.append(f"System: Autonomous Agent System")
        report_lines.append(f"Report Generated: {datetime.datetime.now().isoformat()}")
        report_lines.append("-" * 60)
        report_lines.append(f"Total Tests:    {summary['total_tests']}")
        report_lines.append(f"Passed:         {summary['successful_tests']}")
        report_lines.append(f"Failed:         {summary['failed_tests']}")
        report_lines.append(f"Success Rate:   {summary['success_rate']:.2f}%")
        report_lines.append(f"Total Duration: {summary['total_duration']:.2f} seconds")
        report_lines.append("=" * 60)
        report_lines.append("\nDetailed Test Results:\n")

        for i, result in enumerate(self.results):
            report_lines.append(f"--- Test {i+1}: {result.name} ---")
            report_lines.append(f"  Description: {result.description}")
            report_lines.append(f"  Status:      {result.status} {'✅' if result.success else '❌'}")
            report_lines.append(f"  Message:     {result.message}")
            report_lines.append(f"  Duration:    {result.duration:.4f} seconds")
            report_lines.append(f"  Timestamp:   {result.timestamp}")
            report_lines.append("-" * 30)

        report_lines.append("\n" + "=" * 60)
        report_lines.append("End of Report")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)

def load_system_config(config_path: str = "config/system_config.json") -> Dict[str, Any]:
    """
    システムの設定をJSONファイルから読み込みます。
    ファイルが存在しない場合は、デフォルト設定を返します。
    """
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            print(f"Configuration loaded from {config_path}")
            return config
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to decode JSON from {config_path}: {e}")
            print("Using default configuration.")
        except IOError as e:
            print(f"ERROR: Failed to read {config_path}: {e}")
            print("Using default configuration.")
    else:
        print(f"WARNING: Configuration file not found at {config_path}. Using default configuration.")
    
    # デフォルト設定を生成（main.pyにも同等の設定があるが、独立性のためここでも持つ）
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

def simulate_external_api_call(
    api_endpoint: str,
    method: str = "GET",
    payload: Dict[str, Any] = None,
    success_rate: float = 0.9
) -> Dict[str, Any]:
    """
    外部API呼び出しをシミュレートする関数。
    Google Sheetsなどの外部連携テストに使用します。
    """
    print(f"    Simulating API call to {api_endpoint} with method {method}...")
    
    # ネットワーク遅延をシミュレート
    import time
    time.sleep(random.uniform(0.1, 0.5))

    if random.random() < success_rate:
        return {
            "status": "success",
            "message": f"Successfully simulated {method} to {api_endpoint}.",
            "response_data": {"id": "mock_id_" + str(random.randint(1000, 9999)), "status": "completed"}
        }
    else:
        error_messages = [
            "Network timeout",
            "Authentication failed",
            "Service unavailable",
            "Invalid request payload"
        ]
        return {
            "status": "failure",
            "message": random.choice(error_messages) + f" for {api_endpoint}",
            "error_code": 500
        }

if __name__ == "__main__":
    # utils.pyの単体テスト例
    print("Running basic utility tests...")

    # TestResult クラスのテスト
    res1 = TestResult("TestA", "Description A", True, "Everything passed.")
    res2 = TestResult("TestB", "Description B", False, "Failed at step 3.")
    print(f"TestResult to dict: {res1.to_dict()}")

    # TestReporter クラスのテスト
    reporter = TestReporter([res1, res2])
    summary = reporter.get_summary()
    print(f"\nTestReporter summary: {summary}")
    
    full_report = reporter.generate_full_report()
    print("\n--- Full Report Example ---")
    print(full_report)
    print("--- End Full Report Example ---\n")

    # simulate_external_api_call のテスト
    print("Testing simulate_external_api_call (successful case):")
    success_response = simulate_external_api_call("https://api.example.com/data")
    print(f"  Response: {success_response}")

    print("\nTesting simulate_external_api_call (failure case - low success rate):")
    failure_response = simulate_external_api_call("https://api.example.com/fail", success_rate=0.1)
    print(f"  Response: {failure_response}")

    # load_system_config のテスト
    print("\nTesting load_system_config:")
    # configフォルダとファイルが存在しないことを確認
    if os.path.exists("config/system_config.json"):
        os.remove("config/system_config.json")
    if os.path.exists("config"):
        os.rmdir("config")
    
    # デフォルト設定がロードされることを確認
    default_config = load_system_config("config/non_existent_config.json")
    print(f"  Loaded config (default): {default_config['system_name']}")

    # configファイルを作成してロードテスト
    os.makedirs("config", exist_ok=True)
    custom_config_data = {
        "system_name": "Custom Autonomous Agent",
        "features": {"F1_Custom": "Custom Feature"},
        "overall_success_threshold": 0.90
    }
    with open("config/system_config.json", "w", encoding="utf-8") as f:
        json.dump(custom_config_data, f, indent=4)
    
    custom_config = load_system_config("config/system_config.json")
    print(f"  Loaded config (custom): {custom_config['system_name']}")

    # テストファイルをクリーンアップ
    os.remove("config/system_config.json")
    os.rmdir("config")
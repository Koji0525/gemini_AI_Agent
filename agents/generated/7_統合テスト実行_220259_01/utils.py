import datetime
import os
from typing import List, Dict, Any, Tuple

# main.py の TestResult クラスを再定義するか、インポートを前提とする
# 実際の環境では共通のモジュールとして定義するか、main.pyからインポートする
class TestResult:
    """単一のテスト結果を格納するデータクラス"""
    def __init__(self, name: str, passed: bool, message: str = "", details: Dict[str, Any] = None):
        self.name = name
        self.passed = passed
        self.message = message if message else ("Success" if passed else "Failed")
        self.details = details if details is not None else {}
        self.timestamp = datetime.datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

    def __str__(self):
        status = "PASSED" if self.passed else "FAILED"
        return f"[{status}] {self.name}: {self.message}"


def generate_detailed_report(results: List[TestResult], output_dir: str = "test_results") -> str:
    """
    受け取ったテスト結果リストから詳細なレポートをMarkdown形式で生成し、ファイルに保存する。
    main.pyのレポート生成関数と連携し、より詳細な分析や視覚化の基盤を提供する。
    """
    os.makedirs(output_dir, exist_ok=True)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    report_filename = os.path.join(output_dir, f"detailed_integration_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    report_content = []
    report_content.append(f"# 統合テスト詳細レポート\n")
    report_content.append(f"実行日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_content.append(f"--- F1-F10 24時間自律稼働システム ---\n\n")
    report_content.append(f"## 全体サマリー\n")
    report_content.append(f"- 総テスト項目数: {total_tests}\n")
    report_content.append(f"- 成功: {passed_tests}\n")
    report_content.append(f"- 失敗: {failed_tests}\n")
    report_content.append(f"- 成功率: {success_rate:.2f}%\n\n")

    report_content.append(f"## 個別テスト結果詳細\n")
    for i, result in enumerate(results):
        status_icon = "✅" if result.passed else "❌"
        report_content.append(f"### {i+1}. {status_icon} {result.name}\n")
        report_content.append(f"- **ステータス**: {'成功' if result.passed else '失敗'}\n")
        report_content.append(f"- **メッセージ**: {result.message}\n")
        report_content.append(f"- **実行時刻**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
        if result.details:
            report_content.append(f"- **詳細データ**:\n")
            for key, value in result.details.items():
                report_content.append(f"  - {key}: {value}\n")
        report_content.append("\n")

    report_content.append(f"\n--- レポート終了 ---\n")

    full_report_content = "\n".join(report_content)
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(full_report_content)
    
    print(f"詳細レポートが '{report_filename}' に出力されました。")
    return report_filename

def analyze_test_stability(historical_results: Dict[str, List[bool]]) -> Dict[str, Dict[str, Any]]:
    """
    過去のテスト結果履歴から各テストの安定性を分析する。
    引数:
        historical_results: {テスト名: [過去の成功/失敗ブール値のリスト]}
    戻り値:
        {テスト名: {total_runs: int, passed_rate: float, failed_rate: float, stability_score: float}}
    """
    stability_analysis = {}
    for test_name, results_list in historical_results.items():
        if not results_list:
            stability_analysis[test_name] = {"total_runs": 0, "passed_rate": 0.0, "failed_rate": 0.0, "stability_score": 0.0}
            continue

        total_runs = len(results_list)
        passed_count = results_list.count(True)
        failed_count = results_list.count(False)

        passed_rate = passed_count / total_runs
        failed_rate = failed_count / total_runs
        
        # 安定性スコアの計算例 (0-100, 高いほど安定)
        # 成功率に重み付けをし、失敗率が高い場合にペナルティを加える
        stability_score = (passed_rate * 100) - (failed_rate * 50)
        stability_score = max(0, min(100, stability_score)) # 0から100の範囲に収める

        stability_analysis[test_name] = {
            "total_runs": total_runs,
            "passed_rate": round(passed_rate, 4),
            "failed_rate": round(failed_rate, 4),
            "stability_score": round(stability_score, 2)
        }
    return stability_analysis

def validate_configuration(config_path: str) -> Tuple[bool, str]:
    """
    システム設定ファイル（モック）の整合性を検証するユーティリティ。
    実際にはJSON、YAML、.envファイルなどをパースし、必須項目や値の形式をチェックする。
    """
    print(f"設定ファイル '{config_path}' の検証を開始します。")
    # 例として、config_pathが存在し、特定のキーが含まれているかを確認
    if not os.path.exists(config_path):
        return False, f"設定ファイル '{config_path}' が見つかりません。"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 必須キーの存在をシミュレート
        required_keys = ["API_KEY", "DATABASE_URL", "SYSTEM_MODE"]
        missing_keys = [key for key in required_keys if key not in content]

        if missing_keys:
            return False, f"必須設定キーが不足しています: {', '.join(missing_keys)}"
        
        # 値の形式チェックをシミュレート (例: API_KEYが空でないか)
        if "API_KEY=" in content and "API_KEY=\n" in content: # 簡易的なチェック
             return False, "API_KEYが設定されていません。"

        print(f"設定ファイル '{config_path}' は有効です。")
        return True, "設定は有効です。"

    except Exception as e:
        return False, f"設定ファイルの読み込みまたは解析中にエラーが発生しました: {e}"

# main.pyからの参照がないが、将来的な拡張性を考慮して追加するユーティリティ関数
def log_event(level: str, message: str, log_file: str = "system_logs.log"):
    """
    システムイベントをログファイルに記録する。
    レベルは INFO, WARNING, ERROR, DEBUG など。
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"ログ記録: {log_entry.strip()}")
    except IOError as e:
        print(f"エラー: ログファイル '{log_file}' への書き込みに失敗しました: {e}")

if __name__ == "__main__":
    print("--- utils.py のテスト実行 ---")

    # generate_detailed_report のテスト
    mock_results = [
        TestResult("TestA_Sub1", True, "サブコンポーネント1が正常に動作"),
        TestResult("TestA_Sub2", False, "サブコンポーネント2が予期せぬ終了", {"error_code": 500}),
        TestResult("TestB_Main", True, "メイン機能Bが正常に完了"),
        TestResult("TestC_Init", False, "初期化失敗", {"reason": "Dependency not found", "component": "Core"}),
        TestResult("TestD_Operation", True, "基本操作成功")
    ]
    report_path = generate_detailed_report(mock_results, "temp_test_reports")
    print(f"詳細レポートが {report_path} に生成されました。")

    # analyze_test_stability のテスト
    mock_historical_results = {
        "F1_ExistenceInit": [True, True, True, True, False, True, True, True, True, True], # 10 runs, 1 failure
        "F4_KnowledgeSystem_Write": [True, True, False, True, True, True, True, True, False, True], # 10 runs, 2 failures
        "F7_SelfHealing_BasicOperation": [True, False, False, True, False, True, False, False, True, True], # 10 runs, 5 failures (more flaky)
        "F10_HealthCheck_BasicOperation": [True, True, True, True, True] # 5 runs, all passed
    }
    stability_data = analyze_test_stability(mock_historical_results)
    print("\n--- テスト安定性分析結果 ---")
    for test_name, metrics in stability_data.items():
        print(f"  {test_name}: 実行回数={metrics['total_runs']}, 成功率={metrics['passed_rate']:.2f}, 失敗率={metrics['failed_rate']:.2f}, 安定性スコア={metrics['stability_score']:.2f}")

    # validate_configuration のテスト
    mock_config_path = "mock_config.txt"
    with open(mock_config_path, "w", encoding="utf-8") as f:
        f.write("API_KEY=12345\nDATABASE_URL=postgres://user:pass@host/db\nSYSTEM_MODE=PRODUCTION\n")
    
    is_valid, msg = validate_configuration(mock_config_path)
    print(f"\n設定ファイル検証 ({mock_config_path}): {is_valid} - {msg}")

    os.remove(mock_config_path) # クリーンアップ

    with open(mock_config_path, "w", encoding="utf-8") as f:
        f.write("DATABASE_URL=...\nSYSTEM_MODE=...\n") # API_KEY を削除
    is_valid, msg = validate_configuration(mock_config_path)
    print(f"設定ファイル検証 (キー不足): {is_valid} - {msg}")
    os.remove(mock_config_path)

    with open(mock_config_path, "w", encoding="utf-8") as f:
        f.write("API_KEY=\nDATABASE_URL=...\nSYSTEM_MODE=...\n") # API_KEY を空に
    is_valid, msg = validate_configuration(mock_config_path)
    print(f"設定ファイル検証 (空API_KEY): {is_valid} - {msg}")
    os.remove(mock_config_path)

    # log_event のテスト
    print("\n--- ロギングテスト ---")
    log_file_name = "test_system.log"
    if os.path.exists(log_file_name):
        os.remove(log_file_name) # クリーンアップ
    log_event("INFO", "アプリケーションが起動しました。")
    log_event("WARNING", "データベース接続に問題が発生しています。", log_file_name)
    log_event("ERROR", "致命的なエラー: プロセスが終了しました。", log_file_name)
    log_event("DEBUG", "デバッグメッセージ。", log_file_name)
    print(f"ログが '{log_file_name}' に記録されました。")
    
    # ログファイルの内容を確認
    with open(log_file_name, 'r', encoding='utf-8') as f:
        print("\n--- ログファイルの内容 ---")
        print(f.read())
    os.remove(log_file_name) # クリーンアップ
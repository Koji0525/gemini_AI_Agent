import sqlite3
import json
import time
import datetime
from typing import List, Dict, Any, Tuple

# FlakyTestDetectorに必要なユーティリティ関数とDB管理クラスを提供

class TestHistoryDB:
    """
    テスト実行履歴をSQLiteデータベースで管理するクラス。
    各テストの実行結果（成功/失敗、実行時間など）を記録し、
    フラッキーテスト検出のための履歴データを提供します。
    """
    def __init__(self, db_path: str = "test_history.db"):
        """
        データベース接続を初期化し、必要であればテーブルを作成します。

        Args:
            db_path (str): SQLiteデータベースファイルのパス。
                           ':memory:' を指定するとインメモリデータベースを使用します。
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_table()

    def _connect(self):
        """データベースに接続します。"""
        try:
            self.conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLUMNS)
            self.conn.row_factory = sqlite3.Row  # 行を辞書のようにアクセスできるように設定
        except sqlite3.Error as e:
            print(f"データベース接続エラー: {e}")
            raise

    def _create_table(self):
        """テスト結果を保存するためのテーブルを作成します。"""
        if not self.conn:
            self._connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL, -- 'PASS', 'FAIL', 'ERROR'
                    duration REAL,
                    error_message TEXT,
                    additional_info TEXT, -- JSON形式で追加情報を保存
                    CONSTRAINT unique_test_run UNIQUE (test_id, timestamp)
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"テーブル作成エラー: {e}")
            raise

    def insert_result(self, test_id: str, status: str, duration: float, 
                      error_message: str = None, additional_info: Dict[str, Any] = None):
        """
        テスト実行結果をデータベースに挿入します。

        Args:
            test_id (str): テストを一意に識別するID。
            status (str): テスト結果 ('PASS', 'FAIL', 'ERROR')。
            duration (float): テスト実行時間（秒）。
            error_message (str, optional): 失敗時のエラーメッセージ。
            additional_info (Dict[str, Any], optional): その他の情報（辞書形式）。
        """
        if not self.conn:
            self._connect()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        additional_info_json = json.dumps(additional_info) if additional_info else None
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO test_results (test_id, timestamp, status, duration, error_message, additional_info)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (test_id, timestamp, status, duration, error_message, additional_info_json))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"テスト結果挿入エラー for {test_id}: {e}")
            # エラー発生時はロールバック
            if self.conn:
                self.conn.rollback()

    def get_test_history(self, test_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        特定のテストの最新の実行履歴を取得します。

        Args:
            test_id (str): 履歴を取得するテストのID。
            limit (int): 取得する履歴の最大数。

        Returns:
            List[Dict[str, Any]]: テスト履歴のリスト。各履歴は辞書形式。
        """
        if not self.conn:
            self._connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT test_id, timestamp, status, duration, error_message, additional_info
                FROM test_results
                WHERE test_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (test_id, limit))
            results = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                if row_dict['additional_info']:
                    row_dict['additional_info'] = json.loads(row_dict['additional_info'])
                results.append(row_dict)
            return results
        except sqlite3.Error as e:
            print(f"テスト履歴取得エラー for {test_id}: {e}")
            return []

    def get_all_test_ids(self) -> List[str]:
        """
        データベースに記録されている全てのユニークなテストIDを取得します。

        Returns:
            List[str]: ユニークなテストIDのリスト。
        """
        if not self.conn:
            self._connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT test_id FROM test_results")
            return [row['test_id'] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"全テストID取得エラー: {e}")
            return []

    def close(self):
        """データベース接続を閉じます。"""
        if self.conn:
            self.conn.close()
            self.conn = None

def calculate_stability_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    与えられたテスト実行結果のリストから安定性メトリクスを計算します。

    Args:
        results (List[Dict[str, Any]]): テスト実行結果のリスト。

    Returns:
        Dict[str, Any]: 成功率、失敗回数、平均実行時間、実行時間の標準偏差を含むメトリクス。
    """
    if not results:
        return {
            "total_runs": 0, "pass_rate": 0.0, "fail_count": 0, "error_count": 0,
            "avg_duration": 0.0, "duration_stddev": 0.0
        }

    total_runs = len(results)
    pass_count = sum(1 for r in results if r['status'] == 'PASS')
    fail_count = sum(1 for r in results if r['status'] == 'FAIL')
    error_count = sum(1 for r in results if r['status'] == 'ERROR')
    durations = [r['duration'] for r in results if r['duration'] is not None]

    pass_rate = (pass_count / total_runs) * 100 if total_runs > 0 else 0.0
    avg_duration = sum(durations) / len(durations) if durations else 0.0
    
    duration_stddev = 0.0
    if len(durations) > 1:
        # 標本標準偏差
        sum_sq_diff = sum([(d - avg_duration) ** 2 for d in durations])
        duration_stddev = (sum_sq_diff / (len(durations) - 1)) ** 0.5
    
    return {
        "total_runs": total_runs,
        "pass_rate": pass_rate,
        "fail_count": fail_count,
        "error_count": error_count,
        "avg_duration": avg_duration,
        "duration_stddev": duration_stddev
    }

def is_potentially_flaky(metrics: Dict[str, Any], config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    計算されたメトリクスと設定に基づいて、テストが潜在的にフラッキーであるかを判定します。

    Args:
        metrics (Dict[str, Any]): calculate_stability_metricsで計算されたメトリクス。
        config (Dict[str, Any]): フラッキー判定のための設定値。
                                  'flaky_failure_rate_threshold', 'flaky_duration_stddev_threshold' など。

    Returns:
        Tuple[bool, str]: フラッキーであるかの真偽値と、その理由を示す文字列。
    """
    if metrics["total_runs"] < config.get("min_history_runs", 5):
        return False, "履歴が不足しているため判定できません。"

    # 失敗率に基づくフラッキー判定
    if metrics["pass_rate"] < config.get("flaky_failure_rate_threshold", 90.0): # 例: 失敗率が10%以上なら疑わしい
        return True, f"過去 {metrics['total_runs']} 回中、成功率が {metrics['pass_rate']:.2f}% と低いため。"

    # 実行時間の標準偏差に基づくフラッキー判定 (オプション)
    # 標準偏差が平均実行時間の一定割合を超えている場合
    if metrics["avg_duration"] > 0 and \
       metrics["duration_stddev"] / metrics["avg_duration"] > config.get("flaky_duration_stddev_ratio_threshold", 0.3):
        return True, f"実行時間の標準偏差が平均の {metrics['duration_stddev'] / metrics['avg_duration'] * 100:.2f}% と高いため。"

    return False, "安定していると判断されます。"

if __name__ == "__main__":
    # utils.py のテストと使用例
    print("--- TestHistoryDB Example ---")
    db = TestHistoryDB(db_path=":memory:") # インメモリデータベースを使用

    # テスト結果の挿入
    db.insert_result("test_login_success", "PASS", 0.15)
    time.sleep(0.01)
    db.insert_result("test_login_success", "FAIL", 0.20, "User not found")
    time.sleep(0.01)
    db.insert_result("test_login_success", "PASS", 0.18)
    time.sleep(0.01)
    db.insert_result("test_login_success", "PASS", 0.16)
    time.sleep(0.01)
    db.insert_result("test_login_success", "FAIL", 0.22, "DB connection error")
    time.sleep(0.01)
    db.insert_result("test_login_success", "PASS", 0.17)

    db.insert_result("test_dashboard_load", "PASS", 1.5)
    time.sleep(0.01)
    db.insert_result("test_dashboard_load", "PASS", 1.6)
    time.sleep(0.01)
    db.insert_result("test_dashboard_load", "PASS", 1.4)

    db.insert_result("test_payment_processing", "FAIL", 0.5, "Timeout connecting to external service")
    time.sleep(0.01)
    db.insert_result("test_payment_processing", "PASS", 0.4)
    time.sleep(0.01)
    db.insert_result("test_payment_processing", "FAIL", 2.1, "Service unavailable", {"retry_count": 1}) # 長い実行時間
    time.sleep(0.01)
    db.insert_result("test_payment_processing", "PASS", 0.45)
    time.sleep(0.01)
    db.insert_result("test_payment_processing", "FAIL", 0.6, "External API error")

    # 全テストIDの取得
    all_test_ids = db.get_all_test_ids()
    print(f"\nAll unique test IDs: {all_test_ids}")

    # 特定テストの履歴を取得し、メトリクスを計算
    test_id_to_check = "test_login_success"
    history = db.get_test_history(test_id_to_check, limit=5)
    print(f"\n--- History for {test_id_to_check} (last 5 runs) ---")
    for h in history:
        print(f"  {h['timestamp']} - Status: {h['status']}, Duration: {h['duration']:.2f}s, Error: {h['error_message']}")

    metrics = calculate_stability_metrics(history)
    print(f"\nMetrics for {test_id_to_check}:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")
        else:
            print(f"  {k}: {v}")

    # フラッキー判定
    flaky_config = {
        "min_history_runs": 3,
        "flaky_failure_rate_threshold": 90.0, # 90%未満の成功率で疑わしい
        "flaky_duration_stddev_ratio_threshold": 0.3 # 標準偏差が平均の30%を超えると疑わしい
    }
    is_flaky, reason = is_potentially_flaky(metrics, flaky_config)
    print(f"Is '{test_id_to_check}' potentially flaky? {is_flaky} (Reason: {reason})")

    test_id_to_check_stable = "test_dashboard_load"
    history_stable = db.get_test_history(test_id_to_check_stable, limit=5)
    metrics_stable = calculate_stability_metrics(history_stable)
    is_flaky_stable, reason_stable = is_potentially_flaky(metrics_stable, flaky_config)
    print(f"\nIs '{test_id_to_check_stable}' potentially flaky? {is_flaky_stable} (Reason: {reason_stable})")

    test_id_to_check_variable = "test_payment_processing"
    history_variable = db.get_test_history(test_id_to_check_variable, limit=5)
    metrics_variable = calculate_stability_metrics(history_variable)
    is_flaky_variable, reason_variable = is_potentially_flaky(metrics_variable, flaky_config)
    print(f"\nIs '{test_id_to_check_variable}' potentially flaky? {is_flaky_variable} (Reason: {reason_variable})")


    db.close()
    print("\n--- DB connection closed ---")
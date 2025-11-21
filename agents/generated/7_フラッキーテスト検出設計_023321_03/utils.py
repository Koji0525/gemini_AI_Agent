import sqlite3
import datetime
import statistics
from typing import List, Dict, Any, Optional
from collections import namedtuple

# テスト結果を表すnamedtuple
TestResult = namedtuple("TestResult", ["test_id", "status", "duration", "timestamp", "error_message"])

class SQLiteManager:
    """
    SQLiteデータベースを管理し、テスト実行履歴の永続化を行うユーティリティクラス。
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_connection()

    def _create_connection(self):
        """
        SQLiteデータベースへの接続を確立する。
        """
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to SQLite database at {self.db_path}: {e}")

    def create_table(self):
        """
        テスト結果を保存するためのテーブルを作成する。
        """
        query = """
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id TEXT NOT NULL,
            status TEXT NOT NULL,
            duration REAL NOT NULL,
            timestamp TEXT NOT NULL,
            error_message TEXT
        );
        """
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create table: {e}")

    def insert_result(self, test_id: str, status: str, duration: float, error_message: Optional[str] = None):
        """
        単一のテスト実行結果をデータベースに挿入する。

        Args:
            test_id (str): テストの一意な識別子。
            status (str): テストの結果 ('passed', 'failed', 'skipped', 'error'など)。
            duration (float): テストの実行時間（秒）。
            error_message (Optional[str]): テストが失敗した場合のエラーメッセージ。
        """
        timestamp = datetime.datetime.now().isoformat()
        query = "INSERT INTO test_results (test_id, status, duration, timestamp, error_message) VALUES (?, ?, ?, ?, ?);"
        try:
            self.cursor.execute(query, (test_id, status, duration, timestamp, error_message))
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to insert test result for {test_id}: {e}")

    def get_results(self, test_id: str, limit: Optional[int] = None) -> List[TestResult]:
        """
        指定されたテストIDの過去の実行結果を取得する。

        Args:
            test_id (str): 取得したいテストの識別子。
            limit (Optional[int]): 取得する結果の最大数。Noneの場合、全て取得。

        Returns:
            List[TestResult]: TestResultオブジェクトのリスト。
        """
        query = "SELECT test_id, status, duration, timestamp, error_message FROM test_results WHERE test_id = ? ORDER BY timestamp DESC"
        params = [test_id]
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return [TestResult(*row) for row in rows]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve results for {test_id}: {e}")

    def get_results_since(self, period_days: int) -> List[TestResult]:
        """
        指定された日数以内の全てのテスト実行結果を取得する。

        Args:
            period_days (int): 過去何日間のデータを取得するか。

        Returns:
            List[TestResult]: TestResultオブジェクトのリスト。
        """
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=period_days)).isoformat()
        query = "SELECT test_id, status, duration, timestamp, error_message FROM test_results WHERE timestamp >= ? ORDER BY timestamp DESC;"
        
        try:
            self.cursor.execute(query, (cutoff_date,))
            rows = self.cursor.fetchall()
            return [TestResult(*row) for row in rows]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve results since {period_days} days: {e}")

    def close(self):
        """
        データベース接続を閉じる。
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

def analyze_test_stability(results: List[TestResult]) -> Dict[str, Any]:
    """
    テスト結果のリストを分析し、安定性に関する統計情報を計算する。

    Args:
        results (List[TestResult]): 分析対象のTestResultオブジェクトのリスト。

    Returns:
        Dict[str, Any]: 以下のキーを含む辞書。
            - 'total_runs': 総実行回数。
            - 'passed_runs': 成功した回数。
            - 'failed_runs': 失敗した回数。
            - 'skipped_runs': スキップされた回数。
            - 'pass_rate': 成功率。
            - 'avg_duration': 平均実行時間。
            - 'duration_std_dev': 実行時間の標準偏差 (2回以上の実行が必要)。
            - 'first_run_timestamp': 最も古い実行のタイムスタンプ。
            - 'last_run_timestamp': 最も新しい実行のタイムスタンプ。
    """
    if not results:
        return {
            'total_runs': 0, 'passed_runs': 0, 'failed_runs': 0, 'skipped_runs': 0,
            'pass_rate': 0.0, 'avg_duration': 0.0, 'duration_std_dev': None,
            'first_run_timestamp': None, 'last_run_timestamp': None
        }

    total_runs = len(results)
    passed_runs = sum(1 for r in results if r.status == 'passed')
    failed_runs = sum(1 for r in results if r.status not in ['passed', 'skipped'])
    skipped_runs = sum(1 for r in results if r.status == 'skipped')
    
    pass_rate = passed_runs / total_runs if total_runs > 0 else 0.0

    durations = [r.duration for r in results if r.duration is not None]
    avg_duration = statistics.mean(durations) if durations else 0.0
    
    duration_std_dev = None
    if len(durations) > 1:
        try:
            duration_std_dev = statistics.stdev(durations)
        except statistics.StatisticsError:
            # データが全て同じ値の場合に発生
            duration_std_dev = 0.0

    # タイムスタンプはISOフォーマットで格納されていると仮定
    timestamps = sorted([r.timestamp for r in results])
    first_run_timestamp = timestamps[0] if timestamps else None
    last_run_timestamp = timestamps[-1] if timestamps else None

    return {
        'total_runs': total_runs,
        'passed_runs': passed_runs,
        'failed_runs': failed_runs,
        'skipped_runs': skipped_runs,
        'pass_rate': pass_rate,
        'avg_duration': avg_duration,
        'duration_std_dev': duration_std_dev,
        'first_run_timestamp': first_run_timestamp,
        'last_run_timestamp': last_run_timestamp
    }
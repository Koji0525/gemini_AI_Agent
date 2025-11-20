import sqlite3
import datetime
import json
from typing import List, Dict, Any, Optional

class TestHistoryManager:
    """
    テスト実行履歴とフラッキーテストの情報をSQLiteデータベースに保存・管理するクラス。
    このマネージャーは、テストの実行結果、その統計データ、そしてフラッキーと判定された
    テストの検出情報および修正ステータスを一元的に管理します。
    """

    def __init__(self, db_path: str = 'test_history.db'):
        """
        TestHistoryManagerの初期化。

        Args:
            db_path (str): データベースファイルのパス。指定がなければ 'test_history.db' を使用。
        """
        self.db_path = db_path
        self._create_tables()
        print(f"TestHistoryManager initialized for database: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """
        SQLiteデータベース接続を確立し、Connectionオブジェクトを返す。
        接続エラーが発生した場合は例外を捕捉し、エラーメッセージを出力。
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=10) # タイムアウトを長く設定
            conn.row_factory = sqlite3.Row # 結果を辞書形式で取得できるように設定
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise

    def _create_tables(self):
        """
        必要なデータベーステーブル（test_runsとflaky_tests）を作成する。
        テーブルが既に存在する場合は何もしない (IF NOT EXISTS)。
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS test_runs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_id TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        result TEXT NOT NULL, -- 'passed' or 'failed'
                        duration REAL,        -- Test execution duration in seconds
                        details TEXT          -- Error messages or other relevant info
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS flaky_tests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_id TEXT NOT NULL UNIQUE, -- Unique ID for the flaky test
                        detection_timestamp DATETIME NOT NULL,
                        reason TEXT,                  -- Why it was flagged as flaky
                        status TEXT NOT NULL,         -- 'detected', 'investigating', 'fixed', 'false_positive'
                        last_updated DATETIME NOT NULL,
                        fix_suggestion TEXT           -- JSON string of suggested fixes or applied fixes
                    )
                """)
                conn.commit()
                # print(f"Database tables (test_runs, flaky_tests) ensured in {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error creating database tables: {e}")
            raise

    def save_test_run(self, test_id: str, result: str, duration: float, 
                      timestamp: Optional[datetime.datetime] = None, details: Optional[str] = None):
        """
        単一のテスト実行結果をデータベースの`test_runs`テーブルに保存する。

        Args:
            test_id (str): テストのユニークな識別子 (例: module.test_class::test_method)。
            result (str): テスト結果 ('passed' または 'failed')。
            duration (float): テストの実行時間 (秒)。
            timestamp (Optional[datetime.datetime]): 実行日時。指定がなければ現在時刻を使用。
            details (Optional[str]): 失敗時のエラーメッセージなどの詳細情報。
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO test_runs (test_id, timestamp, result, duration, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (test_id, timestamp.isoformat(), result, duration, details))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving test run for '{test_id}': {e}")

    def get_test_history(self, test_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        特定のテストIDの実行履歴を、最新のものから順に取得する。

        Args:
            test_id (str): 履歴を取得するテストのID。
            limit (Optional[int]): 取得する履歴の最大件数。Noneの場合は全ての履歴を取得。

        Returns:
            List[Dict[str, Any]]: テスト実行履歴のリスト。各エントリは辞書形式。
        """
        history = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT test_id, timestamp, result, duration, details FROM test_runs WHERE test_id = ? ORDER BY timestamp DESC"
                params: List[Any] = [test_id]
                if limit and limit > 0:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    history.append({
                        "test_id": row["test_id"],
                        "timestamp": datetime.datetime.fromisoformat(row["timestamp"]),
                        "result": row["result"],
                        "duration": row["duration"],
                        "details": row["details"]
                    })
        except sqlite3.Error as e:
            print(f"Error getting test history for '{test_id}': {e}")
        return history

    def get_all_test_ids(self) -> List[str]:
        """
        データベースに記録されている全てのユニークなテストIDを取得する。

        Returns:
            List[str]: ユニークなテストIDのリスト。
        """
        test_ids = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT test_id FROM test_runs")
                rows = cursor.fetchall()
                test_ids = [row["test_id"] for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting all test IDs: {e}")
        return test_ids

    def save_flaky_test(self, test_id: str, reason: str, status: str = 'detected', 
                         fix_suggestion: Optional[Dict[str, Any]] = None):
        """
        フラッキーテストの情報をデータベースの`flaky_tests`テーブルに保存または更新する。
        `test_id`が既存の場合は更新(`ON CONFLICT(test_id) DO UPDATE`)。

        Args:
            test_id (str): フラッキーテストのID。
            reason (str): フラッキーと判定された理由。
            status (str): テストの状態 ('detected', 'investigating', 'fixed', 'false_positive' など)。
            fix_suggestion (Optional[Dict[str, Any]]): 提案された修正策の辞書。JSON形式で保存される。
        """
        timestamp = datetime.datetime.now()
        fix_suggestion_json = json.dumps(fix_suggestion, ensure_ascii=False) if fix_suggestion else None
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO flaky_tests 
                    (test_id, detection_timestamp, reason, status, last_updated, fix_suggestion)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(test_id) DO UPDATE SET
                        reason = EXCLUDED.reason,
                        status = EXCLUDED.status,
                        last_updated = EXCLUDED.last_updated,
                        fix_suggestion = EXCLUDED.fix_suggestion
                """, (test_id, timestamp.isoformat(), reason, status, timestamp.isoformat(), fix_suggestion_json))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving flaky test '{test_id}': {e}")

    def mark_flaky_test_status(self, test_id: str, status: str, reason: str = ""):
        """
        既存のフラッキーテストの状態を更新する。

        Args:
            test_id (str): 更新するフラッキーテストのID。
            status (str): 新しい状態 ('detected', 'investigating', 'fixed', 'false_positive' など)。
            reason (str): 状態変更の理由または追加情報。
        """
        timestamp = datetime.datetime.now()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # test_idが存在する場合のみ更新
                cursor.execute("""
                    UPDATE flaky_tests SET 
                        status = ?, 
                        reason = ?, 
                        last_updated = ?
                    WHERE test_id = ?
                """, (status, reason, timestamp.isoformat(), test_id))
                conn.commit()
                if cursor.rowcount == 0:
                    print(f"Warning: Flaky test '{test_id}' not found in DB to update status.")
        except sqlite3.Error as e:
            print(f"Error updating flaky test status for '{test_id}': {e}")

    def get_flaky_tests_status(self) -> List[Dict[str, Any]]:
        """
        現在データベースにトラッキングされている全てのフラッキーテストの情報を取得する。

        Returns:
            List[Dict[str, Any]]: フラッキーテスト情報のリスト。各エントリは辞書形式。
        """
        flaky_status = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT test_id, detection_timestamp, reason, status, last_updated, fix_suggestion FROM flaky_tests")
                rows = cursor.fetchall()
                for row in rows:
                    fix_suggestion = json.loads(row["fix_suggestion"]) if row["fix_suggestion"] else None
                    flaky_status.append({
                        "test_id": row["test_id"],
                        "detection_timestamp": row["detection_timestamp"],
                        "reason": row["reason"],
                        "status": row["status"],
                        "last_updated": row["last_updated"],
                        "fix_suggestion": fix_suggestion
                    })
        except sqlite3.Error as e:
            print(f"Error getting flaky tests status: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding fix_suggestion JSON: {e}")
        return flaky_status

def analyze_test_stability(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    テスト実行履歴リストから安定性指標（成功率、失敗率、実行時間の分散など）を計算する。

    Args:
        history (List[Dict[str, Any]]): TestHistoryManager.get_test_history から取得した履歴リスト。

    Returns:
        Dict[str, Any]: 安定性に関する統計情報。以下のキーを含む:
            - total_runs (int): 総実行回数。
            - success_count (int): 成功回数。
            - failure_count (int): 失敗回数。
            - success_rate (float): 成功率 (0.0-1.0)。
            - failure_rate (float): 失敗率 (0.0-1.0)。
            - avg_duration (float): 平均実行時間 (秒)。
            - duration_std_dev (float): 実行時間の標準偏差 (秒)。
    """
    if not history:
        return {
            "total_runs": 0,
            "success_count": 0,
            "failure_count": 0,
            "success_rate": 0.0,
            "failure_rate": 0.0,
            "avg_duration": 0.0,
            "duration_std_dev": 0.0
        }

    total_runs = len(history)
    success_count = sum(1 for run in history if run["result"] == "passed")
    failure_count = total_runs - success_count
    
    success_rate = success_count / total_runs
    failure_rate = failure_count / total_runs

    durations = [run["duration"] for run in history if run["duration"] is not None]
    avg_duration = sum(durations) / len(durations) if durations else 0.0
    
    duration_std_dev = 0.0
    if len(durations) > 1:
        # 標本標準偏差 (sample standard deviation) を計算
        sum_sq_diff = sum([(d - avg_duration) ** 2 for d in durations])
        duration_std_dev = (sum_sq_diff / (len(durations) - 1)) ** 0.5

    return {
        "total_runs": total_runs,
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": success_rate,
        "failure_rate": failure_rate,
        "avg_duration": avg_duration,
        "duration_std_dev": duration_std_dev
    }

def generate_pytest_rerun_options(num_reruns: int = 3, reruns_delay: int = 0) -> List[str]:
    """
    pytest-rerunfailuresプラグイン用のコマンドラインオプションを生成する。
    このプラグインは、pytestがテストに失敗した際に、指定された回数だけ再実行を試みる機能を提供します。

    Args:
        num_reruns (int): 失敗時にテストを再実行する回数。デフォルトは3回。
        reruns_delay (int): 各再実行間の遅延時間 (秒)。デフォルトは0秒。

    Returns:
        List[str]: pytestコマンドに追加するためのオプション文字列のリスト。
    """
    options = [
        f"--reruns={num_reruns}",
        f"--reruns-delay={reruns_delay}"
    ]
    return options

def generate_sleep_suggestion(test_id: str) -> Dict[str, str]:
    """
    テストコードへのsleep挿入に関する一般的な提案を生成する。
    これは自動コード修正ではなく、開発者向けのガイダンスとして提供されます。
    主にUIテストや非同期処理が絡むテストで有効です。

    Args:
        test_id (str): 提案対象のテストID。

    Returns:
        Dict[str, str]: sleep挿入に関する提案の詳細。
            - type (str): 提案のタイプ ("add_wait_time")。
            - test_id (str): 対象のテストID。
            - description (str): 問題の概要。
            - guidance (str): 解決策への一般的な指針。
            - example (str): コード修正の具体的な例。
    """
    return {
        "type": "add_wait_time",
        "test_id": test_id,
        "description": "テストが非同期処理の完了、UI要素の描画、またはシステム状態の変更を待たずに失敗している可能性があります。",
        "guidance": "固定の `time.sleep()` の使用は避け、代わりに特定の条件が満たされるまで待機する仕組み (例: `WebDriverWait` for UI tests, ポーリング機構 for API responses) を導入することを強く推奨します。",
        "example": "一時的なデバッグ目的の場合、問題の箇所に `import time; time.sleep(0.5)` のような短い遅延を追加し、不安定性が解消されるか確認してください。ただし、これは根本的な解決策ではありません。"
    }
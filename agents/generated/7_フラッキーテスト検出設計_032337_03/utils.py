import sqlite3
import time
import random
import statistics
import logging
import ast
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class TestResult:
    """
    個々のテスト実行の結果を表すデータクラス。
    データベーススキーマのモデルとしても機能する。
    """
    def __init__(self, test_id: str, passed: bool, duration: float, 
                 error_message: Optional[str], timestamp: datetime, attempt_count: int = 1):
        self.test_id = test_id
        self.passed = passed
        self.duration = duration
        self.error_message = error_message
        self.timestamp = timestamp
        self.attempt_count = attempt_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "passed": self.passed,
            "duration": self.duration,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "attempt_count": self.attempt_count
        }

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'TestResult':
        return cls(
            test_id=row[0],
            passed=bool(row[1]),
            duration=row[2],
            error_message=row[3],
            timestamp=datetime.fromisoformat(row[4]),
            attempt_count=row[5]
        )

class TestHistoryManager:
    """
    テスト実行履歴をSQLiteデータベースで管理するクラス。
    履歴の保存、取得、データベースの初期化を行う。
    """
    def __init__(self, db_path: str = "test_history.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """データベースを初期化し、テーブルが存在しない場合は作成する。"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS test_results (
                        test_id TEXT NOT NULL,
                        passed INTEGER NOT NULL, -- 0 for false, 1 for true
                        duration REAL NOT NULL,
                        error_message TEXT,
                        timestamp TEXT NOT NULL, -- ISO format string
                        attempt_count INTEGER NOT NULL DEFAULT 1,
                        PRIMARY KEY (test_id, timestamp)
                    )
                """)
                conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database at {self.db_path}: {e}")

    def record_test_result(self, test_id: str, passed: bool, duration: float, 
                           error_message: Optional[str], attempt_count: int = 1):
        """
        単一のテスト実行結果をデータベースに記録する。
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO test_results (test_id, passed, duration, error_message, timestamp, attempt_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (test_id, int(passed), duration, error_message, 
                      datetime.now().isoformat(), attempt_count))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error recording test result for {test_id}: {e}")

    def get_test_history(self, test_id: str, limit: int = 100) -> List[TestResult]:
        """
        特定のテストIDの過去の実行履歴を取得する。
        新しいものから順に取得される。
        """
        history: List[TestResult] = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT test_id, passed, duration, error_message, timestamp, attempt_count
                    FROM test_results
                    WHERE test_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (test_id, limit))
                rows = cursor.fetchall()
                for row in reversed(rows): # 古いものから順に処理するために逆順にする
                    history.append(TestResult.from_db_row(row))
        except sqlite3.Error as e:
            logger.error(f"Error getting test history for {test_id}: {e}")
        return history

    def get_all_test_ids(self) -> List[str]:
        """
        データベースに記録されている全てのユニークなテストIDを取得する。
        """
        test_ids: List[str] = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT test_id FROM test_results ORDER BY test_id")
                rows = cursor.fetchall()
                test_ids = [row[0] for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting all test IDs: {e}")
        return test_ids

def analyze_test_stability(results: List[TestResult]) -> Dict[str, Any]:
    """
    テスト実行結果のリストから安定性に関する統計情報を分析する。
    成功率、実行時間の平均と分散、よく発生するエラーメッセージを計算する。
    """
    if not results:
        return {
            "num_runs": 0,
            "failure_rate": 0.0,
            "avg_duration": 0.0,
            "duration_std_dev": 0.0,
            "duration_std_dev_ratio": 0.0,
            "common_errors": []
        }

    num_runs = len(results)
    passed_runs = [r for r in results if r.passed]
    failed_runs = [r for r in results if not r.passed]

    failure_rate = len(failed_runs) / num_runs if num_runs > 0 else 0.0

    durations = [r.duration for r in results]
    avg_duration = statistics.mean(durations) if durations else 0.0
    
    duration_std_dev = 0.0
    if len(durations) > 1:
        try:
            duration_std_dev = statistics.stdev(durations)
        except statistics.StatisticsError: # Occurs if only one value
            duration_std_dev = 0.0

    duration_std_dev_ratio = duration_std_dev / avg_duration if avg_duration > 0 else 0.0

    error_counts: Dict[str, int] = defaultdict(int)
    for r in failed_runs:
        if r.error_message:
            error_counts[r.error_message] += 1
    
    common_errors = sorted([{"message": msg, "count": count} for msg, count in error_counts.items()], 
                           key=lambda x: x["count"], reverse=True)[:3] # Top 3 common errors

    return {
        "num_runs": num_runs,
        "failure_rate": failure_rate,
        "avg_duration": avg_duration,
        "duration_std_dev": duration_std_dev,
        "duration_std_dev_ratio": duration_std_dev_ratio,
        "common_errors": common_errors
    }


def simulate_test_run(test_id: str, min_duration: float = 0.05, max_duration: float = 1.0, 
                      failure_probability: float = 0.2) -> TestResult:
    """
    テストの実行をシミュレートするヘルパー関数。
    """
    start_time = time.time()
    passed = random.random() > failure_probability
    time.sleep(min_duration + random.random() * (max_duration - min_duration))
    duration = time.time() - start_time
    error_message = None
    if not passed:
        error_message = f"Simulated transient failure for {test_id} at {datetime.now().strftime('%H:%M:%S')}"
    
    return TestResult(test_id, passed, duration, error_message, datetime.now())

def run_test_with_retries(test_id: str, test_function_ref: Any, max_retries: int = 3, 
                          delay_seconds: float = 1.0) -> TestResult:
    """
    テストを複数回リトライして実行する（修正戦略の一部）。
    実際にはtest_function_refを呼び出す。
    """
    for attempt in range(1, max_retries + 1):
        logger.info(f"Running test '{test_id}' (Attempt {attempt}/{max_retries})...")
        # 実際にはここでtest_function_refを実行
        # 例: result = test_function_ref(test_id)
        # ここではsimulate_test_runで代用
        result = simulate_test_run(test_id, failure_probability=0.1) # リトライ時は成功率を高めに設定
        result.attempt_count = attempt
        
        if result.passed:
            logger.info(f"Test '{test_id}' PASSED on attempt {attempt}.")
            return result
        else:
            logger.warning(f"Test '{test_id}' FAILED on attempt {attempt}: {result.error_message}")
            if attempt < max_retries:
                time.sleep(delay_seconds) # リトライ前に待機
    
    logger.error(f"Test '{test_id}' FAILED after {max_retries} attempts.")
    return result # 最後の失敗結果を返す


class StaticCodeAnalyzer(ast.NodeVisitor):
    """
    テストコードを静的に解析し、フラッキーネスの潜在的な原因を特定する。
    - `time.sleep` の使用 (不適切な待機はタイムアウトや競合状態につながる)
    - `random` モジュールの使用 (非決定的動作)
    - グローバル変数やクラス変数へのアクセス (テスト間の状態漏洩)
    """
    def __init__(self):
        self.findings: List[str] = []
        self.current_test_function: Optional[str] = None
        self.uses_random: bool = False
        self.uses_time_sleep: bool = False
        self.accesses_global_state: bool = False

    def analyze_test_file(self, file_path: str) -> List[str]:
        """指定されたファイルパスのテストコードを解析し、結果を返す。"""
        self.findings = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=file_path)
            self.visit(tree)
        except FileNotFoundError:
            logger.warning(f"Static analysis: File not found at {file_path}")
        except SyntaxError as e:
            logger.warning(f"Static analysis: Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Static analysis: An unexpected error occurred while parsing {file_path}: {e}")
        return self.findings

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """関数定義を訪問し、pytestのテスト関数を識別する。"""
        if node.name.startswith("test_"):
            self.current_test_function = node.name
            self.uses_random = False
            self.uses_time_sleep = False
            self.accesses_global_state = False
            
            # 各テスト関数ブロック内で、さらにNodeVisitorを適用して詳細をチェック
            temp_visitor = _TestFunctionAnalyzer()
            temp_visitor.visit(node)
            
            if temp_visitor.uses_random:
                self.findings.append(f"Function '{node.name}' uses 'random' module (non-deterministic behavior).")
            if temp_visitor.uses_time_sleep:
                self.findings.append(f"Function '{node.name}' uses 'time.sleep' (potential for unstable waits).")
            if temp_visitor.accesses_global_state:
                self.findings.append(f"Function '{node.name}' potentially accesses global/module-level state (risk of state leakage).")
            
            self.current_test_function = None
        self.generic_visit(node) # 子ノードも訪問

# 内部ヘルパークラスで、FunctionDef内の特定の要素をチェック
class _TestFunctionAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.uses_random = False
        self.uses_time_sleep = False
        self.accesses_global_state = False

    def visit_Call(self, node: ast.Call):
        """関数呼び出しを訪問し、time.sleepやrandom.*を検出する。"""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'time' and node.func.attr == 'sleep':
                self.uses_time_sleep = True
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'random':
                self.uses_random = True
        elif isinstance(node.func, ast.Name) and node.func.id == 'random': # direct call if 'from random import random'
            self.uses_random = True
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        """変数アクセスを訪問し、グローバル変数の使用を検出する。"""
        # 単純なグローバル変数アクセス検出。より洗練された検出にはシンボルテーブル解析が必要
        if isinstance(node.ctx, (ast.Load, ast.Store)) and not self._is_local_variable(node):
            self.accesses_global_state = True
        self.generic_visit(node)

    def _is_local_variable(self, node: ast.Name) -> bool:
        """変数がローカルスコープ内で定義されているかを推測する（非常に単純な推測）。"""
        # このメソッドは非常に限定的で、正確なローカル変数検出には不十分です。
        # 実際には、より複雑なスコープ解析が必要になります。
        # ここでは、簡略化のため常にFalseを返すことで、多くのアクセスをグローバルとみなします。
        return False

    def visit_Attribute(self, node: ast.Attribute):
        """属性アクセスを訪問し、グローバルなオブジェクトの属性へのアクセスを検出する。"""
        if isinstance(node.ctx, (ast.Load, ast.Store)):
            # 例えば、_shared_state.append() の _shared_state のようなケース
            # より高度な検出には、このノードの親を解析してコンテキストを理解する必要がある
            self.accesses_global_state = True
        self.generic_visit(node)
"""
実行トレーサー (分散トレーシング)

このモジュールは、エージェント間の関数呼び出しをトレースし、
実行時の依存関係を記録します。

主要機能:
    - コンテキストマネージャーによるトレース記録
    - デコレーターによる自動トレース
    - SQLiteへの高速書き込み
    - UUID生成による分散トレーシング対応

パフォーマンス目標:
    - トレースオーバーヘッド: <5ms
    - DB書き込み: <10ms
"""

import functools
import json
import logging
import sqlite3
import time
import traceback
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Optional

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExecutionTracer:
    """
    実行トレーサー

    Attributes:
        db_path (Path): トレースDBのパス
        conn (sqlite3.Connection): DB接続
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        初期化

        Args:
            db_path: トレースDBのパス (Noneの場合はデフォルト)
        """
        if db_path is None:
            db_path = Path("logs/traces.db")

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # DB接続
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()

        logger.info(f"Initialized ExecutionTracer with DB: {self.db_path}")

    def _init_db(self) -> None:
        """データベーススキーマを初期化"""
        cursor = self.conn.cursor()

        # tracesテーブル作成
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                caller TEXT NOT NULL,
                callee TEXT NOT NULL,
                args TEXT,
                result TEXT,
                duration_ms REAL,
                status TEXT,
                error_message TEXT,
                stack_trace TEXT
            )
        """
        )

        # インデックス作成
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_trace_id ON traces(trace_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp ON traces(timestamp)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_caller ON traces(caller)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_status ON traces(status)
        """
        )

        # 自動削除トリガー (30日以上古いレコード)
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS auto_delete_old_traces
            AFTER INSERT ON traces
            BEGIN
                DELETE FROM traces
                WHERE timestamp < datetime('now', '-30 days');
            END
        """
        )

        self.conn.commit()
        logger.info("Database schema initialized")

    @contextmanager
    def trace_call(self, caller: str, callee: str, args: Optional[dict] = None):
        """
        関数呼び出しをトレースするコンテキストマネージャー

        Args:
            caller: 呼び出し元
            callee: 呼び出し先
            args: 引数 (オプション)

        Yields:
            str: trace_id

        使用例:
            with tracer.trace_call('PMAgent', 'SheetsManager'):
                result = sheets_manager.add_row(...)
        """
        trace_id = str(uuid.uuid4())
        start_time = time.time()
        status = "success"
        error_message = None
        stack_trace = None
        result = None

        try:
            yield trace_id
        except Exception as e:
            status = "error"
            error_message = str(e)
            stack_trace = traceback.format_exc()
            logger.error(f"Error in trace {trace_id}: {e}")
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000

            # トレースを記録
            try:
                self._log_trace(
                    trace_id=trace_id,
                    caller=caller,
                    callee=callee,
                    args=args,
                    result=result,
                    duration_ms=duration_ms,
                    status=status,
                    error_message=error_message,
                    stack_trace=stack_trace,
                )
            except Exception as log_error:
                logger.error(f"Failed to log trace: {log_error}")

    def _log_trace(
        self,
        trace_id: str,
        caller: str,
        callee: str,
        args: Optional[dict],
        result: Any,
        duration_ms: float,
        status: str,
        error_message: Optional[str],
        stack_trace: Optional[str],
    ) -> None:
        """
        トレースをDBに記録

        Args:
            trace_id: トレースID
            caller: 呼び出し元
            callee: 呼び出し先
            args: 引数
            result: 結果
            duration_ms: 実行時間(ミリ秒)
            status: ステータス
            error_message: エラーメッセージ
            stack_trace: スタックトレース
        """
        cursor = self.conn.cursor()

        # JSONシリアライズ
        args_json = json.dumps(args) if args else None
        result_json = json.dumps(str(result)[:1000]) if result else None  # 最初の1000文字のみ

        cursor.execute(
            """
            INSERT INTO traces (
                trace_id, caller, callee, args, result,
                duration_ms, status, error_message, stack_trace
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                trace_id,
                caller,
                callee,
                args_json,
                result_json,
                duration_ms,
                status,
                error_message,
                stack_trace,
            ),
        )

        self.conn.commit()

    def get_recent_traces(self, minutes: int = 10, limit: int = 1000) -> list:
        """
        最近のトレースを取得

        Args:
            minutes: 何分前まで取得するか
            limit: 最大件数

        Returns:
            list: トレースのリスト
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT trace_id, timestamp, caller, callee, duration_ms, status, error_message
            FROM traces
            WHERE timestamp > datetime('now', '-' || ? || ' minutes')
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (minutes, limit),
        )

        columns = [
            "trace_id",
            "timestamp",
            "caller",
            "callee",
            "duration_ms",
            "status",
            "error_message",
        ]
        traces = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return traces

    def get_error_traces(self, limit: int = 100) -> list:
        """
        エラーが発生したトレースを取得

        Args:
            limit: 最大件数

        Returns:
            list: エラートレースのリスト
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT trace_id, timestamp, caller, callee, duration_ms, error_message, stack_trace
            FROM traces
            WHERE status = 'error'
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )

        columns = [
            "trace_id",
            "timestamp",
            "caller",
            "callee",
            "duration_ms",
            "error_message",
            "stack_trace",
        ]
        traces = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return traces

    def get_slow_traces(self, threshold_ms: float = 1000, limit: int = 100) -> list:
        """
        遅いトレースを取得

        Args:
            threshold_ms: 閾値(ミリ秒)
            limit: 最大件数

        Returns:
            list: 遅いトレースのリスト
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT trace_id, timestamp, caller, callee, duration_ms
            FROM traces
            WHERE duration_ms > ?
            ORDER BY duration_ms DESC
            LIMIT ?
        """,
            (threshold_ms, limit),
        )

        columns = ["trace_id", "timestamp", "caller", "callee", "duration_ms"]
        traces = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return traces

    def get_statistics(self) -> dict:
        """
        トレース統計を取得

        Returns:
            dict: 統計情報
        """
        cursor = self.conn.cursor()

        # 総トレース数
        cursor.execute("SELECT COUNT(*) FROM traces")
        total_count = cursor.fetchone()[0]

        # エラー数
        cursor.execute("SELECT COUNT(*) FROM traces WHERE status = 'error'")
        error_count = cursor.fetchone()[0]

        # 平均実行時間
        cursor.execute("SELECT AVG(duration_ms) FROM traces")
        avg_duration = cursor.fetchone()[0] or 0

        # 最も呼ばれているcallee
        cursor.execute(
            """
            SELECT callee, COUNT(*) as count
            FROM traces
            GROUP BY callee
            ORDER BY count DESC
            LIMIT 10
        """
        )
        top_callees = [{"callee": row[0], "count": row[1]} for row in cursor.fetchall()]

        return {
            "total_traces": total_count,
            "error_count": error_count,
            "error_rate": error_count / max(total_count, 1) * 100,
            "avg_duration_ms": avg_duration,
            "top_callees": top_callees,
        }

    def close(self) -> None:
        """DB接続をクローズ"""
        if self.conn:
            self.conn.close()
            logger.info("ExecutionTracer closed")


# グローバルトレーサーインスタンス
tracer = ExecutionTracer()


def trace(caller: str):
    """
    関数をトレースするデコレーター

    Args:
        caller: 呼び出し元の名前

    使用例:
        @trace('PMAgent')
        def decompose_goal(goal: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            callee = func.__name__

            with tracer.trace_call(caller, callee):
                result = func(*args, **kwargs)
                return result

        return wrapper

    return decorator


def main():
    """メイン関数 (テスト用)"""
    print("🔍 ExecutionTracer Test")

    # トレースをテスト
    with tracer.trace_call("TestCaller", "TestCallee", {"arg1": "value1"}):
        time.sleep(0.01)  # 10ms待機

    # 統計を表示
    stats = tracer.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total traces: {stats['total_traces']}")
    print(f"  Error rate: {stats['error_rate']:.2f}%")
    print(f"  Avg duration: {stats['avg_duration_ms']:.2f}ms")

    # 最近のトレースを表示
    recent = tracer.get_recent_traces(minutes=10, limit=5)
    print(f"\n📝 Recent traces ({len(recent)}):")
    for trace in recent:
        print(f"  {trace['caller']} -> {trace['callee']}: {trace['duration_ms']:.2f}ms")

    tracer.close()
    print("\n✅ ExecutionTracer test completed")


if __name__ == "__main__":
    main()

"""
トレース検索

このモジュールは、トレースDBに対する高度な検索機能を提供します。

主要機能:
    - 時間範囲検索
    - caller/callee検索
    - エラー検索
    - パフォーマンス分析
    - SQL最適化
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TraceQuery:
    """
    トレース検索クラス

    Attributes:
        db_path (Path): トレースDBのパス
        conn (sqlite3.Connection): DB接続
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        初期化

        Args:
            db_path: トレースDBのパス
        """
        if db_path is None:
            db_path = Path("logs/traces.db")

        self.db_path = Path(db_path)

        if not self.db_path.exists():
            logger.warning(f"Trace DB not found: {self.db_path}")
            self.conn = None
        else:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            logger.info(f"Connected to trace DB: {self.db_path}")

    def search_by_time_range(
        self, start_time: datetime, end_time: datetime, limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        時間範囲で検索

        Args:
            start_time: 開始時刻
            end_time: 終了時刻
            limit: 最大件数

        Returns:
            List[Dict]: トレースのリスト
        """
        if not self.conn:
            return []

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT trace_id, timestamp, caller, callee, duration_ms, status
            FROM traces
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (start_time.isoformat(), end_time.isoformat(), limit),
        )

        columns = ["trace_id", "timestamp", "caller", "callee", "duration_ms", "status"]
        traces = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return traces

    def search_by_caller(self, caller: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        callerで検索

        Args:
            caller: 呼び出し元
            limit: 最大件数

        Returns:
            List[Dict]: トレースのリスト
        """
        if not self.conn:
            return []

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT trace_id, timestamp, caller, callee, duration_ms, status
            FROM traces
            WHERE caller = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (caller, limit),
        )

        columns = ["trace_id", "timestamp", "caller", "callee", "duration_ms", "status"]
        traces = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return traces

    def search_by_callee(self, callee: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        calleeで検索

        Args:
            callee: 呼び出し先
            limit: 最大件数

        Returns:
            List[Dict]: トレースのリスト
        """
        if not self.conn:
            return []

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT trace_id, timestamp, caller, callee, duration_ms, status
            FROM traces
            WHERE callee = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (callee, limit),
        )

        columns = ["trace_id", "timestamp", "caller", "callee", "duration_ms", "status"]
        traces = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return traces

    def search_errors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        エラーが発生したトレースを検索

        Args:
            limit: 最大件数

        Returns:
            List[Dict]: エラートレースのリスト
        """
        if not self.conn:
            return []

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT trace_id, timestamp, caller, callee, duration_ms, error_message
            FROM traces
            WHERE status = 'error'
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )

        columns = ["trace_id", "timestamp", "caller", "callee", "duration_ms", "error_message"]
        traces = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return traces

    def get_performance_stats(self, callee: Optional[str] = None) -> Dict[str, Any]:
        """
        パフォーマンス統計を取得

        Args:
            callee: 特定のcalleeに絞る (Noneの場合は全体)

        Returns:
            Dict: 統計情報
        """
        if not self.conn:
            return {}

        cursor = self.conn.cursor()

        if callee:
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as count,
                    AVG(duration_ms) as avg_ms,
                    MIN(duration_ms) as min_ms,
                    MAX(duration_ms) as max_ms
                FROM traces
                WHERE callee = ?
            """,
                (callee,),
            )
        else:
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as count,
                    AVG(duration_ms) as avg_ms,
                    MIN(duration_ms) as min_ms,
                    MAX(duration_ms) as max_ms
                FROM traces
            """
            )

        row = cursor.fetchone()

        return {
            "count": row[0],
            "avg_ms": row[1] or 0,
            "min_ms": row[2] or 0,
            "max_ms": row[3] or 0,
        }

    def close(self) -> None:
        """DB接続をクローズ"""
        if self.conn:
            self.conn.close()
            logger.info("TraceQuery closed")


def main():
    """メイン関数 (テスト用)"""
    print("🔍 TraceQuery Test")

    query = TraceQuery()

    # 最近10分間のトレースを検索
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=10)

    traces = query.search_by_time_range(start_time, end_time, limit=10)
    print(f"\n📝 Recent traces: {len(traces)}")

    # パフォーマンス統計
    stats = query.get_performance_stats()
    print(f"\n📊 Performance stats:")
    print(f"  Count: {stats['count']}")
    print(f"  Avg: {stats['avg_ms']:.2f}ms")
    print(f"  Min: {stats['min_ms']:.2f}ms")
    print(f"  Max: {stats['max_ms']:.2f}ms")

    query.close()
    print("\n✅ TraceQuery test completed")


if __name__ == "__main__":
    main()

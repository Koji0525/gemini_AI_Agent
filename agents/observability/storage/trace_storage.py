"""
TraceStorage - 分散トレーシングストレージ管理

【Phase 1.2: 分散トレーシングストレージ構築】
トレースデータの保存・検索・管理機能
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TraceStorage:
    """トレースデータストレージ"""

    def __init__(self, storage_path: str = "/tmp/traces"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # メモリ内キャッシュ（最大1000件）
        self.trace_cache = []
        self.max_cache_size = 1000

        # データ保持ポリシー（デフォルト7日）
        self.retention_days = 7

        print(f"✅ TraceStorage初期化完了: {self.storage_path}")

    def store_trace(self, trace_data: Dict[str, Any]) -> bool:
        """
        トレースデータを保存

        Args:
            trace_data: トレースデータ

        Returns:
            成功フラグ
        """
        try:
            # タイムスタンプ追加
            if "timestamp" not in trace_data:
                trace_data["timestamp"] = datetime.now().isoformat()

            # メモリキャッシュに追加
            self.trace_cache.append(trace_data)

            # キャッシュサイズ制限
            if len(self.trace_cache) > self.max_cache_size:
                self.trace_cache.pop(0)

            # ファイルに永続化
            date_str = datetime.now().strftime("%Y%m%d")
            file_path = self.storage_path / f"traces_{date_str}.jsonl"

            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace_data, ensure_ascii=False) + "\n")

            return True

        except Exception as e:
            logger.error(f"❌ トレース保存エラー: {e}")
            return False

    def search_traces(
        self,
        operation_name: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        トレースを検索

        Args:
            operation_name: オペレーション名でフィルタ
            status: ステータスでフィルタ（success/error）
            start_time: 開始時刻
            end_time: 終了時刻
            limit: 最大取得件数

        Returns:
            マッチしたトレースのリスト
        """
        results = []

        try:
            # メモリキャッシュから検索
            for trace in reversed(self.trace_cache):
                if len(results) >= limit:
                    break

                # フィルタ適用
                if operation_name and trace.get("operation_name") != operation_name:
                    continue

                if status and trace.get("status") != status:
                    continue

                if start_time:
                    trace_time = datetime.fromisoformat(trace.get("timestamp", ""))
                    if trace_time < start_time:
                        continue

                if end_time:
                    trace_time = datetime.fromisoformat(trace.get("timestamp", ""))
                    if trace_time > end_time:
                        continue

                results.append(trace)

            return results

        except Exception as e:
            logger.error(f"❌ トレース検索エラー: {e}")
            return []

    def get_trace_stats(self) -> Dict[str, Any]:
        """トレース統計を取得"""
        try:
            total_traces = len(self.trace_cache)

            success_count = sum(1 for t in self.trace_cache if t.get("status") == "success")
            error_count = sum(1 for t in self.trace_cache if t.get("status") == "error")

            # オペレーション別集計
            operation_stats = {}
            for trace in self.trace_cache:
                op_name = trace.get("operation_name", "unknown")
                if op_name not in operation_stats:
                    operation_stats[op_name] = {"count": 0, "success": 0, "error": 0}

                operation_stats[op_name]["count"] += 1
                if trace.get("status") == "success":
                    operation_stats[op_name]["success"] += 1
                elif trace.get("status") == "error":
                    operation_stats[op_name]["error"] += 1

            return {
                "total_traces": total_traces,
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": success_count / total_traces if total_traces > 0 else 0,
                "operation_stats": operation_stats,
                "cache_size": len(self.trace_cache),
                "max_cache_size": self.max_cache_size,
            }

        except Exception as e:
            logger.error(f"❌ 統計取得エラー: {e}")
            return {}

    def cleanup_old_traces(self):
        """古いトレースデータを削除"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)

            # ファイルベースのクリーンアップ
            for file_path in self.storage_path.glob("traces_*.jsonl"):
                file_date_str = file_path.stem.split("_")[1]
                file_date = datetime.strptime(file_date_str, "%Y%m%d")

                if file_date < cutoff_date:
                    file_path.unlink()
                    print(f"🗑️ 古いトレースファイルを削除: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"❌ クリーンアップエラー: {e}")
            return False


if __name__ == "__main__":
    print("🧪 TraceStorage テスト")

    storage = TraceStorage()

    # テストトレース保存
    test_trace = {
        "trace_id": "test-123",
        "operation_name": "PMAgent.create_task",
        "status": "success",
        "duration_ms": 150,
    }

    success = storage.store_trace(test_trace)
    print(f"保存結果: {success}")

    # 統計取得
    stats = storage.get_trace_stats()
    print(f"\n統計:")
    print(f"  総トレース数: {stats['total_traces']}")
    print(f"  成功率: {stats['success_rate']:.1%}")

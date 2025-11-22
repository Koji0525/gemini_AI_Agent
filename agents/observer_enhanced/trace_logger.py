"""
トレースログ記録

このモジュールは、トレース情報を効率的に記録します。
バッファリングとバッチ書き込みにより、高速化を実現します。

主要機能:
    - バッファリング (100件ごとにフラッシュ)
    - バッチ書き込み
    - UUID生成
    - スレッドセーフ
"""

import logging
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TraceLogger:
    """
    トレースログ記録クラス

    Attributes:
        buffer (List): ログバッファ
        buffer_size (int): バッファサイズ
        lock (threading.Lock): スレッドロック
    """

    def __init__(self, buffer_size: int = 100):
        """
        初期化

        Args:
            buffer_size: バッファサイズ (デフォルト: 100)
        """
        self.buffer: List[Dict[str, Any]] = []
        self.buffer_size = buffer_size
        self.lock = threading.Lock()

        logger.info(f"Initialized TraceLogger with buffer_size={buffer_size}")

    def log(
        self,
        caller: str,
        callee: str,
        duration_ms: float,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> str:
        """
        トレースをログに記録

        Args:
            caller: 呼び出し元
            callee: 呼び出し先
            duration_ms: 実行時間(ミリ秒)
            status: ステータス
            error_message: エラーメッセージ

        Returns:
            str: trace_id
        """
        trace_id = str(uuid.uuid4())

        trace_entry = {
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "caller": caller,
            "callee": callee,
            "duration_ms": duration_ms,
            "status": status,
            "error_message": error_message,
        }

        with self.lock:
            self.buffer.append(trace_entry)

            # バッファが満杯になったらフラッシュ
            if len(self.buffer) >= self.buffer_size:
                self._flush()

        return trace_id

    def _flush(self) -> None:
        """
        バッファをフラッシュ (内部メソッド)

        注意: このメソッドはlockを保持している状態で呼び出される
        """
        if not self.buffer:
            return

        # ここでDBやファイルに書き込む処理を実装
        # 現在は簡易実装としてログ出力のみ
        logger.debug(f"Flushing {len(self.buffer)} traces")

        self.buffer.clear()

    def flush(self) -> None:
        """バッファを強制的にフラッシュ (公開メソッド)"""
        with self.lock:
            self._flush()

    def get_buffer_size(self) -> int:
        """現在のバッファサイズを取得"""
        with self.lock:
            return len(self.buffer)


# グローバルインスタンス
trace_logger = TraceLogger()


def main():
    """メイン関数 (テスト用)"""
    print("🔍 TraceLogger Test")

    # テストログを記録
    for i in range(5):
        trace_id = trace_logger.log(
            caller="TestCaller", callee=f"TestCallee{i}", duration_ms=10.5 + i
        )
        print(f"Logged trace: {trace_id}")

    # バッファサイズを確認
    print(f"\nBuffer size: {trace_logger.get_buffer_size()}")

    # フラッシュ
    trace_logger.flush()
    print(f"Buffer size after flush: {trace_logger.get_buffer_size()}")

    print("\n✅ TraceLogger test completed")


if __name__ == "__main__":
    main()

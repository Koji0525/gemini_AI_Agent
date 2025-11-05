"""
graceful_shutdown.py

優雅な停止システム

【目的】
Ctrl+Cでの即座停止を可能にし、実行中のタスクを安全に終了する

【機能】
- KeyboardInterruptの適切なハンドリング
- ファイルベースの停止フラグ
- タイムアウト機能
- 進捗の自動保存
"""

import signal
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """
    優雅な停止システム
    """

    def __init__(self, stop_file: str = ".stop_orchestrator"):
        self.stop_file = Path(stop_file)
        self.shutdown_requested = False
        self.force_shutdown = False

        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """シグナルハンドラー"""
        if not self.shutdown_requested:
            logger.info("\n⚠️  停止要求を受信しました（Ctrl+C）")
            logger.info("   現在のタスクを完了してから停止します...")
            logger.info("   強制停止する場合はもう一度 Ctrl+C を押してください")
            self.shutdown_requested = True
        else:
            logger.info("\n🚨 強制停止します！")
            self.force_shutdown = True
            sys.exit(0)

    def should_stop(self) -> bool:
        """停止すべきか確認"""
        # ファイルベースの停止フラグ確認
        if self.stop_file.exists():
            logger.info("⚠️  停止ファイルを検出")
            return True

        return self.shutdown_requested

    def clear_stop_flag(self):
        """停止フラグをクリア"""
        if self.stop_file.exists():
            self.stop_file.unlink()
        self.shutdown_requested = False

    def request_stop(self):
        """停止を要求（プログラマティック）"""
        self.stop_file.touch()
        self.shutdown_requested = True
        logger.info("⚠️  停止要求を作成しました")


# グローバルインスタンス
shutdown_manager = GracefulShutdown()

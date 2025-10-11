"""
Python 3.13 非同期互換性修正
Windows環境でのasyncioプロアクターイベントの問題を解決
"""

import asyncio
import sys
import warnings

def apply_windows_async_fix():
    """Windows環境での非同期問題を修正"""
    if sys.platform == "win32":
        # ResourceWarningを無視（一時的対応）
        warnings.filterwarnings("ignore", category=ResourceWarning)
        
        # イベントループポリシーを設定
        if sys.version_info >= (3, 13):
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            except Exception:
                # 既に設定されている場合は無視
                pass

def safe_async_shutdown():
    """安全な非同期シャットダウン"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
        if not loop.is_closed():
            loop.close()
    except Exception:
        pass
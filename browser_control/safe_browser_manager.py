#!/usr/bin/env python3
"""ブラウザを確実に初期化・管理する基盤クラス"""
import asyncio
from pathlib import Path
import logging
from typing import Optional
from browser_control.browser_controller import BrowserController

logger = logging.getLogger(__name__)


class SafeBrowserManager:
    """ブラウザの安全な初期化と管理"""

    _instance: Optional["SafeBrowserManager"] = None
    _controller: Optional[BrowserController] = None
    _is_initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def get_controller(cls) -> BrowserController:
        if cls._controller is None or not cls._is_initialized:
            logger.info("🚀 ブラウザ初期化中...")
            await cls._initialize()
        return cls._controller

    @classmethod
    async def _initialize(cls):
        try:
            cls._controller = BrowserController(download_folder=Path("downloads"))
            await cls._controller.setup_browser()

            if cls._controller.context is None:
                raise RuntimeError("ブラウザ起動失敗")

            cls._is_initialized = True
            logger.info("✅ ブラウザ初期化完了")

        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            cls._controller = None
            cls._is_initialized = False
            raise

    @classmethod
    async def cleanup(cls):
        if cls._controller:
            logger.info("🧹 クリーンアップ中...")
            try:
                await cls._controller.cleanup()
            except Exception as e:
                logger.error(f"⚠️ エラー: {e}")
            finally:
                cls._controller = None
                cls._is_initialized = False


async def get_browser_controller() -> BrowserController:
    return await SafeBrowserManager.get_controller()


async def cleanup_browser():
    await SafeBrowserManager.cleanup()

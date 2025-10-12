# browser_lifecycle.py
"""ブラウザライフサイクル管理クラス"""
import asyncio
import time
from pathlib import Path
from typing import Optional, Dict
from playwright.async_api import async_playwright, Page, BrowserContext
import logging
import psutil

from configuration.config_utils import config, ErrorHandler

logger = logging.getLogger(__name__)

class BrowserLifecycleManager:
    """ブラウザの起動・終了・生存管理を担当"""
    
    def __init__(self, browser_data_dir: Path, download_folder: Path):
        self.browser_data_dir = browser_data_dir
        self.download_folder = download_folder
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        self.download_folder.mkdir(exist_ok=True, parents=True)
        if self.browser_data_dir:
            self.browser_data_dir.mkdir(parents=True, exist_ok=True)
    
    async def setup_browser(self) -> None:
        """ブラウザの初期化（マルチモニター対応版）"""
        try:
            logger.info("="*60)
            logger.info("ブラウザ起動開始...")
            logger.info("="*60)
            
            # 既存のプロセスクリーンアップ
            await self._cleanup_existing_browser_processes()
            
            self.playwright = await async_playwright().start()
            logger.info(f"ユーザーデータディレクトリ: {self.browser_data_dir}")
            
            # マルチモニター対応: ウィンドウ位置とサイズを指定
            window_width = 1280
            window_height = 700
            x_position = 0
            y_position = 0
            
            # ブラウザ起動（位置とサイズ指定）
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.browser_data_dir),
                viewport={'width': window_width, 'height': window_height},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                accept_downloads=True,
                ignore_https_errors=True,
                no_viewport=False,
                **config.BROWSER_CONFIG
            )
            
            logger.info("✅ ブラウザコンテキスト作成成功")
            
            # ページ作成
            self.page = await self.context.new_page()
            
            # ウィンドウを指定位置に移動
            await self.page.evaluate(f"""
                window.moveTo({x_position}, {y_position});
                window.resizeTo({window_width}, {window_height});
            """)
            
            logger.info(f"✅ ウィンドウを位置 ({x_position}, {y_position}) に配置")
            
            # ブラウザが正常に起動したか確認
            await asyncio.sleep(2)
            if not await self._is_browser_alive():
                raise Exception("ブラウザが起動直後にクラッシュしました")
            
            logger.info("✅ ブラウザ生存確認完了")
            
            # 自動化検出を回避
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                window.navigator.chrome = {
                    runtime: {},
                };
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['ja-JP', 'ja', 'en-US', 'en'],
                });
            """)
            
            self.page.set_default_timeout(config.PAGE_TIMEOUT)
            self.page.set_default_navigation_timeout(config.PAGE_TIMEOUT)
            
            logger.info("="*60)
            logger.info("✅ ブラウザ起動完了")
            logger.info("="*60)
            
        except Exception as e:
            ErrorHandler.log_error(e, "ブラウザ起動")
            logger.error("="*60)
            logger.error("❌ ブラウザ起動失敗")
            logger.error("="*60)
            
            logger.error(f"エラー詳細: {str(e)}")
            logger.error(f"ブラウザデータディレクトリ: {self.browser_data_dir}")
            
            await self._cleanup_existing_browser_processes()
            raise Exception(f"ブラウザ起動に失敗しました: {str(e)}")
    
    async def _is_browser_alive(self) -> bool:
        """ブラウザが生きているか確認"""
        try:
            if not self.page:
                return False
            result = await self.page.evaluate("1 + 1")
            return result == 2
        except Exception as e:
            logger.warning(f"ブラウザ生存確認失敗: {e}")
            return False
    
    async def _cleanup_existing_browser_processes(self):
        """既存のChromiumプロセスをクリーンアップ"""
        try:
            logger.info("既存のChromiumプロセスを確認中...")
            
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'chrome' in proc.info['name'].lower() or 'chromium' in proc.info['name'].lower():
                        cmdline = proc.cmdline()
                        if str(self.browser_data_dir) in ' '.join(cmdline):
                            logger.warning(f"既存のChromiumプロセスを終了: PID={proc.info['pid']}")
                            proc.kill()
                            killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed_count > 0:
                logger.info(f"✅ {killed_count}個のプロセスを終了しました")
                await asyncio.sleep(2)
            else:
                logger.info("既存プロセスなし")
                
        except ImportError:
            logger.warning("psutilがインストールされていません。プロセスクリーンアップをスキップ")
        except Exception as e:
            logger.warning(f"プロセスクリーンアップエラー: {e}")
    
    async def cleanup(self) -> None:
        """リソースのクリーンアップ"""
        try:
            logger.info("🔄 リソースクリーンアップを開始します...")

            # 非同期タスクのキャンセル
            try:
                tasks = [t for t in asyncio.all_tasks() 
                        if t is not asyncio.current_task()]
                        
                if tasks:
                    logger.info(f"🔄 {len(tasks)}個の非同期タスクをキャンセル中...")
                    for task in tasks:
                        task.cancel()
                            
                    await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=5.0
                    )
                    logger.info("✅ 非同期タスククリーンアップ完了")
            except asyncio.TimeoutError:
                logger.warning("⚠️ タスクキャンセルのタイムアウト")
            except Exception as e:
                logger.warning(f"⚠️ タスクキャンセル中のエラー: {e}")

            # ページのクローズ
            if self.page:
                try:
                    await self.page.close()
                    logger.info("✅ ページをクローズしました")
                except Exception as e:
                    logger.warning(f"⚠️ ページクローズ中の警告: {e}")

            # コンテキストのクローズ
            if self.context:
                try:
                    await self.context.close()
                    logger.info("✅ ブラウザコンテキストをクローズしました")
                except Exception as e:
                    logger.warning(f"⚠️ コンテキストクローズ中の警告: {e}")

            # Playwrightの停止
            if self.playwright:
                try:
                    await self.playwright.stop()
                    logger.info("✅ Playwrightを停止しました")
                except Exception as e:
                    logger.warning(f"⚠️ Playwright停止中の警告: {e}")

            logger.info("✅ リソースクリーンアップ完了")

        except Exception as e:
            logger.error(f"❌ クリーンアップ中のエラー: {e}")
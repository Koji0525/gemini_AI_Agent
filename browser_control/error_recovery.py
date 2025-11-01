"""
エラーリカバリーモジュール
"""

import asyncio
from typing import Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)


class ErrorRecovery:
    """
    エラーからの自動復旧を管理
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.error_count = 0

    async def execute_with_recovery(
        self, func: Callable, *args, recovery_actions: Optional[list] = None, **kwargs
    ) -> Any:
        """
        エラー時に自動復旧を試みながら関数を実行

        Args:
            func: 実行する関数
            recovery_actions: 復旧アクション（リスト）
        """
        if recovery_actions is None:
            recovery_actions = []

        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)

                # 成功したらエラーカウントをリセット
                self.error_count = 0
                return result

            except Exception as e:
                self.error_count += 1
                logger.error(f"エラー発生（試行 {attempt + 1}/{self.max_retries}）: {e}")

                if attempt < self.max_retries - 1:
                    # 復旧アクションを実行
                    for action in recovery_actions:
                        try:
                            await action()
                        except Exception as recovery_error:
                            logger.error(f"復旧アクション失敗: {recovery_error}")

                    # 待機時間を指数的に増加
                    wait_time = 2**attempt * 5  # 5秒、10秒、20秒...
                    logger.info(f"⏳ {wait_time}秒後に再試行...")
                    await asyncio.sleep(wait_time)
                else:
                    # 最終試行も失敗
                    logger.error(f"❌ {self.max_retries}回試行しましたが失敗しました")
                    raise


# 使用例
async def recovery_reload_page(browser):
    """ページをリロードする復旧アクション"""
    print("🔄 ページをリロード中...")
    await browser.page.reload()
    await asyncio.sleep(3)


async def recovery_re_login(browser):
    """再ログインする復旧アクション"""
    print("🔐 再ログイン中...")
    await browser.navigate_to_gemini()

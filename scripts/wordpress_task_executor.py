#!/usr/bin/env python3
"""
WordPress タスクエグゼキューター（修正版）
- タスクデータ構造の柔軟な対応
- エラーハンドリング強化
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from browser_control.browser_controller import BrowserController
from wordpress.wp_post_creator import WordPressPostCreator
from wordpress.wp_post_editor import WordPressPostEditor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WordPressTaskExecutor:
    """WordPress タスク実行"""

    def __init__(self):
        self.wp_url = "https://uzbek-ma.com"
        self.browser = None
        self.page = None

    async def initialize(self):
        """初期化"""
        logger.info("🔧 ブラウザ初期化中...")
        try:
            self.browser = BrowserController(download_folder="./downloads")

            if hasattr(self.browser, "get_page"):
                self.page = await self.browser.get_page()
            elif hasattr(self.browser, "page"):
                self.page = self.browser.page
            else:
                logger.error("❌ Page取得方法が見つかりません")
                return False

            logger.info("✅ ブラウザ初期化完了")
            return True

        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            return False

    async def cleanup(self):
        """クリーンアップ"""
        if self.browser and hasattr(self.browser, "cleanup"):
            try:
                await self.browser.cleanup()
                logger.info("✅ ブラウザクリーンアップ完了")
            except:
                pass

    def _extract_task_info(self, task: dict) -> tuple:
        """タスク情報を柔軟に抽出"""
        # 複数のキー名に対応
        title_keys = ["title", "description", "task_name", "name"]
        content_keys = ["content", "body", "text", "description"]

        title = None
        for key in title_keys:
            if key in task and task[key]:
                title = str(task[key])
                break

        content = None
        for key in content_keys:
            if key in task and task[key]:
                content = str(task[key])
                break

        # デフォルト値
        if not title:
            title = f"タスク {task.get('task_id', 'unknown')}"

        if not content:
            content = title  # タイトルをコンテンツとして使用

        logger.info(f"📝 抽出結果:")
        logger.info(f"   タイトル: {title[:50]}...")
        logger.info(f"   コンテンツ: {content[:50]}...")

        return title, content

    async def create_draft(self, task: dict) -> dict:
        """下書き作成"""
        logger.info("=" * 80)
        logger.info(f"📝 下書き作成タスク")
        logger.info("=" * 80)

        # タスクデータの内容をログ出力
        logger.info("📋 受け取ったタスクデータ:")
        for key, value in task.items():
            if isinstance(value, str) and len(value) > 100:
                logger.info(f"   {key}: {value[:100]}...")
            else:
                logger.info(f"   {key}: {value}")

        try:
            # タイトルとコンテンツを抽出
            title, content = self._extract_task_info(task)

            # WordPressPostCreator 初期化
            creator = WordPressPostCreator(wp_url=self.wp_url, sheets_manager=None)

            # タスクデータを wp_post_creator が期待する形式に変換
            wp_task = {
                "title": title[:200],  # 200文字制限
                "content": f"""
<h2>{title}</h2>

<p>{content}</p>

<h3>タスク情報</h3>
<ul>
    <li><strong>タスクID:</strong> {task.get('task_id', 'N/A')}</li>
    <li><strong>実行日時:</strong> {datetime.now().strftime("%Y年%m月%d日 %H時%M分")}</li>
    <li><strong>ロール:</strong> {task.get('required_role', 'N/A')}</li>
    <li><strong>優先度:</strong> {task.get('priority', 'N/A')}</li>
</ul>
                """,
                "post_status": "draft",
                "category": "Auto Generated",
                "tags": ["自動生成", f"task_{task.get('task_id', 'unknown')}"],
            }

            logger.info(f"🚀 WordPress記事作成実行...")

            # 記事作成
            result = await creator.create_post(self.page, wp_task)

            logger.info("✅ 下書き作成成功")
            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"❌ 下書き作成エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    async def edit_post(self, task: dict) -> dict:
        """記事編集"""
        logger.info("=" * 80)
        logger.info(f"✏️ 記事編集タスク")
        logger.info("=" * 80)

        try:
            editor = WordPressPostEditor(wp_url=self.wp_url, sheets_manager=None)

            result = await editor.edit_post(self.page, task)

            logger.info("✅ 記事編集成功")
            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"❌ 記事編集エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}


async def test_create_draft():
    """テスト実行"""
    executor = WordPressTaskExecutor()

    if not await executor.initialize():
        logger.error("❌ 初期化失敗")
        return

    try:
        # テストタスク
        task = {
            "task_id": "TEST_001",
            "description": "【タクソノミー】業種カテゴリ作成（industry_category）ワードプレス内でお願いします。",
            "required_role": "wp_dev",
            "priority": "high",
        }

        result = await executor.create_draft(task)

        if result["success"]:
            logger.info("\n🎉 テスト成功！")
        else:
            logger.error(f"\n❌ テスト失敗: {result.get('error')}")

    finally:
        await executor.cleanup()


if __name__ == "__main__":
    asyncio.run(test_create_draft())

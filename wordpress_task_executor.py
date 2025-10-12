#!/usr/bin/env python3
"""
WordPress タスクエグゼキューター
- wp_post_creator.py で下書き作成
- wp_post_editor.py で記事編集
- BrowserController を使用（headless対応）
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from browser_controller import BrowserController
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
            
            # Pageオブジェクトを取得
            if hasattr(self.browser, 'get_page'):
                self.page = await self.browser.get_page()
            elif hasattr(self.browser, 'page'):
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
        if self.browser and hasattr(self.browser, 'cleanup'):
            try:
                await self.browser.cleanup()
                logger.info("✅ ブラウザクリーンアップ完了")
            except:
                pass
    
    async def create_draft(self, task: dict) -> dict:
        """下書き作成"""
        logger.info("=" * 80)
        logger.info(f"📝 下書き作成: {task.get('title', 'Untitled')}")
        logger.info("=" * 80)
        
        try:
            # WordPressPostCreator 初期化
            creator = WordPressPostCreator(wp_url=self.wp_url, sheets_manager=None)
            
            # 記事作成
            result = await creator.create_post(self.page, task)
            
            logger.info("✅ 下書き作成成功")
            return {'success': True, 'result': result}
            
        except Exception as e:
            logger.error(f"❌ 下書き作成エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'success': False, 'error': str(e)}
    
    async def edit_post(self, task: dict) -> dict:
        """記事編集"""
        logger.info("=" * 80)
        logger.info(f"✏️ 記事編集: {task.get('title', 'Untitled')}")
        logger.info("=" * 80)
        
        try:
            # WordPressPostEditor 初期化
            editor = WordPressPostEditor(wp_url=self.wp_url, sheets_manager=None)
            
            # 記事編集
            result = await editor.edit_post(self.page, task)
            
            logger.info("✅ 記事編集成功")
            return {'success': True, 'result': result}
            
        except Exception as e:
            logger.error(f"❌ 記事編集エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'success': False, 'error': str(e)}

async def test_create_draft():
    """下書き作成テスト"""
    executor = WordPressTaskExecutor()
    
    if not await executor.initialize():
        logger.error("❌ 初期化失敗")
        return
    
    try:
        # テスト記事データ
        task = {
            'title': f'🤖 自動生成テスト記事 - {datetime.now().strftime("%Y/%m/%d %H:%M")}',
            'content': f'''
<h2>これは自動生成されたテスト記事です</h2>

<p>このコンテンツは <strong>wp_post_creator.py</strong> によって自動的に作成されました。</p>

<h3>システムの特徴</h3>
<ul>
    <li>✅ エラー自動検出</li>
    <li>✅ 自動修正機能</li>
    <li>✅ Google Sheets連携</li>
    <li>✅ WordPress自動投稿</li>
</ul>

<p><strong>作成日時:</strong> {datetime.now().strftime("%Y年%m月%d日 %H時%M分")}</p>
            ''',
            'post_status': 'draft',
            'category': 'Test',
            'tags': ['自動生成', 'AI', 'Test']
        }
        
        # 下書き作成実行
        result = await executor.create_draft(task)
        
        if result['success']:
            logger.info("\n" + "=" * 80)
            logger.info("🎉 下書き作成成功！")
            logger.info("=" * 80)
            logger.info("📝 確認方法:")
            logger.info("   1. https://uzbek-ma.com/wp-admin/ にアクセス")
            logger.info("   2. 投稿 → 投稿一覧")
            logger.info("   3. ステータス: 下書き でフィルター")
        else:
            logger.error(f"\n❌ 下書き作成失敗: {result.get('error')}")
            
    finally:
        await executor.cleanup()

if __name__ == "__main__":
    asyncio.run(test_create_draft())

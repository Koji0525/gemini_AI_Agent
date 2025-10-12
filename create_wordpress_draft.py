#!/usr/bin/env python3
"""
WordPress下書き作成テスト（実際にブラウザで操作）
"""
import asyncio
import logging
from datetime import datetime
from browser_controller import BrowserController
from wordpress.wp_agent import WordPressAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_draft_post():
    """実際に下書き記事を作成"""
    browser = None
    page = None
    
    try:
        logger.info("🌐 ブラウザ起動中...")
        browser = BrowserController(download_folder="./downloads")
        
        # Pageオブジェクトを取得
        if hasattr(browser, 'get_page'):
            page = await browser.get_page()
        elif hasattr(browser, 'new_page'):
            page = await browser.new_page()
        else:
            logger.error("❌ Pageオブジェクトを取得できません")
            return False
        
        logger.info("✅ ブラウザ起動完了")
        
        # WordPressエージェント初期化
        logger.info("🔧 WordPressエージェント初期化中...")
        wp = WordPressAgent(browser)
        
        # 記事データ
        task = {
            'type': 'create_post',
            'title': f'🤖 自動生成記事 - {datetime.now().strftime("%Y年%m月%d日 %H:%M")}',
            'content': '''
<h2>これは自動生成されたテスト記事です</h2>

<p>このコンテンツは自律型エージェントシステムによって自動的に作成されました。</p>

<h3>システムの特徴</h3>
<ul>
    <li>エラー自動検出</li>
    <li>自動修正機能</li>
    <li>Google Sheets連携</li>
    <li>タスク管理自動化</li>
</ul>

<p>作成日時: {datetime.now().strftime("%Y年%m月%d日 %H時%M分")}</p>
            '''.format(datetime=datetime),
            'post_status': 'draft',
            'post_action': 'create',
            'category': 'テスト',
            'tags': ['自動生成', 'AI', 'テスト']
        }
        
        logger.info(f"📝 記事作成中: {task['title']}")
        
        # WordPress管理画面にログイン・記事作成
        result = await wp.create_post(page, task)
        
        logger.info("✅ 記事作成完了！")
        logger.info(f"📋 結果: {result}")
        
        # スクリーンショット保存
        if hasattr(page, 'screenshot'):
            screenshot_path = f"screenshots/draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            logger.info(f"📸 スクリーンショット保存: {screenshot_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
        
    finally:
        if page and hasattr(page, 'close'):
            try:
                await page.close()
            except:
                pass
        if browser and hasattr(browser, 'cleanup'):
            try:
                await browser.cleanup()
            except:
                pass

async def main():
    logger.info("=" * 80)
    logger.info("🚀 WordPress下書き作成テスト")
    logger.info("=" * 80)
    
    success = await create_draft_post()
    
    if success:
        logger.info("\n✅ 下書き作成成功！")
        logger.info("📝 確認方法:")
        logger.info("   1. WordPress管理画面にログイン")
        logger.info("   2. 投稿 → 投稿一覧")
        logger.info("   3. ステータス: 下書き でフィルター")
    else:
        logger.error("\n❌ 下書き作成失敗")

if __name__ == "__main__":
    asyncio.run(main())

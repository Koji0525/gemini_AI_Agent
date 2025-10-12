#!/usr/bin/env python3
"""
WordPress下書き作成 - wp_post_creator.py を使用
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Playwrightのページオブジェクトをインポート
try:
    from playwright.async_api import async_playwright, Page
except ImportError:
    logger.error("❌ Playwright がインストールされていません: pip install playwright")
    exit(1)

from wordpress.wp_post_creator import WordPressPostCreator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_draft_post():
    """wp_post_creator を使って下書き作成"""
    
    # WordPress設定（実際の値に置き換える）
    wp_url = "https://your-actual-wordpress-site.com"  # 実際のWordPressサイトURL
    
    try:
        logger.info("=" * 80)
        logger.info("📝 WordPress下書き作成開始")
        logger.info("=" * 80)
        
        # WordPressPostCreator 初期化
        logger.info(f"🔧 WordPressPostCreator 初期化中...")
        logger.info(f"   WordPress URL: {wp_url}")
        
        creator = WordPressPostCreator(wp_url=wp_url, sheets_manager=None)
        
        # Playwrightでブラウザを起動
        logger.info("🌐 ブラウザ起動中...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)  # headless=False でブラウザを表示
        context = await browser.new_context()
        page = await context.new_page()
        
        logger.info("✅ ブラウザ起動完了")
        
        # タスクデータ
        task = {
            'title': f'🤖 自動生成記事 - {datetime.now().strftime("%Y年%m月%d日 %H:%M")}',
            'content': f'''
<h2>これは自動生成されたテスト記事です</h2>

<p>このコンテンツは自律型エージェントシステムの <strong>wp_post_creator.py</strong> によって自動的に作成されました。</p>

<h3>システムの特徴</h3>
<ul>
    <li>✅ エラー自動検出</li>
    <li>✅ 自動修正機能</li>
    <li>✅ Google Sheets連携</li>
    <li>✅ タスク管理自動化</li>
    <li>✅ WordPress自動投稿</li>
</ul>

<h3>技術スタック</h3>
<ul>
    <li>Python 3.12</li>
    <li>Playwright（ブラウザ自動化）</li>
    <li>Google Sheets API</li>
    <li>WordPress REST API</li>
</ul>

<p><strong>作成日時:</strong> {datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒")}</p>
<p><strong>ステータス:</strong> 下書き（Draft）</p>
            ''',
            'post_status': 'draft',
            'category': 'テスト',
            'tags': ['自動生成', 'AI', 'テスト', 'wp_post_creator']
        }
        
        logger.info(f"📝 記事作成中: {task['title']}")
        
        # create_post メソッドを呼び出し
        result = await creator.create_post(page, task)
        
        logger.info("✅ 記事作成完了！")
        logger.info(f"📋 結果: {result}")
        
        # スクリーンショット保存
        screenshot_dir = Path("screenshots")
        screenshot_dir.mkdir(exist_ok=True)
        screenshot_path = screenshot_dir / f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        await page.screenshot(path=str(screenshot_path))
        logger.info(f"📸 スクリーンショット保存: {screenshot_path}")
        
        # 少し待機（確認用）
        logger.info("⏳ 5秒待機（確認用）...")
        await asyncio.sleep(5)
        
        # クリーンアップ
        await browser.close()
        await playwright.stop()
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 下書き作成成功！")
        logger.info("=" * 80)
        logger.info("📝 確認方法:")
        logger.info(f"   1. {wp_url}/wp-admin/ にアクセス")
        logger.info("   2. 投稿 → 投稿一覧")
        logger.info("   3. ステータス: 下書き でフィルター")
        logger.info(f"   4. 「{task['title']}」を確認")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    success = await create_draft_post()
    
    if not success:
        logger.error("\n❌ 下書き作成失敗")
        logger.info("\n🔧 トラブルシューティング:")
        logger.info("   1. wp_url を実際のWordPressサイトURLに設定")
        logger.info("   2. WordPress管理画面にアクセスできるか確認")
        logger.info("   3. wp_post_creator.py の create_post メソッドを確認")

if __name__ == "__main__":
    asyncio.run(main())

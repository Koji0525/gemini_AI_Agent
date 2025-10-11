"""WordPress投稿作成"""
import logging
import re
from datetime import datetime
from typing import Dict, Optional
from playwright.async_api import Page

from .wp_utils import TaskContentFetcher

logger = logging.getLogger(__name__)


class WordPressPostCreator:
    """WordPress投稿作成機能"""
    
    def __init__(self, wp_url: str, sheets_manager=None):
        self.wp_url = wp_url
        self.sheets_manager = sheets_manager
    
    async def create_post(self, page: Page, task: Dict) -> Dict:
        """コンテンツ(投稿/ページ)を作成"""
        try:
            logger.info("コンテンツ作成を実行中...")
            
            # task_idを抽出
            target_task_id = TaskContentFetcher.extract_task_id(task['description'])
            post_content = None
            post_title = f"AI投稿_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            if target_task_id:
                logger.info(f"task_id {target_task_id} の記事内容を使用")
                post_content = await TaskContentFetcher.get_task_content(
                    self.sheets_manager, target_task_id
                )
                
                if post_content:
                    # タイトルを抽出(最初の行をタイトルとする)
                    lines = post_content.split('\n')
                    if lines:
                        post_title = lines[0].strip()[:100]
                        # 本文は2行目以降
                        post_content = '\n'.join(lines[1:]).strip()
            
            if not post_content:
                # タスクからタイトルと本文を直接抽出
                title_match = re.search(r'タイトル[　\s]*(.+?)[\n本文]', task['description'])
                content_match = re.search(r'本文[　\s]*(.+?)[\n」]', task['description'])
                
                post_title = title_match.group(1).strip() if title_match else post_title
                post_content = content_match.group(1).strip() if content_match else "自動生成されたコンテンツ"
            
            logger.info(f"投稿内容: タイトル='{post_title}', 本文='{post_content[:50]}...'")
            
            # 新規投稿ページに移動
            await page.goto(f"{self.wp_url}/wp-admin/post-new.php")
            await page.wait_for_timeout(4000)
            
            # タイトル入力
            title_filled = await self._fill_title(page, post_title)
            
            # 本文入力
            content_filled = await self._fill_content(page, post_content)
            
            # Polylangの言語を日本語に設定
            await self._set_polylang_language(page)
            
            # 下書き保存
            saved = await self._save_draft(page)
            
            # スクリーンショット
            screenshot_path = f"wp_post_saved_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            
            if saved:
                return {
                    'success': True,
                    'summary': f'投稿を下書き保存しました。タイトル: {post_title}',
                    'screenshot': screenshot_path,
                    'full_text': f'投稿作成完了\nタイトル: {post_title}\n本文: {post_content[:200]}...\nスクリーンショット: {screenshot_path}'
                }
            else:
                return {
                    'success': True,
                    'summary': f'投稿を作成しました(保存ボタンが見つからなかったため手動確認が必要)',
                    'screenshot': screenshot_path,
                    'full_text': f'投稿作成\nタイトル: {post_title}\n本文: {post_content[:200]}...\nスクリーンショット: {screenshot_path}'
                }
                
        except Exception as e:
            logger.error(f"コンテンツ作成エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _fill_title(self, page: Page, title: str) -> bool:
        """タイトル入力"""
        title_selectors = [
            '.editor-post-title__input',
            'h1[aria-label="タイトルを追加"]',
            'textarea[placeholder*="タイトル"]',
            '#post-title-0'
        ]
        
        for selector in title_selectors:
            try:
                title_input = await page.query_selector(selector)
                if title_input and await title_input.is_visible():
                    await title_input.click()
                    await page.wait_for_timeout(500)
                    await title_input.fill(title)
                    await page.wait_for_timeout(1000)
                    logger.info(f"✅ タイトル入力完了: {title}")
                    return True
            except:
                continue
        
        logger.warning("タイトル入力欄が見つかりません")
        return False
    
    # wp_post_creator.py に追加するメソッド
    async def _fill_html_content(self, page: Page, html_content: str) -> bool:
        """HTMLコンテンツをGutenbergエディタに挿入"""
        try:
            logger.info("HTMLコンテンツを挿入中...")
        
            # カスタムHTMLブロックを追加
            await page.keyboard.press('/')
            await page.wait_for_timeout(1000)
            await page.keyboard.type('html')
            await page.wait_for_timeout(1000)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(2000)
        
            # HTML入力エリアを見つける
            html_input_selectors = [
                'textarea.block-editor-plain-text',
                '.wp-block-html textarea',
                'textarea[aria-label*="HTML"]'
            ]
        
            for selector in html_input_selectors:
                try:
                    html_input = await page.query_selector(selector)
                    if html_input and await html_input.is_visible():
                        await html_input.click()
                        await page.wait_for_timeout(500)
                        await html_input.fill(html_content)
                        await page.wait_for_timeout(1000)
                        logger.info("✅ HTMLコンテンツ挿入完了")
                        return True
                except Exception as e:
                    logger.debug(f"HTML入力試行エラー ({selector}): {e}")
                    continue
        
            return False
        
        except Exception as e:
            logger.error(f"HTMLコンテンツ挿入エラー: {e}")
            return False
    
    async def _fill_content(self, page: Page, content: str) -> bool:
        """本文入力"""
        # Tabキーで本文エリアに移動
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(500)
        
        content_selectors = [
            'p[data-title="段落"]',
            '.block-editor-default-block-appender__content',
            '[aria-label="ブロックを追加"]',
            '.wp-block-paragraph'
        ]
        
        for selector in content_selectors:
            try:
                content_area = await page.query_selector(selector)
                if content_area:
                    await content_area.click()
                    await page.wait_for_timeout(500)
                    await page.keyboard.type(content)
                    await page.wait_for_timeout(1000)
                    logger.info("✅ 本文入力完了")
                    return True
            except:
                continue
        
        # フォールバック: 単純にTabキー後に入力
        await page.keyboard.type(content)
        await page.wait_for_timeout(1000)
        logger.info("✅ 本文入力完了(フォールバック)")
        return True
    
    async def _set_polylang_language(self, page: Page) -> bool:
        """Polylangの言語を日本語に設定（wp_post_editor.pyと同じロジック）"""
        polylang_selectors = [
            'select[name="post_lang_choice"]',
            '#post_lang_choice',
            'select.pll-select-flag',
            '#pll_post_lang_choice',
            'select[id*="lang"]'
        ]
        
        logger.debug("Polylang言語設定セレクタを探索中...")
        
        for i, selector in enumerate(polylang_selectors, 1):
            logger.debug(f"  試行 {i}/{len(polylang_selectors)}: {selector}")
            try:
                lang_select = await page.query_selector(selector)
                if lang_select:
                    is_visible = await lang_select.is_visible()
                    logger.debug(f"  → 要素発見: 表示={is_visible}")
                    
                    if is_visible:
                        # 日本語オプションを探す
                        options = await lang_select.inner_text()
                        logger.debug(f"  → 利用可能な言語: {options[:100]}")
                        
                        # 複数の日本語表記を試す
                        japanese_labels = ['日本語', 'ja', 'Japanese', 'japanese']
                        
                        for label in japanese_labels:
                            try:
                                await lang_select.select_option(label=label)
                                await page.wait_for_timeout(2000)
                                logger.info(f"✅ Polylang言語設定成功: {label}")
                                
                                # 確認ダイアログ処理
                                await self._handle_confirm_dialog(page)
                                
                                return True
                            except:
                                continue
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue
        
        logger.warning("❌ Polylang言語設定要素が見つかりませんでした")
        return False
    
    async def _handle_confirm_dialog(self, page: Page):
        """確認ダイアログを処理（wp_post_editor.pyと同じ）"""
        ok_button_selectors = [
            'button:has-text("OK")',
            'button:has-text("はい")',
            '.ui-dialog-buttonset button:first-child',
            'button[type="button"]:has-text("OK")'
        ]
        
        for selector in ok_button_selectors:
            try:
                ok_button = await page.query_selector(selector)
                if ok_button:
                    is_visible = await ok_button.is_visible()
                    if is_visible:
                        await ok_button.click()
                        await page.wait_for_timeout(1000)
                        logger.debug("✅ 確認ダイアログでOKをクリック")
                        return
            except:
                continue
    
    async def _save_draft(self, page: Page) -> bool:
        """下書き保存"""
        save_selectors = [
            'button[aria-label="下書き保存"]',
            'button:has-text("下書き保存")',
            '.editor-post-save-draft'
        ]
        
        for selector in save_selectors:
            try:
                save_button = await page.query_selector(selector)
                if save_button and await save_button.is_visible():
                    is_disabled = await save_button.is_disabled()
                    if not is_disabled:
                        await save_button.click()
                        await page.wait_for_timeout(3000)
                        logger.info("✅ 下書き保存完了")
                        return True
            except:
                continue
        
        return False
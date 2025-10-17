# browser_ai_chat_agent.py
"""AIチャットエージェントクラス（Gemini/DeepSeek対応）"""
import asyncio
import time
import json
import re
from datetime import datetime
from typing import Optional, Dict
from playwright.async_api import Page
import logging

from configuration.config_utils import ErrorHandler, FileNameGenerator

logger = logging.getLogger(__name__)

class AIChatAgent:
    """AIサービス（Gemini/DeepSeek）との対話を担当"""
    
    def __init__(self, page: Page, service: str = "google", credentials: Dict = None):
        self.page = page
        self.service = service.lower()
        self.credentials = credentials or {}
    
    async def navigate_to_gemini(self) -> None:
        """Geminiサイトにアクセス（クラッシュ検知強化版）"""
        try:
            if not self.page:
                raise Exception("ページが初期化されていません")
            
            logger.info("Geminiサイトにアクセス中...")
            
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(f"Geminiサイトへのアクセス試行 {attempt}/{max_attempts}")
                    
                    await self.page.goto("https://gemini.google.com/", timeout=60000, wait_until="domcontentloaded")
                    await asyncio.sleep(3)
                    
                    logger.info("✅ Geminiサイトへのアクセスが成功しました")
                    break
                    
                except Exception as e:
                    logger.warning(f"試行 {attempt} 失敗: {e}")
                    
                    if attempt == max_attempts:
                        logger.error("全ての試行が失敗しました")
                        logger.error("手動でページをリロードしてください")
                        input("Geminiページが読み込まれたら、Enterキーを押してください: ")
                    else:
                        logger.info("5秒後に再試行します...")
                        await asyncio.sleep(5)
            
            current_url = self.page.url
            logger.info(f"現在のURL: {current_url}")
            
            await self.handle_welcome_screens()
            logger.info("✅ Geminiサイトの準備が完了しました")
            
        except Exception as e:
            ErrorHandler.log_error(e, "Geminiアクセス")
            logger.info("手動でGeminiページを開いてください")
            input("準備完了後、Enterキーを押してください: ")
    
    async def navigate_to_deepseek(self) -> None:
        """DeepSeekサイトにアクセス（Cloudflareボット検証対応版）"""
        try:
            if not self.page:
                raise Exception("ページが初期化されていません")
            logger.info("DeepSeekサイトにアクセス中...")
            
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(f"DeepSeekサイトへのアクセス試行 {attempt}/{max_attempts}")
                    await self.page.goto("https://chat.deepseek.com/", timeout=60000, wait_until="domcontentloaded")
                    await self.page.wait_for_timeout(5000)
                    logger.info("DeepSeekサイトへのアクセスが成功しました")
                    break
                except Exception as e:
                    logger.warning(f"試行 {attempt} 失敗: {e}")
                    if attempt == max_attempts:
                        logger.error("全ての試行が失敗しました。手動でページをリロードしてください")
                        input("DeepSeekページが読み込まれたら、Enterキーを押してください: ")
                    else:
                        logger.info("5秒後に再試行します...")
                        await self.page.wait_for_timeout(5000)
            
            current_url = self.page.url
            logger.info(f"現在のURL: {current_url}")
            
            # Cloudflareボット検証チェック
            logger.info("Cloudflareボット検証をチェック中...")
            cloudflare_check = await self.page.evaluate('''
                () => {
                    const body = document.body.innerText || '';
                    if (body.includes('Verifying you are human') || 
                        body.includes('あなたがボットではないことを確認') ||
                        body.includes('Just a moment') ||
                        body.includes('Checking your browser')) {
                        return true;
                    }
                    return false;
                }
            ''')
            
            if cloudflare_check:
                logger.warning("⚠️ Cloudflareボット検証が検出されました")
                logger.info("ブラウザで自動的にチェックが完了するまで待機します...")
                
                start_time = time.time()
                while time.time() - start_time < 60:
                    await self.page.wait_for_timeout(3000)
                    
                    still_checking = await self.page.evaluate('''
                        () => {
                            const body = document.body.innerText || '';
                            if (body.includes('Verifying you are human') || 
                                body.includes('あなたがボットではないことを確認') ||
                                body.includes('Just a moment') ||
                                body.includes('Checking your browser')) {
                                return true;
                            }
                            return false;
                        }
                    ''')
                    
                    if not still_checking:
                        logger.info("✅ Cloudflare検証が完了しました")
                        break
                    
                    elapsed = int(time.time() - start_time)
                    if elapsed % 10 == 0:
                        logger.info(f"待機中... {elapsed}秒経過")
                
                await self.page.wait_for_timeout(3000)
                current_url = self.page.url
                logger.info(f"検証後のURL: {current_url}")
            
            # ログインページにいるかチェック
            if 'sign_in' in current_url.lower() or 'login' in current_url.lower():
                logger.info("\n" + "="*60)
                logger.info("⚠️ DeepSeekへのログインが必要です")
                logger.info("="*60)
                logger.info("")
                logger.info("📌 ログイン手順：")
                logger.info("1. ブラウザで「Log in with Google」ボタンをクリック")
                logger.info("2. Googleアカウントを選択（または入力）")
                logger.info(f"   使用するアカウント: {self.credentials.get('email', 'B2セルのGoogle ID')}")
                logger.info("3. ログイン完了を待つ")
                logger.info("4. チャット画面が表示されたら、このコンソールに戻ってEnterキーを押す")
                logger.info("")
                logger.info("💡 ヒント：")
                logger.info("  - 「Chrome は自動テスト...」メッセージは無視してください")
                logger.info("  - Googleログインは通常通り動作します")
                logger.info("  - 2回目以降はCookieで自動ログインされます")
                logger.info("="*60)
                
                input("\n✅ ログイン完了後、Enterキーを押してください: ")
                
                await self.page.wait_for_timeout(2000)
                current_url = self.page.url
                logger.info(f"ログイン後のURL: {current_url}")
                
                if 'sign_in' in current_url.lower() or 'login' in current_url.lower():
                    logger.warning("⚠️ まだログインページにいます")
                    logger.info("もう一度「Log in with Google」をクリックしてください")
                    input("完了後、Enterキーを押してください: ")
                    await self.page.wait_for_timeout(2000)
            
            # チャット画面に到達できているか確認
            await self.page.wait_for_timeout(3000)
            chat_ready = await self.page.evaluate('''
                () => {
                    const inputs = document.querySelectorAll('textarea, input[type="text"]');
                    return inputs.length > 0;
                }
            ''')
            
            if not chat_ready:
                logger.warning("⚠️ チャット画面が見つかりません")
                logger.info("ブラウザでチャット画面が表示されるまで待機してください")
                input("\n✅ チャット画面が表示されたら、Enterキーを押してください: ")
            else:
                logger.info("✅ チャット画面を確認しました")
            
            logger.info("✅ DeepSeekサイトの準備が完了しました")
            
        except Exception as e:
            ErrorHandler.log_error(e, "DeepSeekアクセス")
            logger.info("手動でDeepSeekページを開いてください")
            input("準備完了後、Enterキーを押してください: ")
    
    async def handle_welcome_screens(self) -> None:
        """利用規約やウェルカム画面を処理"""
        try:
            if not self.page:
                return
            logger.info("ウェルカム画面やポップアップを確認中...")
            continue_buttons = [
                'text=続行', 'text=開始', 'text=同意', 'text=Continue',
                'text=Get started', 'text=Agree', 'text=Got it', 'text=OK',
                '[data-testid="continue-button"]'
            ]
            start_time = time.time()
            found_buttons = 0
            while time.time() - start_time < 10 and found_buttons < 3:
                for button_selector in continue_buttons:
                    try:
                        button = await self.page.query_selector(button_selector)
                        if button and await button.is_visible():
                            await button.click()
                            await self.page.wait_for_timeout(2000)
                            logger.info(f"ボタンをクリックしました: {button_selector}")
                            found_buttons += 1
                            break
                    except Exception:
                        continue
                await self.page.wait_for_timeout(1000)
            if found_buttons > 0:
                logger.info(f"{found_buttons}個のウェルカム画面を処理しました")
            else:
                logger.info("ウェルカム画面は見つかりませんでした（正常）")
        except Exception as e:
            ErrorHandler.log_error(e, "ウェルカム画面処理")
    
    async def ensure_normal_chat_mode(self) -> None:
        """通常のチャットモードであることを確認（Storybookを回避）- 強化版"""
        try:
            if not self.page:
                return
            logger.info("チャットモードを確認中...")
            current_url = self.page.url
            if 'storybook' in current_url.lower():
                logger.warning("StorybookのURLが検出されました。通常モードに戻します...")
                if self.service == "deepseek":
                    await self.page.goto("https://chat.deepseek.com/", wait_until="domcontentloaded")
                else:
                    await self.page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
                await self.page.wait_for_timeout(3000)
                logger.info("通常のチャットモードに戻しました")
                return
            storybook_active = await self.page.evaluate('''
                () => {
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        const text = btn.textContent || '';
                        const ariaLabel = btn.getAttribute('aria-label') || '';
                        if ((text.includes('Storybook') || ariaLabel.includes('Storybook')) &&
                            (btn.getAttribute('aria-pressed') === 'true' || 
                             btn.classList.contains('active') ||
                             btn.classList.contains('selected'))) {
                            return true;
                        }
                    }
                    return false;
                }
            ''')
            if storybook_active:
                logger.warning("Storybookモードが検出されました。通常モードに戻します...")
                if self.service == "deepseek":
                    await self.page.goto("https://chat.deepseek.com/", wait_until="domcontentloaded")
                else:
                    await self.page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
                await self.page.wait_for_timeout(3000)
                logger.info("通常のチャットモードに戻しました")
            else:
                logger.info("通常のチャットモードです")
        except Exception as e:
            ErrorHandler.log_error(e, "チャットモード確認")
    
    async def send_prompt(self, prompt: str) -> None:
        """プロンプトを入力して送信（サービス自動判別版）"""
        try:
            if not self.page:
                raise Exception("ページが初期化されていません")
            await self.ensure_normal_chat_mode()
            logger.info(f"プロンプトを送信中: {prompt[:50]}...")
            
            if self.service == "deepseek":
                await self.send_prompt_deepseek(prompt)
            else:
                await self.send_prompt_gemini(prompt)
                
        except Exception as e:
            ErrorHandler.log_error(e, "プロンプト送信")
            if self.page:
                await self.page.screenshot(path="debug_send_error.png")
            raise
    
    async def send_prompt_gemini(self, prompt: str) -> None:
        """Geminiでプロンプトを送信(ポップアップ対応版)"""
        try:
            # 入力欄を探す
            input_selectors = [
                'textarea[placeholder*="メッセージを Gemini に送信"]',
                'textarea[placeholder*="Send a message to Gemini"]',
                'div[contenteditable="true"][role="textbox"]',
                'textarea[data-testid="message-input"]',
                'div.ql-editor[contenteditable="true"]',
                'textarea.ql-editor',
                '[data-message-input]',
                'div[contenteditable="true"][aria-label*="メッセージ"]',
                'div[contenteditable="true"][aria-label*="message"]',
                'div[contenteditable="true"][tabindex="0"]',
                'textarea[aria-label*="Gemini"]',
                '[data-testid="input-area"] textarea',
                '[data-testid="input-area"] div[contenteditable="true"]',
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    input_element = await self.page.query_selector(selector)
                    if input_element:
                        logger.info(f"入力欄を発見: {selector}")
                        break
                except:
                    continue
            
            if not input_element:
                await self.page.screenshot(path="debug_input_not_found.png")
                raise Exception("入力欄が見つかりません")
            
            # ポップアップ・オーバーレイを閉じる処理
            try:
                # 1. メール配信登録ポップアップの「後で」ボタンをクリック
                later_button_selectors = [
                    'button:has-text("後で")',
                    'button:has-text("Later")',
                    '[aria-label*="後で"]',
                    '[aria-label*="Later"]'
                ]
                
                for selector in later_button_selectors:
                    try:
                        later_button = await self.page.query_selector(selector)
                        if later_button and await later_button.is_visible():
                            await later_button.click()
                            await self.page.wait_for_timeout(1000)
                            logger.info("✅ メール配信ポップアップを閉じました")
                            break
                    except:
                        continue
                
                # 2. オーバーレイ全体を閉じる（バックドロップクリック）
                overlay_backdrop = await self.page.query_selector('.cdk-overlay-backdrop')
                if overlay_backdrop:
                    try:
                        await overlay_backdrop.click()
                        await self.page.wait_for_timeout(500)
                        logger.info("✅ オーバーレイを閉じました")
                    except:
                        pass
                
                # 3. Escキーでポップアップを閉じる（最終手段）
                await self.page.keyboard.press('Escape')
                await self.page.wait_for_timeout(500)
                
            except Exception as e:
                logger.debug(f"ポップアップ処理: {e}")
            
            # 入力欄をクリック
            await input_element.click()
            await self.page.wait_for_timeout(500)
            
            # 既存のテキストをクリア
            await self.page.keyboard.press("Control+a")
            await self.page.wait_for_timeout(500)
            
            # プロンプトを入力
            await input_element.fill(prompt)
            await self.page.wait_for_timeout(1500)
            
            # 送信ボタンをクリック
            send_selectors = [
                'button[data-testid="send-button"]',
                '[data-testid="send-button"]'
            ]
            
            sent = False
            for selector in send_selectors:
                try:
                    send_button = await self.page.query_selector(selector)
                    if send_button and await send_button.is_enabled():
                        await send_button.click()
                        logger.info("送信ボタンをクリックしました")
                        sent = True
                        break
                except:
                    continue
            
            if not sent:
                await input_element.press('Enter')
                logger.info("Enterキーで送信しました")
            
            await self.page.wait_for_timeout(3000)
            
        except Exception as e:
            ErrorHandler.log_error(e, "プロンプト送信")
            if self.page:
                await self.page.screenshot(path="debug_send_error.png")
            raise
    
    async def send_prompt_deepseek(self, prompt: str) -> None:
        """DeepSeekでプロンプトを送信（改善版）"""
        # まずスクリーンショットを撮って状態を確認
        debug_screenshot = f"debug_deepseek_before_input_{datetime.now().strftime('%H%M%S')}.png"
        try:
            await self.page.screenshot(path=debug_screenshot)
            logger.info(f"📸 入力前のスクリーンショット: {debug_screenshot}")
        except:
            pass
        
        # 複数の可能性のあるセレクタを試す
        input_selectors = [
            'textarea[placeholder*="Ask"]',
            'textarea[placeholder*="Type"]',
            'textarea[placeholder*="message"]',
            'textarea[placeholder*="メッセージ"]',
            'textarea[placeholder*="入力"]',
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"]',
            'textarea',
            'input[type="text"]',
        ]
        
        input_element = None
        used_selector = None
        
        # 各セレクタを順番に試す
        for selector in input_selectors:
            try:
                logger.info(f"入力欄を探索中: {selector}")
                element = await self.page.query_selector(selector)
                if element:
                    # 要素が見えているか確認
                    is_visible = await element.is_visible()
                    if is_visible:
                        input_element = element
                        used_selector = selector
                        logger.info(f"✅ 入力欄を発見: {selector}")
                        break
                    else:
                        logger.info(f"要素は存在するが非表示: {selector}")
            except Exception as e:
                logger.debug(f"セレクタ {selector} でエラー: {e}")
                continue
        
        if not input_element:
            # 全セレクタで失敗した場合
            await self.page.screenshot(path="debug_deepseek_input_not_found.png")
            logger.error("❌ DeepSeek入力欄が見つかりません")
            logger.error("以下を確認してください：")
            logger.error("1. ログインが完了していますか？")
            logger.error("2. チャット画面が表示されていますか？")
            logger.error("3. Cloudflareの検証は完了しましたか？")
            
            # ページのHTMLをデバッグ出力
            page_content = await self.page.evaluate('document.body.innerText')
            logger.info(f"ページ内容（先頭500文字）:\n{page_content[:500]}")
            
            # 手動介入を促す
            logger.info("\n手動で入力欄が見えるまで操作してください")
            input("入力欄が表示されたら、Enterキーを押してください: ")
            
            # 再度探す
            for selector in input_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        input_element = element
                        used_selector = selector
                        logger.info(f"✅ 入力欄を発見（2回目）: {selector}")
                        break
                except:
                    continue
            
            if not input_element:
                raise Exception("入力欄が見つかりません（2回目の試行後）")
        
        # 入力欄にフォーカス
        await input_element.click()
        await self.page.wait_for_timeout(500)
        
        # プロンプトを入力
        await input_element.fill(prompt)
        await self.page.wait_for_timeout(1500)
        
        # 送信ボタンを探す
        send_button = None
        send_selectors = [
            'button[type="submit"]',
            'button[aria-label*="Send"]',
            'button[aria-label*="送信"]',
            'button:has-text("送信")',
            'button:has-text("Send")',
            'button svg',  # アイコンボタン
        ]
        
        for selector in send_selectors:
            try:
                btn = await self.page.query_selector(selector)
                if btn and await btn.is_visible() and await btn.is_enabled():
                    send_button = btn
                    logger.info(f"送信ボタンを発見: {selector}")
                    break
            except:
                continue
        
        if send_button:
            await send_button.click()
            logger.info("✅ DeepSeek送信ボタンをクリックしました")
        else:
            # ボタンが見つからない場合はEnterキーで送信
            logger.info("送信ボタンが見つからないため、Enterキーで送信します")
            await input_element.press("Enter")
            logger.info("✅ Enterキーで送信しました")
        
        await self.page.wait_for_timeout(3000)
    
    async def wait_for_text_generation(self, max_wait: int = 120) -> bool:
        """テキスト生成完了まで待機"""
        try:
            if not self.page:
                return False
            logger.info("テキスト生成を待機中...")
            start_time = time.time()
            check_interval = 2
            await self.page.wait_for_timeout(5000)
            while time.time() - start_time < max_wait:
                await self.page.wait_for_timeout(check_interval * 1000)
                elapsed = int(time.time() - start_time)
                is_complete = await self.page.evaluate('''
                    () => {
                        const allButtons = document.querySelectorAll('button');
                        for (const btn of allButtons) {
                            const text = btn.textContent || '';
                            const ariaLabel = btn.getAttribute('aria-label') || '';
                            if (text.includes('再生成') || text.includes('Regenerate') ||
                                ariaLabel.includes('再生成') || ariaLabel.includes('Regenerate')) {
                                return true;
                            }
                        }
                        const sendButtons = document.querySelectorAll('[data-testid="send-button"], button[type="submit"]');
                        for (const btn of sendButtons) {
                            if (!btn.disabled && !btn.hasAttribute('disabled')) {
                                return true;
                            }
                        }
                        const loadingElements = document.querySelectorAll('[data-testid="loading"], .loading, .spinner');
                        if (loadingElements.length === 0) {
                            return true;
                        }
                        return false;
                    }
                ''')
                if is_complete:
                    logger.info(f"✅ テキスト生成完了を検出")
                    await self.page.wait_for_timeout(2000)
                    return True
                if elapsed % 10 == 0 and elapsed > 0:
                    logger.info(f"⏳ 待機中... {elapsed}秒経過")
            logger.warning(f"⏰ タイムアウト（{max_wait}秒）")
            return False
        except Exception as e:
            ErrorHandler.log_error(e, "テキスト生成待機")
            return False
    
    async def send_prompt_and_wait(self, prompt: str, max_wait: int = 120) -> bool:
        """
        プロンプト送信と応答待機を一括処理（推奨インターフェース）
        
        Args:
            prompt: 送信するプロンプト
            max_wait: 最大待機時間（秒）
            
        Returns:
            bool: 成功時 True
        """
        try:
            # プロンプト送信
            await self.send_prompt(prompt)
            
            # 応答待機
            success = await self.wait_for_text_generation(max_wait)
            
            if success:
                logger.info("✅ プロンプト送信と応答待機が完了しました")
            else:
                logger.warning("⚠️ プロンプト送信は成功しましたが、応答待機がタイムアウトしました")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ プロンプト送信と待機中にエラー: {e}")
            return False

    
    async def extract_latest_text_response(self) -> str:
        """最新のテキスト応答を抽出（サービス自動判別版）"""
        try:
            if self.service == "deepseek":
                return await self.extract_latest_text_response_deepseek()
            else:
                return await self.extract_latest_text_response_gemini()
        except Exception as e:
            ErrorHandler.log_error(e, "テキスト抽出")
            return None
    
    async def extract_latest_text_response_gemini(self) -> str:
        """Geminiの最新のテキスト応答を抽出（コード完全性検証ロジック修正版）"""
        try:
            logger.info("=" * 60)
            logger.info("★★★ Geminiテキスト抽出開始 ★★★")
            logger.info("=" * 60)
            
            all_results = {}
            
            # 方法1: モデルメッセージのデータ属性から取得
            try:
                method1_text = await self.page.evaluate('''() => {
                    const modelMessages = document.querySelectorAll('[data-message-author="model"]');
                    if (modelMessages.length === 0) return null;
                    
                    const latestMessage = modelMessages[modelMessages.length - 1];
                    return latestMessage.innerText || latestMessage.textContent || '';
                }''')
                all_results['方法1'] = method1_text
                logger.info(f"方法1結果: {len(method1_text) if method1_text else 0}文字")
            except Exception as e:
                logger.debug(f"方法1失敗: {e}")
                all_results['方法1'] = None

            # 方法2: マークダウンコンテンツから取得
            try:
                method2_text = await self.page.evaluate('''() => {
                    const markdownContainers = document.querySelectorAll('[class*="markdown"]');
                    if (markdownContainers.length === 0) return null;
                    
                    let longest = '';
                    for (const container of markdownContainers) {
                        const text = container.innerText || container.textContent || '';
                        if (text.length > longest.length) {
                            longest = text;
                        }
                    }
                    return longest;
                }''')
                all_results['方法2'] = method2_text
                logger.info(f"方法2結果: {len(method2_text) if method2_text else 0}文字")
            except Exception as e:
                logger.debug(f"方法2失敗: {e}")
                all_results['方法2'] = None

            # 方法3: メッセージクラスから取得
            try:
                method3_text = await self.page.evaluate('''() => {
                    const messages = document.querySelectorAll('[class*="message"]');
                    if (messages.length === 0) return null;
                    
                    let modelTexts = [];
                    for (const msg of messages) {
                        const text = msg.innerText || msg.textContent || '';
                        // ユーザーメッセージを除外（短いまたは特定のパターン）
                        if (text.length > 100 && 
                            !text.includes('あなたは経験豊富な') &&
                            !text.includes('【あなたの役割】') &&
                            !text.includes('【執筆依頼】')) {
                            modelTexts.push(text);
                        }
                    }
                    return modelTexts.length > 0 ? modelTexts[modelTexts.length - 1] : null;
                }''')
                all_results['方法3'] = method3_text
                logger.info(f"方法3結果: {len(method3_text) if method3_text else 0}文字")
            except Exception as e:
                logger.debug(f"方法3失敗: {e}")
                all_results['方法3'] = None
            
            # 優先順位で選択（コード完全性検証を緩和）
            priority_order = ['方法1', '方法2', '方法3']
            best_result = None
            best_method = None
            
            for method in priority_order:
                if method in all_results and all_results[method] and len(all_results[method]) > 100:
                    text = all_results[method]
                    
                    # プロンプトが混入していないか最終チェック
                    if ('あなたは経験豊富な' in text or 
                        '【あなたの役割】' in text or
                        '【執筆依頼】' in text):
                        logger.warning(f"{method}にプロンプトが混入 - スキップ")
                        continue
                    
                    # コードブロック検証（緩和版）
                    validation_result = self._validate_code_block_completeness_enhanced(text)
                    
                    if validation_result['is_complete']:
                        logger.info(f"✅ {method}: 完全な応答を検出")
                        best_result = text.strip()
                        best_method = method
                        break
                    else:
                        # 不完全でも長文の場合は警告を出して採用する
                        if len(text) > 1500:  # 長文の場合は許容
                            logger.warning(f"⚠️ {method}: 不完全だが長文のため採用 - {validation_result['reason']}")
                            best_result = text.strip()
                            best_method = method
                            break
                        else:
                            logger.warning(f"⚠️ {method}: 不完全な応答 - {validation_result['reason']}")
            
            if best_result:
                logger.info(f"\n🎯 採用: {best_method} ({len(best_result)}文字)")
                logger.info(f"先頭200文字:\n{best_result[:200]}")
                return best_result
            
            # すべて失敗した場合でも、最長のテキストを返す（最終手段）
            fallback_text = None
            for method in priority_order:
                if method in all_results and all_results[method] and len(all_results[method]) > 500:
                    fallback_text = all_results[method]
                    logger.warning(f"⚠️ フォールバック採用: {method} ({len(fallback_text)}文字)")
                    break
            
            if fallback_text:
                return fallback_text.strip()
            
            # 本当に何も取得できない場合
            logger.error("\n❌ 全方法失敗 - Geminiの応答が取得できませんでした")
            
            # デバッグ用: ページの構造を確認
            page_structure = await self.page.evaluate('''() => {
                return {
                    messageCount: document.querySelectorAll('[class*="message"]').length,
                    modelMessages: document.querySelectorAll('[data-message-author="model"]').length,
                    markdownContainers: document.querySelectorAll('[class*="markdown"]').length
                };
            }''')
            logger.info(f"ページ構造: {page_structure}")
            
            return None
                    
        except Exception as e:
            logger.error(f"❌ 抽出全体エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        
    def _validate_code_block_completeness_enhanced(self, text: str) -> Dict:
        """
        コードブロックの完全性を検証(緩和版 - 専門文書・長文対応強化)
            
        Returns:
            Dict: {
                'is_complete': bool,
                'reason': str,
                'details': str,
                'incomplete_blocks': List[Dict]
            }
        """
        try:
            # コードブロック(```)のペアチェック(主要チェック)
            code_fence_pattern = r'```(\w+)?\n(.*?)```'
            code_blocks = re.findall(code_fence_pattern, text, re.DOTALL)
                
            # 開始タグのみで終了タグがないパターンを検出
            open_fences = re.findall(r'```(\w+)?(?![\s\S]*?```)', text, re.DOTALL)
                
            if open_fences:
                # 閉じられていないコードブロックを検出
                incomplete_blocks = []
                for lang in open_fences:
                    # 該当箇所のスニペットを取得
                    pattern = f'```{lang}' if lang else '```'
                    idx = text.find(pattern)
                    snippet = text[idx:idx+100] + '...' if idx != -1 else 'N/A'
                        
                    incomplete_blocks.append({
                        'type': f'code({lang})' if lang else 'code(unknown)',
                        'snippet': snippet
                    })
                    
                return {
                    'is_complete': False,
                    'reason': 'コードブロックが閉じられていません',
                    'details': f'{len(open_fences)}個の未閉じブロックを検出',
                    'incomplete_blocks': incomplete_blocks
                }
                
            # PHPコードの完全性チェック
            if '<?php' in text:
                php_blocks = re.findall(r'```php\n(.*?)```', text, re.DOTALL)
                for php_code in php_blocks:
                    # 関数定義の開始と終了の波括弧の数をチェック
                    open_braces = php_code.count('{')
                    close_braces = php_code.count('}')
                        
                    if open_braces > close_braces:
                        # 最後の10行を取得
                        last_lines = '\n'.join(php_code.split('\n')[-10:])
                            
                        return {
                            'is_complete': False,
                            'reason': 'PHPコードの波括弧が閉じられていません',
                            'details': f'開始: {open_braces}, 終了: {close_braces}',
                            'incomplete_blocks': [{
                                'type': 'php',
                                'snippet': f'...最後の10行:\n{last_lines}'
                            }]
                        }
                
            # JSONコードの完全性チェック
            json_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
            for json_code in json_blocks:
                try:
                    json.loads(json_code)
                except json.JSONDecodeError as e:
                    return {
                        'is_complete': False,
                        'reason': 'JSONコードが不正です',
                        'details': f'JSONエラー: {str(e)}',
                        'incomplete_blocks': [{
                            'type': 'json',
                            'snippet': json_code[-200:] if len(json_code) > 200 else json_code
                        }]
                    }
                
            # ========================================
            # 🔧 Pydanticモデル定義の検証（新規追加）
            # ========================================
            if 'from pydantic import' in text or 'class ' in text and 'BaseModel' in text:
                # Pydanticモデル定義のクラス構造チェック
                pydantic_class_pattern = r'class\s+(\w+)\(BaseModel\):(.*?)(?=\nclass\s|\Z)'
                pydantic_classes = re.findall(pydantic_class_pattern, text, re.DOTALL)
                    
                for class_name, class_body in pydantic_classes:
                    # クラス本体が空でないか確認
                    if not class_body.strip():
                        return {
                            'is_complete': False,
                            'reason': f'Pydanticモデル {class_name} の定義が空です',
                            'details': 'クラス本体にフィールド定義が必要',
                            'incomplete_blocks': [{
                                'type': 'pydantic',
                                'snippet': f'class {class_name}(BaseModel): ...'
                            }]
                        }
                        
                    # フィールド定義が少なくとも1つあるか確認
                    field_pattern = r'^\s+\w+:\s*\w+'
                    if not re.search(field_pattern, class_body, re.MULTILINE):
                        return {
                            'is_complete': False,
                            'reason': f'Pydanticモデル {class_name} にフィールド定義がありません',
                            'details': 'モデルには少なくとも1つのフィールドが必要',
                            'incomplete_blocks': [{
                                'type': 'pydantic',
                                'snippet': class_body[:200]
                            }]
                        }
                
            # ========================================
            # 🔧 OpenAPIスキーマの検証（新規追加）
            # ========================================
            if 'openapi:' in text.lower() or '"openapi"' in text.lower():
                # OpenAPI/Swaggerスキーマの基本構造をチェック
                required_openapi_keys = ['openapi', 'info', 'paths']
                    
                # YAMLまたはJSON形式の検出
                if 'openapi:' in text:
                    # YAML形式の検証
                    for key in required_openapi_keys:
                        if f'{key}:' not in text:
                            return {
                                'is_complete': False,
                                'reason': f'OpenAPIスキーマに必須キー "{key}" がありません',
                                'details': 'OpenAPIスキーマには openapi, info, paths が必要',
                                'incomplete_blocks': [{
                                    'type': 'openapi_yaml',
                                    'snippet': text[:300]
                                }]
                            }
                else:
                    # JSON形式の検証
                    try:
                        # JSON抽出試行
                        json_match = re.search(r'\{.*\}', text, re.DOTALL)
                        if json_match:
                            openapi_json = json.loads(json_match.group(0))
                            for key in required_openapi_keys:
                                if key not in openapi_json:
                                    return {
                                        'is_complete': False,
                                        'reason': f'OpenAPIスキーマに必須キー "{key}" がありません',
                                        'details': 'OpenAPIスキーマには openapi, info, paths が必要',
                                        'incomplete_blocks': [{
                                            'type': 'openapi_json',
                                            'snippet': json_match.group(0)[:300]
                                        }]
                                    }
                    except (json.JSONDecodeError, AttributeError):
                        pass  # JSON形式でない場合はスキップ
                
            # ========================================
            # 🔧 文章の突然の終了チェックを大幅緩和（専門文書対応）
            # ========================================
            text_stripped = text.strip()
            if text_stripped:
                last_char = text_stripped[-1]
                    
                # 専門文書や技術文書の終了パターンを拡張
                japanese_section_endings = [
                    '項', '章', '目', '節', '条', '款', '点',  # 既存
                    '。', '）', ')', '}', ']', '`', '>', '"',  # 新規追加
                    '了', '成', '定', '明', '示', '用', '理'   # 専門用語末尾
                ]
                    
                # 厳格な終了文字リスト（これらで終わればOK）
                strict_end_chars = ['.', '。', '!', '!', '?', '?', '`', '}', ']', ')']
                    
                if (last_char not in strict_end_chars and 
                    last_char not in japanese_section_endings and
                    not text_stripped.endswith('```')):
                        
                    # ========================================
                    # 🔧 長文・専門文書の場合は大幅に緩和（新ロジック）
                    # ========================================
                        
                    # 条件1: 3000文字以上の超長文は終了文字をチェックしない
                    if len(text_stripped) > 3000:
                        logger.info(f"✅ 超長文({len(text_stripped)}文字)のため終了文字チェックをスキップ")
                        return {
                            'is_complete': True,
                            'reason': '超長文のため終了文字チェックを免除',
                            'details': f'文字数: {len(text_stripped)}, 最後の文字: {last_char}'
                        }
                        
                    # 条件2: 2000文字以上でコードブロックが3個以上ある場合は許容
                    if len(text_stripped) > 2000 and len(code_blocks) >= 3:
                        logger.info(f"✅ 長文({len(text_stripped)}文字)かつコードブロック{len(code_blocks)}個のため許容")
                        return {
                            'is_complete': True,
                            'reason': '長文かつ多数のコードブロックを含むため許容',
                            'details': f'文字数: {len(text_stripped)}, コードブロック数: {len(code_blocks)}'
                        }
                        
                    # 条件3: Pydanticモデルやスキーマ定義を含む場合は許容
                    if ('from pydantic import' in text or 
                        'class ' in text and 'BaseModel' in text or
                        'openapi:' in text.lower()):
                        logger.info("✅ 専門的な技術文書(Pydantic/OpenAPI)のため許容")
                        return {
                            'is_complete': True,
                            'reason': '専門的な技術文書として許容',
                            'details': 'Pydanticモデルまたはスキーマ定義を含む'
                        }
                        
                    # 条件4: 1500文字以上で「まとめ」「結論」「以上」などの締めくくり表現がある場合
                    conclusion_patterns = [
                        'まとめ', '結論', '以上', '完了', '終わり',
                        'summary', 'conclusion', 'end', 'complete'
                    ]
                    if len(text_stripped) > 1500 and any(pattern in text_stripped[-500:].lower() for pattern in conclusion_patterns):
                        logger.info("✅ 長文で締めくくり表現を含むため許容")
                        return {
                            'is_complete': True,
                            'reason': '長文で締めくくり表現を含む',
                            'details': f'文字数: {len(text_stripped)}'
                        }
                        
                    # 上記条件に該当しない短文は不完全と判定
                    if len(text_stripped) < 1500:
                        last_50_chars = text_stripped[-50:]
                            
                        return {
                            'is_complete': False,
                            'reason': '文章が途中で切れている可能性があります',
                            'details': f'最後の文字: "{last_char}"',
                            'incomplete_blocks': [{
                                'type': 'text',
                                'snippet': f'...最後の50文字: {last_50_chars}'
                            }]
                        }
                    else:
                        # 1500文字以上だが条件に該当しない場合は警告のみで許容
                        logger.warning(f"⚠️ 長文({len(text_stripped)}文字)だが終了文字が不明瞭: '{last_char}'")
                        return {
                            'is_complete': True,
                            'reason': '長文のため警告付きで許容',
                            'details': f'文字数: {len(text_stripped)}, 最後の文字: {last_char}'
                        }
                
            # すべてのチェックをパス
            return {
                'is_complete': True,
                'reason': 'すべての検証に合格',
                'details': f'コードブロック数: {len(code_blocks)}'
            }
                
        except Exception as e:
            logger.error(f"コード完全性検証エラー: {e}")
            # エラー時は安全側に倒して不完全とみなす
            return {
                'is_complete': False,
                'reason': '検証処理でエラー発生',
                'details': str(e),
                'incomplete_blocks': []
            }
    
    async def extract_latest_text_response_deepseek(self) -> str:
        """DeepSeekの最新のテキスト応答を抽出（改良版）"""
        try:
            logger.info("=" * 60)
            logger.info("★★★ DeepSeekテキスト抽出開始 ★★★")
            logger.info("=" * 60)
            
            # DeepSeek特有のセレクタで応答を取得
            response_text = await self.page.evaluate('''() => {
                // メッセージコンテナを探す
                const messages = document.querySelectorAll('[class*="message"], [class*="chat"], div[role="article"]');
                let longest = '';
                
                for (const msg of messages) {
                    const text = msg.innerText || '';
                    // ユーザーのメッセージは除外
                    if (text.length > 100 && text.length > longest.length) {
                        // システムやアシスタントのメッセージのみ
                        const isUserMessage = msg.querySelector('[class*="user"]') || 
                                            msg.classList.toString().includes('user');
                        if (!isUserMessage) {
                            longest = text;
                        }
                    }
                }
                
                if (!longest) {
                    // フォールバック: 最後の長いdivを取得
                    const divs = document.querySelectorAll('div');
                    for (const d of divs) {
                        const t = d.innerText || '';
                        if (t.length > longest.length && t.length > 200) {
                            longest = t;
                        }
                    }
                }
                
                return longest;
            }''')
            
            if response_text and len(response_text) > 50:
                logger.info(f"✅ DeepSeek応答抽出成功: {len(response_text)}文字")
                logger.info(f"先頭500文字:\n{response_text[:500]}")
                
                # 検証を実行（緩和版）
                validation_result = self._validate_code_block_completeness_enhanced(response_text)
                
                if not validation_result['is_complete'] and len(response_text) > 1500:
                    logger.warning(f"⚠️ DeepSeek応答不完全だが長文のため採用: {validation_result['reason']}")
                    # 長文の場合は不完全でも採用
                    return response_text.strip()
                elif validation_result['is_complete']:
                    logger.info("✅ DeepSeek応答検証合格")
                    return response_text.strip()
                else:
                    logger.warning(f"⚠️ DeepSeek応答不完全: {validation_result['reason']}")
                    return response_text.strip()  # 不完全でも返す（以前はNoneを返していた）
            else:
                logger.error("❌ DeepSeek応答が見つかりません")
                return None
                
        except Exception as e:
            logger.error(f"❌ DeepSeek抽出エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    # === 既存のメソッドは変更なし（extract_json_from_text など） ===

    # 旧バージョンのメソッドを新しいメソッドで置き換えるための互換性レイヤー
    def _validate_code_block_completeness(self, text: str) -> Dict:
        """
        旧バージョンのメソッド - 新しいメソッドを呼び出す
        （既存コードとの互換性維持のため）
        """
        return self._validate_code_block_completeness_enhanced(text)

    def extract_json_from_text(self, text: str) -> str:
        """テキストからJSON部分を抽出"""
        try:
            if not text:
                return None
                
            # パターン1: ```json ... ``` に囲まれたJSON
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                return json_match.group(1).strip()
            
            # パターン2: 単純なJSONオブジェクトの抽出
            json_match = re.search(r'^\s*(\{.*\})\s*$', text, re.DOTALL)
            if json_match:
                return json_match.group(1).strip()
            
            # パターン3: 先頭からJSONを探す
            start_idx = text.find('{')
            if start_idx != -1:
                # { から始めて、対応する } までを探す
                brace_count = 0
                for i, char in enumerate(text[start_idx:]):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            potential_json = text[start_idx:start_idx+i+1]
                            try:
                                json.loads(potential_json)
                                return potential_json.strip()
                            except:
                                continue
            return None
        except Exception as e:
            logger.error(f"JSON抽出エラー: {e}")
            return None
        
    
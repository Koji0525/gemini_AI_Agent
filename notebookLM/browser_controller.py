# browser_controller.py
"""ブラウザ制御クラス（分割リファクタリング版）"""
import asyncio
from pathlib import Path
from typing import Optional, Dict
import logging

from browser_lifecycle import BrowserLifecycleManager
from brower_cookie_and_session import CookieSessionManager  # ファイル名修正
from browser_ai_chat_agent import AIChatAgent
from browser_wp_session_manager import WPSessionManager
from config_utils import config, ErrorHandler

logger = logging.getLogger(__name__)

class BrowserController:
    """ブラウザ制御ファサードクラス"""
    
    def __init__(self, download_folder: Path, mode: str = "image", service: str = "google", credentials: Dict = None):
        self.download_folder = download_folder
        self.mode = mode
        self.service = service.lower()
        self.credentials = credentials or {}
        
        # 設定ファイルのパス
        self.cookies_file = Path(config.COOKIES_FILE) if config.COOKIES_FILE else None
        self.browser_data_dir = Path(config.BROWSER_DATA_DIR) if config.BROWSER_DATA_DIR else None
        self.wp_cookies_file = Path(config.BROWSER_DATA_DIR) / "wp_cookies.json" if config.BROWSER_DATA_DIR else None
        
        # マネージャーの初期化（setup_browserで完全初期化）
        self.lifecycle_manager: Optional[BrowserLifecycleManager] = None
        self.session_manager: Optional[CookieSessionManager] = None
        self.ai_agent: Optional[AIChatAgent] = None
        self.wp_manager: Optional[WPSessionManager] = None
    
    async def setup_browser(self) -> None:
        """ブラウザのセットアップ - すべてのマネージャーを初期化"""
        try:
            # ライフサイクルマネージャーの初期化とセットアップ
            self.lifecycle_manager = BrowserLifecycleManager(
                browser_data_dir=self.browser_data_dir,
                download_folder=self.download_folder
            )
            await self.lifecycle_manager.setup_browser()
            
            # セッションマネージャーの初期化
            self.session_manager = CookieSessionManager(
                context=self.lifecycle_manager.context,
                cookies_file=self.cookies_file
            )
            
            # AIチャットエージェントの初期化
            self.ai_agent = AIChatAgent(
                page=self.lifecycle_manager.page,
                service=self.service,
                credentials=self.credentials
            )
            
            # WordPressセッションマネージャーの初期化
            self.wp_manager = WPSessionManager(
                context=self.lifecycle_manager.context,
                wp_cookies_file=self.wp_cookies_file
            )
            
            logger.info(f"✅ ブラウザ制御ファサード初期化完了（サービス: {self.service}）")
            
        except Exception as e:
            ErrorHandler.log_error(e, "ブラウザファサードセットアップ")
            raise
    
    # プロパティの委譲
    @property
    def context(self):
        return self.lifecycle_manager.context if self.lifecycle_manager else None
    
    @property
    def page(self):
        return self.lifecycle_manager.page if self.lifecycle_manager else None
    
    @property
    def wp_page(self):
        return self.wp_manager.wp_page if self.wp_manager else None
    
    @property
    def is_logged_in(self):
        return self.wp_manager.is_logged_in if self.wp_manager else False
    
    # AIチャット関連メソッドの委譲
    async def navigate_to_gemini(self) -> None:
        """Geminiにナビゲート - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.navigate_to_gemini()
    
    async def navigate_to_deepseek(self) -> None:
        """DeepSeekにナビゲート - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.navigate_to_deepseek()
    
    async def send_prompt(self, prompt: str) -> None:
        """プロンプト送信 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.send_prompt(prompt)
    
    async def wait_for_text_generation(self, max_wait: int = 180) -> bool:
        """
        テキスト生成完了を待機（強化版）
            
        Args:
            max_wait: 最大待機時間（秒）
                
        Returns:
            bool: 生成完了フラグ
        """
        try:
            logger.info(f"⏱️ テキスト生成待機開始（最大{max_wait}秒）")
                
            start_time = asyncio.get_event_loop().time()
            check_interval = 2.0  # 2秒ごとにチェック
            last_length = 0
            stable_count = 0
            required_stable = 3  # 3回連続で変化なしで完了と判定
                
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                    
                if elapsed > max_wait:
                    logger.warning(f"⏱️ タイムアウト（{max_wait}秒）")
                    return False
                    
                # 現在のテキスト長を取得
                try:
                    current_text = await self._get_current_text_quick()
                    current_length = len(current_text)
                        
                    # テキストが増えているか確認
                    if current_length > last_length:
                        logger.info(f"📝 生成中: {current_length}文字（経過: {int(elapsed)}秒）")
                        last_length = current_length
                        stable_count = 0
                    else:
                        # 長さが変わらない
                        stable_count += 1
                        logger.info(f"⏸️ 安定: {stable_count}/{required_stable}（{current_length}文字）")
                            
                        if stable_count >= required_stable:
                            logger.info(f"✅ 生成完了（{current_length}文字、{int(elapsed)}秒）")
                            return True
                    
                except Exception as e:
                    logger.warning(f"⚠️ チェックエラー: {e}")
                    
                # 待機
                await asyncio.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"❌ 待機エラー: {e}")
            return False
    
    async def extract_latest_text_response(self, allow_partial: bool = True) -> Optional[str]:
        """
        最新のテキスト応答を抽出（強化版）
        
        Args:
            allow_partial: 部分的な応答も許可するか
            
        Returns:
            Optional[str]: 抽出されたテキスト
        """
        try:
            logger.info("="*60)
            logger.info("★★★ Gemini応答抽出開始（強化版） ★★★")
            logger.info("="*60)
            
            results = {}
            
            # ============================================================
            # === 方法1: model-response-text クラス ===
            # ============================================================
            try:
                message_divs = await self.page.query_selector_all('div.model-response-text')
                if message_divs:
                    last_message = message_divs[-1]
                    text1 = await last_message.inner_text()
                    if text1 and len(text1) > 100:
                        results['method1'] = text1
                        logger.info(f"✅ 方法1成功: {len(text1)}文字")
            except Exception as e:
                logger.warning(f"⚠️ 方法1失敗: {e}")
            
            # ============================================================
            # === 方法2: markdown-container クラス ===
            # ============================================================
            try:
                markdown_divs = await self.page.query_selector_all('div.markdown-container')
                if markdown_divs:
                    last_markdown = markdown_divs[-1]
                    text2 = await last_markdown.inner_text()
                    if text2 and len(text2) > 100:
                        results['method2'] = text2
                        logger.info(f"✅ 方法2成功: {len(text2)}文字")
            except Exception as e:
                logger.warning(f"⚠️ 方法2失敗: {e}")
            
            # ============================================================
            # === 方法3: message-content クラス ===
            # ============================================================
            try:
                content_divs = await self.page.query_selector_all('div.message-content')
                if content_divs:
                    # 最後のメッセージコンテンツ
                    for div in reversed(content_divs):
                        text3 = await div.inner_text()
                        if text3 and len(text3) > 100 and 'model-response' not in text3.lower():
                            results['method3'] = text3
                            logger.info(f"✅ 方法3成功: {len(text3)}文字")
                            break
            except Exception as e:
                logger.warning(f"⚠️ 方法3失敗: {e}")
            
            # ============================================================
            # === 方法4: data-test-id 属性 ===
            # ============================================================
            try:
                test_divs = await self.page.query_selector_all('[data-test-id*="conversation-turn"]')
                if test_divs:
                    last_turn = test_divs[-1]
                    text4 = await last_turn.inner_text()
                    if text4 and len(text4) > 100:
                        results['method4'] = text4
                        logger.info(f"✅ 方法4成功: {len(text4)}文字")
            except Exception as e:
                logger.warning(f"⚠️ 方法4失敗: {e}")
            
            # ============================================================
            # === 結果選択（最長のものを選択） ===
            # ============================================================
            if not results:
                logger.error("❌ 全方法失敗 - 応答が取得できませんでした")
                
                # デバッグ情報
                try:
                    page_content = await self.page.content()
                    logger.info(f"📄 ページ長: {len(page_content)}文字")
                except:
                    pass
                
                return None
            
            # 最も長いテキストを選択
            best_method = max(results.items(), key=lambda x: len(x[1]))
            selected_text = best_method[1]
            
            logger.info(f"✅ 最適結果選択: {best_method[0]} ({len(selected_text)}文字)")
            
            # ============================================================
            # === 品質チェック（緩和版） ===
            # ============================================================
            warnings = []
            
            # 長さチェック
            if len(selected_text) < 500:
                warnings.append(f'短い応答（{len(selected_text)}文字）')
            
            # コードブロックチェック（緩和）
            if allow_partial:
                # 部分的なコードブロックも許可
                if '```' in selected_text:
                    open_count = selected_text.count('```')
                    if open_count % 2 != 0:
                        warnings.append('コードブロック未完結（許可）')
            else:
                # 厳密なチェック
                open_blocks = selected_text.count('```')
                if open_blocks % 2 != 0:
                    warnings.append('コードブロック未完結')
            
            # 警告表示
            if warnings:
                logger.warning("⚠️ 品質警告:")
                for w in warnings:
                    logger.warning(f"  - {w}")
            
            # 部分応答も許可する場合は、警告があっても返す
            if allow_partial:
                logger.info("✅ 部分応答を許可 - そのまま返却")
                return selected_text
            
            # 厳密モードの場合、重大な問題があればNone
            if len(selected_text) < 100:
                logger.error("❌ 応答が短すぎる（100文字未満）")
                return None
            
            logger.info("="*60)
            logger.info(f"✅ 応答抽出完了: {len(selected_text)}文字")
            logger.info("="*60)
            
            return selected_text
        
        except Exception as e:
            logger.error(f"❌ 応答抽出エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def send_prompt_and_wait(self, prompt: str, max_wait: int = 120) -> bool:
        """プロンプト送信と待機 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        return await self.ai_agent.send_prompt_and_wait(prompt, max_wait)
    
    # クッキー管理の委譲
    async def save_cookies(self) -> None:
        """クッキー保存 - セッションマネージャーに委譲"""
        if not self.session_manager:
            raise Exception("セッションマネージャーが初期化されていません")
        await self.session_manager.save_cookies()
    
    async def load_cookies(self) -> bool:
        """クッキー読み込み - セッションマネージャーに委譲"""
        if not self.session_manager:
            logger.warning("セッションマネージャーが初期化されていません")
            return False
        return await self.session_manager.load_cookies()
    
    # WordPress関連メソッドの委譲
    async def initialize_wp_session(self, auth_module=None) -> bool:
        """WordPressセッション初期化 - WPマネージャーに委譲"""
        if not self.wp_manager:
            raise Exception("WordPressマネージャーが初期化されていません")
        return await self.wp_manager.initialize_wp_session(auth_module)
    
    async def save_wordpress_cookies(self, wp_url: str) -> bool:
        """WordPressクッキー保存 - WPマネージャーに委譲"""
        if not self.wp_manager:
            raise Exception("WordPressマネージャーが初期化されていません")
        return await self.wp_manager.save_wordpress_cookies(wp_url)
    
    async def load_wordpress_cookies(self, wp_url: str) -> bool:
        """WordPressクッキー読み込み - WPマネージャーに委譲"""
        if not self.wp_manager:
            raise Exception("WordPressマネージャーが初期化されていません")
        return await self.wp_manager.load_wordpress_cookies(wp_url)
    
    # クリーンアップの委譲
    async def cleanup(self) -> None:
        """リソースクリーンアップ - ライフサイクルマネージャーに委譲"""
        # WordPressセッションを閉じる
        if self.wp_manager:
            await self.wp_manager.close_wp_session()
        
        # メインのブラウザリソースをクリーンアップ
        if self.lifecycle_manager:
            await self.lifecycle_manager.cleanup()
    
    # ユーティリティメソッド
    async def save_text_to_file(self, text: str, filename: str) -> bool:
        """テキストファイル保存 - ユーティリティとして維持"""
        try:
            save_path = self.download_folder / filename
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)
            if save_path.exists():
                file_size = save_path.stat().st_size
                logger.info(f"✅ テキスト保存成功: {filename} ({file_size:,} bytes)")
                return True
            else:
                logger.error(f"❌ テキスト保存失敗: {filename}")
                return False
        except Exception as e:
            ErrorHandler.log_error(e, "テキストファイル保存")
            return False
    
    # 後方互換性のためのメソッド
    async def _is_browser_alive(self) -> bool:
        """ブラウザ生存確認 - ライフサイクルマネージャーに委譲"""
        if not self.lifecycle_manager:
            return False
        return await self.lifecycle_manager._is_browser_alive()
    
    async def handle_welcome_screens(self) -> None:
        """ウェルカム画面処理 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.handle_welcome_screens()
    
    async def ensure_normal_chat_mode(self) -> None:
        """通常チャットモード確認 - AIエージェントに委譲"""
        if not self.ai_agent:
            raise Exception("AIエージェントが初期化されていません")
        await self.ai_agent.ensure_normal_chat_mode()
    
    # 非推奨メソッド（後方互換性のため）
    async def _wait_for_generation_complete(self, max_wait: int = 120) -> bool:
        """非推奨メソッド - 後方互換性のため維持"""
        logger.warning("⚠️ 非推奨メソッド _wait_for_generation_complete が呼び出されました")
        return await self.wait_for_text_generation(max_wait)
    
async def ensure_browser_ready(self) -> bool:
    """
    ブラウザの準備完了を確認（セッション管理強化版）
        
    Returns:
        bool: 準備完了フラグ
    """
    try:
        # ブラウザが起動しているか確認
        if not self.browser:
            logger.error("❌ ブラウザが起動していません")
            return False
            
        # コンテキストが有効か確認
        if not self.context:
            logger.error("❌ ブラウザコンテキストがありません")
            return False
            
        # ページが有効か確認
        if not self.page:
            logger.error("❌ ページがありません")
            return False
            
        # ページが閉じられていないか確認
        try:
            is_closed = self.page.is_closed()
            if is_closed:
                logger.error("❌ ページが閉じられています - 再作成")
                self.page = await self.context.new_page()
                await self.page.goto('https://gemini.google.com/app', wait_until='networkidle')
                await asyncio.sleep(3)
                logger.info("✅ ページを再作成しました")
        except Exception as e:
            logger.warning(f"⚠️ ページ状態確認エラー: {e}")
            
        # Geminiページにいるか確認
        current_url = self.page.url
        if 'gemini.google.com' not in current_url:
            logger.warning(f"⚠️ Geminiページではありません: {current_url}")
            logger.info("🔄 Geminiページに移動中...")
            await self.page.goto('https://gemini.google.com/app', wait_until='networkidle')
            await asyncio.sleep(3)
            
        logger.info("✅ ブラウザ準備完了")
        return True
        
    except Exception as e:
        logger.error(f"❌ ブラウザ準備確認エラー: {e}")
        return False
    
async def send_prompt(self, prompt: str) -> bool:
    """
    プロンプト送信（セッション管理付き）
        
    Args:
        prompt: 送信するプロンプト
            
    Returns:
        bool: 送信成功フラグ
    """
    try:
        # ブラウザ準備確認
        if not await self.ensure_browser_ready():
            logger.error("❌ ブラウザが準備できていません")
            return False
            
        logger.info("📤 プロンプト送信中...")
            
        # プロンプト入力欄を探す
        input_selectors = [
            'textarea[placeholder*="メッセージ"]',
            'textarea[aria-label*="メッセージ"]',
            'div[contenteditable="true"]',
            'textarea.ql-editor',
            'div.ql-editor'
        ]
            
        input_box = None
        for selector in input_selectors:
            try:
                input_box = await self.page.wait_for_selector(selector, timeout=5000)
                if input_box:
                    break
            except:
                continue
            
        if not input_box:
            logger.error("❌ 入力欄が見つかりません")
            return False
            
        # プロンプト入力
        await input_box.click()
        await asyncio.sleep(0.5)
        await input_box.fill(prompt)
        await asyncio.sleep(1)
            
        # 送信ボタンクリック
        send_button = await self.page.query_selector('button[aria-label*="送信"]')
        if send_button:
            await send_button.click()
            logger.info("✅ プロンプト送信完了")
            return True
        else:
            # Enterキーで送信
            await self.page.keyboard.press('Enter')
            logger.info("✅ プロンプト送信完了（Enter）")
            return True
        
    except Exception as e:
        logger.error(f"❌ プロンプト送信エラー: {e}")
        return False
    
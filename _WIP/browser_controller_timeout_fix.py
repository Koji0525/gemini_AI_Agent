"""
BrowserController タイムアウト問題の修正版
"""

# browser_control/browser_controller.py の修正箇所

async def navigate_to_gemini(self, max_retries: int = 3) -> bool:
    """
    Gemini AIに移動（リトライ機能付き）
    
    Args:
        max_retries: 最大リトライ回数
        
    Returns:
        bool: ログイン状態
    """
    for attempt in range(max_retries):
        try:
            print(f"📱 Gemini AIに移動中... (試行 {attempt + 1}/{max_retries})")
            
            # タイムアウトを段階的に増加（30秒 → 60秒 → 90秒）
            timeout = 30000 + (attempt * 30000)
            
            await self.page.goto(
                "https://gemini.google.com/app",
                timeout=timeout,
                wait_until="domcontentloaded"  # networkidle より軽い
            )
            
            # ページ読み込み待機
            await asyncio.sleep(3)
            
            # ログイン状態確認
            is_logged_in = await self._check_login_status()
            
            if is_logged_in:
                print("✅ ログイン状態: True")
                return True
            else:
                print("⚠️  ログインが必要です")
                return False
                
        except Exception as e:
            print(f"⚠️  試行 {attempt + 1} 失敗: {e}")
            
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"   {wait_time}秒後に再試行...")
                await asyncio.sleep(wait_time)
            else:
                print(f"❌ {max_retries}回試行しましたが失敗しました")
                raise

async def send_prompt(self, prompt: str, timeout: int = 60000, max_retries: int = 2) -> None:
    """
    Geminiにプロンプトを送信（リトライ機能付き）
    
    Args:
        prompt: 送信するプロンプト
        timeout: タイムアウト時間（ミリ秒）
        max_retries: 最大リトライ回数
    """
    for attempt in range(max_retries):
        try:
            print(f"📝 プロンプト送信: {prompt[:80]}...")
            
            # 入力欄を探す（複数のセレクタを試行）
            selectors = [
                "div[contenteditable='true']",
                ".ql-editor",
                "rich-textarea"
            ]
            
            textarea = None
            for selector in selectors:
                try:
                    textarea = await self.page.locator(selector).first
                    if await textarea.is_visible():
                        break
                except:
                    continue
            
            if not textarea:
                raise Exception("入力欄が見つかりません")
            
            # クリアしてからテキスト入力
            await textarea.click()
            await textarea.fill("")
            await textarea.fill(prompt)
            
            # Enterキーで送信
            await textarea.press("Enter")
            
            print("✅ プロンプト送信完了")
            return
            
        except Exception as e:
            print(f"⚠️  試行 {attempt + 1} 失敗: {e}")
            
            if attempt < max_retries - 1:
                print(f"   3秒後に再試行...")
                await asyncio.sleep(3)
            else:
                raise BrowserOperationError(f"プロンプト送信失敗: {e}")


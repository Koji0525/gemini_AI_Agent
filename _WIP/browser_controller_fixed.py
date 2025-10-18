# この部分だけ修正が必要な send_prompt メソッド

    async def send_prompt(self, prompt: str, timeout: int = 60000) -> None:
        """
        Geminiにプロンプトを送信
        
        Args:
            prompt: 送信するプロンプト
            timeout: タイムアウト時間（ミリ秒）
        """
        try:
            logger.info(f"📝 プロンプト送信: {prompt[:80]}...")
            
            # 🔧 修正: textareaではなく、div[contenteditable='true']を使用
            textarea = await self.page.locator("div[contenteditable='true']").first
            
            # クリアしてからテキスト入力
            await textarea.click()
            await textarea.fill("")  # クリア
            await textarea.fill(prompt)
            
            # Enterキーで送信
            await textarea.press("Enter")
            
            logger.info("✅ プロンプト送信完了")
            
        except Exception as e:
            logger.error(f"❌ プロンプト送信エラー: {e}")
            raise BrowserOperationError(f"プロンプト送信失敗: {e}")


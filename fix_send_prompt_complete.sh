#!/bin/bash
set -e

echo "=========================================="
echo "🔧 send_prompt メソッド完全修正"
echo "=========================================="

# バックアップ
cp browser_control/browser_controller.py browser_control/browser_controller.py.backup_send_prompt_fix

python3 << 'PYTHON_FIX'
import re

# ファイル読み込み
with open("browser_control/browser_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

print("📝 send_prompt メソッドを改良中...")

# 新しいsend_promptメソッド（待機時間とデバッグ強化）
new_send_prompt = '''    async def send_prompt(self, prompt: str, timeout: int = 60000, max_retries: int = 3) -> None:
        """
        Geminiにプロンプトを送信（リトライ機能付き・待機時間強化）
        
        Args:
            prompt: 送信するプロンプト
            timeout: タイムアウト時間（ミリ秒）
            max_retries: 最大リトライ回数
        """
        for attempt in range(max_retries):
            try:
                print(f"📝 プロンプト送信: {prompt[:80]}...")
                
                # ページが完全に読み込まれるまで待機（重要！）
                if attempt == 0:
                    print("⏳ ページ読み込み待機中（5秒）...")
                    await asyncio.sleep(5)
                
                # 入力欄を探す（複数のセレクタを試行）
                selectors = [
                    "div[contenteditable='true']",
                    "[contenteditable='true']",
                    "div[role='textbox']",
                    "[role='textbox']",
                    ".ql-editor",
                    "rich-textarea",
                    "textarea"
                ]
                
                textarea = None
                found_selector = None
                
                for selector in selectors:
                    try:
                        # 要素を待機（最大10秒）
                        await self.page.wait_for_selector(selector, timeout=10000, state="visible")
                        
                        elements = await self.page.locator(selector).all()
                        
                        if elements:
                            # 表示されている要素を探す
                            for elem in elements:
                                if await elem.is_visible():
                                    textarea = elem
                                    found_selector = selector
                                    print(f"✅ 入力欄発見: {selector}")
                                    break
                        
                        if textarea:
                            break
                            
                    except Exception as e:
                        # このセレクタでは見つからなかった
                        continue
                
                if not textarea:
                    raise Exception("入力欄が見つかりません")
                
                # テキスト入力
                print("📝 テキスト入力中...")
                await textarea.click()
                
                # クリア
                await textarea.fill("")
                await asyncio.sleep(0.5)
                
                # テキスト入力
                await textarea.fill(prompt)
                await asyncio.sleep(1)
                
                # Enterキーで送信
                await textarea.press("Enter")
                
                print("✅ プロンプト送信完了")
                return
                
            except Exception as e:
                print(f"⚠️  試行 {attempt + 1}/{max_retries} 失敗: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"   {wait_time}秒後に再試行...")
                    await asyncio.sleep(wait_time)
                else:
                    # 最終試行失敗時はスクリーンショットを撮る
                    try:
                        await self.page.screenshot(path="error_send_prompt.png")
                        print("📸 エラー時のスクリーンショット: error_send_prompt.png")
                    except:
                        pass
                    
                    raise BrowserOperationError(f"プロンプト送信失敗: {e}")
'''

# 既存のsend_promptメソッドを置換
pattern = r'    async def send_prompt\(self.*?\n(?=    async def |    def |class |\Z)'
content = re.sub(pattern, new_send_prompt + '\n', content, flags=re.DOTALL)

# 保存
with open("browser_control/browser_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ send_prompt メソッド修正完了")

PYTHON_FIX

# 構文チェック
python3 -m py_compile browser_control/browser_controller.py

if [ $? -eq 0 ]; then
    echo "✅ 構文チェック成功"
else
    echo "❌ 構文エラー"
    echo "バックアップから復元:"
    echo "  cp browser_control/browser_controller.py.backup_send_prompt_fix browser_control/browser_controller.py"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 完了"
echo "=========================================="


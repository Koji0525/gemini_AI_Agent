#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🔧 ブラウザタイムアウト修正適用"
echo "=========================================="

# ====================================================================
# STEP 1: バックアップ作成
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/4] バックアップ作成${NC}"
echo "=========================================="

cp browser_control/browser_controller.py browser_control/browser_controller.py.backup_v1_integrated
echo "✅ バックアップ作成完了"

# ====================================================================
# STEP 2: タイムアウト修正を適用
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/4] タイムアウト修正適用${NC}"
echo "=========================================="

python3 << 'PYTHON_FIX'
import re

# ファイル読み込み
with open("browser_control/browser_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

print("📝 navigate_to_gemini メソッドを修正中...")

# navigate_to_gemini メソッドを修正
new_navigate = '''    async def navigate_to_gemini(self, max_retries: int = 3) -> bool:
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
'''

# 既存のnavigate_to_geminiメソッドを置換
pattern = r'    async def navigate_to_gemini\(self.*?\n(?=    async def |    def |class |\Z)'
content = re.sub(pattern, new_navigate + '\n', content, flags=re.DOTALL)

print("📝 send_prompt メソッドを修正中...")

# send_prompt メソッドを修正（リトライ機能追加）
new_send_prompt = '''    async def send_prompt(self, prompt: str, timeout: int = 60000, max_retries: int = 2) -> None:
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
'''

# send_promptメソッドを置換
pattern = r'    async def send_prompt\(self.*?\n(?=    async def |    def |class |\Z)'
content = re.sub(pattern, new_send_prompt + '\n', content, flags=re.DOTALL)

# 保存
with open("browser_control/browser_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ タイムアウト修正適用完了")

PYTHON_FIX

# ====================================================================
# STEP 3: 変更内容を確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/4] 変更内容確認${NC}"
echo "=========================================="

echo "修正されたメソッド:"
grep -n "async def navigate_to_gemini\|async def send_prompt" browser_control/browser_controller.py

# ====================================================================
# STEP 4: 構文チェック
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 4/4] 構文チェック${NC}"
echo "=========================================="

python3 -m py_compile browser_control/browser_controller.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 構文チェック成功${NC}"
else
    echo -e "${RED}❌ 構文エラーがあります${NC}"
    echo "バックアップから復元: "
    echo "  cp browser_control/browser_controller.py.backup_v1_integrated browser_control/browser_controller.py"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ タイムアウト修正適用完了！${NC}"
echo "=========================================="


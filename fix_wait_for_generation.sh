#!/bin/bash
set -e

echo "=========================================="
echo "🔧 レスポンス待機ロジック修正"
echo "=========================================="

# バックアップ
cp browser_control/browser_controller.py browser_control/browser_controller.py.backup_wait_fix

python3 << 'PYTHON_FIX'
import re

# ファイル読み込み
with open("browser_control/browser_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

print("📝 wait_for_text_generation メソッドを改良中...")

# 新しいwait_for_text_generationメソッド
new_wait_method = '''    async def wait_for_text_generation(self, max_wait: int = 90) -> bool:
        """
        Geminiのテキスト生成完了を待機（改良版）
        
        Args:
            max_wait: 最大待機時間（秒）
            
        Returns:
            bool: 生成完了したかどうか
        """
        try:
            print("⏳ レスポンス生成を待機中...")
            
            start_time = asyncio.get_event_loop().time()
            last_length = 0
            stable_count = 0
            
            while (asyncio.get_event_loop().time() - start_time) < max_wait:
                # レスポンス要素を探す
                selectors = [
                    ".response-container",
                    ".model-response-text",
                    ".markdown"
                ]
                
                current_text = ""
                
                for selector in selectors:
                    try:
                        elements = await self.page.locator(selector).all()
                        if elements:
                            # 最後の要素（最新のレスポンス）
                            last_elem = elements[-1]
                            if await last_elem.is_visible():
                                current_text = await last_elem.text_content() or ""
                                break
                    except:
                        continue
                
                current_length = len(current_text.strip())
                
                # "Just a sec..." のような短いメッセージはスキップ
                if current_length > 50:  # 50文字以上なら実際のレスポンス
                    # テキストの長さが安定しているか確認
                    if current_length == last_length:
                        stable_count += 1
                        
                        # 3回連続で同じ長さなら生成完了
                        if stable_count >= 3:
                            print(f"✅ レスポンス生成完了（{current_length} 文字）")
                            return True
                    else:
                        stable_count = 0
                        last_length = current_length
                        print(f"   生成中... {current_length} 文字")
                
                # 1秒待機
                await asyncio.sleep(1)
            
            # タイムアウト
            print(f"⚠️  待機タイムアウト（{max_wait}秒）")
            
            # タイムアウトでも50文字以上あれば成功とみなす
            if last_length > 50:
                print(f"   ただし、{last_length}文字のレスポンスを取得済み")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 待機エラー: {e}")
            return False
'''

# 既存のwait_for_text_generationメソッドを置換
pattern = r'    async def wait_for_text_generation\(self.*?\n(?=    async def |    def |class |\Z)'
content = re.sub(pattern, new_wait_method + '\n', content, flags=re.DOTALL)

# 保存
with open("browser_control/browser_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ wait_for_text_generation メソッド修正完了")

PYTHON_FIX

# 構文チェック
python3 -m py_compile browser_control/browser_controller.py

if [ $? -eq 0 ]; then
    echo "✅ 構文チェック成功"
else
    echo "❌ 構文エラー"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 完了"
echo "=========================================="


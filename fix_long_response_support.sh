#!/bin/bash
set -e

echo "=========================================="
echo "🔧 長文レスポンス対応の実装"
echo "=========================================="

# バックアップ
cp browser_control/browser_controller.py browser_control/browser_controller.py.backup_long_response

python3 << 'PYTHON_FIX'
import re

with open("browser_control/browser_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

print("📝 wait_for_text_generation を長文対応版に修正中...")

# 長文対応版のメソッド
new_method = '''    async def wait_for_text_generation(self, max_wait: int = 120, min_stable_time: int = 7) -> bool:
        """
        Geminiのテキスト生成完了を待機（長文対応版）
        
        Args:
            max_wait: 最大待機時間（秒）デフォルト120秒
            min_stable_time: 安定判定の回数（秒）デフォルト7秒
            
        Returns:
            bool: 生成完了したかどうか
            
        判定ロジック:
        - 1秒ごとに文字数をチェック
        - 短文（1,000文字未満）: 3秒安定で完了
        - 中文（1,000-3,000文字）: 5秒安定で完了
        - 長文（3,000文字以上）: 7秒安定で完了
        """
        try:
            print("⏳ レスポンス生成を待機中...")
            
            start_time = asyncio.get_event_loop().time()
            last_length = 0
            stable_count = 0
            max_length_seen = 0  # これまでの最大文字数
            
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
                            last_elem = elements[-1]
                            if await last_elem.is_visible():
                                current_text = await last_elem.text_content() or ""
                                break
                    except:
                        continue
                
                current_length = len(current_text.strip())
                
                # 最大文字数を記録
                if current_length > max_length_seen:
                    max_length_seen = current_length
                
                # 50文字以上なら実際のレスポンス
                if current_length > 50:
                    # 文字数に応じて必要な安定時間を決定
                    if current_length < 1000:
                        required_stable = 3  # 短文: 3秒
                    elif current_length < 3000:
                        required_stable = 5  # 中文: 5秒
                    else:
                        required_stable = 7  # 長文: 7秒
                    
                    # 文字数が安定しているか確認
                    if current_length == last_length:
                        stable_count += 1
                        
                        # 必要な安定時間に達したら完了
                        if stable_count >= required_stable:
                            print(f"✅ レスポンス生成完了（{current_length} 文字、{required_stable}秒安定）")
                            return True
                        else:
                            # 安定中の表示
                            if stable_count % 2 == 0:  # 2秒ごとに表示
                                print(f"   安定確認中... {current_length} 文字（{stable_count}/{required_stable}秒）")
                    else:
                        # 文字数が増えた
                        stable_count = 0
                        last_length = current_length
                        
                        # 進捗表示（100文字ごと）
                        if current_length % 100 < 50 and current_length > 100:
                            print(f"   生成中... {current_length} 文字")
                
                # 1秒待機
                await asyncio.sleep(1)
            
            # タイムアウト
            elapsed = int(asyncio.get_event_loop().time() - start_time)
            print(f"⚠️  待機タイムアウト（{elapsed}秒）")
            
            # タイムアウトでも50文字以上あれば部分的に成功
            if max_length_seen > 50:
                print(f"   ただし、{max_length_seen}文字のレスポンスを取得済み")
                print(f"   最終的な文字数: {last_length}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 待機エラー: {e}")
            return False
'''

# 既存のメソッドを置換
pattern = r'    async def wait_for_text_generation\(self.*?\n(?=    async def |    def |class |\Z)'
content = re.sub(pattern, new_method + '\n', content, flags=re.DOTALL)

# 保存
with open("browser_control/browser_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 長文対応版に修正完了")

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
echo "✅ 修正完了"
echo "=========================================="
echo ""
echo "📊 新しい判定ロジック:"
echo "  短文（<1,000文字）: 3秒安定で完了"
echo "  中文（1,000-3,000文字）: 5秒安定で完了"
echo "  長文（>3,000文字）: 7秒安定で完了"
echo "  最大待機時間: 120秒（2分）"
echo ""


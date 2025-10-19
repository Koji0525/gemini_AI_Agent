#!/bin/bash
set -e

echo "=========================================="
echo "🔧 オーバーレイ問題の修正"
echo "=========================================="

# バックアップ
cp browser_control/browser_controller.py browser_control/browser_controller.py.backup_overlay_fix

python3 << 'PYTHON_FIX'
import re

with open("browser_control/browser_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

print("📝 send_prompt メソッドにオーバーレイ対策を追加中...")

# send_promptメソッドを探して、クリック前にオーバーレイチェックを追加
# テキスト入力の前に以下を挿入:
overlay_check_code = '''
                # オーバーレイが表示されていたら閉じる
                try:
                    overlay = await self.page.locator(".cdk-overlay-backdrop").first
                    if await overlay.is_visible():
                        print("⚠️  オーバーレイを検出、閉じています...")
                        # Escapeキーで閉じる
                        await self.page.keyboard.press("Escape")
                        await asyncio.sleep(1)
                        print("✅ オーバーレイを閉じました")
                except:
                    pass  # オーバーレイがなければ無視
                
'''

# "# テキスト入力" の前に挿入
if "# テキスト入力" in content:
    content = content.replace(
        "                # テキスト入力",
        overlay_check_code + "                # テキスト入力"
    )
    print("✅ オーバーレイチェック追加完了")
else:
    print("⚠️  挿入箇所が見つかりません - 手動で追加が必要です")

with open("browser_control/browser_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

PYTHON_FIX

# 構文チェック
python3 -m py_compile browser_control/browser_controller.py

if [ $? -eq 0 ]; then
    echo "✅ 構文チェック成功"
else
    echo "❌ 構文エラー - バックアップから復元してください"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ オーバーレイ対策完了"
echo "=========================================="


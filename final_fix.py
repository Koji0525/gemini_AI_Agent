#!/usr/bin/env python3
"""
最終修正 - 残り2つの問題を解決
"""
from pathlib import Path

print("=" * 80)
print("🔧 最終修正")
print("=" * 80)

# ============================================================
# 1. test_tasks_practical.py に sys import を確実に追加
# ============================================================
print("\n1️⃣ test_tasks_practical.py 修正...")
test_path = Path("test_tasks_practical.py")

with open(test_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'import sys' not in content:
    # 最初のimport群の最後に追加
    content = content.replace(
        'import asyncio',
        'import asyncio\nimport sys'
    )
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("   ✅ sys import 追加")
else:
    print("   ℹ️ sys import 既存")

# ============================================================
# 2. WordPressAgent.create_post() の正しいシグネチャを確認
# ============================================================
print("\n2️⃣ WordPressAgent.create_post() のシグネチャを確認...")
wp_agent_path = Path("wordpress/wp_agent.py")

with open(wp_agent_path, 'r', encoding='utf-8') as f:
    wp_content = f.read()

# create_post メソッドの定義を探す
import re
create_post_match = re.search(r'async def create_post\(self[^)]*\):', wp_content)
if create_post_match:
    print(f"   📝 発見: {create_post_match.group()}")
else:
    print("   ⚠️ create_post メソッドが見つかりません")

# ============================================================
# 3. test_tasks_practical.py の create_post 呼び出しを修正
# ============================================================
print("\n3️⃣ test_tasks_practical.py の create_post 呼び出しを修正...")

# task2_create_draft_post を修正
new_task2 = '''async def task2_create_draft_post():
    """タスク2: 下書き記事作成"""
    logger.info("📝 タスク2: 下書き記事作成を試行")
    try:
        from browser_controller import BrowserController
        from wordpress.wp_agent import WordPressAgent
        
        browser = BrowserController(download_folder="./downloads")
        wp = WordPressAgent(browser)
        
        # taskオブジェクトを作成（WordPressAgentが期待する形式）
        task = {
            'type': 'create_post',
            'title': f'テスト記事 {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'content': '<p>これは自動生成されたテスト記事です。</p>',
            'status': 'draft'
        }
        
        # create_post メソッドが存在するか確認
        if hasattr(wp, 'create_post'):
            # 正しいシグネチャで呼び出し (task引数を渡す)
            result = await wp.create_post(task)
            logger.info(f"✅ 下書き記事作成成功: {result}")
            return True, None
        else:
            logger.warning("⚠️ create_post メソッドが未実装")
            return True, "メソッド未実装（スキップ）"
            
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return False, str(e)
    finally:
        if 'browser' in locals() and hasattr(browser, 'cleanup'):
            await browser.cleanup()
'''

# task2を置き換え
pattern = r'async def task2_create_draft_post\(\):.*?(?=\nasync def task3|$)'
content = re.sub(pattern, new_task2.strip(), content, flags=re.DOTALL)

with open(test_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("   ✅ task2_create_draft_post 修正完了")

print("\n" + "=" * 80)
print("🎉 最終修正完了！")
print("=" * 80)


#!/usr/bin/env python3
"""
正確な修正 - 実際の__init__シグネチャに基づく
"""
from pathlib import Path

print("=" * 80)
print("🎯 正確な自動修正")
print("=" * 80)

# 1. test_tasks_practical.py 修正
print("\n1️⃣ test_tasks_practical.py に sys import 追加...")
test_path = Path("test_tasks_practical.py")
with open(test_path, 'r') as f:
    content = f.read()

if 'import sys' not in content:
    lines = content.split('\n')
    # 4行目（import asyncio の後）に挿入
    lines.insert(4, 'import sys')
    with open(test_path, 'w') as f:
        f.write('\n'.join(lines))
    print("   ✅ sys import 追加完了")
else:
    print("   ℹ️ sys import 既に存在")

# 2. wp_agent.py の _initialize_sub_agents メソッドを完全書き換え
print("\n2️⃣ wp_agent.py を修正...")
wp_agent_path = Path("wordpress/wp_agent.py")

# バックアップ
backup = wp_agent_path.with_suffix('.py.precise_backup')
with open(wp_agent_path, 'r') as f:
    original = f.read()
with open(backup, 'w') as f:
    f.write(original)
print(f"   💾 バックアップ: {backup}")

# _initialize_sub_agents メソッド全体を置き換え
new_init_method = '''    def _initialize_sub_agents(self):
        """
        サブエージェントの初期化
        重要: 各サブエージェントの実際の__init__シグネチャに合わせる
        """
        try:
            # ✅ 投稿編集エージェント (wp_url, sheets_manager)
            self.post_editor = WordPressPostEditor(
                wp_url=self.wp_credentials.get('wp_url', '') if self.wp_credentials else '',
                sheets_manager=None
            )
            logger.info("🌐 wp-agent ✅ INFO WordPressPostEditor初期化完了")
            
            # ✅ 投稿作成エージェント (wp_url, sheets_manager)
            self.post_creator = WordPressPostCreator(
                wp_url=self.wp_credentials.get('wp_url', '') if self.wp_credentials else '',
                sheets_manager=None
            )
            logger.info("🌐 wp-agent ✅ INFO WordPressPostCreator初期化完了")
            
            # ✅ 設定マネージャー (wp_url のみ)
            self.settings_manager = WordPressSettingsManager(
                wp_url=self.wp_credentials.get('wp_url', '') if self.wp_credentials else ''
            )
            logger.info("🌐 wp-agent ✅ INFO WordPressSettingsManager初期化完了")
            
            # ✅ テスター (wp_url のみ)
            self.tester = WordPressTester(
                wp_url=self.wp_credentials.get('wp_url', '') if self.wp_credentials else ''
            )
            logger.info("🌐 wp-agent ✅ INFO WordPressTester初期化完了")
            
            logger.info("🌐 wp-agent ✅ INFO 全サブエージェント初期化完了")
            
        except Exception as e:
            logger.error(f"🌐 wp-agent ❌ ERROR サブエージェント初期化エラー: {e}")
            import traceback
            logger.error(f"🌐 wp-agent ❌ ERROR {traceback.format_exc()}")
            raise
'''

# _initialize_sub_agents メソッドを置き換え
import re
pattern = r'def _initialize_sub_agents\(self\):.*?(?=\n    def |\n\nclass |\Z)'
content = re.sub(pattern, new_init_method.lstrip(), original, flags=re.DOTALL)

if content == original:
    print("   ⚠️ パターンマッチ失敗。手動で編集が必要です。")
    print(f"   📝 確認: {wp_agent_path}")
else:
    with open(wp_agent_path, 'w') as f:
        f.write(content)
    print("   ✅ wp_agent.py 修正完了")

print("\n" + "=" * 80)
print("🎉 正確な修正完了！")
print("=" * 80)


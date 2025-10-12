#!/usr/bin/env python3
"""
WordPressAgent自動修正スクリプト
"""
import re
from pathlib import Path

wp_agent_path = Path("wordpress/wp_agent.py")

# ファイルを読み込む
with open(wp_agent_path, 'r', encoding='utf-8') as f:
    content = f.read()

# WordPressPostEditorの初期化部分を探す
# browser_controller引数を削除
pattern = r'self\.post_editor = WordPressPostEditor\(\s*browser_controller=self\.browser_controller,'
replacement = 'self.post_editor = WordPressPostEditor('

content_fixed = re.sub(pattern, replacement, content)

# もし上記で見つからなければ、別のパターンを試す
if content == content_fixed:
    pattern2 = r'WordPressPostEditor\([^)]*browser_controller[^)]*\)'
    # この場合はもっと慎重に処理する必要がある
    print("⚠️ パターン1では見つかりませんでした。手動確認が必要です。")
    print(f"📝 確認箇所: {wp_agent_path}:124付近")
else:
    # バックアップ
    backup_path = wp_agent_path.with_suffix('.py.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 バックアップ作成: {backup_path}")
    
    # 修正版を保存
    with open(wp_agent_path, 'w', encoding='utf-8') as f:
        f.write(content_fixed)
    
    print(f"✅ 修正完了: {wp_agent_path}")
    print("🔄 test_tasks_practical.py を再実行してください")


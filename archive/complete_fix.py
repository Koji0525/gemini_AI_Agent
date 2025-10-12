#!/usr/bin/env python3
"""
完全自動修正 - すべてのWordPressエージェント初期化を修正
"""
from pathlib import Path
import re

print("=" * 80)
print("🔧 完全自動修正システム")
print("=" * 80)

# ============================================================
# 1. test_tasks_practical.py に sys import 追加
# ============================================================
print("\n1️⃣ test_tasks_practical.py を修正...")
test_path = Path("test_tasks_practical.py")

with open(test_path, 'r', encoding='utf-8') as f:
    test_content = f.read()

if 'import sys' not in test_content:
    # ファイルの先頭付近に追加
    lines = test_content.split('\n')
    new_lines = []
    added = False
    
    for line in lines:
        new_lines.append(line)
        # import asyncio の直後に追加
        if 'import asyncio' in line and not added:
            new_lines.append('import sys')
            added = True
            print("   ✅ sys import を追加")
    
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
else:
    print("   ℹ️ sys import は既に存在")

# ============================================================
# 2. wp_agent.py のすべてのサブエージェント初期化を修正
# ============================================================
print("\n2️⃣ wp_agent.py のすべてのエージェントを修正...")
wp_agent_path = Path("wordpress/wp_agent.py")

# バックアップ
backup = wp_agent_path.with_suffix('.py.complete_backup')
with open(wp_agent_path, 'r', encoding='utf-8') as f:
    original = f.read()
with open(backup, 'w', encoding='utf-8') as f:
    f.write(original)
print(f"   💾 バックアップ: {backup}")

# まず、どのエージェントがあるか確認
with open(wp_agent_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修正が必要なパターンを検索
agents_to_fix = [
    'WordPressPostEditor',
    'WordPressPostCreator',
    'WordPressMediaUploader',
    'WordPressCategoryManager',
]

lines = content.split('\n')
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # 各エージェントの初期化を検出
    agent_found = None
    for agent_name in agents_to_fix:
        if f'self.{agent_name.lower().replace("wordpress", "").replace("manager", "mgr")} = {agent_name}(' in line or \
           f'{agent_name}(' in line and 'self.' in line:
            agent_found = agent_name
            break
    
    if agent_found and i + 1 < len(lines) and 'browser_controller' in lines[i + 1]:
        print(f"   🔍 {i+1}行目: {agent_found} を修正")
        
        # agent_nameに応じて適切な初期化コードに置き換え
        indent = '            '
        
        if agent_found == 'WordPressPostEditor':
            fixed_lines.append(f'{indent}self.post_editor = WordPressPostEditor(')
            fixed_lines.append(f"{indent}    wp_url=self.wp_credentials.get('wp_url', '') if self.wp_credentials else '',")
            fixed_lines.append(f'{indent}    sheets_manager=None')
            fixed_lines.append(f'{indent})')
        elif agent_found == 'WordPressPostCreator':
            fixed_lines.append(f'{indent}self.post_creator = WordPressPostCreator(')
            fixed_lines.append(f"{indent}    wp_url=self.wp_credentials.get('wp_url', '') if self.wp_credentials else ''")
            fixed_lines.append(f'{indent})')
        elif agent_found == 'WordPressMediaUploader':
            fixed_lines.append(f'{indent}self.media_uploader = WordPressMediaUploader(')
            fixed_lines.append(f"{indent}    wp_url=self.wp_credentials.get('wp_url', '') if self.wp_credentials else ''")
            fixed_lines.append(f'{indent})')
        elif agent_found == 'WordPressCategoryManager':
            fixed_lines.append(f'{indent}self.category_mgr = WordPressCategoryManager(')
            fixed_lines.append(f"{indent}    wp_url=self.wp_credentials.get('wp_url', '') if self.wp_credentials else ''")
            fixed_lines.append(f'{indent})')
        
        # 元の初期化コード（複数行）をスキップ
        skip = 0
        while i + skip + 1 < len(lines) and ')' not in lines[i + skip]:
            skip += 1
        i += skip + 1
        continue
    
    fixed_lines.append(line)
    i += 1

# 保存
with open(wp_agent_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print(f"   ✅ wp_agent.py 修正完了")

# ============================================================
# 3. 各エージェントクラスの__init__シグネチャを確認
# ============================================================
print("\n3️⃣ 各エージェントの__init__シグネチャを確認...")

agent_files = {
    'WordPressPostEditor': 'wordpress/wp_post_editor.py',
    'WordPressPostCreator': 'wordpress/wp_post_creator.py',
}

for agent_name, file_path in agent_files.items():
    path = Path(file_path)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # __init__ の定義を探す
        match = re.search(rf'def __init__\(self[^)]*\):', content)
        if match:
            print(f"   📝 {agent_name}: {match.group()}")
    else:
        print(f"   ⚠️ {file_path} が見つかりません")

print("\n" + "=" * 80)
print("🎉 完全修正完了！")
print("=" * 80)


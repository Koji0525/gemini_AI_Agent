#!/usr/bin/env python3
"""
WordPressAgent自動修正 v2
"""
from pathlib import Path
import re

wp_agent_path = Path("wordpress/wp_agent.py")

# バックアップ作成
backup_path = wp_agent_path.with_suffix('.py.bak2')
with open(wp_agent_path, 'r', encoding='utf-8') as f:
    original = f.read()
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(original)
print(f"💾 バックアップ: {backup_path}")

# 修正：WordPressPostEditor初期化を正しい引数に変更
# 複数行マッチング
pattern = r'self\.post_editor = WordPressPostEditor\(\s+browser_controller=self\.browser,\s+wp_credentials=self\.wp_credentials\s+\)'

# wp_urlを使用（もしwp_credentialsがある場合）
replacement = '''self.post_editor = WordPressPostEditor(
                wp_url=self.wp_credentials.get('wp_url', ''),
                sheets_manager=None
            )'''

content = re.sub(pattern, replacement, original, flags=re.MULTILINE)

if content == original:
    print("⚠️ パターンマッチ失敗。直接編集します...")
    
    # 行ごとに処理
    lines = original.split('\n')
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 124行目付近（インデックスは123）
        if 'self.post_editor = WordPressPostEditor(' in line:
            print(f"🔍 {i+1}行目で発見")
            # この行と次の2行をスキップして新しいコードに置き換え
            fixed_lines.append('            self.post_editor = WordPressPostEditor(')
            fixed_lines.append("                wp_url=self.wp_credentials.get('wp_url', ''),")
            fixed_lines.append('                sheets_manager=None')
            fixed_lines.append('            )')
            # 元の3行をスキップ（現在の行 + 次の2行）
            i += 3
            continue
        
        fixed_lines.append(line)
        i += 1
    
    content = '\n'.join(fixed_lines)

# 保存
with open(wp_agent_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ 修正完了: {wp_agent_path}")
print("📝 変更内容:")
print("  - WordPressPostEditor(browser_controller=..., wp_credentials=...)")
print("  → WordPressPostEditor(wp_url=..., sheets_manager=None)")

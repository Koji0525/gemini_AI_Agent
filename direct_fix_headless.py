#!/usr/bin/env python3
"""
browser_lifecycle.py を直接修正
"""

with open('browser_control/browser_lifecycle.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# launch_persistent_context の呼び出しを探して修正
in_launch_call = False
new_lines = []
skip_until_closing = False

for i, line in enumerate(lines):
    if 'launch_persistent_context(' in line:
        in_launch_call = True
        new_lines.append(line)
        # 次の行に browser_config の処理を追加
        new_lines.append('                # BROWSER_CONFIG から headless を除外\n')
        new_lines.append('                browser_config = {k: v for k, v in config.BROWSER_CONFIG.items() if k != "headless"}\n')
        new_lines.append('                \n')
        continue
    
    # headless=True で始まる行をスキップ（最初の1つだけ保持）
    if in_launch_call and 'headless=True' in line:
        continue
    
    # **config.BROWSER_CONFIG を **browser_config に置換
    if in_launch_call and '**config.BROWSER_CONFIG' in line:
        line = line.replace('**config.BROWSER_CONFIG', 'headless=True,  # 明示的に指定\n                **browser_config')
    
    new_lines.append(line)
    
    # ) だけの行で launch_persistent_context 呼び出しが終了
    if in_launch_call and line.strip() == ')':
        in_launch_call = False

with open('browser_control/browser_lifecycle.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 直接修正完了")

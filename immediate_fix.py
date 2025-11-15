#!/usr/bin/env python3
"""即時修正：task_executor_enhanced.pyを完全修復"""

import re

with open('agents/task_executor_enhanced.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 問題の文字列リテラルを修正
# 120-125行目あたりの問題を解決
lines = content.split('\n')
fixed_lines = []

i = 0
while i < len(lines):
    line = lines[i]
    
    # 問題の行を特定して修正
    if i >= 115 and i <= 130 and '"' in line and lines[i+1].startswith('pathlib2'):
        # 問題のrequirements部分を修正
        fixed_lines.append('        requirements = "click>=8.0.0"')
        fixed_lines.append('        requirements_content = requirements + "\\npathlib2>=2.3.0\\n"')
        fixed_lines.append('        (output_dir / "cli" / "requirements.txt").write_text(requirements_content)')
        # 次の2行をスキップ
        i += 3
        continue
    elif '"""' in line and '実際のCLI実装完了' in line:
        # 三重引用符の問題を修正
        if lines[i+4].strip() == '"""':
            # 正常な三重引用符ブロック
            fixed_lines.append(line)
        else:
            # 壊れたブロックを修正
            fixed_lines.append(line)
            j = i + 1
            while j < len(lines) and '"""' not in lines[j]:
                fixed_lines.append(lines[j])
                j += 1
            if j < len(lines):
                fixed_lines.append(lines[j])
            i = j
    else:
        fixed_lines.append(line)
    
    i += 1

# 修正内容を保存
with open('agents/task_executor_enhanced.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("✅ 即時修正完了")

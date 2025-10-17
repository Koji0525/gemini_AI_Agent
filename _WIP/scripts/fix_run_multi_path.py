#!/usr/bin/env python3
"""run_multi_agent.py のパス問題を修正"""
from pathlib import Path

file = Path('scripts/run_multi_agent.py')
if not file.exists():
    print("❌ scripts/run_multi_agent.py が見つかりません")
    exit(1)

content = file.read_text()

# 間違ったパスを修正
replacements = [
    ("exec(open('task_executor.py').read())", "exec(open('../task_executor/task_executor_ma.py').read())"),
    ("exec(open('task_executor/task_executor.py').read())", "exec(open('../task_executor/task_executor_ma.py').read())"),
]

modified = False
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        modified = True
        print(f"✅ 修正: {old} → {new}")

if modified:
    file.write_text(content)
    print("✅ run_multi_agent.py のパスを修正")
else:
    print("ℹ️ 既に修正済みまたは該当箇所なし")

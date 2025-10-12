#!/usr/bin/env python3
from pathlib import Path

file = Path('scripts/run_multi_agent.py')
content = file.read_text()

# 間違ったパスを修正
content = content.replace(
    "exec(open('task_executor.py').read())",
    "exec(open('task_executor/task_executor.py').read())"
)

file.write_text(content)
print("✅ task_executor.py のパスを修正")

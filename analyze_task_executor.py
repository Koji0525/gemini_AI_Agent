#!/usr/bin/env python3
"""TaskExecutorの詳細分析"""

print("🔍 TaskExecutor詳細分析")
print("=" * 70)

# 1. 全メソッド一覧
print("\n📋 1. TaskExecutorの全メソッド:")
import subprocess
result = subprocess.run(
    ['grep', '-n', 'def ', 'scripts/task_executor.py'],
    capture_output=True,
    text=True
)
print(result.stdout)

# 2. design_agent, dev_agent, review_agentが登場する行
print("\n📋 2. エージェント変数が登場する行:")
with open('scripts/task_executor.py', 'r') as f:
    lines = f.readlines()
    
for i, line in enumerate(lines, 1):
    if any(keyword in line.lower() for keyword in ['design_agent', 'dev_agent', 'review_agent']):
        if '#' not in line or line.strip().index('#') > line.index('agent'):
            print(f"  {i:4}: {line.rstrip()}")

# 3. __init__の引数
print("\n📋 3. TaskExecutor.__init__の引数:")
for i, line in enumerate(lines, 1):
    if 'def __init__(self' in line:
        # __init__の引数部分を複数行取得
        init_start = i - 1
        init_lines = []
        for j in range(init_start, min(init_start + 20, len(lines))):
            init_lines.append(lines[j].rstrip())
            if ')' in lines[j] and ':' in lines[j]:
                break
        print('\n'.join(init_lines))
        break

# 4. self.browser = の行
print("\n📋 4. self.browser 設定:")
for i, line in enumerate(lines, 1):
    if 'self.browser' in line and '=' in line:
        print(f"  {i:4}: {line.rstrip()}")

print("\n" + "=" * 70)

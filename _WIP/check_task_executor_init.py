#!/usr/bin/env python3
"""TaskExecutorのエージェント初期化コードを確認"""

print("🔍 TaskExecutorのエージェント初期化確認")
print("=" * 70)

# __init__メソッドを確認
print("\n📋 TaskExecutor.__init__のエージェント初期化部分:")
with open('scripts/task_executor.py', 'r') as f:
    lines = f.readlines()
    
in_init = False
init_lines = []

for i, line in enumerate(lines, 1):
    if 'def __init__' in line and 'TaskExecutor' not in line:
        continue
    
    if 'def __init__(self' in line:
        in_init = True
    
    if in_init:
        init_lines.append((i, line.rstrip()))
        
        # 次のdefで終了
        if 'def ' in line and '__init__' not in line and len(init_lines) > 5:
            break

# DesignAgent/DevAgent/ReviewAgentの初期化部分を表示
print("\nDesignAgent初期化:")
for line_num, line in init_lines:
    if 'design_agent' in line.lower() or 'DesignAgent' in line:
        print(f"  {line_num:4}: {line}")

print("\nDevAgent初期化:")
for line_num, line in init_lines:
    if 'dev_agent' in line.lower() or 'DevAgent' in line:
        print(f"  {line_num:4}: {line}")

print("\nReviewAgent初期化:")
for line_num, line in init_lines:
    if 'review_agent' in line.lower() or 'ReviewAgent' in line:
        print(f"  {line_num:4}: {line}")

print("\n" + "=" * 70)

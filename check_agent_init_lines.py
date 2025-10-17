#!/usr/bin/env python3
"""235行目と266行目の前後確認"""

print("🔍 DesignAgent/DevAgent初期化コード確認")
print("=" * 70)

with open('scripts/task_executor.py', 'r') as f:
    lines = f.readlines()

# 235行目前後
print("\n📋 1. 235行目前後（±10行）:")
for i in range(max(0, 225), min(len(lines), 245)):
    marker = " → " if i == 234 else "    "
    print(f"{marker}{i+1:4}: {lines[i].rstrip()}")

# 266行目前後
print("\n📋 2. 266行目前後（±10行）:")
for i in range(max(0, 256), min(len(lines), 276)):
    marker = " → " if i == 265 else "    "
    print(f"{marker}{i+1:4}: {lines[i].rstrip()}")

# _initialize_agentsメソッド全体
print("\n📋 3. _initialize_agentsメソッド:")
in_method = False
for i, line in enumerate(lines, 1):
    if 'def _initialize_agents(self):' in line:
        in_method = True
    
    if in_method:
        print(f"  {i:4}: {line.rstrip()}")
        
        # 次のdefで終了
        if 'def ' in line and '_initialize_agents' not in line and i > 290:
            break

print("\n" + "=" * 70)

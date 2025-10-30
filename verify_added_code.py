#!/usr/bin/env python3
"""追加したコードの確認"""

print("🔍 追加コードの検証")
print("=" * 70)

with open("scripts/task_executor.py", "r") as f:
    lines = f.readlines()

# 1. DesignAgent/DevAgent初期化コードが存在するか
print("\n📋 1. DesignAgent初期化コードの存在確認:")
design_found = False
for i, line in enumerate(lines, 1):
    if "self.design_agent = None" in line or "DesignAgent(" in line:
        print(f"  {i:4}: {line.rstrip()}")
        design_found = True

if not design_found:
    print("  ❌ DesignAgent初期化コードが見つかりません")

print("\n📋 2. DevAgent初期化コードの存在確認:")
dev_found = False
for i, line in enumerate(lines, 1):
    if "self.dev_agent = None" in line or "DevAgent(" in line:
        print(f"  {i:4}: {line.rstrip()}")
        dev_found = True

if not dev_found:
    print("  ❌ DevAgent初期化コードが見つかりません")

# 2. ReviewAgent初期化の周辺（挿入箇所確認）
print("\n📋 3. ReviewAgent周辺（160-200行）:")
for i in range(159, min(len(lines), 200)):
    if any(keyword in lines[i].lower() for keyword in ["design", "dev_agent", "review"]):
        print(f"  {i+1:4}: {lines[i].rstrip()}")

# 3. __init__内でif self.browserのブロック確認
print("\n📋 4. 'if self.browser'の行:")
for i, line in enumerate(lines, 1):
    if "if self.browser" in line:
        print(f"  {i:4}: {line.rstrip()}")
        # 前後5行も表示
        for j in range(max(0, i - 2), min(len(lines), i + 8)):
            print(f"       {j+1:4}: {lines[j].rstrip()}")
        print()

print("=" * 70)

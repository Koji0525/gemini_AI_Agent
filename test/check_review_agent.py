#!/usr/bin/env python3
"""
レビューエージェントの確認
"""
import os
from pathlib import Path

# レビューエージェント関連ファイルを探す
review_files = []

for pattern in ["*review*.py", "review_agent*.py"]:
    for file in Path(".").rglob(pattern):
        review_files.append(file)

print("📋 レビュー関連ファイル:")
for file in review_files:
    print(f"  - {file}")

# review_agent.py が存在するか確認
if Path("review_agent.py").exists():
    print("\n✅ review_agent.py が見つかりました")
    print("\n📝 クラスとメソッド:")
    import subprocess

    result = subprocess.run(["grep", "-n", "class\\|def ", "review_agent.py"], capture_output=True, text=True)
    print(result.stdout[:500])
else:
    print("\n⚠️ review_agent.py が見つかりません")

    # agents/ ディレクトリ内を確認
    agents_dir = Path("agents")
    if agents_dir.exists():
        print("\n📁 agents/ ディレクトリの内容:")
        for file in agents_dir.glob("*.py"):
            print(f"  - {file}")

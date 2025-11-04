#!/usr/bin/env python3
"""
v15のタスク辞書型エラーを修正
"""

import sys
from pathlib import Path
import re

v15_files = list(Path("scripts").glob("*_v15_*.py"))

if not v15_files:
    print("❌ v15ファイルが見つかりません")
    sys.exit(1)

v15_file = v15_files[0]
print(f"📝 修正対象: {v15_file}")

with open(v15_file, "r") as f:
    content = f.read()

# execute_tasks内のタスクデータ構造を修正
# 'str' object has no attribute 'get' エラーの原因を修正

# pending_tasksの構築部分を探して修正
old_pattern = r"pending_tasks\.append\(\s*task\['task_id'\]\s*\)"
new_code = """pending_tasks.append({
                        'task_id': row[0] if len(row) > 0 else '',
                        'parent_goal_id': row[1] if len(row) > 1 else '',
                        'description': row[2] if len(row) > 2 else '',
                        'required_role': row[3] if len(row) > 3 else '',
                        'status': row[4] if len(row) > 4 else 'pending',
                        'priority': row[5] if len(row) > 5 else 'medium',
                        'execution_type': row[12] if len(row) > 12 else 'content'
                    })"""

if re.search(old_pattern, content):
    content = re.sub(old_pattern, new_code, content)
    print("✅ タスク辞書型構造を修正")

with open(v15_file, "w") as f:
    f.write(content)

print(f"✅ {v15_file} タスク構造修正完了")

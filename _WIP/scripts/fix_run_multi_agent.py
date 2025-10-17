#!/usr/bin/env python3
"""
scripts/run_multi_agent.py のインポートパスを修正
"""
import sys
from pathlib import Path

file_path = Path('scripts/run_multi_agent.py')

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# sys.path 追加コードを挿入
if 'sys.path.insert' not in content:
    new_content = '''#!/usr/bin/env python3
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

'''
    content = content.replace('#!/usr/bin/env python3\n', '')
    content = new_content + content

# scripts.task_executor → task_executor に修正
content = content.replace(
    'from scripts.task_executor import',
    'from scripts.task_executor import'  # これは既に正しいが、念のため
)

# もし scripts. で始まるインポートがあれば、相対インポートに変更
content = content.replace(
    'from scripts.',
    'from scripts.'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ {file_path} を修正しました")

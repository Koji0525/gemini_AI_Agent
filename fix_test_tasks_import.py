#!/usr/bin/env python3
"""
test_tasks.py のインポートパスを修正
"""
import sys
from pathlib import Path

# test/test_tasks.py を修正
test_file = Path('test/test_tasks.py')

with open(test_file, 'r', encoding='utf-8') as f:
    content = f.read()

# sys.path 追加コードを挿入
if 'sys.path.insert' not in content:
    # インポートの前に sys.path を追加
    new_content = '''#!/usr/bin/env python3
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

'''
    # 既存の shebang と import を置換
    content = content.replace('#!/usr/bin/env python3\n', '')
    content = new_content + content
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {test_file} を修正しました")
else:
    print(f"ℹ️  {test_file} は既に修正済みです")

#!/usr/bin/env python3
"""
autonomous_system.py のファイルパスを更新
"""

with open('autonomous_system.py', 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

# test_tasks.py は test/ に移動
content = content.replace(
    'python3 test_tasks.py',
    'python3 test/test_tasks.py'
).replace(
    '"test_tasks.py"',
    '"test/test_tasks.py"'
).replace(
    "'test_tasks.py'",
    "'test/test_tasks.py'"
)

# run_multi_agent.py は scripts/ に移動  
content = content.replace(
    'python3 run_multi_agent.py',
    'python3 scripts/run_multi_agent.py'
).replace(
    '"run_multi_agent.py"',
    '"scripts/run_multi_agent.py"'
).replace(
    "'run_multi_agent.py'",
    "'scripts/run_multi_agent.py'"
)

# ただし、コメント内の説明文は元のまま（わかりやすさのため）
# ドキュメント部分を復元
doc_lines = [
    '1. test_tasks.py を実行',
    '2. エラーが出たら main_hybrid_fix.py で自動修正',
    '3. run_multi_agent.py を実行',
    '4. エラーが出たら main_hybrid_fix.py で自動修正',
]

if original_content != content:
    with open('autonomous_system.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ autonomous_system.py のパスを更新しました")
    print("  - test_tasks.py → test/test_tasks.py")
    print("  - run_multi_agent.py → scripts/run_multi_agent.py")
else:
    print("ℹ️  パスは既に更新されています")

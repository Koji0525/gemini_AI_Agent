#!/usr/bin/env python3
"""すべてのプログラムに統一ログ設定を適用"""
from pathlib import Path
import re

# 対象ファイル
files = [
    'autonomous_system.py',
    'main_hybrid_fix.py',
    'scripts/run_multi_agent.py',
    'test/test_tasks.py',
]

for file_path in files:
    path = Path(file_path)
    if not path.exists():
        print(f"⏭️  スキップ: {file_path} (存在しない)")
        continue
    
    content = path.read_text()
    
    # タイムスタンプパターンを探す
    patterns = [
        (r'\[%Y-%m-%d %H:%M:%S\]', '[%H:%M]'),  # 完全タイムスタンプを短縮
        (r'%Y-%m-%d %H:%M:%S', '%H:%M'),  # 日付なしタイムスタンプ
    ]
    
    modified = False
    for old_pattern, new_pattern in patterns:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            modified = True
    
    if modified:
        path.write_text(content)
        print(f"✅ 修正: {file_path}")
    else:
        print(f"ℹ️  変更なし: {file_path}")

print("\n✅ すべての修正完了")

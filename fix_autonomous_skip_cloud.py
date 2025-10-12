#!/usr/bin/env python3
"""CloudFixAgent を一時的にスキップ"""
from pathlib import Path

file = Path('main_hybrid_fix.py')
content = file.read_text()

# CloudFixAgent の初期化をコメントアウト
content = content.replace(
    'cloud_agent = CloudFixAgent(config)',
    '# cloud_agent = CloudFixAgent(config)  # 一時的にスキップ'
)

content = content.replace(
    'cloud_agent=cloud_agent',
    'cloud_agent=None  # 一時的にスキップ'
)

file.write_text(content)
print("✅ CloudFixAgent を一時的にスキップ")

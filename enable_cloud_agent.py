#!/usr/bin/env python3
"""CloudFixAgent を再度有効化"""
from pathlib import Path

file = Path('main_hybrid_fix.py')
content = file.read_text()

# コメントアウトを解除
content = content.replace(
    '# cloud_agent = CloudFixAgent(config)  # 一時的にスキップ',
    'cloud_agent = CloudFixAgent(config)'
)

content = content.replace(
    'cloud_agent=None  # 一時的にスキップ',
    'cloud_agent=cloud_agent'
)

file.write_text(content)
print("✅ CloudFixAgent を再有効化")

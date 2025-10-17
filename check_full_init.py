#!/usr/bin/env python3
"""ReviewAgent.__init__の全コードを確認"""
import inspect
from core_agents.review_agent import ReviewAgent

print("📋 ReviewAgent.__init__ 全コード")
print("=" * 70)

source = inspect.getsource(ReviewAgent.__init__)
lines = source.split('\n')

for i, line in enumerate(lines, 1):
    print(f"{i:3}: {line}")

print("=" * 70)
print(f"総行数: {len(lines)}")

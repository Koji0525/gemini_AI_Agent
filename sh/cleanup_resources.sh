#!/bin/bash
# リソースクリーンアップ実行

cd /workspaces/gemini_AI_Agent

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.robustness.resource_cleaner import ResourceCleaner

cleaner = ResourceCleaner()
results = cleaner.cleanup_all()

PYTHON


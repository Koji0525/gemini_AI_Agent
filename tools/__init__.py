"""
Tools Package

各種ユーティリティツールを提供
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

__version__ = "1.0.0"
__author__ = "AI Agent System"

print(f"🔧 tools package initialized - Project root: {project_root}")

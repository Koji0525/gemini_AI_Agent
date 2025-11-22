"""
pytest設定・フィクスチャ
"""

import pytest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@pytest.fixture
def project_root():
    """プロジェクトルートパス"""
    return Path('/workspaces/gemini_AI_Agent')

@pytest.fixture
def config_path():
    """設定ファイルパス"""
    return Path('/workspaces/gemini_AI_Agent/config/observer_config.yaml')

@pytest.fixture
def sample_python_file(tmp_path):
    """テスト用Pythonファイル"""
    file_path = tmp_path / "sample.py"
    file_path.write_text("""
import sys
import os
from pathlib import Path

class SampleClass:
    def method(self):
        pass
""")
    return file_path

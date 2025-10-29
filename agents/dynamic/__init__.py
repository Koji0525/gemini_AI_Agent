"""
Dynamic Agent System
- Agent Generator: 動的エージェント生成
- Test Generator: 自動テスト生成（オプション）
"""

# 基本的なエージェント生成機能のみエクスポート
from .agent_generator import AgentGenerator

# test_generatorは存在する場合のみインポート
try:
    from .test_generator import AgentTestGenerator, TestGenerator, create_test_case

    __all__ = ["AgentGenerator", "AgentTestGenerator", "TestGenerator", "create_test_case"]
except ImportError:
    # test_generatorが存在しない場合はAgentGeneratorのみ
    __all__ = ["AgentGenerator"]
    print("⚠️ test_generator module not found - using AgentGenerator only")

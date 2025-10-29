"""
Week 6: 動的エージェント生成システム

エージェントを動的に生成・管理するシステム
"""

from .agent_template import (
    AgentTemplate,
    AgentMetadata,
    AgentConfig,
    SimpleAPIAgentTemplate,
    DataProcessingAgentTemplate
)
from .agent_generator import AgentGenerator

__all__ = [
    'AgentTemplate',
    'AgentMetadata',
    'AgentConfig',
    'SimpleAPIAgentTemplate',
    'DataProcessingAgentTemplate',
    'AgentGenerator',
]

"""
階層型組織アーキテクチャモジュール
Executive Manager → Team Leader → Worker の3階層構造
"""

from agents.hierarchy.executive_manager import ExecutiveManager
from agents.hierarchy.hierarchical_worker import HierarchicalWorker
# インポート順序重要: 依存関係の少ない順
from agents.hierarchy.messaging import (HierarchicalMessenger, Message,
                                        MessageBus, MessageType)
from agents.hierarchy.team_leader import TeamLeader

__all__ = [
    # Messaging
    "Message",
    "MessageType",
    "MessageBus",
    "HierarchicalMessenger",
    # Hierarchy
    "ExecutiveManager",
    "TeamLeader",
    "HierarchicalWorker",
]

__version__ = "1.0.0"

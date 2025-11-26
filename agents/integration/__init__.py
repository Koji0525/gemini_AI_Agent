"""
統合エージェントパッケージ

新規実装:
- shared_blackboard_manager: 共有黒板システム
- blackboard_history_viewer: 履歴管理
- legacy_bridge: 既存システム統合ブリッジ

既存の統合エージェント（progress_analyzer等）はインポートしない
（依存関係の問題を回避）
"""

# 新規実装のみをエクスポート
__all__ = [
    'SharedBlackboardManager',
    'BlackboardHistoryViewer', 
    'LegacySystemBridge'
]

# 遅延インポート（循環参照回避）
def get_shared_blackboard_manager():
    from .shared_blackboard_manager import SharedBlackboardManager
    return SharedBlackboardManager

def get_blackboard_history_viewer():
    from .blackboard_history_viewer import BlackboardHistoryViewer
    return BlackboardHistoryViewer

def get_legacy_bridge():
    from .legacy_bridge import LegacySystemBridge
    return LegacySystemBridge

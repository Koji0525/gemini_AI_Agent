"""
意思決定支援システム
パターンから修正戦略を生成
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DecisionSupportSystem:
    """修正戦略を提案するシステム"""

    def __init__(self):
        self.logger = logger

    async def decide(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        パターンから修正戦略を生成

        Args:
            patterns: 抽出されたパターンリスト

        Returns:
            修正戦略のリスト
        """
        strategies = []

        for pattern in patterns:
            strategy = {
                "pattern_id": pattern.get("id"),
                "error_type": pattern.get("error_type"),
                "recommended_action": self._generate_action(pattern),
                "confidence": pattern.get("confidence", 0.5),
                "priority": self._calculate_priority(pattern),
            }
            strategies.append(strategy)

        # 優先度順にソート
        strategies.sort(key=lambda x: x["priority"], reverse=True)

        return strategies

    def _generate_action(self, pattern: Dict[str, Any]) -> str:
        """修正アクションを生成"""
        error_type = pattern.get("error_type", "unknown")

        # エラータイプ別の推奨アクション
        action_map = {
            "ModuleNotFoundError": "パッケージ再インストール",
            "ImportError": "インポートパス修正",
            "AttributeError": "API仕様確認",
            "TypeError": "型変換追加",
        }

        return action_map.get(error_type, "手動調査")

    def _calculate_priority(self, pattern: Dict[str, Any]) -> float:
        """優先度を計算"""
        frequency = pattern.get("frequency", 1)
        confidence = pattern.get("confidence", 0.5)

        # 頻度と信頼度から優先度を算出
        return frequency * confidence

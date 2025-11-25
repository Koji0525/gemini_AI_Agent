"""
アラート管理システム

このモジュールは、システムの異常状態を検知し、
適切な通知を行います。

主要機能:
    - ヘルススコアに基づくアラート判定
    - 重要度レベル分類 (Low/Medium/High/Critical)
    - 通知の送信（ログ出力）
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# ロギング設定
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """アラートレベル"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertManager:
    """
    アラート管理クラス

    システムの健全性スコアや異常イベントを監視し、
    適切なアラートを生成・通知します。
    """

    def __init__(self):
        """初期化"""
        self.alert_history: List[Dict[str, Any]] = []
        logger.info("AlertManager 初期化完了")

    async def send_alert(
        self, health_score: float, details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        アラートを送信

        Args:
            health_score: ヘルススコア (0-100)
            details: 詳細情報

        Returns:
            bool: 送信成功
        """
        try:
            # アラートレベル判定
            level = self._determine_alert_level(health_score)

            # アラート生成
            alert = {
                "timestamp": datetime.now().isoformat(),
                "level": level.value,
                "health_score": health_score,
                "details": details or {},
            }

            # 履歴に追加
            self.alert_history.append(alert)

            # ログ出力
            log_method = self._get_log_method(level)
            log_method(
                f"🚨 アラート発生 [{level.value.upper()}] " f"ヘルススコア: {health_score:.1f}点"
            )

            if details:
                logger.info(f"詳細: {details}")

            return True

        except Exception as e:
            logger.error(f"アラート送信エラー: {e}")
            return False

    def _determine_alert_level(self, health_score: float) -> AlertLevel:
        """
        ヘルススコアからアラートレベルを判定

        Args:
            health_score: ヘルススコア (0-100)

        Returns:
            AlertLevel: アラートレベル
        """
        if health_score >= 80:
            return AlertLevel.LOW
        elif health_score >= 70:
            return AlertLevel.MEDIUM
        elif health_score >= 60:
            return AlertLevel.HIGH
        else:
            return AlertLevel.CRITICAL

    def _get_log_method(self, level: AlertLevel):
        """
        アラートレベルに応じたログメソッドを取得

        Args:
            level: アラートレベル

        Returns:
            logging method
        """
        level_map = {
            AlertLevel.LOW: logger.info,
            AlertLevel.MEDIUM: logger.warning,
            AlertLevel.HIGH: logger.error,
            AlertLevel.CRITICAL: logger.critical,
        }
        return level_map.get(level, logger.info)

    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        最近のアラートを取得

        Args:
            count: 取得件数

        Returns:
            List[Dict]: アラート一覧
        """
        return self.alert_history[-count:]


# テスト実行
if __name__ == "__main__":
    import asyncio

    async def test():
        manager = AlertManager()

        # テストアラート送信
        test_scores = [92, 75, 65, 45]

        for score in test_scores:
            await manager.send_alert(health_score=score, details={"test": True, "score": score})

        # 履歴確認
        print("\n📊 アラート履歴:")
        for alert in manager.get_recent_alerts():
            print(f"  - [{alert['level'].upper()}] {alert['health_score']}点")

    asyncio.run(test())

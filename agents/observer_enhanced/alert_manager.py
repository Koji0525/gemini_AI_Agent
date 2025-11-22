"""
アラート管理

このモジュールは、システムの異常を検知し、アラートを管理します。

主要機能:
    - アラート作成
    - アラートレベル判定 (info/warning/error/critical)
    - アラート履歴管理
    - 通知 (将来的にSlack/Email対応予定)
"""

import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """アラートレベル"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertManager:
    """
    アラート管理クラス

    Attributes:
        alerts (List[Dict]): アラート履歴
        alert_file (Path): アラート履歴ファイル
    """

    def __init__(self, alert_file: Optional[Path] = None):
        """
        初期化

        Args:
            alert_file: アラート履歴ファイルパス
        """
        if alert_file is None:
            alert_file = Path("logs/alerts.json")

        self.alert_file = Path(alert_file)
        self.alert_file.parent.mkdir(parents=True, exist_ok=True)

        # 既存アラートを読み込み
        self.alerts = self._load_alerts()

        logger.info(f"Initialized AlertManager with {len(self.alerts)} existing alerts")

    def create_alert(
        self, level: str, title: str, message: str, details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        アラートを作成

        Args:
            level: アラートレベル ('info', 'warning', 'error', 'critical')
            title: タイトル
            message: メッセージ
            details: 詳細情報 (オプション)

        Returns:
            Dict: 作成されたアラート
        """
        alert = {
            "id": str(uuid.uuid4()),
            "level": level,
            "title": title,
            "message": message,
            "details": details or {},
            "created_at": datetime.now().isoformat(),
            "resolved": False,
        }

        self.alerts.append(alert)
        self._save_alerts()

        # ログ出力
        log_level = {
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }.get(level, logging.INFO)

        logger.log(log_level, f"Alert created: {title} - {message}")

        return alert

    def get_alerts(
        self,
        level: Optional[str] = None,
        resolved: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        アラートを取得

        Args:
            level: フィルター用レベル
            resolved: 解決済みフラグでフィルター
            limit: 最大件数

        Returns:
            List[Dict]: アラートのリスト
        """
        filtered = self.alerts

        if level:
            filtered = [a for a in filtered if a["level"] == level]

        if resolved is not None:
            filtered = [a for a in filtered if a["resolved"] == resolved]

        # 最新順にソート
        filtered = sorted(filtered, key=lambda x: x["created_at"], reverse=True)

        if limit:
            filtered = filtered[:limit]

        return filtered

    def resolve_alert(self, alert_id: str) -> bool:
        """
        アラートを解決済みにする

        Args:
            alert_id: アラートID

        Returns:
            bool: 成功したかどうか
        """
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["resolved"] = True
                alert["resolved_at"] = datetime.now().isoformat()
                self._save_alerts()
                logger.info(f"Alert resolved: {alert_id}")
                return True

        logger.warning(f"Alert not found: {alert_id}")
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        アラート統計を取得

        Returns:
            Dict: 統計情報
        """
        total = len(self.alerts)
        unresolved = len([a for a in self.alerts if not a["resolved"]])

        by_level = {
            "info": len([a for a in self.alerts if a["level"] == "info"]),
            "warning": len([a for a in self.alerts if a["level"] == "warning"]),
            "error": len([a for a in self.alerts if a["level"] == "error"]),
            "critical": len([a for a in self.alerts if a["level"] == "critical"]),
        }

        return {"total_alerts": total, "unresolved_alerts": unresolved, "by_level": by_level}

    def _load_alerts(self) -> List[Dict[str, Any]]:
        """アラート履歴を読み込み"""
        if not self.alert_file.exists():
            return []

        try:
            with open(self.alert_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load alerts: {e}")
            return []

    def _save_alerts(self) -> None:
        """アラート履歴を保存"""
        try:
            with open(self.alert_file, "w", encoding="utf-8") as f:
                json.dump(self.alerts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")


def main():
    """メイン関数 (テスト用)"""
    print("🚨 AlertManager Test")

    manager = AlertManager(Path("logs/test_alerts.json"))

    # テストアラートを作成
    alert1 = manager.create_alert(
        level="warning", title="Test Warning", message="This is a test warning alert"
    )
    print(f"\n✅ Created alert: {alert1['id']}")

    alert2 = manager.create_alert(
        level="error",
        title="Test Error",
        message="This is a test error alert",
        details={"error_code": "TEST001"},
    )
    print(f"✅ Created alert: {alert2['id']}")

    # 統計を表示
    stats = manager.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total alerts: {stats['total_alerts']}")
    print(f"  Unresolved: {stats['unresolved_alerts']}")
    print(f"  By level: {stats['by_level']}")

    # アラートを解決
    manager.resolve_alert(alert1["id"])
    print(f"\n✅ Resolved alert: {alert1['id']}")

    print("\n✅ AlertManager test completed")


if __name__ == "__main__":
    main()

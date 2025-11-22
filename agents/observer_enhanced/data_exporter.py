"""
データエクスポート機能

システムデータをJSON/CSV形式でエクスポート
"""

import csv
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataExporter:
    """データエクスポートマネージャー"""

    def __init__(self):
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
        logger.info(f"Initialized DataExporter with export dir: {self.export_dir}")

    def export_health_history(self, format: str = "json", days: int = 7) -> Optional[str]:
        """
        ヘルススコア履歴をエクスポート

        Args:
            format: 出力形式（json/csv）
            days: 過去何日分

        Returns:
            エクスポートファイルパス
        """
        try:
            # TODO: 実装（ヘルススコア履歴の取得）
            data = {
                "export_date": datetime.now().isoformat(),
                "format": format,
                "days": days,
                "records": [],
            }

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_history_{timestamp}.{format}"
            filepath = self.export_dir / filename

            if format == "json":
                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)
            elif format == "csv":
                # CSV形式の実装
                pass

            logger.info(f"Health history exported to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to export health history: {e}")
            return None

    def export_traces(self, format: str = "json", hours: int = 24) -> Optional[str]:
        """
        トレースログをエクスポート

        Args:
            format: 出力形式（json/csv）
            hours: 過去何時間分

        Returns:
            エクスポートファイルパス
        """
        try:
            db_path = Path("logs/traces.db")
            if not db_path.exists():
                logger.warning("Traces database not found")
                return None

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            query = """
                SELECT * FROM traces
                WHERE timestamp >= datetime('now', ? || ' hours')
                ORDER BY timestamp DESC
            """

            cursor.execute(query, (f"-{hours}",))
            rows = cursor.fetchall()

            # カラム名取得
            columns = [desc[0] for desc in cursor.description]

            conn.close()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"traces_{timestamp}.{format}"
            filepath = self.export_dir / filename

            if format == "json":
                data = {
                    "export_date": datetime.now().isoformat(),
                    "hours": hours,
                    "count": len(rows),
                    "traces": [dict(zip(columns, row)) for row in rows],
                }

                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)

            elif format == "csv":
                with open(filepath, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    writer.writerows(rows)

            logger.info(f"Traces exported to {filepath}: {len(rows)} records")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to export traces: {e}")
            return None

    def export_graph(self, format: str = "json") -> Optional[str]:
        """
        依存関係グラフをエクスポート

        Args:
            format: 出力形式（json/graphml）

        Returns:
            エクスポートファイルパス
        """
        try:
            graph_path = Path("logs/system_graph.json")
            if not graph_path.exists():
                logger.warning("Graph file not found")
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dependency_graph_{timestamp}.{format}"
            filepath = self.export_dir / filename

            if format == "json":
                # JSONはそのままコピー
                with open(graph_path) as src:
                    data = json.load(src)

                # メタデータ追加
                data["export_date"] = datetime.now().isoformat()

                with open(filepath, "w") as dst:
                    json.dump(data, dst, indent=2)

            elif format == "graphml":
                # GraphML形式の実装
                # TODO: NetworkXを使用してGraphML変換
                pass

            logger.info(f"Graph exported to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to export graph: {e}")
            return None

    def export_alerts(self, format: str = "json", days: int = 7) -> Optional[str]:
        """
        アラート履歴をエクスポート

        Args:
            format: 出力形式（json/csv）
            days: 過去何日分

        Returns:
            エクスポートファイルパス
        """
        try:
            alerts_path = Path("logs/alerts.json")
            if not alerts_path.exists():
                logger.warning("Alerts file not found")
                return None

            with open(alerts_path) as f:
                all_alerts = json.load(f)

            # 日付フィルタリング
            # TODO: 実装（日付による絞り込み）

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alerts_{timestamp}.{format}"
            filepath = self.export_dir / filename

            if format == "json":
                data = {
                    "export_date": datetime.now().isoformat(),
                    "days": days,
                    "count": len(all_alerts),
                    "alerts": all_alerts,
                }

                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)

            elif format == "csv":
                with open(filepath, "w", newline="") as f:
                    if all_alerts:
                        writer = csv.DictWriter(f, fieldnames=all_alerts[0].keys())
                        writer.writeheader()
                        writer.writerows(all_alerts)

            logger.info(f"Alerts exported to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to export alerts: {e}")
            return None

    def list_exports(self) -> List[Dict[str, Any]]:
        """
        エクスポートファイル一覧を取得

        Returns:
            ファイル情報のリスト
        """
        try:
            files = []
            for filepath in self.export_dir.glob("*"):
                if filepath.is_file():
                    stat = filepath.stat()
                    files.append(
                        {
                            "filename": filepath.name,
                            "size": stat.st_size,
                            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            "path": str(filepath),
                        }
                    )

            # 作成日時でソート（新しい順）
            files.sort(key=lambda x: x["created"], reverse=True)

            return files

        except Exception as e:
            logger.error(f"Failed to list exports: {e}")
            return []


# テストコード
if __name__ == "__main__":
    pass

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    exporter = DataExporter()

    print("【DataExporter テスト】")
    print()

    # 1. トレースエクスポート
    print("1. トレースエクスポート（JSON）...")
    traces_json = exporter.export_traces(format="json", hours=24)
    if traces_json:
        print(f"   ✅ {traces_json}")
    else:
        print(f"   ⚠️  エクスポート失敗")

    # 2. グラフエクスポート
    print("\n2. グラフエクスポート（JSON）...")
    graph_json = exporter.export_graph(format="json")
    if graph_json:
        print(f"   ✅ {graph_json}")
    else:
        print(f"   ⚠️  エクスポート失敗")

    # 3. アラートエクスポート
    print("\n3. アラートエクスポート（JSON）...")
    alerts_json = exporter.export_alerts(format="json", days=7)
    if alerts_json:
        print(f"   ✅ {alerts_json}")
    else:
        print(f"   ⚠️  エクスポート失敗")

    # 4. エクスポート一覧
    print("\n4. エクスポート一覧...")
    exports = exporter.list_exports()
    print(f"   総数: {len(exports)}件")
    for exp in exports[:3]:  # 最新3件
        print(f"   - {exp['filename']} ({exp['size']} bytes)")

    print("\n✅ DataExporter テスト完了")

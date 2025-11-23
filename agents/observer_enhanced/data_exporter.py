"""
Data Exporter - データエクスポート機能
Phase 5: データ出力
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("observer_enhanced.data_exporter")


class DataExporter:
    """データエクスポートクラス"""

    def __init__(self, output_dir: str = "exports"):
        """初期化"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
        self.logger.info("Initialized DataExporter")

    def export_json(self, data: Dict, filename: str = None) -> str:
        """JSON形式でエクスポート"""
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        file_path = self.output_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Exported JSON: {file_path}")
        return str(file_path)

    def export_csv(self, data: List[Dict], filename: str = None) -> str:
        """CSV形式でエクスポート"""
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        if not data:
            return None

        file_path = self.output_dir / filename

        keys = data[0].keys()
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

        self.logger.info(f"Exported CSV: {file_path}")
        return str(file_path)

    def export_html_report(self, data: Dict, filename: str = None) -> str:
        """HTMLレポート形式でエクスポート"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        file_path = self.output_dir / filename

        html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>システム分析レポート</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>システム分析レポート</h1>
    <p>生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>統計情報</h2>
    <pre>{json.dumps(data.get('stats', {}), indent=2, ensure_ascii=False)}</pre>
    
    <h2>重複ファイル</h2>
    <p>検出数: {len(data.get('duplicates', {}))}</p>
    
    <h2>未使用ファイル</h2>
    <p>検出数: {len(data.get('unused_files', []))}</p>
</body>
</html>
"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)

        self.logger.info(f"Exported HTML report: {file_path}")
        return str(file_path)

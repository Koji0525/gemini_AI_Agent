#!/usr/bin/env python3
"""
リアルタイムダッシュボード v2
Chart.js統合版

【機能】
1. システムヘルス監視
2. 階層型組織図表示
3. タスクDAG可視化
4. 品質トレンドグラフ（Chart.js）
5. アラート通知

Google Docstring形式
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

try:
    import uvicorn
    from fastapi import FastAPI, WebSocket
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:
    print("❌ FastAPIが見つかりません: pip install fastapi uvicorn")
    exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CompleteEngine Dashboard v2")

# 静的ファイル
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class DashboardDataCollector:
    """ダッシュボードデータ収集

    システム全体の状態を収集してJSON形式で提供

    Attributes:
        project_root (Path): プロジェクトルート
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent

    async def collect_all(self) -> Dict:
        """全データを収集

        Returns:
            ダッシュボード用データ辞書
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": await self._get_system_health(),
            "hierarchy": await self._get_hierarchy_status(),
            "tasks": await self._get_task_summary(),
            "quality": await self._get_quality_metrics(),
            "alerts": await self._get_alerts(),
        }

    async def _get_system_health(self) -> Dict:
        """システムヘルス取得"""
        # 簡易版（実際はsystem_health_check.shを実行）
        return {
            "status": "healthy",
            "test_success_rate": 84.3,
            "memory_usage_mb": 1200,
            "disk_usage_gb": 4.5,
            "agent_count": 30,
        }

    async def _get_hierarchy_status(self) -> Dict:
        """階層型組織状態"""
        return {
            "executive": {"status": "active", "goals_managing": 3},
            "teams": [
                {"name": "Data Team", "leader": "TL_001", "progress": 80},
                {"name": "Analysis Team", "leader": "TL_002", "progress": 60},
                {"name": "Report Team", "leader": "TL_003", "progress": 40},
            ],
            "workers": {"total": 20, "active": 15, "idle": 5},
        }

    async def _get_task_summary(self) -> Dict:
        """タスク概要"""
        return {
            "total": 456,
            "completed": 309,
            "in_progress": 98,
            "pending": 49,
            "completion_rate": 67.8,
        }

    async def _get_quality_metrics(self) -> Dict:
        """品質メトリクス"""
        return {
            "avg_score": 82.5,
            "reflexion_loops": 45,
            "success_rate": 73.3,
            "trend": [60, 65, 70, 75, 80, 82.5],  # 過去6サイクル
        }

    async def _get_alerts(self) -> List[Dict]:
        """アラート一覧"""
        return [
            {
                "level": "warning",
                "message": "Task 105の品質スコアが50点",
                "timestamp": "2025-11-26T15:00:00",
            },
            {
                "level": "info",
                "message": "Team Leader Aが新規タスクを追加",
                "timestamp": "2025-11-26T14:30:00",
            },
        ]


# データコレクター初期化
collector = DashboardDataCollector()


@app.get("/")
async def root():
    """ダッシュボードHTML（v2）"""
    html_path = Path(__file__).parent / "templates" / "dashboard_v2.html"

    if not html_path.exists():
        # v1にフォールバック
        html_path = Path(__file__).parent / "templates" / "dashboard.html"

    if not html_path.exists():
        return HTMLResponse(
            """
        <html>
        <head><title>Dashboard</title></head>
        <body>
            <h1>CompleteEngine Dashboard (Mock)</h1>
            <p>テンプレートファイルを作成中...</p>
            <pre id="data"></pre>
            <script>
                async function fetchData() {
                    const res = await fetch('/api/data');
                    const data = await res.json();
                    document.getElementById('data').textContent = JSON.stringify(data, null, 2);
                }
                setInterval(fetchData, 5000);
                fetchData();
            </script>
        </body>
        </html>
        """
        )

    with open(html_path, "r") as f:
        return HTMLResponse(f.read())


@app.get("/api/data")
async def get_data():
    """データAPI"""
    return await collector.collect_all()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocketエンドポイント（リアルタイム更新）

    Args:
        websocket: WebSocket接続
    """
    await websocket.accept()
    logger.info("🔌 WebSocket接続確立")

    try:
        while True:
            # 10秒ごとにデータ送信
            data = await collector.collect_all()
            await websocket.send_json(data)
            await asyncio.sleep(10)
    except Exception as e:
        logger.error(f"❌ WebSocketエラー: {e}")
    finally:
        logger.info("🔌 WebSocket切断")


def start_dashboard(host: str = "0.0.0.0", port: int = 8000):
    """ダッシュボード起動

    Args:
        host: ホストアドレス
        port: ポート番号
    """
    logger.info(f"🚀 ダッシュボード起動: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_dashboard()

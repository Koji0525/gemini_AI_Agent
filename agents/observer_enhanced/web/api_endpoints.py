"""
Enhanced Observer REST API

このモジュールは、強化版オブザーバーシステムのREST APIを提供します。

主要エンドポイント:
    - GET /api/health - ヘルススコア取得
    - GET /api/graph - 依存関係グラフ取得
    - GET /api/traces - トレースログ取得
    - GET /api/alerts - アラート一覧取得
    - POST /api/analyze - 影響範囲分析実行

技術スタック:
    - FastAPI: 高速なWeb APIフレームワーク
    - Uvicorn: ASGI サーバー
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# FastAPIのインポート
try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
except ImportError:
    print("Error: FastAPI and Uvicorn are required.")
    print("Install with: pip install fastapi uvicorn --break-system-packages")
    sys.exit(1)

# 内部モジュールのインポート
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
try:
    from agents.observer_enhanced.alert_manager import AlertManager
    from agents.observer_enhanced.graph_db import SystemGraphDB
    from agents.observer_enhanced.health_checker import HealthChecker
    from agents.observer_enhanced.impact_analyzer import ImpactAnalyzer
    from agents.observer_enhanced.tracer import ExecutionTracer
except ImportError as e:
    print(f"Error importing observer_enhanced modules: {e}")
    sys.exit(1)

# ロガー設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション初期化
app = FastAPI(
    title="Enhanced Observer API",
    description="強化版オブザーバーシステム REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバルインスタンス
health_checker = HealthChecker()
tracer = ExecutionTracer()
graph_db = SystemGraphDB()
alert_manager = AlertManager()
impact_analyzer = ImpactAnalyzer()

logger.info("Enhanced Observer API initialized")


# ============================================================
# ヘルスチェック系エンドポイント
# ============================================================


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    ルートエンドポイント

    簡易的なHTML画面を返す
    """
    html_content = (
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enhanced Observer API</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            h1 { margin-top: 0; font-size: 2.5em; }
            .status { 
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .endpoint {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #4ade80;
            }
            .method {
                display: inline-block;
                padding: 4px 12px;
                background: #4ade80;
                border-radius: 4px;
                font-weight: bold;
                font-size: 0.9em;
                color: #1a1a1a;
            }
            a { color: #4ade80; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Enhanced Observer API</h1>
            <div class="status">
                <h2>✅ System Status: Running</h2>
                <p>API Version: 1.0.0</p>
                <p>Start Time: """
        + datetime.now().isoformat()
        + """</p>
            </div>
            
            <h2>📚 Available Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <a href="/api/health">/api/health</a>
                <p>システムのヘルススコアを取得</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <a href="/api/graph">/api/graph</a>
                <p>依存関係グラフを取得</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <a href="/api/traces">/api/traces</a>
                <p>トレースログを取得</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <a href="/api/alerts">/api/alerts</a>
                <p>アラート一覧を取得</p>
            </div>
            
            <h2>📖 Documentation</h2>
            <p>
                <a href="/docs">Swagger UI</a> | 
                <a href="/redoc">ReDoc</a>
            </p>
        </div>
    </body>
    </html>
    """
    )
    return HTMLResponse(content=html_content)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """
    簡易Webダッシュボード

    リアルタイムでシステム状態を可視化
    """
    template_path = Path(__file__).parent / "templates" / "dashboard_simple.html"

    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard template not found")

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)


@app.get("/api/health")
async def get_health():
    """
    ヘルススコア取得

    Returns:
        Dict: ヘルスレポート
            - overall_score: 総合スコア (0-100)
            - grade: グレード (A-F)
            - component_scores: 各項目のスコア
            - recommendations: 改善推奨事項
    """
    try:
        report = health_checker.calculate_health_score()

        return {"status": "ok", "timestamp": datetime.now().isoformat(), "health": report}
    except Exception as e:
        logger.error(f"Error in get_health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph")
async def get_graph(limit: Optional[int] = Query(None, description="最大ノード数")):
    """
    依存関係グラフ取得

    Args:
        limit: 返すノードの最大数（Noneの場合は全て）

    Returns:
        Dict: グラフデータ
            - nodes: ノードのリスト
            - edges: エッジのリスト
            - metrics: 統計情報
    """
    try:
        # グラフデータをエクスポート
        temp_path = Path("/tmp/temp_graph.json")
        graph_db.save(temp_path)

        with open(temp_path, "r") as f:
            data = json.load(f)

        # limitが指定されている場合、ノードを制限
        if limit:
            data["nodes"] = data["nodes"][:limit]
            # エッジもフィルタ
            node_ids = {node["id"] for node in data["nodes"]}
            data["edges"] = [
                edge
                for edge in data["edges"]
                if edge["source"] in node_ids and edge["target"] in node_ids
            ]

        return {"status": "ok", "timestamp": datetime.now().isoformat(), "graph": data}
    except Exception as e:
        logger.error(f"Error in get_graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/traces")
async def get_traces(
    minutes: int = Query(10, description="何分前まで取得するか"),
    limit: int = Query(100, description="最大件数"),
):
    """
    トレースログ取得

    Args:
        minutes: 何分前まで取得するか (デフォルト: 10)
        limit: 最大件数 (デフォルト: 100)

    Returns:
        Dict: トレースログ
            - traces: トレースのリスト
            - count: 件数
            - statistics: 統計情報
    """
    try:
        traces = tracer.get_recent_traces(minutes=minutes, limit=limit)
        stats = tracer.get_statistics()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "traces": traces,
            "count": len(traces),
            "statistics": stats,
        }
    except Exception as e:
        logger.error(f"Error in get_traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts(
    level: Optional[str] = Query(None, description="フィルター用レベル"),
    resolved: Optional[bool] = Query(None, description="解決済みフラグ"),
    limit: Optional[int] = Query(50, description="最大件数"),
):
    """
    アラート一覧取得

    Args:
        level: フィルター用レベル ('info', 'warning', 'error', 'critical')
        resolved: 解決済みフラグでフィルター
        limit: 最大件数

    Returns:
        Dict: アラート一覧
            - alerts: アラートのリスト
            - count: 件数
            - statistics: 統計情報
    """
    try:
        alerts = alert_manager.get_alerts(level=level, resolved=resolved, limit=limit)
        stats = alert_manager.get_statistics()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "count": len(alerts),
            "statistics": stats,
        }
    except Exception as e:
        logger.error(f"Error in get_alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_impact(
    component_id: str = Query(..., description="変更対象コンポーネントID"),
    depth: int = Query(3, description="探索深さ"),
):
    """
    影響範囲分析実行

    Args:
        component_id: 変更対象コンポーネントID
        depth: 探索深さ (デフォルト: 3)

    Returns:
        Dict: 影響範囲分析レポート
            - component_id: 変更対象
            - risk_level: リスクレベル
            - impact_summary: 影響サマリー
            - affected_components: 影響を受けるコンポーネント
            - recommended_tests: 推奨テスト
    """
    try:
        report = impact_analyzer.analyze_component_change(component_id=component_id, depth=depth)

        return {"status": "ok", "timestamp": datetime.now().isoformat(), "analysis": report}
    except Exception as e:
        logger.error(f"Error in analyze_impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# サーバー起動
# ============================================================


def start_server(host: str = "0.0.0.0", port: int = 5000):
    """
    APIサーバーを起動

    Args:
        host: ホスト (デフォルト: 0.0.0.0)
        port: ポート (デフォルト: 5000)
    """
    logger.info(f"Starting Enhanced Observer API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 4: メトリクスAPI（P4-001, P4-002）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@app.get("/api/metrics/current")
async def get_current_metrics():
    """
    現在のシステムメトリクスを取得

    CPU、メモリ、ディスク、ネットワークなどのリアルタイムメトリクス
    """
    try:
        from agents.observer_enhanced.metrics_collector import \
            get_metrics_collector

        collector = get_metrics_collector()
        metrics = collector.collect_system_metrics()

        return {"status": "ok", "timestamp": datetime.now().isoformat(), "metrics": metrics}
    except Exception as e:
        logger.error(f"Error in get_current_metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/history")
async def get_metrics_history(minutes: int = 10, limit: int = 100):
    """
    メトリクス履歴を取得

    Args:
        minutes: サマリーの時間範囲（分）
        limit: 取得する最大件数
    """
    try:
        from agents.observer_enhanced.metrics_collector import \
            get_metrics_collector

        collector = get_metrics_collector()

        return {
            "status": "ok",
            "summary": collector.get_metrics_summary(minutes=minutes),
            "history": collector.get_all_metrics(limit=limit),
        }
    except Exception as e:
        logger.error(f"Error in get_metrics_history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/performance/status")
async def get_performance_status():
    """
    現在のパフォーマンスステータスを取得

    メトリクスを分析してパフォーマンス評価
    """
    try:
        from agents.observer_enhanced.metrics_collector import \
            get_metrics_collector
        from agents.observer_enhanced.performance_monitor import \
            get_performance_monitor

        collector = get_metrics_collector()
        monitor = get_performance_monitor()

        # 現在のメトリクスを収集
        metrics = collector.collect_system_metrics()

        # パフォーマンス分析
        analysis = monitor.analyze_metrics(metrics)

        return {"status": "ok", "timestamp": datetime.now().isoformat(), "performance": analysis}
    except Exception as e:
        logger.error(f"Error in get_performance_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/performance/trends")
async def get_performance_trends(minutes: int = 60):
    """
    パフォーマンストレンドを取得

    Args:
        minutes: 分析期間（分）
    """
    try:
        from agents.observer_enhanced.metrics_collector import \
            get_metrics_collector
        from agents.observer_enhanced.performance_monitor import \
            get_performance_monitor

        collector = get_metrics_collector()
        monitor = get_performance_monitor()

        # メトリクス履歴を取得
        history = collector.get_all_metrics(limit=1000)

        # トレンド分析
        trends = monitor.get_performance_trends(history, minutes=minutes)

        return {"status": "ok", "timestamp": datetime.now().isoformat(), "trends": trends}
    except Exception as e:
        logger.error(f"Error in get_performance_trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/performance/alerts")
async def get_performance_alerts(limit: int = 20, hours: int = 24):
    """
    パフォーマンスアラートを取得

    Args:
        limit: 取得する最大件数
        hours: サマリーの集計期間（時間）
    """
    try:
        from agents.observer_enhanced.performance_monitor import \
            get_performance_monitor

        monitor = get_performance_monitor()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "alerts": monitor.get_recent_alerts(limit=limit),
            "summary": monitor.get_alert_summary(hours=hours),
        }
    except Exception as e:
        logger.error(f"Error in get_performance_alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Observer API Server")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0)"
    )
    parser.add_argument("--port", type=int, default=5000, help="Port number (default: 5000)")

    args = parser.parse_args()
    start_server(host=args.host, port=args.port)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# エクスポート機能（P4-006）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from fastapi.responses import FileResponse

from agents.observer_enhanced.data_exporter import DataExporter

# エクスポーター初期化
data_exporter = DataExporter()


@app.get("/api/export/traces")
async def export_traces(format: str = "json", hours: int = 24):
    """トレースログをエクスポート"""
    try:
        filepath = data_exporter.export_traces(format=format, hours=hours)
        if filepath:
            return FileResponse(
                filepath,
                media_type="application/json" if format == "json" else "text/csv",
                filename=Path(filepath).name,
            )
        else:
            raise HTTPException(status_code=500, detail="Export failed")
    except Exception as e:
        logger.error(f"Export traces error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/graph")
async def export_graph(format: str = "json"):
    """依存関係グラフをエクスポート"""
    try:
        filepath = data_exporter.export_graph(format=format)
        if filepath:
            return FileResponse(
                filepath, media_type="application/json", filename=Path(filepath).name
            )
        else:
            raise HTTPException(status_code=500, detail="Export failed")
    except Exception as e:
        logger.error(f"Export graph error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/alerts")
async def export_alerts(format: str = "json", days: int = 7):
    """アラート履歴をエクスポート"""
    try:
        filepath = data_exporter.export_alerts(format=format, days=days)
        if filepath:
            return FileResponse(
                filepath,
                media_type="application/json" if format == "json" else "text/csv",
                filename=Path(filepath).name,
            )
        else:
            raise HTTPException(status_code=500, detail="Export failed")
    except Exception as e:
        logger.error(f"Export alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/list")
async def list_exports():
    """エクスポートファイル一覧"""
    try:
        exports = data_exporter.list_exports()
        return {"exports": exports, "count": len(exports)}
    except Exception as e:
        logger.error(f"List exports error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 通知システム（P4-007）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from agents.observer_enhanced.notification_manager import (
    NotificationManager, NotificationPriority)

# 通知マネージャー初期化
notification_manager = NotificationManager()


@app.post("/api/notifications/send")
async def send_notification(title: str, message: str, priority: str = "medium"):
    """通知送信"""
    try:
        priority_map = {
            "low": NotificationPriority.LOW,
            "medium": NotificationPriority.MEDIUM,
            "high": NotificationPriority.HIGH,
            "critical": NotificationPriority.CRITICAL,
        }

        priority_enum = priority_map.get(priority, NotificationPriority.MEDIUM)

        success = notification_manager.send_notification(
            title=title, message=message, priority=priority_enum
        )

        return {"success": success, "title": title, "priority": priority}
    except Exception as e:
        logger.error(f"Send notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notifications/history")
async def get_notification_history(limit: int = 50, priority: Optional[str] = None):
    """通知履歴取得"""
    try:
        priority_enum = None
        if priority:
            priority_map = {
                "low": NotificationPriority.LOW,
                "medium": NotificationPriority.MEDIUM,
                "high": NotificationPriority.HIGH,
                "critical": NotificationPriority.CRITICAL,
            }
            priority_enum = priority_map.get(priority)

        history = notification_manager.get_history(limit=limit, priority=priority_enum)

        return {"history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Get notification history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notifications/test")
async def test_notification():
    """通知テスト"""
    try:
        success = notification_manager.send_notification(
            title="テスト通知",
            message=f"通知システムのテストです（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）",
            priority=NotificationPriority.LOW,
        )

        return {"success": success, "message": "Test notification sent"}
    except Exception as e:
        logger.error(f"Test notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

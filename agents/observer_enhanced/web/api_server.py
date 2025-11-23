"""
依存関係可視化システム API Server
Phase 0-3完全版（ダッシュボード対応）
"""

import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI アプリケーション
app = FastAPI(
    title="依存関係可視化システム API",
    description="Pythonプロジェクトの依存関係を可視化するAPI",
    version="1.0.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グラフデータをメモリに保持
graph_data = None


def load_graph_data():
    """グラフデータを読み込む"""
    global graph_data

    try:
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent
        graph_file = project_root / "docs" / "dependency_map.json"

        logger.info(f"📂 グラフファイルパス: {graph_file}")

        if not graph_file.exists():
            logger.error(f"❌ グラフファイルが見つかりません: {graph_file}")
            graph_data = {"nodes": [], "edges": [], "metadata": {"error": "File not found"}}
            return graph_data

        with open(graph_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        logger.info(f"✅ グラフデータ読み込み成功")
        logger.info(f"   - ノード数: {len(nodes)}")
        logger.info(f"   - エッジ数: {len(edges)}")

        graph_data = {"nodes": nodes, "edges": edges, "metadata": data.get("metadata", {})}

        return graph_data

    except Exception as e:
        logger.error(f"❌ グラフデータ読み込みエラー: {e}")
        graph_data = {"nodes": [], "edges": [], "metadata": {"error": str(e)}}
        return graph_data


def calculate_signal(imported_by_count: int) -> str:
    """被依存数から信号機を計算"""
    if imported_by_count >= 20:
        return "🔴"
    elif imported_by_count >= 10:
        return "🟡"
    elif imported_by_count >= 1:
        return "🟢"
    else:
        return "💤"


def calculate_risk_level(imported_by_count: int) -> str:
    """リスクレベルを計算"""
    if imported_by_count >= 20:
        return "high"
    elif imported_by_count >= 10:
        return "medium"
    elif imported_by_count >= 1:
        return "low"
    else:
        return "unused"


def analyze_signals(graph_data: dict) -> dict:
    """全ファイルの信号機を分析"""
    nodes = graph_data.get("nodes", [])

    signal_counts = {"🔴": 0, "🟡": 0, "🟢": 0, "💤": 0}
    signals_by_file = []

    for node in nodes:
        imported_by_count = len(node.get("imported_by", []))
        signal = calculate_signal(imported_by_count)
        risk_level = calculate_risk_level(imported_by_count)

        signal_counts[signal] += 1

        signals_by_file.append(
            {
                "path": node.get("path", ""),
                "filename": node.get("filename", ""),
                "imported_by_count": imported_by_count,
                "signal": signal,
                "risk_level": risk_level,
            }
        )

    signals_by_file.sort(key=lambda x: x["imported_by_count"], reverse=True)

    return {
        "total_files": len(nodes),
        "signal_counts": signal_counts,
        "high_risk_files": [f for f in signals_by_file if f["risk_level"] == "high"],
        "medium_risk_files": [f for f in signals_by_file if f["risk_level"] == "medium"],
        "low_risk_files": [f for f in signals_by_file if f["risk_level"] == "low"],
        "unused_files": [f for f in signals_by_file if f["risk_level"] == "unused"],
        "all_files": signals_by_file,
    }


@app.on_event("startup")
async def startup_event():
    """起動時処理"""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🚀 依存関係可視化システム API 起動")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    load_graph_data()
    if graph_data and len(graph_data.get("nodes", [])) > 0:
        logger.info(f"✅ グラフデータ読み込み成功: {len(graph_data['nodes'])} ノード")


@app.on_event("shutdown")
async def shutdown_event():
    """終了時処理"""
    logger.info("👋 API Server シャットダウン")


@app.get("/")
async def root():
    """ルート - ダッシュボードにリダイレクト"""
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard")
async def dashboard():
    """ダッシュボードを表示"""
    dashboard_file = Path(__file__).parent / "dashboard" / "index.html"
    if not dashboard_file.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return FileResponse(dashboard_file)


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}


@app.get("/api/dependencies")
async def get_dependencies():
    """依存関係データを取得"""
    global graph_data

    if graph_data is None:
        load_graph_data()

    if graph_data is None or len(graph_data.get("nodes", [])) == 0:
        return {"nodes": [], "edges": [], "metadata": {"error": "No data"}}

    return graph_data


@app.get("/api/signals")
async def get_signals():
    """信号機データを取得"""
    global graph_data

    if graph_data is None:
        load_graph_data()

    if graph_data is None or len(graph_data.get("nodes", [])) == 0:
        return {
            "total_files": 0,
            "signal_counts": {"🔴": 0, "🟡": 0, "🟢": 0, "💤": 0},
            "high_risk_files": [],
            "all_files": [],
        }

    result = analyze_signals(graph_data)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)

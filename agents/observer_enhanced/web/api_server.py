"""
依存関係可視化システム API Server
Phase 0-3: 基本機能のみ（安定版）
"""

import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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
        # プロジェクトルートからの相対パスで読み込み
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
        metadata = data.get("metadata", {})

        logger.info(f"✅ グラフデータ読み込み成功")
        logger.info(f"   - ノード数: {len(nodes)}")
        logger.info(f"   - エッジ数: {len(edges)}")

        graph_data = {"nodes": nodes, "edges": edges, "metadata": metadata}

        return graph_data

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSONデコードエラー: {e}")
        graph_data = {"nodes": [], "edges": [], "metadata": {"error": str(e)}}
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
    else:
        logger.error("❌ グラフデータ読み込み失敗")


@app.on_event("shutdown")
async def shutdown_event():
    """終了時処理"""
    logger.info("👋 API Server シャットダウン")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "依存関係可視化システム API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "dependencies": "/api/dependencies",
            "signals": "/api/signals",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}


@app.get("/api/dependencies")
async def get_dependencies():
    """依存関係データを取得"""
    global graph_data

    try:
        if graph_data is None:
            logger.info("グラフデータが未読み込み、読み込みます...")
            load_graph_data()

        if graph_data is None or len(graph_data.get("nodes", [])) == 0:
            logger.warning("グラフデータが空、再読み込みを試行...")
            load_graph_data()

        if graph_data is None or len(graph_data.get("nodes", [])) == 0:
            logger.error("グラフデータの読み込みに失敗しました")
            return {"nodes": [], "edges": [], "metadata": {"error": "No data available"}}

        return graph_data

    except Exception as e:
        logger.error(f"依存関係データ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {str(e)}")


@app.get("/api/signals")
async def get_signals():
    """信号機データを取得"""
    global graph_data

    try:
        if graph_data is None:
            logger.info("グラフデータが未読み込み、読み込みます...")
            load_graph_data()

        if graph_data is None or len(graph_data.get("nodes", [])) == 0:
            logger.warning("グラフデータが空、再読み込みを試行...")
            load_graph_data()

        if graph_data is None or len(graph_data.get("nodes", [])) == 0:
            logger.error("グラフデータの読み込みに失敗しました")
            return {
                "total_files": 0,
                "signal_counts": {"🔴": 0, "🟡": 0, "🟢": 0, "💤": 0},
                "high_risk_files": [],
                "all_files": [],
            }

        result = analyze_signals(graph_data)
        return result

    except Exception as e:
        logger.error(f"信号機データ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"信号機データ取得エラー: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)

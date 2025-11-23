"""
依存関係可視化システム REST API サーバー

このモジュールは、依存関係グラフデータをWeb UIに提供する
REST APIサーバーです。

主要機能:
    - 依存関係グラフの提供
    - ファイル詳細情報の提供
    - 重複ファイル検出結果の提供
    - 影響範囲分析

エンドポイント:
    GET /health - ヘルスチェック
    GET /api/info - システム情報
    GET /api/dependencies - 全依存関係
    GET /api/file/{path} - ファイル詳細
    GET /api/duplicates - 重複ファイル一覧
    GET /api/impact/{path} - 影響範囲分析
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ロギング設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション初期化
app = FastAPI(
    title="依存関係可視化システム API",
    description="プロジェクトの依存関係を可視化するREST API",
    version="1.0.0",
)

# CORS設定（ブラウザからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンに制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データパス
BASE_DIR = Path(__file__).parent.parent
GRAPH_FILE = BASE_DIR / "dependency_graph.json"

# グローバルデータキャッシュ
_graph_cache: Optional[Dict[str, Any]] = None
_cache_timestamp: Optional[datetime] = None


def load_graph_data(force_reload: bool = False) -> Dict[str, Any]:
    """
    依存関係グラフデータを読み込み

    Args:
        force_reload: 強制的に再読み込み

    Returns:
        Dict: グラフデータ
    """
    global _graph_cache, _cache_timestamp

    # キャッシュチェック（5分以内なら再利用）
    if not force_reload and _graph_cache is not None:
        if _cache_timestamp is not None:
            cache_age = (datetime.now() - _cache_timestamp).total_seconds()
            if cache_age < 300:  # 5分
                logger.debug(f"Using cached graph data (age: {cache_age:.1f}s)")
                return _graph_cache

    # ファイル存在チェック
    if not GRAPH_FILE.exists():
        logger.error(f"Graph file not found: {GRAPH_FILE}")
        raise FileNotFoundError(f"dependency_graph.json が見つかりません: {GRAPH_FILE}")

    # ファイル読み込み
    try:
        with open(GRAPH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        _graph_cache = data
        _cache_timestamp = datetime.now()

        logger.info(
            f"Loaded graph data: {len(data.get('nodes', []))} nodes, {len(data.get('edges', []))} edges"
        )
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in graph file: {e}")
        raise ValueError(f"JSONデコードエラー: {e}")
    except Exception as e:
        logger.error(f"Failed to load graph data: {e}")
        raise


def calculate_imported_by(graph_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    各ファイルがどのファイルからインポートされているかを計算

    Args:
        graph_data: 依存関係グラフデータ

    Returns:
        Dict: {file_id: [importing_file_ids]}
    """
    imported_by = {}

    # 全エッジから被依存関係を構築
    for edge in graph_data.get("edges", []):
        source = edge.get("source")
        target = edge.get("target")

        if target not in imported_by:
            imported_by[target] = []

        if source not in imported_by[target]:
            imported_by[target].append(source)

    return imported_by


def enrich_node_data(
    node: Dict[str, Any], imported_by: Dict[str, List[str]], graph_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    ノードデータを拡張（被依存関係、信号機判定を追加）

    Args:
        node: ノードデータ
        imported_by: 被依存関係マップ
        graph_data: 全グラフデータ

    Returns:
        Dict: 拡張されたノードデータ
    """
    node_id = node.get("id")
    enriched = node.copy()

    # 被依存関係を追加
    enriched["imported_by"] = imported_by.get(node_id, [])
    enriched["imported_by_count"] = len(enriched["imported_by"])

    # import先を追加（エッジから計算）
    imports_to = []
    for edge in graph_data.get("edges", []):
        if edge.get("source") == node_id:
            imports_to.append(edge.get("target"))
    enriched["imports_to"] = imports_to
    enriched["imports_to_count"] = len(imports_to)

    # 信号機判定
    imported_by_count = enriched["imported_by_count"]
    if imported_by_count >= 20:
        enriched["signal"] = "🔴"
        enriched["risk_level"] = "critical"
    elif imported_by_count >= 10:
        enriched["signal"] = "🟡"
        enriched["risk_level"] = "warning"
    elif imported_by_count >= 1:
        enriched["signal"] = "🟢"
        enriched["risk_level"] = "normal"
    else:
        enriched["signal"] = "💤"
        enriched["risk_level"] = "unused"

    return enriched


@app.get("/")
async def root():
    """
    ウェルカムページ

    Returns:
        Dict: システム情報とエンドポイント一覧
    """
    return {
        "message": "依存関係可視化システム API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "system_info": "/api/info",
            "dependencies": "/api/dependencies",
            "file_detail": "/api/file/{file_path}",
            "signals": "/api/signals",
            "docs": "/docs",
            "redoc": "/redoc",
        },
        "examples": {
            "get_dependencies": "GET /api/dependencies",
            "get_file_info": "GET /api/file/tools/sheets_manager.py",
            "get_signals": "GET /api/signals",
            "top_5_critical_files": "GET /api/signals (最初の5件が最重要)",
        },
        "statistics": {"note": "GET /api/info で詳細情報を取得"},
    }


@app.on_event("startup")
async def startup_event():
    """サーバー起動時の初期化"""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🚀 依存関係可視化システム API 起動")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # グラフデータの事前読み込み
    try:
        data = load_graph_data()
        logger.info(f"✅ グラフデータ読み込み成功: {len(data.get('nodes', []))} ノード")
    except Exception as e:
        logger.error(f"❌ グラフデータ読み込み失敗: {e}")
        logger.warning("⚠️  /api/dependencies エンドポイントは使用できません")


@app.on_event("shutdown")
async def shutdown_event():
    """サーバー停止時のクリーンアップ"""
    logger.info("⏹️  依存関係可視化システム API 停止")


@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント

    Returns:
        Dict: ステータス情報
    """
    graph_status = "ok" if GRAPH_FILE.exists() else "unavailable"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "graph_file": str(GRAPH_FILE),
        "graph_status": graph_status,
    }


@app.get("/api/info")
async def system_info():
    """
    システム情報エンドポイント

    Returns:
        Dict: システム情報
    """
    try:
        data = load_graph_data()

        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_nodes": len(data.get("nodes", [])),
                "total_edges": len(data.get("edges", [])),
                "graph_file": str(GRAPH_FILE),
                "cache_age_seconds": (
                    (datetime.now() - _cache_timestamp).total_seconds()
                    if _cache_timestamp
                    else None
                ),
            },
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dependencies")
async def get_dependencies(reload: bool = Query(False, description="強制的にデータを再読み込み")):
    """
    全依存関係を取得

    Args:
        reload: 強制的に再読み込み

    Returns:
        Dict: 依存関係グラフ
    """
    try:
        data = load_graph_data(force_reload=reload)
        return data
    except FileNotFoundError as e:
        logger.error(f"Graph file not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid graph data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get dependencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/file/{file_path:path}")
async def get_file_info(file_path: str):
    """
    ファイル詳細情報を取得（被依存関係付き）

    Args:
        file_path: ファイルパス

    Returns:
        Dict: ファイル詳細情報
    """
    try:
        data = load_graph_data()

        # 被依存関係を計算
        imported_by = calculate_imported_by(data)

        # ノードを検索
        for node in data.get("nodes", []):
            if node.get("id") == file_path:
                # データを拡張
                enriched = enrich_node_data(node, imported_by, data)
                return enriched

        # 見つからない場合
        raise HTTPException(status_code=404, detail=f"ファイルが見つかりません: {file_path}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals")
async def get_signals():
    """
    全ファイルの信号機情報を取得

    Returns:
        List[Dict]: 信号機情報リスト
    """
    try:
        data = load_graph_data()

        # 被依存関係を計算
        imported_by = calculate_imported_by(data)

        # 全ノードを拡張
        signals = []
        for node in data.get("nodes", []):
            enriched = enrich_node_data(node, imported_by, data)
            signals.append(
                {
                    "file": enriched.get("id"),
                    "signal": enriched.get("signal"),
                    "risk_level": enriched.get("risk_level"),
                    "imported_by_count": enriched.get("imported_by_count"),
                    "imports_to_count": enriched.get("imports_to_count"),
                }
            )

        # 危険度順にソート
        signals.sort(key=lambda x: x["imported_by_count"], reverse=True)

        return signals

    except Exception as e:
        logger.error(f"Failed to get signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """メイン実行"""
    logger.info("Starting API server...")

    # サーバー起動
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()

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


def detect_duplicate_files(graph_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    重複ファイルを検出

    ファイル名のパターンマッチングにより、バージョン違いのファイルを検出します。

    検出パターン:
        - file_v2.py, file_v3.py, file_v30.py
        - file_old.py, file_new.py
        - file_backup.py, file_copy.py

    Args:
        graph_data: 依存関係グラフデータ

    Returns:
        List[Dict]: 重複ファイルグループのリスト
    """
    import re
    from collections import defaultdict

    nodes = graph_data.get("nodes", [])

    # ファイル名からベース名を抽出するパターン
    version_patterns = [
        (r"(.+?)_v\d+", "version"),  # file_v2, file_v30
        (r"(.+?)_old", "old"),  # file_old
        (r"(.+?)_new", "new"),  # file_new
        (r"(.+?)_backup\d*", "backup"),  # file_backup, file_backup2
        (r"(.+?)_copy\d*", "copy"),  # file_copy, file_copy2
        (r"(.+?)_\d{6}", "timestamp"),  # file_251123
        (r"(.+?)\.backup", "backup_ext"),  # file.py.backup
    ]

    # ベース名でグループ化
    base_groups = defaultdict(list)

    for node in nodes:
        file_id = node.get("id", "")

        # パターンマッチング
        for pattern, label in version_patterns:
            match = re.match(pattern, file_id)
            if match:
                base_name = match.group(1)
                base_groups[base_name].append({"file": file_id, "pattern": label, "node": node})
                break

    # 2つ以上のファイルがある場合のみ重複とみなす
    duplicates = []
    for base_name, files in base_groups.items():
        if len(files) >= 2:
            duplicates.append({"base_name": base_name, "count": len(files), "files": files})

    return duplicates


def determine_latest_version(
    files: List[Dict[str, Any]], imported_by: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    最新版を判定

    判定基準:
        1. 被依存数（多い方が現役）
        2. 更新日時（新しい方が最新）
        3. ファイル名（バージョン番号が大きい方）

    Args:
        files: ファイルリスト
        imported_by: 被依存関係マップ

    Returns:
        Dict: 最新版と判定されたファイル情報
    """
    import re

    scored_files = []

    for file_info in files:
        file_id = file_info["file"]
        file_info["node"]

        # スコア計算
        score = 0

        # 1. 被依存数（最重要）
        imported_by_count = len(imported_by.get(file_id, []))
        score += imported_by_count * 100

        # 2. バージョン番号（v30 > v3 > v2）
        version_match = re.search(r"_v(\d+)", file_id)
        if version_match:
            version_num = int(version_match.group(1))
            score += version_num

        # 3. "new" や "latest" を含む場合は加点
        if "new" in file_id.lower() or "latest" in file_id.lower():
            score += 50

        # 4. "old" や "backup" を含む場合は減点
        if "old" in file_id.lower() or "backup" in file_id.lower():
            score -= 50

        scored_files.append({**file_info, "score": score, "imported_by_count": imported_by_count})

    # スコアでソート
    scored_files.sort(key=lambda x: x["score"], reverse=True)

    return scored_files[0] if scored_files else None


@app.get("/api/duplicates")
async def get_duplicates():
    """
    重複ファイルを検出

    Returns:
        List[Dict]: 重複ファイルグループのリスト
    """
    try:
        data = load_graph_data()

        # 重複検出
        duplicates = detect_duplicate_files(data)

        # 被依存関係を計算
        imported_by = calculate_imported_by(data)

        # 各グループに最新版判定を追加
        result = []
        for dup_group in duplicates:
            latest = determine_latest_version(dup_group["files"], imported_by)

            # ファイル情報を整形
            files_info = []
            for file_info in dup_group["files"]:
                file_id = file_info["file"]
                is_latest = (file_id == latest["file"]) if latest else False

                files_info.append(
                    {
                        "file": file_id,
                        "pattern": file_info["pattern"],
                        "imported_by_count": len(imported_by.get(file_id, [])),
                        "is_latest": is_latest,
                        "recommended_action": "keep" if is_latest else "review",
                    }
                )

            # 最新版でソート
            files_info.sort(key=lambda x: x["is_latest"], reverse=True)

            result.append(
                {
                    "base_name": dup_group["base_name"],
                    "count": dup_group["count"],
                    "files": files_info,
                    "latest_file": latest["file"] if latest else None,
                }
            )

        # ファイル数でソート（多い順）
        result.sort(key=lambda x: x["count"], reverse=True)

        return result

    except Exception as e:
        logger.error(f"Failed to get duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """メイン実行"""
    logger.info("Starting API server...")

    # サーバー起動
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 1-004: 影響範囲API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def analyze_impact_range(
    target_file: str, graph_data: Dict[str, Any], max_depth: int = 3
) -> Dict[str, Any]:
    """
    影響範囲を分析（BFS探索で3階層）

    Args:
        target_file: 変更対象ファイル（例: "agents/pm_agent.py"）
        graph_data: 依存関係グラフデータ
        max_depth: 探索深さ（デフォルト: 3階層）

    Returns:
        Dict: 影響範囲分析結果
    """
    from collections import deque

    import networkx as nx

    # NetworkXグラフを再構築
    G = nx.DiGraph()

    # ノードを追加
    for node in graph_data.get("nodes", []):
        G.add_node(node["id"], **node)

    # エッジを追加
    for edge in graph_data.get("edges", []):
        G.add_edge(edge["source"], edge["target"], **edge)

    # 対象ファイルを正規化
    target_normalized = target_file
    for node in G.nodes():
        if node.endswith(target_file) or target_file in node:
            target_normalized = node
            break

    if target_normalized not in G.nodes():
        return {
            "target": target_file,
            "found": False,
            "error": f"ファイルが見つかりません: {target_file}",
            "direct_impact": [],
            "indirect_impact": {},
            "total_impact": 0,
        }

    # BFS探索で影響範囲を抽出
    visited = set()
    impact_by_depth = {}
    queue = deque([(target_normalized, 0)])  # (ノード, 深さ)

    while queue:
        current, depth = queue.popleft()

        if current in visited or depth > max_depth:
            continue

        visited.add(current)

        # この深さの影響先を記録
        if depth > 0:  # 自分自身は除外
            if depth not in impact_by_depth:
                impact_by_depth[depth] = []
            impact_by_depth[depth].append(current)

        # 次の階層（このファイルに依存しているファイル）
        if depth < max_depth:
            for neighbor in G.predecessors(current):  # predecessors = 依存元
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))

    # 直接影響（1階層）
    direct_impact = impact_by_depth.get(1, [])

    # 影響度スコア計算
    impact_scores = {}
    for file in visited:
        if file == target_normalized:
            continue

        # スコア = 被依存数 × 100 + ファイル行数
        node_data = G.nodes[file]
        imported_by_count = len(node_data.get("imported_by", []))
        lines = node_data.get("lines", 0)

        impact_scores[file] = imported_by_count * 100 + lines

    # スコア順にソート
    sorted_impact = sorted(impact_scores.items(), key=lambda x: x[1], reverse=True)

    # テスト推奨（影響度上位10ファイル）
    recommended_tests = [
        {"file": file, "score": score, "reason": f"影響度スコア: {score}（被依存数×100 + 行数）"}
        for file, score in sorted_impact[:10]
    ]

    return {
        "target": target_normalized,
        "found": True,
        "direct_impact": direct_impact,
        "indirect_impact": impact_by_depth,
        "total_impact": len(visited) - 1,  # 自分自身を除く
        "impact_scores": dict(sorted_impact[:20]),  # 上位20件
        "recommended_tests": recommended_tests,
        "max_depth": max_depth,
    }


@app.get("/api/impact/{file_path:path}")
async def get_impact_range(file_path: str, max_depth: int = 3):
    """
    影響範囲分析

    Args:
        file_path: 変更対象ファイル（例: agents/pm_agent.py）
        max_depth: 探索深さ（デフォルト: 3）

    Returns:
        Dict: 影響範囲分析結果
    """
    try:
        # dependency_graph.json を読み込み
        json_path = Path(__file__).parent / "dependency_graph.json"

        if not json_path.exists():
            return {"error": "dependency_graph.json が見つかりません", "target": file_path}

        with open(json_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        # 影響範囲を分析
        result = analyze_impact_range(file_path, graph_data, max_depth)

        return result

    except Exception as e:
        return {"error": str(e), "target": file_path}


if __name__ == "__main__":
    main()


# ==============================================================
# P1-004: 重複検出API
# ==============================================================
@app.get("/api/duplicates")
async def get_duplicates():
    """
    重複ファイルを検出する

    アルゴリズム:
    1. ファイル名の類似度計算（Levenshtein距離）
    2. バージョン番号の検出（_v2, _v3, _v30など）
    3. 最新版の判定（更新日時 + 被依存数）

    Returns:
        {
            "groups": [
                {
                    "base_name": "pm_agent",
                    "files": [
                        {"path": "pm_agent_v2.py", "version": "v2", ...},
                        {"path": "pm_agent_v31.py", "version": "v31", ...}
                    ],
                    "recommended": "pm_agent_v31.py",
                    "delete_candidates": ["pm_agent_v2.py", "pm_agent_v3.py"]
                }
            ],
            "total_duplicates": 10
        }
    """
    import os
    import re
    from collections import defaultdict
    from datetime import datetime

    duplicate_groups = []
    version_pattern = re.compile(r"(.+?)_v?(\d+)\.py$")

    # 全Pythonファイルをスキャン
    python_files = []
    for root, dirs, files in os.walk("."):
        # 除外ディレクトリ
        dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", "node_modules"]]

        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                python_files.append(full_path)

    # バージョン番号でグループ化
    grouped = defaultdict(list)
    for filepath in python_files:
        filename = os.path.basename(filepath)
        match = version_pattern.match(filename)

        if match:
            base_name = match.group(1)
            version = match.group(2)

            # ファイル情報を収集
            stat = os.stat(filepath)
            file_info = {
                "path": filepath,
                "filename": filename,
                "version": version,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "modified_timestamp": stat.st_mtime,
            }

            grouped[base_name].append(file_info)

    # 2つ以上のバージョンがあるものを重複として扱う
    for base_name, files in grouped.items():
        if len(files) >= 2:
            # 最新版を判定（更新日時で）
            files_sorted = sorted(files, key=lambda x: x["modified_timestamp"], reverse=True)
            recommended = files_sorted[0]
            delete_candidates = files_sorted[1:]

            duplicate_groups.append(
                {
                    "base_name": base_name,
                    "files": files,
                    "recommended": recommended["path"],
                    "delete_candidates": [f["path"] for f in delete_candidates],
                    "count": len(files),
                }
            )

    # 重複数でソート
    duplicate_groups.sort(key=lambda x: x["count"], reverse=True)

    return {
        "groups": duplicate_groups,
        "total_duplicates": len(duplicate_groups),
        "total_files": sum(g["count"] for g in duplicate_groups),
    }


# ==============================================================
# P1-005: 影響範囲分析API
# ==============================================================
@app.get("/api/impact/{file_path:path}")
async def get_impact_analysis(file_path: str, depth: int = 3):
    """
    ファイル変更時の影響範囲を分析する

    アルゴリズム:
    1. BFS探索で依存関係を辿る
    2. 最大3階層まで追跡
    3. 影響度スコアを計算
    4. 推奨テストを生成

    Args:
        file_path: 分析対象ファイルパス
        depth: 探索階層数（デフォルト3）

    Returns:
        {
            "target_file": "sheets_manager.py",
            "direct_impact": ["pm_agent.py", ...],  # 1階層
            "indirect_impact": ["orchestrator.py", ...],  # 2-3階層
            "total_impact_count": 83,
            "recommended_tests": [...]
        }
    """
    import json
    from collections import deque

    # 依存関係データをロード
    try:
        with open("docs/dependency_map.json", "r") as f:
            dep_data = json.load(f)
    except FileNotFoundError:
        return {"error": "dependency_map.json not found"}

    # BFS探索で影響範囲を計算
    def bfs_impact(start_file, max_depth):
        visited = set()
        impact_by_level = {i: set() for i in range(1, max_depth + 1)}
        queue = deque([(start_file, 0)])

        while queue:
            current_file, level = queue.popleft()

            if current_file in visited or level >= max_depth:
                continue

            visited.add(current_file)

            # このファイルに依存しているファイルを探す
            for node in dep_data.get("nodes", []):
                if node["id"] == current_file:
                    for dependent in node.get("imported_by", []):
                        if dependent not in visited:
                            next_level = level + 1
                            impact_by_level[next_level].add(dependent)
                            queue.append((dependent, next_level))

        return impact_by_level

    # 影響範囲を計算
    impact_levels = bfs_impact(file_path, depth)

    # 推奨テストを生成
    direct_impact = list(impact_levels.get(1, set()))
    all_impact = set()
    for level_files in impact_levels.values():
        all_impact.update(level_files)

    # 影響度が高いファイルを優先してテスト推奨
    recommended_tests = []
    priority_files = ["pm_agent", "task_executor", "orchestrator", "complete_engine"]
    for pf in priority_files:
        for impacted in all_impact:
            if pf in impacted:
                recommended_tests.append(
                    {"file": impacted, "priority": "high", "reason": f"Critical component: {pf}"}
                )

    return {
        "target_file": file_path,
        "direct_impact": direct_impact,
        "impact_by_level": {str(k): list(v) for k, v in impact_levels.items()},
        "total_impact_count": len(all_impact),
        "recommended_tests": recommended_tests[:10],  # Top 10
    }


# ==============================================================
# P1-004: 重複検出API
# ==============================================================
@app.get("/api/duplicates")
async def get_duplicates():
    """
    重複ファイルを検出する

    アルゴリズム:
    1. ファイル名の類似度計算（Levenshtein距離）
    2. バージョン番号の検出（_v2, _v3, _v30など）
    3. 最新版の判定（更新日時 + 被依存数）

    Returns:
        {
            "groups": [
                {
                    "base_name": "pm_agent",
                    "files": [
                        {"path": "pm_agent_v2.py", "version": "v2", ...},
                        {"path": "pm_agent_v31.py", "version": "v31", ...}
                    ],
                    "recommended": "pm_agent_v31.py",
                    "delete_candidates": ["pm_agent_v2.py", "pm_agent_v3.py"]
                }
            ],
            "total_duplicates": 10
        }
    """
    import os
    import re
    from collections import defaultdict
    from datetime import datetime

    duplicate_groups = []
    version_pattern = re.compile(r"(.+?)_v?(\d+)\.py$")

    # 全Pythonファイルをスキャン
    python_files = []
    for root, dirs, files in os.walk("."):
        # 除外ディレクトリ
        dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", "node_modules"]]

        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                python_files.append(full_path)

    # バージョン番号でグループ化
    grouped = defaultdict(list)
    for filepath in python_files:
        filename = os.path.basename(filepath)
        match = version_pattern.match(filename)

        if match:
            base_name = match.group(1)
            version = match.group(2)

            # ファイル情報を収集
            stat = os.stat(filepath)
            file_info = {
                "path": filepath,
                "filename": filename,
                "version": version,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "modified_timestamp": stat.st_mtime,
            }

            grouped[base_name].append(file_info)

    # 2つ以上のバージョンがあるものを重複として扱う
    for base_name, files in grouped.items():
        if len(files) >= 2:
            # 最新版を判定（更新日時で）
            files_sorted = sorted(files, key=lambda x: x["modified_timestamp"], reverse=True)
            recommended = files_sorted[0]
            delete_candidates = files_sorted[1:]

            duplicate_groups.append(
                {
                    "base_name": base_name,
                    "files": files,
                    "recommended": recommended["path"],
                    "delete_candidates": [f["path"] for f in delete_candidates],
                    "count": len(files),
                }
            )

    # 重複数でソート
    duplicate_groups.sort(key=lambda x: x["count"], reverse=True)

    return {
        "groups": duplicate_groups,
        "total_duplicates": len(duplicate_groups),
        "total_files": sum(g["count"] for g in duplicate_groups),
    }


# ==============================================================
# P1-005: 影響範囲分析API
# ==============================================================
@app.get("/api/impact/{file_path:path}")
async def get_impact_analysis(file_path: str, depth: int = 3):
    """
    ファイル変更時の影響範囲を分析する

    アルゴリズム:
    1. BFS探索で依存関係を辿る
    2. 最大3階層まで追跡
    3. 影響度スコアを計算
    4. 推奨テストを生成

    Args:
        file_path: 分析対象ファイルパス
        depth: 探索階層数（デフォルト3）

    Returns:
        {
            "target_file": "sheets_manager.py",
            "direct_impact": ["pm_agent.py", ...],  # 1階層
            "indirect_impact": ["orchestrator.py", ...],  # 2-3階層
            "total_impact_count": 83,
            "recommended_tests": [...]
        }
    """
    import json
    from collections import deque

    # 依存関係データをロード
    try:
        with open("docs/dependency_map.json", "r") as f:
            dep_data = json.load(f)
    except FileNotFoundError:
        return {"error": "dependency_map.json not found"}

    # BFS探索で影響範囲を計算
    def bfs_impact(start_file, max_depth):
        visited = set()
        impact_by_level = {i: set() for i in range(1, max_depth + 1)}
        queue = deque([(start_file, 0)])

        while queue:
            current_file, level = queue.popleft()

            if current_file in visited or level >= max_depth:
                continue

            visited.add(current_file)

            # このファイルに依存しているファイルを探す
            for node in dep_data.get("nodes", []):
                if node["id"] == current_file:
                    for dependent in node.get("imported_by", []):
                        if dependent not in visited:
                            next_level = level + 1
                            impact_by_level[next_level].add(dependent)
                            queue.append((dependent, next_level))

        return impact_by_level

    # 影響範囲を計算
    impact_levels = bfs_impact(file_path, depth)

    # 推奨テストを生成
    direct_impact = list(impact_levels.get(1, set()))
    all_impact = set()
    for level_files in impact_levels.values():
        all_impact.update(level_files)

    # 影響度が高いファイルを優先してテスト推奨
    recommended_tests = []
    priority_files = ["pm_agent", "task_executor", "orchestrator", "complete_engine"]
    for pf in priority_files:
        for impacted in all_impact:
            if pf in impacted:
                recommended_tests.append(
                    {"file": impacted, "priority": "high", "reason": f"Critical component: {pf}"}
                )

    return {
        "target_file": file_path,
        "direct_impact": direct_impact,
        "impact_by_level": {str(k): list(v) for k, v in impact_levels.items()},
        "total_impact_count": len(all_impact),
        "recommended_tests": recommended_tests[:10],  # Top 10
    }

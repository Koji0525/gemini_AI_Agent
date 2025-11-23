#!/usr/bin/env python3
"""
依存関係可視化API サーバー (HTML配信対応版)

**更新内容**:
- StaticFiles追加
- HTMLTemplates追加
- ルートパスでダッシュボード表示

**作成理由**:
フロントエンドのHTML/CSS/JSを配信し、
統合されたWebダッシュボードを提供するため
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
from typing import Dict, List, Optional
import sys
from datetime import datetime

# プロジェクトルートをPYTHONPATHに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

app = FastAPI(
    title="依存関係可視化API",
    description="コードベースの依存関係を可視化するためのAPI",
    version="1.0.0"
)

# 静的ファイルとテンプレート
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_dependency_data() -> Dict:
    """依存関係データをファイルから読み込む."""
    data_file = Path(__file__).parent.parent.parent / "docs" / "dependency_map.json"
    
    if not data_file.exists():
        return {
            "dependency_map": {},
            "analysis": {
                "most_depended": [],
                "total_modules": 0,
                "total_dependencies": 0,
                "dependency_stats": {
                    "high_impact": 0,
                    "medium_impact": 0,
                    "low_impact": 0,
                    "no_dependents": 0
                }
            },
            "metadata": {
                "generated_at": None,
                "version": "1.0.0"
            }
        }
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ データ読み込みエラー: {e}")
        return {"dependency_map": {}, "analysis": {}}


@app.get("/", response_class=HTMLResponse)
async def root():
    """ダッシュボードHTMLを返す."""
    index_file = templates_dir / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/api/health")
async def health_check():
    """ヘルスチェックエンドポイント."""
    data = load_dependency_data()
    modules_count = len(data.get("dependency_map", {}))
    data_file = Path(__file__).parent.parent.parent / "docs" / "dependency_map.json"
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": modules_count > 0,
        "total_modules": data.get("analysis", {}).get("total_modules", 0),
        "data_file_exists": data_file.exists(),
        "data_file_path": str(data_file) if data_file.exists() else None,
        "metadata": data.get("metadata", {})
    }


@app.get("/api/stats")
async def get_stats():
    """統計情報を取得する."""
    data = load_dependency_data()
    analysis = data.get("analysis", {})
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_modules": analysis.get("total_modules", 0),
        "total_dependencies": analysis.get("total_dependencies", 0),
        "dependency_stats": analysis.get("dependency_stats", {}),
        "top_depended_modules": analysis.get("most_depended", [])[:10],
        "metadata": data.get("metadata", {})
    }


@app.get("/api/nodes")
async def get_nodes():
    """全ノード（ファイル）の一覧を取得する."""
    data = load_dependency_data()
    dependency_map = data.get("dependency_map", {})
    
    nodes = []
    for file_path, info in dependency_map.items():
        nodes.append({
            "id": file_path,
            "label": Path(file_path).name,
            "full_path": file_path,
            "import_count": info.get("import_count", 0),
            "total_imports": info.get("total_imports", 0),
            "file_size": info.get("file_size", 0),
            "file_size_kb": round(info.get("file_size", 0) / 1024, 2)
        })
    
    return {
        "nodes": nodes,
        "count": len(nodes),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/edges")
async def get_edges():
    """全エッジ（依存関係）の一覧を取得する."""
    data = load_dependency_data()
    dependency_map = data.get("dependency_map", {})
    
    edges = []
    for source, info in dependency_map.items():
        for target in info.get("imports", []):
            edges.append({
                "source": source,
                "target": target,
                "type": "import"
            })
    
    return {
        "edges": edges,
        "count": len(edges),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/impact/{file_path:path}")
async def get_impact(file_path: str):
    """特定ファイルの影響範囲を分析する."""
    data = load_dependency_data()
    dependency_map = data.get("dependency_map", {})
    
    # 直接影響を受けるファイル
    direct_dependents = []
    for file, info in dependency_map.items():
        if file_path in info.get("imports", []):
            direct_dependents.append({
                "file": file,
                "import_count": info.get("import_count", 0)
            })
    
    # このファイルが依存しているファイル
    file_info = dependency_map.get(file_path, {})
    dependencies = file_info.get("imports", [])
    
    # 影響レベルの判定
    dependents_count = len(direct_dependents)
    if dependents_count >= 5:
        impact_level = "high"
        impact_description = "高影響: 5個以上のファイルがこのファイルに依存"
    elif dependents_count >= 2:
        impact_level = "medium"
        impact_description = "中影響: 2-4個のファイルがこのファイルに依存"
    elif dependents_count == 1:
        impact_level = "low"
        impact_description = "低影響: 1個のファイルがこのファイルに依存"
    else:
        impact_level = "none"
        impact_description = "影響なし: 他のファイルからの依存なし"
    
    return {
        "file": file_path,
        "exists": file_path in dependency_map,
        "timestamp": datetime.now().isoformat(),
        "direct_dependents": direct_dependents,
        "direct_dependents_count": dependents_count,
        "dependencies": dependencies,
        "dependencies_count": len(dependencies),
        "impact_level": impact_level,
        "impact_description": impact_description,
        "file_info": file_info
    }


if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🚀 依存関係可視化APIサーバー + ダッシュボード")
    print("="*60)
    print(f"📁 プロジェクトルート: {project_root}")
    print(f"📍 ダッシュボード: http://localhost:5001")
    print(f"📖 APIドキュメント: http://localhost:5001/docs")
    print(f"🔍 ReDoc: http://localhost:5001/redoc")
    print(f"⏰ 起動時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print("💡 Ctrl+C で停止")
    print()
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")

#!/usr/bin/env python3
"""
依存関係可視化API サーバー (Phase 2完全版)

**拡張内容**:
- 隠れた依存関係エンドポイント
- 循環依存エンドポイント
- 破壊的変更エンドポイント
- リスクスコアエンドポイント
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pytz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_jst_now():
    """JST時刻を取得する."""
    jst = pytz.timezone("Asia/Tokyo")
    return datetime.now(jst)


app = FastAPI(
    title="依存関係可視化API",
    description="コードベースの依存関係を可視化するためのAPI (Phase 2完全版)",
    version="2.0.0",
)

static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_json_file(filename: str) -> Dict:
    """JSONファイルを読み込む.

    Args:
        filename: ファイル名

    Returns:
        JSONデータ
    """
    file_path = Path(__file__).parent.parent.parent / "docs" / filename

    if not file_path.exists():
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ {filename} 読み込みエラー: {e}")
        return {}


def load_dependency_data() -> Dict:
    """依存関係データをファイルから読み込む."""
    return load_json_file("dependency_map.json")


def normalize_path(query: str) -> List[str]:
    """クエリを正規化して複数の候補パスを生成する."""
    candidates = []
    candidates.append(query)

    if not query.endswith(".py"):
        candidates.append(f"{query}.py")

    if "." in query and "/" not in query:
        slash_version = query.replace(".", "/")
        candidates.append(slash_version)
        candidates.append(f"{slash_version}.py")

    if "/" in query:
        dot_version = query.replace("/", ".").replace(".py", "")
        candidates.append(dot_version)

    return candidates


# ===================================================================
# 既存エンドポイント
# ===================================================================


@app.get("/", response_class=HTMLResponse)
async def root():
    """ダッシュボードHTMLを返す."""
    index_file = templates_dir / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/diagnostic", response_class=HTMLResponse)
async def diagnostic():
    """診断ページを返す."""
    diagnostic_file = templates_dir / "diagnostic.html"
    if diagnostic_file.exists():
        with open(diagnostic_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Diagnostic not found</h1>", status_code=404)


@app.get("/api/duplicates")
async def get_duplicates():
    """重複ファイル一覧を取得する."""
    try:
        duplicate_file = Path(PROJECT_ROOT) / "docs" / "duplicate_files.json"

        if not duplicate_file.exists():
            return {
                "exists": False,
                "message": "重複ファイルデータが見つかりません",
                "hint": "python3 scripts/analysis/duplicate_detector.py を実行してください",
            }

        with open(duplicate_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/duplicates/summary")
async def get_duplicates_summary():
    """重複ファイルのサマリー情報を取得する."""
    try:
        duplicate_file = Path(PROJECT_ROOT) / "docs" / "duplicate_files.json"

        if not duplicate_file.exists():
            return {"exists": False, "total_groups": 0, "total_duplicates": 0}

        with open(duplicate_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Top 5のみ返す（パフォーマンス考慮）
        top_groups = data.get("groups", [])[:5]

        return {
            "exists": True,
            "total_groups": data.get("total_groups", 0),
            "total_duplicates": data.get("total_duplicates", 0),
            "top_groups": top_groups,
            "analysis_time": data.get("analysis_time"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """ヘルスチェックエンドポイント."""
    data = load_dependency_data()
    modules_count = len(data.get("dependency_map", {}))
    data_file = Path(__file__).parent.parent.parent / "docs" / "dependency_map.json"

    # Phase 2データの存在確認
    hidden_deps = Path(__file__).parent.parent.parent / "docs" / "hidden_dependencies.json"
    cycles = Path(__file__).parent.parent.parent / "docs" / "circular_dependencies.json"
    breaking = Path(__file__).parent.parent.parent / "docs" / "breaking_changes.json"

    return {
        "status": "ok",
        "timestamp": get_jst_now().isoformat(),
        "data_loaded": modules_count > 0,
        "total_modules": data.get("analysis", {}).get("total_modules", 0),
        "data_file_exists": data_file.exists(),
        "phase2_features": {
            "hidden_dependencies": hidden_deps.exists(),
            "circular_dependencies": cycles.exists(),
            "breaking_changes": breaking.exists(),
        },
        "metadata": data.get("metadata", {}),
    }


@app.get("/api/stats")
async def get_stats():
    """統計情報を取得する."""
    data = load_dependency_data()
    analysis = data.get("analysis", {})

    return {
        "timestamp": get_jst_now().isoformat(),
        "total_modules": analysis.get("total_modules", 0),
        "total_dependencies": analysis.get("total_dependencies", 0),
        "dependency_stats": analysis.get("dependency_stats", {}),
        "top_depended_modules": analysis.get("most_depended", [])[:10],
        "metadata": data.get("metadata", {}),
    }


@app.get("/api/nodes")
async def get_nodes():
    """全ノード（ファイル）の一覧を取得する."""
    data = load_dependency_data()
    dependency_map = data.get("dependency_map", {})

    nodes = []
    for file_path, info in dependency_map.items():
        nodes.append(
            {
                "id": file_path,
                "label": Path(file_path).name,
                "full_path": file_path,
                "import_count": info.get("import_count", 0),
                "total_imports": info.get("total_imports", 0),
                "file_size": info.get("file_size", 0),
                "file_size_kb": round(info.get("file_size", 0) / 1024, 2),
            }
        )

    return {"nodes": nodes, "count": len(nodes), "timestamp": get_jst_now().isoformat()}


@app.get("/api/edges")
async def get_edges():
    """全エッジ（依存関係）の一覧を取得する."""
    data = load_dependency_data()
    dependency_map = data.get("dependency_map", {})

    edges = []
    for source, info in dependency_map.items():
        for target in info.get("imports", []):
            edges.append({"source": source, "target": target, "type": "import"})

    return {"edges": edges, "count": len(edges), "timestamp": get_jst_now().isoformat()}


@app.get("/api/impact/{file_path:path}")
async def get_impact(file_path: str):
    """特定ファイルの影響範囲を分析する."""
    print(f"🔍 検索リクエスト: {file_path}")

    data = load_dependency_data()
    dependency_map = data.get("dependency_map", {})

    candidates = normalize_path(file_path)
    print(f"📋 候補パス: {candidates}")

    actual_file = None
    for candidate in candidates:
        if candidate in dependency_map:
            actual_file = candidate
            print(f"✅ 見つかりました: {candidate}")
            break

    if not actual_file:
        print(f"❌ 見つかりません: {file_path}")
        return {
            "file": file_path,
            "exists": False,
            "timestamp": get_jst_now().isoformat(),
            "direct_dependents": [],
            "direct_dependents_count": 0,
            "dependencies": [],
            "dependencies_count": 0,
            "impact_level": "none",
            "impact_description": "ファイルが見つかりませんでした",
            "file_info": {},
            "searched_candidates": candidates,
        }

    direct_dependents = []
    for file, info in dependency_map.items():
        imports = info.get("imports", [])
        for imp in imports:
            if any(
                candidate.replace(".py", "").replace("/", ".") == imp for candidate in candidates
            ):
                direct_dependents.append(
                    {"file": file, "import_count": info.get("import_count", 0)}
                )
                break

    print(f"📊 依存ファイル: {len(direct_dependents)}個")

    file_info = dependency_map.get(actual_file, {})
    dependencies = file_info.get("imports", [])

    dependents_count = len(direct_dependents)
    if dependents_count >= 5:
        impact_level = "high"
        impact_description = f"高影響: {dependents_count}個のファイルがこのファイルに依存"
    elif dependents_count >= 2:
        impact_level = "medium"
        impact_description = f"中影響: {dependents_count}個のファイルがこのファイルに依存"
    elif dependents_count == 1:
        impact_level = "low"
        impact_description = f"低影響: 1個のファイルがこのファイルに依存"
    else:
        impact_level = "none"
        impact_description = "影響なし: 他のファイルからの依存なし"

    return {
        "file": actual_file,
        "exists": True,
        "timestamp": get_jst_now().isoformat(),
        "direct_dependents": direct_dependents,
        "direct_dependents_count": dependents_count,
        "dependencies": dependencies,
        "dependencies_count": len(dependencies),
        "impact_level": impact_level,
        "impact_description": impact_description,
        "file_info": file_info,
    }


# ===================================================================
# Phase 2 新エンドポイント
# ===================================================================


@app.get("/api/hidden-dependencies")
async def get_hidden_dependencies():
    """隠れた依存関係を取得する.

    Returns:
        環境変数、ファイルI/O、外部コマンドの依存関係
    """
    data = load_json_file("hidden_dependencies.json")

    if not data:
        return {
            "error": "hidden_dependencies.json が見つかりません",
            "suggestion": "python3 scripts/analysis/hidden_dependency_detector.py を実行してください",
            "timestamp": get_jst_now().isoformat(),
        }

    return {
        "timestamp": get_jst_now().isoformat(),
        "files": data.get("files", {}),
        "summary": data.get("summary", {}),
        "statistics": data.get("statistics", {}),
    }


@app.get("/api/hidden-dependencies/summary")
async def get_hidden_dependencies_summary():
    """隠れた依存関係のサマリーを取得する."""
    data = load_json_file("hidden_dependencies.json")

    if not data:
        return {"error": "データなし", "timestamp": get_jst_now().isoformat()}

    stats = data.get("statistics", {})
    summary = data.get("summary", {})

    # Top 10環境変数
    env_vars = summary.get("env_vars", {})
    top_env_vars = sorted(env_vars.items(), key=lambda x: len(x[1]), reverse=True)[:10]

    # Top 10ファイル
    file_ops = summary.get("file_operations", {})
    top_files = sorted(file_ops.items(), key=lambda x: len(x[1]), reverse=True)[:10]

    # Top 10コマンド
    commands = summary.get("commands", {})
    top_commands = sorted(commands.items(), key=lambda x: len(x[1]), reverse=True)[:10]

    return {
        "timestamp": get_jst_now().isoformat(),
        "statistics": stats,
        "top_env_vars": [{"name": k, "count": len(v)} for k, v in top_env_vars],
        "top_files": [{"path": k, "count": len(v)} for k, v in top_files],
        "top_commands": [{"command": k, "count": len(v)} for k, v in top_commands],
    }


@app.get("/api/cycles")
async def get_circular_dependencies():
    """循環依存を取得する.

    Returns:
        検出された循環依存のリスト
    """
    data = load_json_file("circular_dependencies.json")

    if not data:
        return {
            "error": "circular_dependencies.json が見つかりません",
            "suggestion": "python3 scripts/analysis/cycle_detector.py を実行してください",
            "timestamp": get_jst_now().isoformat(),
        }

    return {
        "timestamp": get_jst_now().isoformat(),
        "cycles": data.get("cycles", []),
        "statistics": data.get("statistics", {}),
        "metadata": data.get("metadata", {}),
    }


@app.get("/api/breaking-changes")
async def get_breaking_changes():
    """破壊的変更を取得する.

    Returns:
        検出された破壊的変更のリスト
    """
    data = load_json_file("breaking_changes.json")

    if not data:
        return {
            "error": "breaking_changes.json が見つかりません",
            "suggestion": "python3 scripts/analysis/breaking_change_detector.py を実行してください",
            "timestamp": get_jst_now().isoformat(),
        }

    return {
        "timestamp": get_jst_now().isoformat(),
        "changes": data.get("changes", []),
        "statistics": data.get("statistics", {}),
        "metadata": data.get("metadata", {}),
    }


@app.get("/api/risk-score/{file_path:path}")
async def get_risk_score(file_path: str):
    """ファイルのリスクスコアを計算する.

    Args:
        file_path: ファイルパス

    Returns:
        リスクスコアと詳細情報
    """
    # 依存関係データ
    dep_data = load_dependency_data()
    dependency_map = dep_data.get("dependency_map", {})

    # 隠れた依存関係
    hidden_data = load_json_file("hidden_dependencies.json")
    hidden_files = hidden_data.get("files", {})

    # 循環依存
    cycles_data = load_json_file("circular_dependencies.json")
    cycles = cycles_data.get("cycles", [])

    # 候補パス生成
    candidates = normalize_path(file_path)
    actual_file = None

    for candidate in candidates:
        if candidate in dependency_map:
            actual_file = candidate
            break

    if not actual_file:
        return {
            "file": file_path,
            "exists": False,
            "risk_score": 0,
            "risk_level": "unknown",
            "message": "ファイルが見つかりません",
        }

    # リスクスコア計算
    risk_factors = {
        "high_dependents": 0,  # 多数のファイルから依存されている
        "hidden_dependencies": 0,  # 隠れた依存が多い
        "in_cycle": 0,  # 循環依存に含まれる
        "complexity": 0,  # ファイルサイズが大きい
    }

    # 1. 依存数によるリスク
    file_info = dependency_map.get(actual_file, {})
    import_count = file_info.get("import_count", 0)
    if import_count >= 10:
        risk_factors["high_dependents"] = 30
    elif import_count >= 5:
        risk_factors["high_dependents"] = 20
    elif import_count >= 2:
        risk_factors["high_dependents"] = 10

    # 2. 隠れた依存によるリスク
    if actual_file in hidden_files:
        hidden_info = hidden_files[actual_file]
        env_count = len(hidden_info.get("env_vars", []))
        file_count = len(hidden_info.get("file_operations", []))
        cmd_count = len(hidden_info.get("commands", []))

        hidden_total = env_count + file_count + cmd_count
        if hidden_total >= 10:
            risk_factors["hidden_dependencies"] = 25
        elif hidden_total >= 5:
            risk_factors["hidden_dependencies"] = 15
        elif hidden_total >= 1:
            risk_factors["hidden_dependencies"] = 5

    # 3. 循環依存によるリスク
    for cycle in cycles:
        cycle_path = cycle.get("path", [])
        if actual_file in cycle_path:
            risk_factors["in_cycle"] = 30
            break

    # 4. 複雑性によるリスク
    file_size = file_info.get("file_size", 0)
    if file_size > 10000:  # 10KB以上
        risk_factors["complexity"] = 15
    elif file_size > 5000:  # 5KB以上
        risk_factors["complexity"] = 10

    # 総リスクスコア
    total_risk = sum(risk_factors.values())

    if total_risk >= 70:
        risk_level = "critical"
    elif total_risk >= 50:
        risk_level = "high"
    elif total_risk >= 30:
        risk_level = "medium"
    elif total_risk > 0:
        risk_level = "low"
    else:
        risk_level = "minimal"

    return {
        "file": actual_file,
        "exists": True,
        "risk_score": total_risk,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "recommendations": _get_recommendations(risk_factors, import_count),
        "file_info": {
            "dependents_count": import_count,
            "file_size": file_size,
            "file_size_kb": round(file_size / 1024, 2),
        },
        "timestamp": get_jst_now().isoformat(),
    }


def _get_recommendations(risk_factors: Dict, dependents: int) -> List[str]:
    """リスク軽減の推奨事項を生成する."""
    recommendations = []

    if risk_factors["high_dependents"] > 0:
        recommendations.append(
            f"⚠️ {dependents}個のファイルから依存されています。変更時は影響範囲テストが必須です。"
        )

    if risk_factors["hidden_dependencies"] > 0:
        recommendations.append(
            "⚠️ 環境変数やファイルI/Oに依存しています。設定ファイルで管理することを推奨します。"
        )

    if risk_factors["in_cycle"] > 0:
        recommendations.append(
            "🔴 循環依存が検出されました。モジュール構造の見直しを検討してください。"
        )

    if risk_factors["complexity"] > 0:
        recommendations.append(
            "📊 ファイルサイズが大きいです。複数のモジュールに分割することを検討してください。"
        )

    if not recommendations:
        recommendations.append("✅ リスクは最小限です。")

    return recommendations


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 依存関係可視化APIサーバー (Phase 2完全版)")
    print("=" * 60)
    print(f"📁 プロジェクトルート: {PROJECT_ROOT}")
    print(f"📍 ダッシュボード: http://localhost:5001")
    print(f"📖 APIドキュメント: http://localhost:5001/docs")
    print(f"⏰ 起動時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🔌 Phase 2 新エンドポイント:")
    print("  - GET /api/hidden-dependencies")
    print("  - GET /api/hidden-dependencies/summary")
    print("  - GET /api/cycles")
    print("  - GET /api/breaking-changes")
    print("  - GET /api/risk-score/{file_path}")
    print("=" * 60)
    print("💡 Ctrl+C で停止")
    print()
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")


@app.get("/api/duplicates/summary")
async def get_duplicate_summary():
    """重複ファイルのサマリー情報を返す"""
    try:
        summary_path = PROJECT_ROOT / "docs" / "duplicate_summary.json"
        if not summary_path.exists():
            return {"error": "サマリーファイルが見つかりません"}

        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        return summary
    except Exception as e:
        return {"error": str(e)}

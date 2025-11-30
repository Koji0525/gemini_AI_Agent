#!/usr/bin/env python3
"""
オブザーバーAPI Server v2
- 重複コード検知統合
- 詳細データエンドポイント
- CSV出力機能
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import csv
import io
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Observer Dashboard API v2")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル変数
dependency_graph = {}
duplicate_report = {}


@app.on_event("startup")
async def load_data():
    """起動時にデータロード"""
    global dependency_graph, duplicate_report

    # 依存関係データ
    dep_file = Path("dependency_map.json")
    if dep_file.exists():
        with open(dep_file, "r") as f:
            dependency_graph = json.load(f)

    # 重複検知データ
    dup_file = Path("duplicate_report.json")
    if dup_file.exists():
        with open(dup_file, "r") as f:
            duplicate_report = json.load(f)


@app.get("/api/stats")
async def get_stats():
    """統計情報"""
    total_modules = len(dependency_graph)

    # 依存関係カウント
    total_deps = sum(len(data.get("imports", [])) for data in dependency_graph.values())

    # 影響度分類
    high_impact = []
    medium_impact = []
    low_impact = []

    for module, data in dependency_graph.items():
        dep_count = len(data.get("imports", []))

        if dep_count >= 10:
            high_impact.append({"module": module, "count": dep_count})
        elif dep_count >= 5:
            medium_impact.append({"module": module, "count": dep_count})
        elif dep_count > 0:
            low_impact.append({"module": module, "count": dep_count})

    return {
        "total_modules": total_modules,
        "total_dependencies": total_deps,
        "high_impact": {
            "count": len(high_impact),
            "modules": sorted(high_impact, key=lambda x: x["count"], reverse=True),
        },
        "medium_impact": {
            "count": len(medium_impact),
            "modules": sorted(medium_impact, key=lambda x: x["count"], reverse=True),
        },
        "low_impact": {
            "count": len(low_impact),
            "modules": sorted(low_impact, key=lambda x: x["count"], reverse=True),
        },
        "duplicates": {
            "classes": duplicate_report.get("summary", {}).get("duplicate_classes", 0),
            "methods": duplicate_report.get("summary", {}).get("duplicate_methods", 0),
            "functions": duplicate_report.get("summary", {}).get(
                "duplicate_functions", 0
            ),
        },
    }


@app.get("/api/duplicates")
async def get_duplicates():
    """重複コード詳細"""
    return duplicate_report


@app.get("/api/duplicates/summary")
async def get_duplicates_summary():
    """重複コードサマリー"""
    summary = duplicate_report.get("summary", {})

    # 上位重複
    top_classes = []
    for name, locations in duplicate_report.get("classes", {}).items():
        top_classes.append(
            {"name": name, "count": len(locations), "locations": locations}
        )

    top_methods = []
    for name, locations in list(duplicate_report.get("methods", {}).items())[:20]:
        top_methods.append(
            {"name": name, "count": len(locations), "locations": locations}
        )

    return {
        "summary": summary,
        "top_classes": sorted(top_classes, key=lambda x: x["count"], reverse=True)[:10],
        "top_methods": sorted(top_methods, key=lambda x: x["count"], reverse=True)[:10],
    }


@app.get("/api/modules/{module_path:path}")
async def get_module_detail(module_path: str):
    """モジュール詳細"""
    if module_path not in dependency_graph:
        raise HTTPException(status_code=404, detail="Module not found")

    return dependency_graph[module_path]


@app.get("/api/export/csv")
async def export_csv(category: str = "all"):
    """CSV出力"""

    output = io.StringIO()
    writer = csv.writer(output)

    if category == "high":
        writer.writerow(["モジュール", "依存数", "インポート一覧"])

        for module, data in dependency_graph.items():
            dep_count = len(data.get("imports", []))
            if dep_count >= 10:
                imports = ", ".join(data.get("imports", [])[:10])
                writer.writerow([module, dep_count, imports])

    elif category == "medium":
        writer.writerow(["モジュール", "依存数", "インポート一覧"])

        for module, data in dependency_graph.items():
            dep_count = len(data.get("imports", []))
            if 5 <= dep_count < 10:
                imports = ", ".join(data.get("imports", [])[:10])
                writer.writerow([module, dep_count, imports])

    elif category == "low":
        writer.writerow(["モジュール", "依存数", "インポート一覧"])

        for module, data in dependency_graph.items():
            dep_count = len(data.get("imports", []))
            if 0 < dep_count < 5:
                imports = ", ".join(data.get("imports", []))
                writer.writerow([module, dep_count, imports])

    elif category == "duplicates":
        writer.writerow(["タイプ", "名前", "重複数", "ファイル1", "ファイル2", "ファイル3"])

        for name, locations in duplicate_report.get("classes", {}).items():
            files = [loc["file"] for loc in locations[:3]]
            writer.writerow(["クラス", name, len(locations)] + files)

        for name, locations in duplicate_report.get("methods", {}).items():
            files = [loc["file"] for loc in locations[:3]]
            writer.writerow(["メソッド", name, len(locations)] + files)

    else:  # all
        writer.writerow(["モジュール", "依存数", "ファイルサイズ", "インポート数"])

        for module, data in dependency_graph.items():
            writer.writerow(
                [
                    module,
                    len(data.get("imports", [])),
                    data.get("file_size", 0),
                    data.get("import_count", 0),
                ]
            )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=observer_export_{category}_{datetime.now().strftime('%Y%m%d')}.csv"
        },
    )


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "modules_loaded": len(dependency_graph),
        "duplicates_loaded": bool(duplicate_report),
    }


# 静的ファイル
app.mount(
    "/static",
    StaticFiles(directory="agents/observer_enhanced/web/static"),
    name="static",
)


@app.get("/")
async def root():
    """ルート"""
    return FileResponse("agents/observer_enhanced/web/templates/dashboard_v2.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)

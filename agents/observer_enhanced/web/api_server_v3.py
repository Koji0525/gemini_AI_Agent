#!/usr/bin/env python3
"""
オブザーバーAPI Server v3
- 契約監視統合
- テスト結果統合
- リアルタイム破壊検知
"""

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Observer Dashboard API v3")

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
contract_violations = {}
test_results = {}
change_report = {}


@app.on_event("startup")
async def load_data():
    """起動時にデータロード"""
    global dependency_graph, duplicate_report, contract_violations, test_results, change_report

    # 依存関係
    if Path("dependency_map.json").exists():
        with open("dependency_map.json", "r") as f:
            dependency_graph = json.load(f)

    # 重複検知
    if Path("duplicate_report.json").exists():
        with open("duplicate_report.json", "r") as f:
            duplicate_report = json.load(f)

    # 契約違反
    if Path("contract_violations_report.json").exists():
        with open("contract_violations_report.json", "r") as f:
            contract_violations = json.load(f)

    # テスト結果
    if Path("test_integration_report.json").exists():
        with open("test_integration_report.json", "r") as f:
            test_results = json.load(f)

    # 変更レポート
    if Path("hybrid_change_report.json").exists():
        with open("hybrid_change_report.json", "r") as f:
            change_report = json.load(f)


@app.get("/api/stats")
async def get_stats():
    """統計情報（拡張版）"""
    total_modules = len(dependency_graph)
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
        "duplicates": duplicate_report.get("summary", {}),
        "contract_violations": contract_violations.get("summary", {}),
        "test_results": test_results.get("test_summary", {}),
        "changes": change_report.get("summary", {}),
    }


@app.get("/api/violations")
async def get_violations():
    """契約違反一覧"""
    return contract_violations


@app.get("/api/test_results")
async def get_test_results():
    """テスト結果"""
    return test_results


@app.get("/api/changes")
async def get_changes():
    """変更レポート"""
    return change_report


@app.get("/api/health_check")
async def health_check():
    """システムヘルスチェック"""
    issues = []

    # 契約違反チェック
    if contract_violations.get("summary", {}).get("high_severity", 0) > 0:
        issues.append(
            {
                "severity": "HIGH",
                "type": "contract_violation",
                "count": contract_violations["summary"]["high_severity"],
            }
        )

    # テスト失敗チェック
    test_summary = test_results.get("test_summary", {})
    if test_summary.get("pass_rate", 100) < 80:
        issues.append(
            {
                "severity": "HIGH",
                "type": "test_failure",
                "pass_rate": test_summary.get("pass_rate", 0),
            }
        )

    # 破壊的変更チェック
    if change_report.get("summary", {}).get("broken_dependencies", 0) > 0:
        issues.append(
            {
                "severity": "HIGH",
                "type": "broken_dependency",
                "count": change_report["summary"]["broken_dependencies"],
            }
        )

    return {
        "status": "healthy" if len(issues) == 0 else "warning",
        "issues": issues,
        "timestamp": test_results.get("timestamp", ""),
    }


app.mount(
    "/static",
    StaticFiles(directory="agents/observer_enhanced/web/static"),
    name="static",
)


@app.get("/")
async def root():
    return FileResponse("agents/observer_enhanced/web/templates/dashboard_v3.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)

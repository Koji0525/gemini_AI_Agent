"""
Flask Web Server - REST API提供
Phase 5: Dashboard & Visualization Layer
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observer_enhanced.dependency_analyzer import DependencyAnalyzer
# Phase 4コンポーネントをインポート
from agents.observer_enhanced.metrics_collector import MetricsCollector
from agents.observer_enhanced.performance_monitor import PerformanceMonitor

# ロガーのセットアップ
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("observer_enhanced.web_server")

# Flaskアプリケーション初期化
app = Flask(__name__, template_folder="templates", static_folder="static")

# CORS有効化
CORS(app)

# グローバルインスタンス
metrics_collector = None
performance_monitor = None
dependency_analyzer = None


def initialize_components():
    """コンポーネント初期化"""
    global metrics_collector, performance_monitor, dependency_analyzer

    try:
        metrics_collector = MetricsCollector(metrics_file="logs/web_metrics.json")
        performance_monitor = PerformanceMonitor(alert_file="logs/web_alerts.json")
        dependency_analyzer = DependencyAnalyzer()
        logger.info("✅ Components initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {e}")
        raise


@app.route("/")
def index():
    """トップページ"""
    try:
        return render_template("dashboard.html")
    except Exception as e:
        logger.error(f"Failed to render dashboard: {e}")
        return jsonify({"error": "Dashboard not available", "message": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """健全性チェックAPI"""
    try:
        latest_metrics = metrics_collector.get_latest()

        if not latest_metrics:
            latest_metrics = metrics_collector.collect()

        cpu = latest_metrics.get("cpu_percent", 0)
        memory = latest_metrics.get("memory_percent", 0)
        disk = latest_metrics.get("disk_percent", 0)

        health_score = 100 - ((cpu + memory + disk) / 3)
        health_score = max(0, min(100, health_score))

        if health_score >= 80:
            status, grade = "excellent", "A"
        elif health_score >= 60:
            status, grade = "good", "B"
        elif health_score >= 40:
            status, grade = "fair", "C"
        elif health_score >= 20:
            status, grade = "poor", "D"
        else:
            status, grade = "critical", "F"

        return jsonify(
            {
                "timestamp": datetime.now().isoformat(),
                "health_score": round(health_score, 1),
                "status": status,
                "grade": grade,
                "metrics": {"cpu_percent": cpu, "memory_percent": memory, "disk_percent": disk},
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"error": "Health check failed", "message": str(e)}), 500


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """最新メトリクス取得API"""
    try:
        history_count = request.args.get("history", default=1, type=int)

        if history_count == 1:
            metrics = metrics_collector.collect()
            return jsonify({"timestamp": datetime.now().isoformat(), "data": metrics})
        else:
            history = metrics_collector.get_history(count=history_count)
            return jsonify(
                {"timestamp": datetime.now().isoformat(), "count": len(history), "data": history}
            )

    except Exception as e:
        logger.error(f"Get metrics failed: {e}")
        return jsonify({"error": "Failed to get metrics", "message": str(e)}), 500


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """アラート取得API"""
    try:
        count = request.args.get("count", default=10, type=int)
        alerts = performance_monitor.get_recent_alerts(count=count)
        return jsonify(
            {"timestamp": datetime.now().isoformat(), "count": len(alerts), "data": alerts}
        )
    except Exception as e:
        logger.error(f"Get alerts failed: {e}")
        return jsonify({"error": "Failed to get alerts", "message": str(e)}), 500


@app.route("/api/status", methods=["GET"])
def get_status():
    """統合ステータス取得API"""
    try:
        metrics = metrics_collector.collect()
        analysis = performance_monitor.analyze_metrics(metrics)
        alert_summary = performance_monitor.get_alert_summary()
        trends = performance_monitor.get_performance_trends()

        return jsonify(
            {
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "analysis": analysis,
                "alerts": alert_summary,
                "trends": trends,
                "status": performance_monitor.get_status(),
            }
        )
    except Exception as e:
        logger.error(f"Get status failed: {e}")
        return jsonify({"error": "Failed to get status", "message": str(e)}), 500


@app.route("/api/dependencies/scan", methods=["GET"])
def scan_dependencies():
    """依存関係スキャンAPI"""
    try:
        import time

        start_time = time.time()

        result = dependency_analyzer.scan_project()
        result["scan_time"] = round(time.time() - start_time, 2)

        return jsonify({"timestamp": datetime.now().isoformat(), "data": result})
    except Exception as e:
        logger.error(f"Dependency scan failed: {e}")
        return jsonify({"error": "Failed to scan dependencies", "message": str(e)}), 500


@app.route("/api/dependencies/impact/<path:file_path>", methods=["GET"])
def get_impact(file_path):
    """ファイル影響範囲分析API"""
    try:
        result = dependency_analyzer.find_impact(file_path)
        return jsonify({"timestamp": datetime.now().isoformat(), "data": result})
    except Exception as e:
        logger.error(f"Impact analysis failed: {e}")
        return jsonify({"error": "Failed to analyze impact", "message": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラー"""
    return jsonify({"error": "Not Found", "message": "The requested resource was not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラー"""
    logger.error(f"Internal Server Error: {error}")
    return (
        jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}),
        500,
    )


def run_server(host="0.0.0.0", port=5000, debug=False):
    """Webサーバー起動"""
    try:
        initialize_components()
        logger.info(f"🌐 Starting web server on {host}:{port}")
        app.run(host=host, port=port, debug=debug, use_reloader=False)
    except Exception as e:
        logger.error(f"❌ Failed to start web server: {e}")
        raise


if __name__ == "__main__":
    run_server(debug=True)


@app.route("/dependencies")
def dependencies_page():
    """依存関係ページ"""
    try:
        return render_template("dependencies.html")
    except Exception as e:
        logger.error(f"Failed to render dependencies: {e}")
        return jsonify({"error": "Dependencies page not available", "message": str(e)}), 500


@app.route("/api/analysis/report", methods=["GET"])
def get_comprehensive_report():
    """包括的な分析レポートAPI"""
    try:
        report = dependency_analyzer.get_comprehensive_report()
        return jsonify({"timestamp": datetime.now().isoformat(), "data": report})
    except Exception as e:
        logger.error(f"Comprehensive report failed: {e}")
        return jsonify({"error": "Failed to generate report", "message": str(e)}), 500


@app.route("/api/analysis/duplicates", methods=["GET"])
def get_duplicates():
    """重複ファイル検出API"""
    try:
        duplicates = dependency_analyzer.detect_duplicates()
        return jsonify(
            {"timestamp": datetime.now().isoformat(), "count": len(duplicates), "data": duplicates}
        )
    except Exception as e:
        logger.error(f"Duplicate detection failed: {e}")
        return jsonify({"error": "Failed to detect duplicates", "message": str(e)}), 500


@app.route("/api/analysis/unused", methods=["GET"])
def get_unused_files():
    """未使用ファイル検出API"""
    try:
        unused = dependency_analyzer.detect_unused_files()
        return jsonify(
            {"timestamp": datetime.now().isoformat(), "count": len(unused), "data": unused}
        )
    except Exception as e:
        logger.error(f"Unused file detection failed: {e}")
        return jsonify({"error": "Failed to detect unused files", "message": str(e)}), 500


@app.route("/api/analysis/reusable", methods=["GET"])
def get_reusable_tools():
    """再利用可能ツール推奨API"""
    try:
        reusable = dependency_analyzer.suggest_reusable_tools()
        return jsonify(
            {"timestamp": datetime.now().isoformat(), "count": len(reusable), "data": reusable}
        )
    except Exception as e:
        logger.error(f"Reusable tools suggestion failed: {e}")
        return jsonify({"error": "Failed to suggest reusable tools", "message": str(e)}), 500


@app.route("/analysis")
def analysis_page():
    """問題検出&分析ページ"""
    try:
        return render_template("analysis.html")
    except Exception as e:
        logger.error(f"Failed to render analysis: {e}")
        return jsonify({"error": "Analysis page not available", "message": str(e)}), 500

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request
import json
import asyncio
import subprocess
import os
import psutil
from datetime import datetime
from pathlib import Path
import logging

app = FastAPI(
    title="24時間AI開発システム ダッシュボード", description="WordPress自動開発AIの監視と管理", version="2.0.0"
)

# パス設定
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")
templates = Jinja2Templates(directory=current_dir / "templates")

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """システム監視クラス"""

    def __init__(self):
        self.base_dir = current_dir.parent

    def get_system_stats(self):
        """システム統計を取得"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # メモリ使用率
            memory = psutil.virtual_memory()

            # ディスク使用率
            disk = psutil.disk_usage("/")

            # プロセス情報
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # 開発ログから情報を取得
            development_info = self.get_development_info()

            stats = {
                "system": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent,
                    "active_processes": len(processes),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                "development": development_info,
                "wordpress": {
                    "status": self.check_wordpress_connection(),
                    "last_activity": self.get_last_wordpress_activity(),
                },
                "ai_system": {
                    "status": "🟢 稼働中",
                    "development_cycles": development_info.get("total_cycles", 0),
                    "errors_detected": development_info.get("total_errors", 0),
                    "improvements_made": development_info.get("total_improvements", 0),
                },
            }

            return stats

        except Exception as e:
            logger.error(f"統計取得エラー: {e}")
            return self.get_fallback_stats()

    def get_development_info(self):
        """開発情報を取得"""
        try:
            dev_log = self.base_dir / "logs" / "ai_development.log"
            if not dev_log.exists():
                return {"total_cycles": 0, "total_errors": 0, "total_improvements": 0}

            with open(dev_log, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 簡単な分析
            total_cycles = sum(1 for line in lines if "開発サイクル" in line)
            total_errors = sum(1 for line in lines if "ERROR" in line)
            total_improvements = sum(1 for line in lines if "改善実施" in line)

            return {
                "total_cycles": total_cycles,
                "total_errors": total_errors,
                "total_improvements": total_improvements,
                "last_activity": lines[-1].strip() if lines else "なし",
            }

        except Exception as e:
            logger.error(f"開発情報取得エラー: {e}")
            return {"total_cycles": 0, "total_errors": 0, "total_improvements": 0}

    def check_wordpress_connection(self):
        """WordPress接続状態を確認"""
        try:
            import requests
            from requests.auth import HTTPBasicAuth

            # 環境変数から取得
            wp_url = os.getenv("WP_URL", "https://uzbek-ma.com")
            wp_username = os.getenv("WP_USERNAME", "uzbek")
            wp_password = os.getenv("WP_PASSWORD", "RkLU07FkrNpeiENdFx3swseJ")

            response = requests.get(
                f"{wp_url}/wp-json/wp/v2/posts", auth=HTTPBasicAuth(wp_username, wp_password), timeout=10
            )

            return "🟢 接続正常" if response.status_code == 200 else "🔴 接続異常"

        except Exception:
            return "🔴 接続エラー"

    def get_last_wordpress_activity(self):
        """最後のWordPress活動を取得"""
        try:
            report_dir = self.base_dir / "reports" / "day4"
            if report_dir.exists():
                reports = list(report_dir.glob("report_*.md"))
                if reports:
                    latest = max(reports, key=lambda x: x.stat().st_mtime)
                    return f"最終投稿: {latest.stem.replace('report_', '')}"

            return "活動記録なし"

        except Exception:
            return "記録取得エラー"

    def get_fallback_stats(self):
        """フォールバック統計"""
        return {
            "system": {
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
                "active_processes": 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "development": {
                "total_cycles": 0,
                "total_errors": 0,
                "total_improvements": 0,
                "last_activity": "データなし",
            },
            "wordpress": {"status": "🔴 状態不明", "last_activity": "データなし"},
            "ai_system": {
                "status": "🟡 状態不明",
                "development_cycles": 0,
                "errors_detected": 0,
                "improvements_made": 0,
            },
        }


# システムモニターの初期化
monitor = SystemMonitor()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """メインダッシュボード"""
    stats = monitor.get_system_stats()
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": stats})


@app.get("/api/stats")
async def get_stats():
    """統計データを取得（強化版）"""
    return monitor.get_system_stats()


@app.get("/api/development/logs")
async def get_development_logs():
    """開発ログを取得"""
    try:
        log_file = current_dir.parent / "logs" / "ai_development.log"
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                logs = f.read().split("\n")
            return {"logs": logs[-50:]}  # 最新50行
        else:
            return {"logs": ["開発ログが存在しません"]}
    except Exception as e:
        return {"logs": [f"ログ取得エラー: {str(e)}"]}


@app.post("/api/development/start")
async def start_development(background_tasks: BackgroundTasks):
    """AI開発を開始"""
    try:
        script_path = current_dir.parent / "scripts" / "ai_development_system.py"

        def run_development():
            subprocess.run(["python3", str(script_path)], cwd=str(current_dir.parent))

        background_tasks.add_task(run_development)

        return JSONResponse(
            {"status": "started", "message": "AI開発システムを起動しました", "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"起動エラー: {str(e)}")


@app.post("/api/wordpress/post")
async def manual_wordpress_post():
    """手動でWordPress投稿を実行"""
    try:
        script_path = current_dir.parent / "scripts" / "run_day4_integrated.py"

        process = subprocess.Popen(
            ["python3", str(script_path)],
            cwd=str(current_dir.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return JSONResponse({"status": "started", "message": "WordPress投稿を開始しました", "pid": process.pid})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"実行エラー: {str(e)}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocketでリアルタイム更新"""
    await websocket.accept()
    try:
        while True:
            # 統計データを送信
            stats = monitor.get_system_stats()
            await websocket.send_json({"type": "stats", "data": stats})

            # 開発ログを送信
            logs_response = await get_development_logs()
            await websocket.send_json({"type": "logs", "data": logs_response["logs"][-10:]})  # 最新10行

            await asyncio.sleep(3)  # 3秒ごとに更新

    except Exception as e:
        logger.error(f"WebSocketエラー: {e}")


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "24時間AI開発システム",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

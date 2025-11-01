from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
import json
import asyncio
import psutil
import time
from datetime import datetime
from pathlib import Path

app = FastAPI(title="常時AI開発システムダッシュボード")

# 現在のディレクトリ
current_dir = Path(__file__).parent

# 静的ファイルとテンプレート
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")
templates = Jinja2Templates(directory=current_dir / "templates")


class SystemMonitor:
    def get_system_stats(self):
        """システム統計を取得"""
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # AI開発システムの状態をチェック
            ai_status = self.check_ai_system()

            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cpu_usage": cpu,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "ai_system": ai_status,
                "wordpress_status": self.check_wordpress(),
                "development_cycles": self.get_development_cycles(),
                "active_features": ["自動テーマ改善", "パフォーマンス監視", "セキュリティ強化", "ユーザー分析"],
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "ai_system": {"status": "❌ エラー", "message": str(e)},
            }

    def check_ai_system(self):
        """AIシステムの状態をチェック"""
        try:
            # プロセスチェック
            for proc in psutil.process_iter(["name", "cmdline"]):
                if proc.info["cmdline"] and "ai_development_system.py" in str(proc.info["cmdline"]):
                    return {"status": "🟢 稼働中", "pid": proc.pid, "message": "常時開発実行中"}

            return {"status": "🔴 停止中", "message": "AIシステムが起動していません"}
        except:
            return {"status": "🟡 状態不明", "message": "状態を取得できません"}

    def check_wordpress(self):
        """WordPress状態をチェック"""
        try:
            import requests

            response = requests.get("https://uzbek-ma.com", timeout=5)
            return {
                "status": "🟢 オンライン" if response.status_code == 200 else "🔴 オフライン",
                "response_time": response.elapsed.total_seconds(),
            }
        except:
            return {"status": "🔴 接続エラー", "response_time": None}

    def get_development_cycles(self):
        """開発サイクル数を取得"""
        try:
            # ログファイルからサイクル数をカウント
            log_file = Path(__file__).parent.parent / "logs" / "ai_development.log"
            if log_file.exists():
                with open(log_file, "r") as f:
                    content = f.read()
                    return content.count("開発サイクル")
            return 0
        except:
            return 0


monitor = SystemMonitor()


@app.get("/")
async def dashboard(request: Request):
    """メインダッシュボード"""
    stats = monitor.get_system_stats()
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": stats})


@app.get("/api/stats")
async def get_stats():
    """統計API"""
    return monitor.get_system_stats()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocketリアルタイム更新"""
    await websocket.accept()
    try:
        while True:
            stats = monitor.get_system_stats()
            await websocket.send_json({"type": "stats", "data": stats})
            await asyncio.sleep(5)
    except Exception as e:
        print(f"WebSocket error: {e}")


@app.get("/api/start_ai")
async def start_ai_system():
    """AIシステムを起動"""
    import subprocess

    try:
        process = subprocess.Popen(
            ["python3", "../scripts/ai_development_system.py"],
            cwd=Path(__file__).parent.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return {"status": "started", "message": "AI開発システムを起動しました", "pid": process.pid}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

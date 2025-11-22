"""
Webダッシュボードサーバー（エラー修正版）
詳細なログとエラーハンドリングを追加
"""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from pydantic import BaseModel
except ImportError:
    print("❌ FastAPIがインストールされていません")
    sys.exit(1)

from agents.f9_human_interface import F9HumanInterface
from tools.sheets_manager import GoogleSheetsManager

app = FastAPI(title="自律開発システム ダッシュボード")

# グローバル変数
sheets_manager = None
f9_interface = None


class InstructionRequest(BaseModel):
    """人間指示のリクエストモデル"""

    instruction_type: str
    content: str
    priority: str = "medium"
    target_task: str = ""


@app.on_event("startup")
async def startup_event():
    """起動時の初期化"""
    global sheets_manager, f9_interface
    try:
        sheets_manager = GoogleSheetsManager()
        f9_interface = F9HumanInterface(sheets_manager)
        print("✅ ダッシュボードサーバー起動")
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        traceback.print_exc()


# エラーハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """グローバルエラーハンドラー"""
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": request.url.path,
        "method": request.method,
    }

    print(f"\n{'=' * 80}")
    print(f"❌ エラー発生: {request.method} {request.url.path}")
    print(f"   エラータイプ: {type(exc).__name__}")
    print(f"   エラー内容: {exc}")
    print("=" * 80)
    traceback.print_exc()
    print("=" * 80)
    print()

    return JSONResponse(status_code=500, content=error_detail)


@app.get("/", response_class=HTMLResponse)
async def root():
    """メインダッシュボード"""
    # HTMLは前回と同じなので省略
    with open("/workspaces/gemini_AI_Agent/agents/web_dashboard/dashboard.html", "r") as f:
        return f.read()


@app.get("/api/stats")
async def get_stats():
    """システム統計を取得"""
    try:
        print("📊 /api/stats 呼び出し")

        result = (
            sheets_manager.service.spreadsheets()
            .values()
            .get(spreadsheetId=sheets_manager.spreadsheet_id, range="pm_tasks!A2:M1000")
            .execute()
        )

        values = result.get("values", [])

        total_tasks = len(values)
        completed_tasks = sum(1 for row in values if len(row) > 4 and row[4] == "completed")
        pending_tasks = sum(1 for row in values if len(row) > 4 and row[4] == "pending")

        stats = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "avg_quality": 8.5,
        }

        print(f"   ✅ 統計: {stats}")
        return stats

    except Exception as e:
        print(f"   ❌ エラー: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/pending")
async def get_pending_tasks():
    """ペンディングタスクを取得"""
    try:
        print("📋 /api/tasks/pending 呼び出し")

        result = (
            sheets_manager.service.spreadsheets()
            .values()
            .get(spreadsheetId=sheets_manager.spreadsheet_id, range="pm_tasks!A2:M1000")
            .execute()
        )

        values = result.get("values", [])

        pending = []
        for row in values:
            if len(row) > 4 and row[4] == "pending":
                pending.append(
                    {
                        "task_id": row[0],
                        "description": row[2] if len(row) > 2 else "",
                        "priority": row[5] if len(row) > 5 else "medium",
                        "estimated_time": row[6] if len(row) > 6 else "1h",
                    }
                )

        print(f"   ✅ ペンディングタスク: {len(pending)}件")
        return pending[:10]

    except Exception as e:
        print(f"   ❌ エラー: {e}")
        traceback.print_exc()
        return []


@app.get("/api/instructions")
async def get_instructions():
    """人間指示一覧を取得"""
    try:
        print("📨 /api/instructions 呼び出し")

        instructions = f9_interface.check_human_instructions()

        result = [
            {
                "timestamp": inst.get("timestamp", ""),
                "instruction_type": inst.get("instruction_type", ""),
                "status": inst.get("status", ""),
                "content": inst.get("content", ""),
            }
            for inst in instructions[:10]
        ]

        print(f"   ✅ 指示一覧: {len(result)}件")
        return result

    except Exception as e:
        print(f"   ❌ エラー: {e}")
        traceback.print_exc()
        return []


@app.post("/api/instruction")
async def add_instruction(request: InstructionRequest):
    """人間指示を追加"""
    try:
        print("\n" + "=" * 80)
        print("📝 /api/instruction POST 呼び出し")
        print(f"   instruction_type: {request.instruction_type}")
        print(f"   content: {request.content}")
        print(f"   priority: {request.priority}")
        print(f"   target_task: {request.target_task}")
        print("=" * 80)

        # F9HumanInterfaceのadd_instructionメソッドを呼び出し
        success = f9_interface.add_instruction(
            instruction_type=request.instruction_type,
            content=request.content,
            priority=request.priority,
            target_task=request.target_task,
        )

        print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
        print("=" * 80)
        print()

        return {"success": success}

    except Exception as e:
        print(f"\n{'=' * 80}")
        print("❌ /api/instruction エラー")
        print(f"   エラータイプ: {type(e).__name__}")
        print(f"   エラー内容: {e}")
        print("=" * 80)
        traceback.print_exc()
        print("=" * 80)
        print()

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "instruction_type": request.instruction_type,
                "content": request.content,
            },
        )


@app.get("/api/logs")
async def get_logs():
    """最新ログを取得"""
    try:
        print("📝 /api/logs 呼び出し")

        log_files = sorted(
            Path("logs").glob("autonomous_v*.log"), key=os.path.getmtime, reverse=True
        )

        if log_files:
            with open(log_files[0], "r", encoding="utf-8") as f:
                lines = f.readlines()
                result = "".join(lines[-50:])
                print(f"   ✅ ログ取得: {len(lines)}行")
                return {"logs": result}

        print("   ⚠️  ログファイルなし")
        return {"logs": "ログファイルが見つかりません"}

    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return {"logs": f"エラー: {str(e)}"}


@app.get("/api/snapshot")
async def get_snapshot():
    """システムスナップショットを取得（新規追加）"""
    try:
        print("📸 /api/snapshot 呼び出し")

        # 統計情報を集約
        stats = await get_stats()
        pending = await get_pending_tasks()
        instructions = await get_instructions()

        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "pending_tasks_count": len(pending),
            "pending_instructions_count": len(instructions),
            "system_status": "running",
        }

        print(f"   ✅ スナップショット生成")
        return snapshot

    except Exception as e:
        print(f"   ❌ エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def start_server(port: int = 8000):
    """サーバーを起動"""
    print(f"\n{'=' * 80}")
    print("🌐 Webダッシュボードサーバー起動（エラー修正版）")
    print("=" * 80)
    print(f"\n📍 アクセスURL: http://localhost:{port}")
    print("\n🔧 改善点:")
    print("  ✅ 詳細なエラーログ追加")
    print("  ✅ グローバルエラーハンドラー追加")
    print("  ✅ /api/snapshot エンドポイント追加")
    print("  ✅ 各エンドポイントのログ出力")
    print("\n⏹️  停止: Ctrl+C")
    print("=" * 80)
    print()

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    start_server()

"""
Webダッシュボードサーバー（システム制御拡張版）
既存機能 + システム起動/停止制御
"""

import os
import signal
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

# 既存のdashboard_server.pyをインポート

from fastapi import HTTPException

# ステート管理ファイル
STATE_FILE = "/tmp/system_control.state"
PID_FILE = "/tmp/system_executor.pid"


def get_system_state():
    """システム状態を取得"""
    if not os.path.exists(STATE_FILE):
        return "stopped"

    with open(STATE_FILE, "r") as f:
        state = f.read().strip()

    # PIDファイルでプロセスの実存を確認
    if state == "running" and os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        try:
            os.kill(pid, 0)  # プロセスが存在するかチェック
            return "running"
        except OSError:
            return "stopped"

    return state


def set_system_state(state: str):
    """システム状態を設定"""
    with open(STATE_FILE, "w") as f:
        f.write(state)


@app.get("/api/system/status")
async def get_system_status():
    """システム状態を取得"""
    state = get_system_state()

    pid = None
    if state == "running" and os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

    return {"state": state, "pid": pid, "is_running": state == "running"}


@app.post("/api/system/start")
async def start_system():
    """システムを起動"""
    try:
        print("\n" + "=" * 80)
        print("🚀 システム起動リクエスト")
        print("=" * 80)

        current_state = get_system_state()

        if current_state == "running":
            print("⚠️  システムは既に起動中です")
            return {"success": False, "message": "システムは既に起動中です"}

        # 起動スクリプトをバックグラウンドで実行
        print("🔄 24時間稼働システムを起動中...")

        process = subprocess.Popen(
            ["bash", "sh/run_autonomous_24h_v6_final.sh"],
            stdout=open("logs/executor_stdout.log", "w"),
            stderr=open("logs/executor_stderr.log", "w"),
            cwd="/workspaces/gemini_AI_Agent",
        )

        # PIDを保存
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))

        # 状態を更新
        set_system_state("running")

        print(f"✅ システム起動完了 (PID: {process.pid})")
        print("=" * 80)

        return {"success": True, "message": "システムを起動しました", "pid": process.pid}

    except Exception as e:
        print(f"❌ システム起動エラー: {e}")
        return {"success": False, "message": f"起動エラー: {str(e)}"}


@app.post("/api/system/stop")
async def stop_system():
    """システムを停止"""
    try:
        print("\n" + "=" * 80)
        print("⏹️  システム停止リクエスト")
        print("=" * 80)

        current_state = get_system_state()

        if current_state != "running":
            print("⚠️  システムは起動していません")
            return {"success": False, "message": "システムは起動していません"}

        # PIDを取得
        if not os.path.exists(PID_FILE):
            print("⚠️  PIDファイルが見つかりません")
            set_system_state("stopped")
            return {"success": False, "message": "PIDファイルが見つかりません"}

        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        print(f"🔄 プロセス(PID: {pid})を停止中...")

        # プロセスを停止
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"✅ プロセス停止シグナル送信")
        except OSError:
            print(f"⚠️  プロセスが既に終了しています")

        # ファイルを削除
        os.remove(PID_FILE)
        set_system_state("stopped")

        print("✅ システム停止完了")
        print("=" * 80)

        return {"success": True, "message": "システムを停止しました"}

    except Exception as e:
        print(f"❌ システム停止エラー: {e}")
        return {"success": False, "message": f"停止エラー: {str(e)}"}


# 既存の start_server 関数を使用

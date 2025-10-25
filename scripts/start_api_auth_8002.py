#!/usr/bin/env python3
"""ポート8002で起動するAPIキー管理システム"""

import sys
import os
import asyncio
import secrets
import hashlib
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging

# プロジェクトのルートパスを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーションの作成
app = FastAPI(
    title="Multi-Agent System API with Authentication",
    description="APIキー管理機能付きマルチエージェントシステム",
    version="2.0.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIキー認証
api_key_header = APIKeyHeader(name="X-API-Key")


# データモデル
class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class TaskRequest(BaseModel):
    goal: str = Field(..., min_length=5, max_length=1000)
    task_type: str = Field(default="content_creation")
    priority: str = Field(default="medium")


class TaskResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    message: str
    result: Optional[Dict] = None
    created_by: str


class SystemStatus(BaseModel):
    status: str
    version: str
    total_users: int
    total_tasks: int
    active_tasks: int


# データストレージ
users_db = {}
api_keys_db = {}
tasks_db = {}


# APIキーマネージャー
class APIKeyManager:
    @staticmethod
    def generate_api_key() -> str:
        return f"ma_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def register_user(username: str, email: str) -> tuple:
        user_id = f"user_{secrets.token_urlsafe(8)}"
        api_key = APIKeyManager.generate_api_key()
        hashed_key = APIKeyManager.hash_api_key(api_key)

        users_db[user_id] = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "is_active": True,
        }

        api_keys_db[hashed_key] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "is_active": True,
            "usage_count": 0,
            "last_used": None,
        }

        logger.info(f"新しいユーザー登録: {username} ({user_id})")
        return user_id, api_key

    @staticmethod
    def validate_api_key(api_key: str) -> Optional[str]:
        if not api_key:
            return None

        hashed_key = APIKeyManager.hash_api_key(api_key)
        key_info = api_keys_db.get(hashed_key)

        if not key_info or not key_info["is_active"]:
            return None

        key_info["usage_count"] += 1
        key_info["last_used"] = datetime.now().isoformat()

        return key_info["user_id"]


# APIキー認証
async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    user_id = APIKeyManager.validate_api_key(api_key)
    if not user_id:
        raise HTTPException(
            status_code=401, detail="無効なAPIキーまたは権限がありません"
        )
    return user_id


# エンドポイント
@app.get("/", response_model=SystemStatus)
async def root():
    active_tasks = len(
        [t for t in tasks_db.values() if t["status"] in ["accepted", "processing"]]
    )
    return SystemStatus(
        status="running",
        version="2.0.0",
        total_users=len(users_db),
        total_tasks=len(tasks_db),
        active_tasks=active_tasks,
    )


@app.post("/api/v1/auth/register")
async def register_user(request: UserRegistration):
    try:
        for user in users_db.values():
            if user["email"] == request.email:
                raise HTTPException(
                    status_code=400, detail="このメールアドレスは既に登録されています"
                )

        user_id, api_key = APIKeyManager.register_user(request.username, request.email)

        return {
            "success": True,
            "user_id": user_id,
            "api_key": api_key,
            "message": "ユーザー登録が完了しました！APIキーを安全に保管してください。",
            "note": "このAPIキーは一度しか表示されません。紛失した場合は再登録が必要です。",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登録に失敗: {str(e)}")


@app.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(
    request: TaskRequest, current_user: str = Depends(verify_api_key)
):
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    tasks_db[task_id] = {
        "task_id": task_id,
        "status": "accepted",
        "progress": 0.0,
        "message": "タスクを受信しました",
        "result": None,
        "goal": request.goal,
        "task_type": request.task_type,
        "priority": request.priority,
        "created_by": current_user,
        "created_at": datetime.now().isoformat(),
    }

    asyncio.create_task(process_task(task_id, request.goal, current_user))

    logger.info(f"新しいタスク: {task_id} by {current_user}")
    return TaskResponse(**tasks_db[task_id])


@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: str = Depends(verify_api_key)):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")

    task = tasks_db[task_id]
    if task["created_by"] != current_user:
        raise HTTPException(
            status_code=403, detail="このタスクへのアクセス権がありません"
        )

    return TaskResponse(**task)


@app.get("/api/v1/tasks")
async def list_tasks(current_user: str = Depends(verify_api_key)):
    user_tasks = [
        task for task in tasks_db.values() if task["created_by"] == current_user
    ]

    return {
        "user_id": current_user,
        "username": users_db[current_user]["username"],
        "total_tasks": len(user_tasks),
        "active_tasks": len(
            [t for t in user_tasks if t["status"] in ["accepted", "processing"]]
        ),
        "completed_tasks": len([t for t in user_tasks if t["status"] == "completed"]),
        "tasks": user_tasks,
    }


async def process_task(task_id: str, goal: str, user_id: str):
    try:
        logger.info(f"タスク処理開始: {task_id} by {user_id}")

        steps = [
            ("分析中...", 10),
            ("計画作成...", 25),
            ("実行中...", 50),
            ("品質チェック...", 75),
            ("最終処理...", 90),
            ("完了", 100),
        ]

        for message, progress in steps:
            await asyncio.sleep(2)
            if task_id in tasks_db:
                tasks_db[task_id].update(
                    {
                        "status": "processing",
                        "progress": float(progress),
                        "message": f"{message} {progress}%完了",
                    }
                )

        tasks_db[task_id].update(
            {
                "status": "completed",
                "progress": 100.0,
                "message": "タスクが正常に完了しました",
                "result": {
                    "output": f"目標 '{goal}' の処理が完了しました",
                    "quality_score": 8.5,
                    "execution_time": "12秒",
                    "output_files": ["result.md", "report.json"],
                },
            }
        )

        logger.info(f"タスク完了: {task_id} by {user_id}")

    except Exception as e:
        logger.error(f"タスク処理エラー: {task_id} - {e}")
        if task_id in tasks_db:
            tasks_db[task_id].update(
                {
                    "status": "failed",
                    "message": f"処理エラー: {str(e)}",
                    "progress": 0.0,
                }
            )


if __name__ == "__main__":
    import uvicorn

    port = 8002
    print("🚀 APIキー管理機能付きマルチエージェントシステムAPI")
    print("=" * 60)
    print(f"📍 ポート: {port}")
    print("")
    print("🌐 アクセスURL:")
    print(
        f"   📚 ドキュメント: https://gory-cackle-69xw7jw55qxwc557w-{port}.app.github.dev/docs"
    )
    print("")
    print("🔐 機能:")
    print("   • ユーザー登録とAPIキー発行")
    print("   • 個人別タスク管理")
    print("   • 進捗状況追跡")
    print("")
    print("⏳ 起動中...")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

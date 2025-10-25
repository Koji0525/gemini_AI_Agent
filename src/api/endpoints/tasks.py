#!/usr/bin/env python3
"""タスク関連APIエンドポイント"""

from fastapi import APIRouter, HTTPException
from ..models.request_models import TaskSubmissionRequest, TaskStatusResponse

router = APIRouter()


@router.post("/tasks", response_model=TaskStatusResponse)
async def submit_task(request: TaskSubmissionRequest):
    """タスクを投入する最小限のAPI"""
    try:
        return TaskStatusResponse(
            task_id=f"mock_task_{hash(request.goal)}",
            status="accepted",
            progress=0.0,
            message="APIテストモード: タスクを受信しました",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """タスクステータスを取得する最小限のAPI"""
    return TaskStatusResponse(
        task_id=task_id,
        status="completed",
        progress=100.0,
        message="APIテストモード: 完了",
    )

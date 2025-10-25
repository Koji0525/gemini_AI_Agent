#!/usr/bin/env python3
"""APIリクエスト/レスポンスモデル"""

from pydantic import BaseModel, Field
from typing import Optional


class TaskSubmissionRequest(BaseModel):
    goal: str = Field(..., min_length=5, max_length=500)
    task_type: str = Field(default="content_creation")
    priority: str = Field(default="medium")


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    message: Optional[str] = None

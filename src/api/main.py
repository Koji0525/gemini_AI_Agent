#!/usr/bin/env python3
"""マルチエージェントシステムAPIサーバー"""

from fastapi import FastAPI
from .endpoints.tasks import router as tasks_router

app = FastAPI(
    title="Multi-Agent System API", description="最小限のAPI実装", version="0.1.0"
)

# ルーターの登録
app.include_router(tasks_router, prefix="/api/v1", tags=["tasks"])


@app.get("/")
async def root():
    return {"status": "running", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

#!/usr/bin/env python3
"""
RESTful API実装 - FastAPI

タスクID: {task_id}
説明: {description}
生成日時: {timestamp}
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
from datetime import datetime

# アプリケーション初期化
app = FastAPI(
    title="{description}",
    description="自動生成されたRESTful API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# モデル定義
# ========================================

class ItemBase(BaseModel):
    """アイテムの基本モデル"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, ge=0)
    tags: List[str] = Field(default_factory=list)


class ItemCreate(ItemBase):
    """アイテム作成用モデル"""
    pass


class Item(ItemBase):
    """アイテムレスポンスモデル"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class HealthCheck(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str
    timestamp: datetime


# ========================================
# インメモリストレージ（本番ではDBに置き換え）
# ========================================

items_db: List[Item] = []
next_id = 1


# ========================================
# エンドポイント
# ========================================

@app.get("/", response_model=HealthCheck, tags=["Health"])
async def root():
    """ヘルスチェック"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now()
    )


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """詳細ヘルスチェック"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now()
    )


@app.get("/items", response_model=List[Item], tags=["Items"])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    tag: Optional[str] = None
):
    """アイテム一覧取得
    
    - **skip**: スキップ件数（ページネーション用）
    - **limit**: 取得件数上限
    - **tag**: タグフィルター（オプション）
    """
    filtered_items = items_db
    
    if tag:
        filtered_items = [item for item in items_db if tag in item.tags]
    
    return filtered_items[skip:skip + limit]


@app.get("/items/{{item_id}}", response_model=Item, tags=["Items"])
async def get_item(item_id: int):
    """アイテム詳細取得"""
    for item in items_db:
        if item.id == item_id:
            return item
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item {{item_id}} not found"
    )


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item: ItemCreate):
    """アイテム作成"""
    global next_id
    
    new_item = Item(
        id=next_id,
        name=item.name,
        description=item.description,
        price=item.price,
        tags=item.tags,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    items_db.append(new_item)
    next_id += 1
    
    return new_item


@app.put("/items/{{item_id}}", response_model=Item, tags=["Items"])
async def update_item(item_id: int, item_update: ItemCreate):
    """アイテム更新"""
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            updated_item = Item(
                id=item_id,
                name=item_update.name,
                description=item_update.description,
                price=item_update.price,
                tags=item_update.tags,
                created_at=item.created_at,
                updated_at=datetime.now()
            )
            items_db[idx] = updated_item
            return updated_item
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item {{item_id}} not found"
    )


@app.delete("/items/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
async def delete_item(item_id: int):
    """アイテム削除"""
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(idx)
            return
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item {{item_id}} not found"
    )


# ========================================
# エラーハンドラー
# ========================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={{"detail": str(exc)}}
    )


# ========================================
# 起動
# ========================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

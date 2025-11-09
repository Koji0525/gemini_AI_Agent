# knowledge_system/core_agents/data_models.py
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class KnowledgeEntry(BaseModel):
    """
    ナレッジエントリーのデータモデルを定義します。
    Pydanticを使用して、データの型と構造を保証します。
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    category: str = "Uncategorized"
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydanticモデルの設定"""
        from_attributes = True # ORMモデルなどからも変換可能にする
        validate_assignment = True # フィールドへの再代入時もバリデーションを実行

if __name__ == '__main__':
    # データモデルの使用例
    entry = KnowledgeEntry(
        content="これはテストナレッジです。",
        category="Testing",
        tags=["test", "example"],
        metadata={"source": "manual"}
    )
    print("--- 作成されたナレッジエントリー ---")
    print(entry.model_dump_json(indent=4))

    # IDとタイムスタンプが自動的に設定されることを確認
    assert isinstance(entry.id, str)
    assert isinstance(entry.created_at, datetime)

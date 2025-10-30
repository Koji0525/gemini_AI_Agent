#!/usr/bin/env python3
"""
統一データモデル

全てのログソースは、このモデルに変換される
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


class ContentType(Enum):
    """コンテンツタイプ"""

    TASK = "task"
    ERROR = "error"
    INSIGHT = "insight"
    DECISION = "decision"
    SUCCESS = "success"
    FAILURE = "failure"


class SourceType(Enum):
    """ソースタイプ"""

    CONVERSATION = "conversation"
    SPREADSHEET = "spreadsheet"
    GITHUB = "github"
    PRODUCTION = "production"
    SLACK = "slack"


@dataclass
class UnifiedLogEntry:
    """
    統一ログエントリ

    どんなソースからも変換される標準フォーマット
    """

    # 必須フィールド
    timestamp: datetime
    source_type: SourceType
    source_id: str

    # 内容
    content_type: ContentType
    content: Dict[str, Any]

    # メタデータ
    quality_score: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.8

    # 関連情報
    related_entries: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "content_type": self.content_type.value,
            "content": self.content,
            "quality_score": self.quality_score,
            "tags": self.tags,
            "confidence": self.confidence,
            "related_entries": self.related_entries,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnifiedLogEntry":
        """辞書から生成"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source_type=SourceType(data["source_type"]),
            source_id=data["source_id"],
            content_type=ContentType(data["content_type"]),
            content=data["content"],
            quality_score=data.get("quality_score"),
            tags=data.get("tags", []),
            confidence=data.get("confidence", 0.8),
            related_entries=data.get("related_entries", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class IntegrationMetrics:
    """統合パイプラインのメトリクス"""

    # データ量
    total_entries: int = 0
    entries_by_source: Dict[str, int] = field(default_factory=dict)
    entries_by_type: Dict[str, int] = field(default_factory=dict)

    # 品質
    avg_quality_score: float = 0.0
    high_quality_ratio: float = 0.0

    # パターン
    patterns_extracted: Dict[str, int] = field(default_factory=dict)
    deduplication_ratio: float = 0.0

    # パフォーマンス
    execution_time: float = 0.0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "total_entries": self.total_entries,
            "entries_by_source": self.entries_by_source,
            "entries_by_type": self.entries_by_type,
            "avg_quality_score": self.avg_quality_score,
            "high_quality_ratio": self.high_quality_ratio,
            "patterns_extracted": self.patterns_extracted,
            "deduplication_ratio": self.deduplication_ratio,
            "execution_time": self.execution_time,
            "errors": self.errors,
        }

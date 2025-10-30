"""
汎用データ統合フレームワーク

どんなログソースからもナレッジを抽出し、
knowledge_baseに統合する汎用的なシステム
"""

from .pipeline import DataIntegrationPipeline
from .models import UnifiedLogEntry
from .sources import DataSourceRegistry

__all__ = [
    'DataIntegrationPipeline',
    'UnifiedLogEntry',
    'DataSourceRegistry',
]

"""
データ統合パッケージ
"""

from .pipeline import DataIntegrationPipeline


# create_pipeline関数が存在しないため、代わりにDataIntegrationPipelineクラスを提供
def create_pipeline():
    """パイプラインを作成する関数（後方互換性のため）"""
    return DataIntegrationPipeline()


__all__ = ["DataIntegrationPipeline", "create_pipeline"]

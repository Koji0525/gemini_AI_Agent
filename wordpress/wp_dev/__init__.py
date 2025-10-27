"""
WordPress開発専門エージェント統合パッケージ
"""
from .wp_requirements_agent import WordPressRequirementsAgent
from .wp_cpt_agent import WordPressCPTAgent
# from .wp_taxonomy_agent import WordPressTaxonomyAgent  # 未実装
from .wp_acf_agent import WordPressACFAgent
from .wp_dev_agent import WordPressDevAgent  # 統合エージェント

__all__ = [
    'WordPressRequirementsAgent',
    'WordPressCPTAgent',
    # 'WordPressTaxonomyAgent',  # 未実装
    'WordPressACFAgent',
    'WordPressDevAgent'  # 追加
]

__version__ = '1.0.1'

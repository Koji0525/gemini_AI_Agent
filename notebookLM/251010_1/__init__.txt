"""
WordPressエージェントパッケージ
機能別に分割された各モジュールを統合
"""

from .wp_agent import WordPressAgent

__all__ = ['WordPressAgent']
__version__ = '2.0.0'
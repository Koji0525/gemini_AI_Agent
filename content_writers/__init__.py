# content_writers/__init__.py
"""コンテンツライターエージェントパッケージ - 言語別ライター統合"""

from .base_writer import BaseContentWriter
from .ja_writer_agent import JapaneseContentWriter
from .en_writer_agent import EnglishContentWriter

__all__ = [
    'BaseContentWriter',
    'JapaneseContentWriter',
    'EnglishContentWriter',
]

# 将来の拡張用（実装済みの場合のみ有効化）
try:
    from .ru_writer_agent import RussianContentWriter
    __all__.append('RussianContentWriter')
except ImportError:
    pass

try:
    from .uz_writer_agent import UzbekContentWriter
    __all__.append('UzbekContentWriter')
except ImportError:
    pass

try:
    from .zh_writer_agent import ChineseContentWriter
    __all__.append('ChineseContentWriter')
except ImportError:
    pass

try:
    from .ko_writer_agent import KoreanContentWriter
    __all__.append('KoreanContentWriter')
except ImportError:
    pass

try:
    from .tr_writer_agent import TurkishContentWriter
    __all__.append('TurkishContentWriter')
except ImportError:
    pass
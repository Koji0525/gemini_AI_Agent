"""
統一されたインポートシステム
"""
import sys
import os

# 親ディレクトリをパスに追加
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 利用可能なモジュールを明示的にエクスポート
try:
    from .database_fixed import DatabaseManager
    DATABASE_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  DatabaseManager インポート不可: {e}")
    DATABASE_MANAGER_AVAILABLE = False

try:
    from .models_fixed import EmbeddingModel
    EMBEDDING_MODEL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  EmbeddingModel インポート不可: {e}")
    EMBEDDING_MODEL_AVAILABLE = False

# 利用可能なクラスをエクスポート
__all__ = []
if DATABASE_MANAGER_AVAILABLE:
    __all__.append('DatabaseManager')
if EMBEDDING_MODEL_AVAILABLE:
    __all__.append('EmbeddingModel')

print(f"✅ 利用可能なクラス: {__all__}")

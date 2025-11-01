"""
WordPress開発エージェント群（簡易版）
変更理由: 依存関係の問題を解決、REST API直接版を優先
"""

# 簡易版エージェント（playwright不要）
try:
    from wordpress.wp_dev.wp_simple_agents import (
        SimpleCPTAgent,
        SimpleACFAgent,
        SimplePostCreator,
    )
    
    # エイリアス（既存コードとの互換性）
    WordPressCPTAgent = SimpleCPTAgent
    WordPressACFAgent = SimpleACFAgent
    WordPressTaxonomyAgent = SimpleCPTAgent  # タクソノミーは簡易版で対応
    
    __all__ = [
        'SimpleCPTAgent',
        'SimpleACFAgent',
        'SimplePostCreator',
        'WordPressCPTAgent',
        'WordPressACFAgent',
        'WordPressTaxonomyAgent',
    ]
    
except Exception as e:
    print(f"⚠️ 簡易版エージェントのインポートエラー: {e}")
    __all__ = []

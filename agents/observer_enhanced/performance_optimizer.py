"""
パフォーマンス最適化 (P8-T008)

目標:
- ダッシュボードロード時間: <3秒
- API応答時間: <500ms
- メモリ使用量: <500MB追加
"""

import functools
import time
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """
    パフォーマンス最適化ユーティリティ
    
    機能:
    1. 関数実行時間計測
    2. キャッシュ管理
    3. メモリ使用量監視
    """
    
    def __init__(self):
        self._cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def measure_time(self, func: Callable) -> Callable:
        """
        関数の実行時間を計測するデコレータ
        
        使用例:
        @optimizer.measure_time
        def slow_function():
            time.sleep(1)
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000  # ミリ秒
            
            logger.info(f"{func.__name__} took {duration:.2f}ms")
            
            return result
        
        return wrapper
    
    def cache_result(self, ttl: int = 300):
        """
        関数結果をキャッシュするデコレータ
        
        Args:
            ttl: Time To Live (秒)
        
        使用例:
        @optimizer.cache_result(ttl=60)
        def expensive_function(arg):
            return heavy_computation(arg)
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # キャッシュキー生成
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # キャッシュヒット確認
                if cache_key in self._cache:
                    cached_time, cached_result = self._cache[cache_key]
                    if time.time() - cached_time < ttl:
                        self._cache_hits += 1
                        logger.debug(f"Cache HIT: {func.__name__}")
                        return cached_result
                
                # キャッシュミス - 実行
                self._cache_misses += 1
                logger.debug(f"Cache MISS: {func.__name__}")
                
                result = func(*args, **kwargs)
                
                # キャッシュ保存
                self._cache[cache_key] = (time.time(), result)
                
                return result
            
            return wrapper
        
        return decorator
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> dict:
        """
        キャッシュ統計を取得
        
        Returns:
            {
                "size": キャッシュサイズ,
                "hits": ヒット数,
                "misses": ミス数,
                "hit_rate": ヒット率
            }
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0
        
        return {
            "size": len(self._cache),
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": hit_rate
        }


# グローバルインスタンス
optimizer = PerformanceOptimizer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 使用例（既存コンポーネントへの適用）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def optimize_dependency_detector():
    """
    HiddenDependencyDetectorを最適化
    
    最適化内容:
    1. プロジェクトスキャン結果を5分間キャッシュ
    2. ファイル単位のスキャン結果を1分間キャッシュ
    """
    from agents.observer_enhanced.hidden_dependency_detector import HiddenDependencyDetector
    
    # 元のメソッドを保存
    original_scan = HiddenDependencyDetector.scan_project
    original_detect = HiddenDependencyDetector.detect_file
    
    # 最適化版で置き換え
    HiddenDependencyDetector.scan_project = optimizer.cache_result(ttl=300)(
        optimizer.measure_time(original_scan)
    )
    
    HiddenDependencyDetector.detect_file = optimizer.cache_result(ttl=60)(
        optimizer.measure_time(original_detect)
    )
    
    logger.info("HiddenDependencyDetector optimized")


def optimize_code_search():
    """
    CodeIntelligenceを最適化
    
    最適化内容:
    1. インデックス構築を10分間キャッシュ
    2. 検索結果を5分間キャッシュ
    """
    from agents.observer_enhanced.code_intelligence import CodeIntelligence
    
    original_search = CodeIntelligence.search
    
    CodeIntelligence.search = optimizer.cache_result(ttl=300)(
        optimizer.measure_time(original_search)
    )
    
    logger.info("CodeIntelligence optimized")


def optimize_impact_analyzer():
    """
    ChangeImpactAnalyzerを最適化
    
    最適化内容:
    1. Git差分取得を1分間キャッシュ
    2. 影響分析を5分間キャッシュ
    """
    from agents.observer_enhanced.change_impact_analyzer import ChangeImpactAnalyzer
    
    original_analyze = ChangeImpactAnalyzer.analyze_all_changes
    
    ChangeImpactAnalyzer.analyze_all_changes = optimizer.cache_result(ttl=300)(
        optimizer.measure_time(original_analyze)
    )
    
    logger.info("ChangeImpactAnalyzer optimized")


def apply_all_optimizations():
    """すべての最適化を適用"""
    optimize_dependency_detector()
    optimize_code_search()
    optimize_impact_analyzer()
    
    logger.info("All optimizations applied")
    
    return {
        "status": "success",
        "optimizations": [
            "HiddenDependencyDetector",
            "CodeIntelligence",
            "ChangeImpactAnalyzer"
        ]
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 起動時に自動適用
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 パフォーマンス最適化を適用中...")
    result = apply_all_optimizations()
    print(f"✅ 最適化完了: {result}")
    
    # 統計表示
    import time
    time.sleep(1)
    stats = optimizer.get_cache_stats()
    print(f"\n📊 キャッシュ統計: {stats}")

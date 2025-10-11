"""
CacheManager - インテリジェントキャッシュ管理エージェント

頻繁なエラーパターンのキャッシュ、修正済みエラーの記録、
類似エラーの検出と高速修正、キャッシュ有効期限管理を提供する。
"""

import json
import hashlib
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import Counter
import logging

logger = logging.getLogger(__name__)


@dataclass
class ErrorPattern:
    """エラーパターン"""
    error_type: str
    error_message_pattern: str
    stack_trace_pattern: str
    file_pattern: str
    frequency: int = 0
    last_seen: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "error_message_pattern": self.error_message_pattern,
            "stack_trace_pattern": self.stack_trace_pattern,
            "file_pattern": self.file_pattern,
            "frequency": self.frequency,
            "last_seen": self.last_seen.isoformat()
        }


@dataclass
class CachedFix:
    """キャッシュされた修正"""
    error_hash: str
    fix_code: str
    fix_description: str
    success_rate: float
    application_count: int
    created_at: datetime
    last_used: datetime
    ttl_hours: int = 168  # 1週間
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """有効期限切れかチェック"""
        expiry = self.created_at + timedelta(hours=self.ttl_hours)
        return datetime.now() > expiry
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_hash": self.error_hash,
            "fix_code": self.fix_code,
            "fix_description": self.fix_description,
            "success_rate": self.success_rate,
            "application_count": self.application_count,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "ttl_hours": self.ttl_hours,
            "metadata": self.metadata
        }


class CacheManagerAgent:
    """
    インテリジェントキャッシュ管理エージェント
    
    主な機能:
    1. エラーパターンの学習とキャッシュ
    2. 修正済みエラーの記録
    3. 類似エラーの高速検出
    4. キャッシュ有効期限管理
    5. キャッシュヒット率の最適化
    """
    
    def __init__(self, 
                 cache_dir: str = ".cache",
                 similarity_threshold: float = 0.85,
                 max_cache_size: int = 1000):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.similarity_threshold = similarity_threshold
        self.max_cache_size = max_cache_size
        
        # キャッシュストレージ
        self.fix_cache: Dict[str, CachedFix] = {}
        self.error_patterns: Dict[str, ErrorPattern] = {}
        
        # 統計情報
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "patterns_learned": 0,
            "fixes_cached": 0,
            "successful_applications": 0,
            "failed_applications": 0
        }
        
        # キャッシュファイル
        self.cache_file = self.cache_dir / "fix_cache.pkl"
        self.patterns_file = self.cache_dir / "error_patterns.json"
        
        # 起動時にキャッシュを読み込む
        self._load_cache()
        
        logger.info(f"CacheManagerAgent initialized (cache_dir={cache_dir})")
    
    def compute_error_hash(self, error_context: Dict[str, Any]) -> str:
        """
        エラーコンテキストからハッシュを計算
        
        類似したエラーは同じハッシュを持つように正規化する
        """
        # エラーメッセージから変数名や値を除去して正規化
        error_type = error_context.get("error_type", "")
        error_message = error_context.get("error_message", "")
        source_file = error_context.get("source_file", "")
        
        # 正規化: 数字、ファイルパスの具体的な部分を除去
        normalized_message = self._normalize_error_message(error_message)
        normalized_file = Path(source_file).name if source_file else ""
        
        # ハッシュ用の文字列を作成
        hash_string = f"{error_type}|{normalized_message}|{normalized_file}"
        
        return hashlib.sha256(hash_string.encode()).hexdigest()[:16]
    
    def _normalize_error_message(self, message: str) -> str:
        """エラーメッセージを正規化"""
        import re
        
        # 数字を除去
        message = re.sub(r'\d+', 'N', message)
        
        # ファイルパスを除去
        message = re.sub(r'[/\\][^\s]+', '<PATH>', message)
        
        # 変数名を一般化（簡易版）
        message = re.sub(r"'[^']+'" , '<VAR>', message)
        message = re.sub(r'"[^"]+"', '<VAR>', message)
        
        return message.lower().strip()
    
    def cache_fix(self,
                 error_context: Dict[str, Any],
                 fix_code: str,
                 fix_description: str,
                 ttl_hours: int = 168) -> str:
        """
        修正をキャッシュに保存
        
        Args:
            error_context: エラーコンテキスト
            fix_code: 修正コード
            fix_description: 修正の説明
            ttl_hours: 有効期限（時間）
        
        Returns:
            エラーハッシュ
        """
        error_hash = self.compute_error_hash(error_context)
        
        if error_hash in self.fix_cache:
            # 既存のキャッシュを更新
            cached_fix = self.fix_cache[error_hash]
            cached_fix.last_used = datetime.now()
            logger.debug(f"Updated existing cache entry: {error_hash}")
        else:
            # 新しいキャッシュエントリを作成
            cached_fix = CachedFix(
                error_hash=error_hash,
                fix_code=fix_code,
                fix_description=fix_description,
                success_rate=0.0,
                application_count=0,
                created_at=datetime.now(),
                last_used=datetime.now(),
                ttl_hours=ttl_hours,
                metadata={
                    "error_type": error_context.get("error_type"),
                    "original_message": error_context.get("error_message", "")[:200]
                }
            )
            self.fix_cache[error_hash] = cached_fix
            self.stats["fixes_cached"] += 1
            logger.info(f"Cached new fix: {error_hash}")
        
        # エラーパターンを学習
        self._learn_error_pattern(error_context)
        
        # キャッシュを保存
        self._save_cache()
        
        # サイズ制限をチェック
        self._enforce_cache_size_limit()
        
        return error_hash
    
    def get_cached_fix(self, error_context: Dict[str, Any]) -> Optional[CachedFix]:
        """
        キャッシュから修正を取得
        
        Args:
            error_context: エラーコンテキスト
        
        Returns:
            キャッシュされた修正（見つからない場合はNone）
        """
        error_hash = self.compute_error_hash(error_context)
        
        # 完全一致を探す
        if error_hash in self.fix_cache:
            cached_fix = self.fix_cache[error_hash]
            
            # 有効期限をチェック
            if cached_fix.is_expired():
                logger.info(f"Cache entry expired: {error_hash}")
                del self.fix_cache[error_hash]
                self._save_cache()
                self.stats["cache_misses"] += 1
                return None
            
            # 使用情報を更新
            cached_fix.last_used = datetime.now()
            self.stats["cache_hits"] += 1
            logger.info(f"Cache hit: {error_hash}")
            
            return cached_fix
        
        # 類似したエラーを探す
        similar_fix = self._find_similar_fix(error_context)
        
        if similar_fix:
            self.stats["cache_hits"] += 1
            logger.info(f"Similar cache hit: {similar_fix.error_hash}")
            return similar_fix
        
        self.stats["cache_misses"] += 1
        logger.debug(f"Cache miss: {error_hash}")
        
        return None
    
    def _find_similar_fix(self, error_context: Dict[str, Any]) -> Optional[CachedFix]:
        """類似したエラーの修正を検索"""
        error_type = error_context.get("error_type", "")
        error_message = error_context.get("error_message", "")
        
        # 同じエラータイプのキャッシュエントリを検索
        candidates = []
        
        for cached_fix in self.fix_cache.values():
            if cached_fix.metadata.get("error_type") == error_type:
                # 類似度を計算
                similarity = self._calculate_similarity(
                    error_message,
                    cached_fix.metadata.get("original_message", "")
                )
                
                if similarity >= self.similarity_threshold:
                    candidates.append((similarity, cached_fix))
        
        if not candidates:
            return None
        
        # 最も類似度の高いものを返す
        best_similarity, best_fix = max(candidates, key=lambda x: x[0])
        logger.debug(f"Found similar fix with similarity: {best_similarity:.2f}")
        
        return best_fix
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """2つのテキストの類似度を計算（簡易版）"""
        if not text1 or not text2:
            return 0.0
        
        # 正規化
        text1 = self._normalize_error_message(text1)
        text2 = self._normalize_error_message(text2)
        
        # 単語レベルのJaccard類似度
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def record_fix_result(self, error_hash: str, success: bool):
        """
        修正結果を記録してキャッシュの信頼性を更新
        
        Args:
            error_hash: エラーハッシュ
            success: 修正が成功したか
        """
        if error_hash not in self.fix_cache:
            logger.warning(f"Error hash not found in cache: {error_hash}")
            return
        
        cached_fix = self.fix_cache[error_hash]
        cached_fix.application_count += 1
        
        if success:
            self.stats["successful_applications"] += 1
        else:
            self.stats["failed_applications"] += 1
        
        # 成功率を更新（移動平均）
        old_rate = cached_fix.success_rate
        new_rate = 1.0 if success else 0.0
        
        # 指数移動平均（より最近の結果を重視）
        alpha = 0.3
        cached_fix.success_rate = alpha * new_rate + (1 - alpha) * old_rate
        
        logger.debug(f"Updated fix success rate: {error_hash} -> {cached_fix.success_rate:.2f}")
        
        self._save_cache()
    
    def _learn_error_pattern(self, error_context: Dict[str, Any]):
        """エラーパターンを学習"""
        error_type = error_context.get("error_type", "")
        error_message = error_context.get("error_message", "")
        stack_trace = error_context.get("stack_trace", "")
        source_file = error_context.get("source_file", "")
        
        # パターンキーを作成
        pattern_key = f"{error_type}_{self._normalize_error_message(error_message)[:50]}"
        
        if pattern_key in self.error_patterns:
            # 既存パターンの頻度を増やす
            pattern = self.error_patterns[pattern_key]
            pattern.frequency += 1
            pattern.last_seen = datetime.now()
        else:
            # 新しいパターンを記録
            pattern = ErrorPattern(
                error_type=error_type,
                error_message_pattern=self._normalize_error_message(error_message),
                stack_trace_pattern=self._extract_stack_pattern(stack_trace),
                file_pattern=Path(source_file).name if source_file else "",
                frequency=1,
                last_seen=datetime.now()
            )
            self.error_patterns[pattern_key] = pattern
            self.stats["patterns_learned"] += 1
        
        self._save_patterns()
    
    def _extract_stack_pattern(self, stack_trace: str) -> str:
        """スタックトレースからパターンを抽出"""
        import re
        
        # ファイル名と行番号を除いて、関数名のみを抽出
        lines = stack_trace.split('\n')
        functions = []
        
        for line in lines:
            # "in <function_name>" のパターンを探す
            match = re.search(r'in (\w+)', line)
            if match:
                functions.append(match.group(1))
        
        return ' -> '.join(functions[:5])  # 最初の5つの関数のみ
    
    def get_frequent_errors(self, limit: int = 10) -> List[Tuple[str, ErrorPattern]]:
        """頻繁に発生するエラーパターンを取得"""
        sorted_patterns = sorted(
            self.error_patterns.items(),
            key=lambda x: x[1].frequency,
            reverse=True
        )
        
        return sorted_patterns[:limit]
    
    def get_best_fixes(self, limit: int = 10) -> List[CachedFix]:
        """成功率の高い修正を取得"""
        valid_fixes = [
            fix for fix in self.fix_cache.values()
            if not fix.is_expired() and fix.application_count >= 3
        ]
        
        sorted_fixes = sorted(
            valid_fixes,
            key=lambda f: f.success_rate,
            reverse=True
        )
        
        return sorted_fixes[:limit]
    
    def get_cache_hit_rate(self) -> float:
        """キャッシュヒット率を取得"""
        total = self.stats["cache_hits"] + self.stats["cache_misses"]
        if total == 0:
            return 0.0
        
        return self.stats["cache_hits"] / total
    
    def cleanup_expired(self) -> int:
        """有効期限切れのキャッシュを削除"""
        expired_keys = [
            key for key, fix in self.fix_cache.items()
            if fix.is_expired()
        ]
        
        for key in expired_keys:
            del self.fix_cache[key]
        
        if expired_keys:
            self._save_cache()
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def cleanup_low_success_rate(self, threshold: float = 0.3) -> int:
        """成功率の低いキャッシュを削除"""
        low_success_keys = [
            key for key, fix in self.fix_cache.items()
            if fix.application_count >= 5 and fix.success_rate < threshold
        ]
        
        for key in low_success_keys:
            logger.info(f"Removing low success rate fix: {key} "
                       f"(rate={self.fix_cache[key].success_rate:.2f})")
            del self.fix_cache[key]
        
        if low_success_keys:
            self._save_cache()
            logger.info(f"Cleaned up {len(low_success_keys)} low success rate entries")
        
        return len(low_success_keys)
    
    def _enforce_cache_size_limit(self):
        """キャッシュサイズ制限を適用"""
        if len(self.fix_cache) <= self.max_cache_size:
            return
        
        # 最も使われていないエントリを削除（LRU）
        sorted_fixes = sorted(
            self.fix_cache.items(),
            key=lambda x: x[1].last_used
        )
        
        to_remove = len(self.fix_cache) - self.max_cache_size
        
        for key, _ in sorted_fixes[:to_remove]:
            del self.fix_cache[key]
        
        logger.info(f"Removed {to_remove} least recently used cache entries")
        self._save_cache()
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        valid_fixes = sum(1 for fix in self.fix_cache.values() if not fix.is_expired())
        expired_fixes = len(self.fix_cache) - valid_fixes
        
        avg_success_rate = 0.0
        if valid_fixes > 0:
            rates = [
                fix.success_rate for fix in self.fix_cache.values()
                if not fix.is_expired() and fix.application_count >= 3
            ]
            if rates:
                avg_success_rate = sum(rates) / len(rates)
        
        return {
            **self.stats,
            "cache_hit_rate": round(self.get_cache_hit_rate() * 100, 2),
            "total_cached_fixes": len(self.fix_cache),
            "valid_fixes": valid_fixes,
            "expired_fixes": expired_fixes,
            "error_patterns": len(self.error_patterns),
            "avg_fix_success_rate": round(avg_success_rate * 100, 2)
        }
    
    def export_report(self) -> Dict[str, Any]:
        """詳細レポートをエクスポート"""
        return {
            "statistics": self.get_statistics(),
            "frequent_errors": [
                {
                    "pattern_key": key,
                    "error_type": pattern.error_type,
                    "frequency": pattern.frequency,
                    "last_seen": pattern.last_seen.isoformat()
                }
                for key, pattern in self.get_frequent_errors()
            ],
            "best_fixes": [
                {
                    "error_hash": fix.error_hash,
                    "success_rate": round(fix.success_rate * 100, 2),
                    "application_count": fix.application_count,
                    "description": fix.fix_description[:100]
                }
                for fix in self.get_best_fixes()
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def _save_cache(self):
        """キャッシュをファイルに保存"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.fix_cache, f)
            logger.debug(f"Cache saved: {len(self.fix_cache)} entries")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _load_cache(self):
        """キャッシュをファイルから読み込む"""
        if not self.cache_file.exists():
            return
        
        try:
            with open(self.cache_file, 'rb') as f:
                self.fix_cache = pickle.load(f)
            logger.info(f"Cache loaded: {len(self.fix_cache)} entries")
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            self.fix_cache = {}
    
    def _save_patterns(self):
        """エラーパターンをファイルに保存"""
        try:
            patterns_data = {
                key: pattern.to_dict()
                for key, pattern in self.error_patterns.items()
            }
            
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Patterns saved: {len(self.error_patterns)} patterns")
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")
    
    def _load_patterns(self):
        """エラーパターンをファイルから読み込む"""
        if not self.patterns_file.exists():
            return
        
        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                patterns_data = json.load(f)
            
            for key, pattern_dict in patterns_data.items():
                pattern = ErrorPattern(
                    error_type=pattern_dict["error_type"],
                    error_message_pattern=pattern_dict["error_message_pattern"],
                    stack_trace_pattern=pattern_dict["stack_trace_pattern"],
                    file_pattern=pattern_dict["file_pattern"],
                    frequency=pattern_dict["frequency"],
                    last_seen=datetime.fromisoformat(pattern_dict["last_seen"])
                )
                self.error_patterns[key] = pattern
            
            logger.info(f"Patterns loaded: {len(self.error_patterns)} patterns")
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
            self.error_patterns = {}


# 使用例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    cache_manager = CacheManagerAgent()
    
    # エラーコンテキストの例
    error_context1 = {
        "error_type": "ImportError",
        "error_message": "cannot import name 'foo' from 'bar'",
        "stack_trace": "Traceback...\n  in main\n  in process",
        "source_file": "/path/to/file.py"
    }
    
    # 修正をキャッシュ
    error_hash = cache_manager.cache_fix(
        error_context1,
        fix_code="from bar import foo_new as foo",
        fix_description="Updated import statement",
        ttl_hours=168
    )
    
    print(f"\nCached fix with hash: {error_hash}")
    
    # キャッシュから取得
    cached_fix = cache_manager.get_cached_fix(error_context1)
    if cached_fix:
        print(f"\nCache hit! Fix: {cached_fix.fix_description}")
    
    # 修正結果を記録
    cache_manager.record_fix_result(error_hash, success=True)
    cache_manager.record_fix_result(error_hash, success=True)
    cache_manager.record_fix_result(error_hash, success=False)
    
    # 類似エラーをテスト
    error_context2 = {
        "error_type": "ImportError",
        "error_message": "cannot import name 'baz' from 'qux'",
        "stack_trace": "Traceback...\n  in main\n  in process",
        "source_file": "/path/to/other.py"
    }
    
    similar_fix = cache_manager.get_cached_fix(error_context2)
    if similar_fix:
        print(f"\nSimilar fix found! Description: {similar_fix.fix_description}")
    
    # 統計情報
    stats = cache_manager.get_statistics()
    print(f"\nStatistics:")
    print(json.dumps(stats, indent=2))
    
    # レポート
    report = cache_manager.export_report()
    print(f"\nReport:")
    print(json.dumps(report, indent=2))

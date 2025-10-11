"""
LogAnalyzer - ログ分析と異常検知エージェント

ログパターンの分析、異常なログの検出、エラーの根本原因分析、
ログ集約とフィルタリング、トレンド分析を提供する。
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import Counter, deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """ログレベル"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass
class LogEntry:
    """ログエントリ"""
    timestamp: datetime
    level: LogLevel
    message: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.name,
            "message": self.message,
            "source": self.source,
            "metadata": self.metadata
        }


@dataclass
class LogPattern:
    """ログパターン"""
    pattern: str
    regex: re.Pattern
    level: LogLevel
    frequency: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    examples: List[str] = field(default_factory=list)
    
    def matches(self, message: str) -> bool:
        return self.regex.search(message) is not None


@dataclass
class Anomaly:
    """異常検知結果"""
    anomaly_type: str
    severity: str  # low, medium, high, critical
    description: str
    timestamp: datetime
    affected_logs: List[LogEntry]
    recommendation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "affected_logs_count": len(self.affected_logs),
            "recommendation": self.recommendation
        }


class LogAnalyzerAgent:
    """
    ログ分析と異常検知エージェント
    
    主な機能:
    1. ログパターンの学習と分析
    2. 異常なログの自動検出
    3. エラーの根本原因分析
    4. ログ集約とフィルタリング
    5. トレンド分析とレポート生成
    """
    
    def __init__(self, 
                 max_log_entries: int = 10000,
                 anomaly_threshold: float = 3.0):
        self.max_log_entries = max_log_entries
        self.anomaly_threshold = anomaly_threshold  # 標準偏差の倍数
        
        # ログストレージ
        self.log_entries: deque = deque(maxlen=max_log_entries)
        
        # パターン管理
        self.known_patterns: List[LogPattern] = []
        self.error_patterns: Dict[str, LogPattern] = {}
        
        # 統計情報
        self.stats = {
            "total_logs": 0,
            "by_level": Counter(),
            "by_source": Counter(),
            "anomalies_detected": 0
        }
        
        # 異常検知
        self.detected_anomalies: List[Anomaly] = []
        
        # エラーパターンの初期化
        self._initialize_error_patterns()
        
        logger.info("LogAnalyzerAgent initialized")
    
    def _initialize_error_patterns(self):
        """一般的なエラーパターンを初期化"""
        patterns = [
            (r"(?i)connection.*(?:refused|timeout|failed)", LogLevel.ERROR, "Connection issues"),
            (r"(?i)out of memory|memory.*overflow", LogLevel.CRITICAL, "Memory issues"),
            (r"(?i)permission denied|access denied", LogLevel.ERROR, "Permission issues"),
            (r"(?i)file not found|no such file", LogLevel.ERROR, "File not found"),
            (r"(?i)syntax error|parse error", LogLevel.ERROR, "Syntax errors"),
            (r"(?i)null pointer|null reference", LogLevel.ERROR, "Null pointer errors"),
            (r"(?i)deadlock|race condition", LogLevel.CRITICAL, "Concurrency issues"),
            (r"(?i)stack overflow|recursion", LogLevel.CRITICAL, "Stack issues"),
            (r"(?i)database.*error|sql.*error", LogLevel.ERROR, "Database errors"),
            (r"(?i)authentication failed|unauthorized", LogLevel.WARNING, "Auth issues")
        ]
        
        for pattern_str, level, description in patterns:
            pattern = LogPattern(
                pattern=description,
                regex=re.compile(pattern_str),
                level=level
            )
            self.error_patterns[description] = pattern
    
    def parse_log_line(self, line: str, source: str = "unknown") -> Optional[LogEntry]:
        """
        ログ行をパース
        
        標準的なログフォーマットに対応:
        - [YYYY-MM-DD HH:MM:SS] LEVEL: message
        - YYYY-MM-DD HH:MM:SS - LEVEL - message
        - 2024-01-01T12:00:00Z [LEVEL] message
        """
        # タイムスタンプパターン
        timestamp_patterns = [
            r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]',
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)'
        ]
        
        timestamp = None
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    # ISO形式を試す
                    if 'T' in timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    break
                except:
                    continue
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # ログレベルの抽出
        level = LogLevel.INFO
        level_match = re.search(r'\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)\b', line, re.IGNORECASE)
        if level_match:
            level_str = level_match.group(1).upper()
            if level_str == 'WARN':
                level_str = 'WARNING'
            elif level_str == 'FATAL':
                level_str = 'CRITICAL'
            level = LogLevel[level_str]
        
        # メッセージの抽出（ログレベルの後ろの部分）
        if level_match:
            message = line[level_match.end():].strip()
            # コロンやハイフンの後ろを取得
            message = re.sub(r'^[\s:\-]+', '', message)
        else:
            message = line.strip()
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source=source
        )
    
    def ingest_log(self, log_entry: LogEntry):
        """ログエントリを取り込む"""
        self.log_entries.append(log_entry)
        
        # 統計を更新
        self.stats["total_logs"] += 1
        self.stats["by_level"][log_entry.level.name] += 1
        self.stats["by_source"][log_entry.source] += 1
        
        # パターンマッチング
        self._match_patterns(log_entry)
        
        # 異常検知
        if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self._detect_anomalies()
    
    def ingest_log_file(self, filepath: str, source: Optional[str] = None):
        """ログファイルを読み込む"""
        if source is None:
            source = Path(filepath).name
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        log_entry = self.parse_log_line(line, source)
                        if log_entry:
                            self.ingest_log(log_entry)
            
            logger.info(f"Ingested log file: {filepath} ({self.stats['total_logs']} total logs)")
        except Exception as e:
            logger.error(f"Failed to ingest log file {filepath}: {e}")
    
    def _match_patterns(self, log_entry: LogEntry):
        """ログエントリをパターンとマッチング"""
        for pattern_name, pattern in self.error_patterns.items():
            if pattern.matches(log_entry.message):
                pattern.frequency += 1
                pattern.last_seen = log_entry.timestamp
                
                # サンプルを保存（最大5件）
                if len(pattern.examples) < 5:
                    pattern.examples.append(log_entry.message[:100])
    
    def _detect_anomalies(self):
        """異常を検出"""
        recent_window = timedelta(minutes=5)
        recent_cutoff = datetime.now() - recent_window
        
        # 最近のエラーログを取得
        recent_errors = [
            entry for entry in self.log_entries
            if entry.timestamp >= recent_cutoff and entry.level >= LogLevel.ERROR
        ]
        
        if len(recent_errors) >= 10:  # 5分間に10件以上のエラー
            anomaly = Anomaly(
                anomaly_type="high_error_rate",
                severity="high",
                description=f"High error rate detected: {len(recent_errors)} errors in 5 minutes",
                timestamp=datetime.now(),
                affected_logs=recent_errors[-10:],
                recommendation="Investigate recent changes or system issues"
            )
            self.detected_anomalies.append(anomaly)
            self.stats["anomalies_detected"] += 1
            logger.warning(f"Anomaly detected: {anomaly.description}")
    
    def analyze_root_cause(self, error_message: str) -> Dict[str, Any]:
        """
        エラーの根本原因を分析
        
        Args:
            error_message: エラーメッセージ
        
        Returns:
            根本原因分析結果
        """
        # 類似エラーを検索
        similar_errors = []
        for entry in self.log_entries:
            if entry.level >= LogLevel.ERROR:
                similarity = self._calculate_similarity(error_message, entry.message)
                if similarity > 0.7:
                    similar_errors.append((similarity, entry))
        
        # 時系列分析（エラーの前に何が起きたか）
        context_logs = []
        if similar_errors:
            # 最も類似したエラーの前後のログを取得
            _, target_error = max(similar_errors, key=lambda x: x[0])
            target_idx = None
            
            for i, entry in enumerate(self.log_entries):
                if entry == target_error:
                    target_idx = i
                    break
            
            if target_idx is not None:
                # 前後5件のログを取得
                start_idx = max(0, target_idx - 5)
                end_idx = min(len(self.log_entries), target_idx + 1)
                context_logs = list(self.log_entries)[start_idx:end_idx]
        
        # パターンマッチング
        matched_pattern = None
        for pattern_name, pattern in self.error_patterns.items():
            if pattern.matches(error_message):
                matched_pattern = pattern_name
                break
        
        return {
            "error_message": error_message,
            "matched_pattern": matched_pattern,
            "similar_errors_count": len(similar_errors),
            "context_logs": [log.to_dict() for log in context_logs],
            "recommendations": self._generate_recommendations(error_message, matched_pattern)
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """テキストの類似度を計算"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _generate_recommendations(self, 
                                 error_message: str,
                                 pattern: Optional[str]) -> List[str]:
        """エラーに対する推奨事項を生成"""
        recommendations = []
        
        if pattern == "Connection issues":
            recommendations.extend([
                "Check network connectivity",
                "Verify firewall settings",
                "Check if the remote service is running"
            ])
        elif pattern == "Memory issues":
            recommendations.extend([
                "Increase available memory",
                "Check for memory leaks",
                "Optimize resource usage"
            ])
        elif pattern == "Permission issues":
            recommendations.extend([
                "Check file/directory permissions",
                "Verify user has required access rights",
                "Check SELinux or AppArmor policies"
            ])
        elif pattern == "File not found":
            recommendations.extend([
                "Verify file path is correct",
                "Check if file exists",
                "Check file permissions"
            ])
        elif pattern == "Database errors":
            recommendations.extend([
                "Check database connection",
                "Verify SQL syntax",
                "Check database credentials"
            ])
        else:
            recommendations.append("Review the error message and stack trace")
        
        return recommendations
    
    def filter_logs(self,
                   level: Optional[LogLevel] = None,
                   source: Optional[str] = None,
                   time_range: Optional[Tuple[datetime, datetime]] = None,
                   pattern: Optional[str] = None) -> List[LogEntry]:
        """
        ログをフィルタリング
        
        Args:
            level: ログレベルでフィルタ
            source: ソースでフィルタ
            time_range: 時間範囲でフィルタ (start, end)
            pattern: 正規表現パターンでフィルタ
        
        Returns:
            フィルタされたログエントリ
        """
        filtered = list(self.log_entries)
        
        if level is not None:
            filtered = [log for log in filtered if log.level == level]
        
        if source is not None:
            filtered = [log for log in filtered if log.source == source]
        
        if time_range is not None:
            start, end = time_range
            filtered = [log for log in filtered if start <= log.timestamp <= end]
        
        if pattern is not None:
            regex = re.compile(pattern, re.IGNORECASE)
            filtered = [log for log in filtered if regex.search(log.message)]
        
        return filtered
    
    def get_error_trend(self, hours: int = 24) -> Dict[str, List[Tuple[datetime, int]]]:
        """
        エラートレンドを取得
        
        Args:
            hours: 過去何時間分のデータを取得するか
        
        Returns:
            時間ごとのエラーカウント
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # 1時間ごとのバケット
        buckets = {}
        for level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            buckets[level.name] = {}
        
        for entry in self.log_entries:
            if entry.timestamp < cutoff:
                continue
            
            if entry.level not in [LogLevel.ERROR, LogLevel.CRITICAL]:
                continue
            
            # 時間を1時間単位に丸める
            hour_key = entry.timestamp.replace(minute=0, second=0, microsecond=0)
            
            level_buckets = buckets[entry.level.name]
            level_buckets[hour_key] = level_buckets.get(hour_key, 0) + 1
        
        # ソート済みリストに変換
        result = {}
        for level_name, level_buckets in buckets.items():
            result[level_name] = sorted(level_buckets.items())
        
        return result
    
    def get_top_errors(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        頻繁に発生するエラーパターンを取得
        
        Args:
            limit: 取得する件数
        
        Returns:
            (パターン名, 頻度) のリスト
        """
        patterns_with_freq = [
            (name, pattern.frequency)
            for name, pattern in self.error_patterns.items()
            if pattern.frequency > 0
        ]
        
        patterns_with_freq.sort(key=lambda x: x[1], reverse=True)
        
        return patterns_with_freq[:limit]
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """サマリーレポートを生成"""
        total = self.stats["total_logs"]
        
        # ログレベル別の割合
        level_distribution = {}
        for level_name, count in self.stats["by_level"].items():
            level_distribution[level_name] = {
                "count": count,
                "percentage": round(count / total * 100, 2) if total > 0 else 0
            }
        
        # 最近の異常
        recent_anomalies = [
            anomaly.to_dict()
            for anomaly in self.detected_anomalies[-5:]
        ]
        
        # エラーパターン統計
        top_errors = self.get_top_errors(5)
        
        return {
            "summary": {
                "total_logs": total,
                "time_range": {
                    "start": min(log.timestamp for log in self.log_entries).isoformat() if self.log_entries else None,
                    "end": max(log.timestamp for log in self.log_entries).isoformat() if self.log_entries else None
                },
                "anomalies_detected": self.stats["anomalies_detected"]
            },
            "level_distribution": level_distribution,
            "top_errors": [
                {"pattern": name, "frequency": freq}
                for name, freq in top_errors
            ],
            "recent_anomalies": recent_anomalies,
            "sources": dict(self.stats["by_source"])
        }
    
    def export_analysis(self, filepath: str):
        """分析結果をファイルにエクスポート"""
        report = self.generate_summary_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis exported to {filepath}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            **self.stats,
            "unique_sources": len(self.stats["by_source"]),
            "patterns_matched": sum(1 for p in self.error_patterns.values() if p.frequency > 0),
            "avg_logs_per_source": self.stats["total_logs"] / len(self.stats["by_source"]) if self.stats["by_source"] else 0
        }


# 使用例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = LogAnalyzerAgent()
    
    # サンプルログを生成
    sample_logs = [
        "[2024-01-01 10:00:00] INFO: Application started",
        "[2024-01-01 10:01:00] DEBUG: Processing request",
        "[2024-01-01 10:02:00] ERROR: Connection timeout to database",
        "[2024-01-01 10:03:00] WARNING: Retry attempt 1",
        "[2024-01-01 10:04:00] ERROR: Connection timeout to database",
        "[2024-01-01 10:05:00] CRITICAL: Database connection failed after 3 retries",
        "[2024-01-01 10:06:00] INFO: Switching to backup database",
        "[2024-01-01 10:07:00] ERROR: File not found: /tmp/data.csv",
        "[2024-01-01 10:08:00] ERROR: Permission denied for /var/log/app.log",
    ]
    
    # ログを取り込む
    for log_line in sample_logs:
        entry = analyzer.parse_log_line(log_line, "test_app")
        analyzer.ingest_log(entry)
    
    # サマリーレポート
    print("\n=== Summary Report ===")
    report = analyzer.generate_summary_report()
    print(json.dumps(report, indent=2))
    
    # エラーの根本原因分析
    print("\n=== Root Cause Analysis ===")
    root_cause = analyzer.analyze_root_cause("Connection timeout to database")
    print(json.dumps(root_cause, indent=2))
    
    # 統計情報
    print("\n=== Statistics ===")
    stats = analyzer.get_statistics()
    print(json.dumps(stats, indent=2))
    
    # トップエラー
    print("\n=== Top Errors ===")
    for pattern, freq in analyzer.get_top_errors():
        print(f"{pattern}: {freq} occurrences")

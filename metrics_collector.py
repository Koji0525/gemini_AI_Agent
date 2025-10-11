"""
MetricsCollector - メトリクス収集とレポート生成エージェント

修正成功率、平均修正時間、エージェント別パフォーマンス分析、
日次/週次/月次レポート生成、ダッシュボード用データ生成を提供する。
"""

import json
import statistics
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """メトリクスタイプ"""
    COUNTER = "counter"  # 累積カウンター
    GAUGE = "gauge"  # 現在値
    HISTOGRAM = "histogram"  # 分布
    TIMER = "timer"  # 時間計測


class ReportPeriod(Enum):
    """レポート期間"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class MetricEntry:
    """メトリクスエントリ"""
    name: str
    value: float
    type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


@dataclass
class PerformanceStats:
    """パフォーマンス統計"""
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    percentile_50: float = 0.0
    percentile_95: float = 0.0
    percentile_99: float = 0.0
    
    @property
    def success_rate(self) -> float:
        return self.success_count / self.total_count if self.total_count > 0 else 0.0
    
    @property
    def failure_rate(self) -> float:
        return self.failure_count / self.total_count if self.total_count > 0 else 0.0


class MetricsCollectorAgent:
    """
    メトリクス収集とレポート生成エージェント
    
    主な機能:
    1. 修正成功率の追跡
    2. 平均修正時間の計算
    3. エージェント別パフォーマンス分析
    4. 日次/週次/月次レポート生成
    5. ダッシュボード用データ生成
    """
    
    def __init__(self, storage_dir: str = ".metrics"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # メトリクスストレージ
        self.metrics: List[MetricEntry] = []
        
        # エージェント別統計
        self.agent_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "tasks_processed": 0,
                "tasks_succeeded": 0,
                "tasks_failed": 0,
                "total_duration": 0.0,
                "durations": []
            }
        )
        
        # エラータイプ別統計
        self.error_stats: Dict[str, int] = Counter()
        
        # 修正タイプ別統計
        self.fix_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"attempted": 0, "succeeded": 0, "failed": 0}
        )
        
        # タスク実行中のトラッキング
        self.active_tasks: Dict[str, datetime] = {}
        
        logger.info(f"MetricsCollectorAgent initialized (storage_dir={storage_dir})")
    
    def record_metric(self, 
                     name: str,
                     value: float,
                     metric_type: MetricType = MetricType.GAUGE,
                     tags: Dict[str, str] = None):
        """
        メトリクスを記録
        
        Args:
            name: メトリクス名
            value: 値
            metric_type: メトリクスタイプ
            tags: タグ
        """
        entry = MetricEntry(
            name=name,
            value=value,
            type=metric_type,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        
        self.metrics.append(entry)
        logger.debug(f"Recorded metric: {name}={value} {tags}")
    
    def start_task(self, task_id: str, agent_name: str):
        """タスク開始を記録"""
        self.active_tasks[task_id] = datetime.now()
        self.agent_stats[agent_name]["tasks_processed"] += 1
        
        self.record_metric(
            name="task_started",
            value=1,
            metric_type=MetricType.COUNTER,
            tags={"agent": agent_name, "task_id": task_id}
        )
        
        logger.debug(f"Task started: {task_id} by {agent_name}")
    
    def end_task(self, 
                task_id: str,
                agent_name: str,
                success: bool,
                error_type: Optional[str] = None):
        """タスク終了を記録"""
        if task_id not in self.active_tasks:
            logger.warning(f"Task {task_id} was not tracked")
            return
        
        # 実行時間を計算
        start_time = self.active_tasks.pop(task_id)
        duration = (datetime.now() - start_time).total_seconds()
        
        # エージェント統計を更新
        stats = self.agent_stats[agent_name]
        if success:
            stats["tasks_succeeded"] += 1
        else:
            stats["tasks_failed"] += 1
        
        stats["total_duration"] += duration
        stats["durations"].append(duration)
        
        # エラー統計を更新
        if error_type:
            self.error_stats[error_type] += 1
        
        # メトリクスを記録
        self.record_metric(
            name="task_duration",
            value=duration,
            metric_type=MetricType.TIMER,
            tags={
                "agent": agent_name,
                "task_id": task_id,
                "success": str(success),
                "error_type": error_type or "none"
            }
        )
        
        self.record_metric(
            name="task_completed",
            value=1,
            metric_type=MetricType.COUNTER,
            tags={
                "agent": agent_name,
                "success": str(success)
            }
        )
        
        logger.debug(f"Task ended: {task_id} (success={success}, duration={duration:.2f}s)")
    
    def record_fix_attempt(self,
                          fix_type: str,
                          success: bool,
                          duration: float,
                          error_type: str):
        """修正試行を記録"""
        self.fix_stats[fix_type]["attempted"] += 1
        
        if success:
            self.fix_stats[fix_type]["succeeded"] += 1
        else:
            self.fix_stats[fix_type]["failed"] += 1
        
        self.record_metric(
            name="fix_attempt",
            value=duration,
            metric_type=MetricType.TIMER,
            tags={
                "fix_type": fix_type,
                "success": str(success),
                "error_type": error_type
            }
        )
        
        logger.debug(f"Fix attempt recorded: {fix_type} (success={success})")
    
    def get_agent_performance(self, agent_name: str) -> PerformanceStats:
        """エージェントのパフォーマンス統計を取得"""
        if agent_name not in self.agent_stats:
            return PerformanceStats()
        
        stats = self.agent_stats[agent_name]
        durations = stats["durations"]
        
        if not durations:
            return PerformanceStats(
                total_count=stats["tasks_processed"],
                success_count=stats["tasks_succeeded"],
                failure_count=stats["tasks_failed"]
            )
        
        # パーセンタイルを計算
        sorted_durations = sorted(durations)
        
        return PerformanceStats(
            total_count=stats["tasks_processed"],
            success_count=stats["tasks_succeeded"],
            failure_count=stats["tasks_failed"],
            avg_duration=statistics.mean(durations),
            min_duration=min(durations),
            max_duration=max(durations),
            percentile_50=self._percentile(sorted_durations, 50),
            percentile_95=self._percentile(sorted_durations, 95),
            percentile_99=self._percentile(sorted_durations, 99)
        )
    
    def get_all_agents_performance(self) -> Dict[str, PerformanceStats]:
        """全エージェントのパフォーマンス統計を取得"""
        return {
            agent_name: self.get_agent_performance(agent_name)
            for agent_name in self.agent_stats.keys()
        }
    
    def get_fix_success_rate(self, fix_type: Optional[str] = None) -> float:
        """修正成功率を取得"""
        if fix_type:
            stats = self.fix_stats.get(fix_type, {"attempted": 0, "succeeded": 0})
            if stats["attempted"] == 0:
                return 0.0
            return stats["succeeded"] / stats["attempted"]
        
        # 全体の成功率
        total_attempted = sum(s["attempted"] for s in self.fix_stats.values())
        total_succeeded = sum(s["succeeded"] for s in self.fix_stats.values())
        
        if total_attempted == 0:
            return 0.0
        
        return total_succeeded / total_attempted
    
    def get_error_distribution(self) -> Dict[str, int]:
        """エラー分布を取得"""
        return dict(self.error_stats)
    
    def get_top_errors(self, limit: int = 10) -> List[Tuple[str, int]]:
        """頻度の高いエラーを取得"""
        return self.error_stats.most_common(limit)
    
    def generate_report(self, 
                       period: ReportPeriod = ReportPeriod.DAILY,
                       start_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        レポートを生成
        
        Args:
            period: レポート期間
            start_time: 開始時刻（Noneの場合は現在時刻から期間を逆算）
        
        Returns:
            レポートデータ
        """
        if start_time is None:
            start_time = datetime.now()
        
        # 期間を計算
        if period == ReportPeriod.HOURLY:
            cutoff = start_time - timedelta(hours=1)
        elif period == ReportPeriod.DAILY:
            cutoff = start_time - timedelta(days=1)
        elif period == ReportPeriod.WEEKLY:
            cutoff = start_time - timedelta(weeks=1)
        elif period == ReportPeriod.MONTHLY:
            cutoff = start_time - timedelta(days=30)
        else:
            cutoff = datetime.min
        
        # 期間内のメトリクスをフィルタ
        period_metrics = [m for m in self.metrics if m.timestamp >= cutoff]
        
        # タスク統計
        task_started = sum(1 for m in period_metrics if m.name == "task_started")
        task_completed = sum(1 for m in period_metrics if m.name == "task_completed")
        task_succeeded = sum(
            1 for m in period_metrics 
            if m.name == "task_completed" and m.tags.get("success") == "True"
        )
        task_failed = task_completed - task_succeeded
        
        # 修正統計
        fix_attempts = sum(1 for m in period_metrics if m.name == "fix_attempt")
        fix_succeeded = sum(
            1 for m in period_metrics
            if m.name == "fix_attempt" and m.tags.get("success") == "True"
        )
        
        # 平均実行時間
        durations = [
            m.value for m in period_metrics
            if m.name == "task_duration"
        ]
        avg_duration = statistics.mean(durations) if durations else 0.0
        
        # エージェント別統計
        agent_performance = {}
        for agent_name in self.agent_stats.keys():
            perf = self.get_agent_performance(agent_name)
            agent_performance[agent_name] = {
                "total_tasks": perf.total_count,
                "success_rate": perf.success_rate,
                "avg_duration": perf.avg_duration,
                "p95_duration": perf.percentile_95
            }
        
        # エラー分布
        error_dist = self.get_error_distribution()
        
        report = {
            "period": period.value,
            "start_time": cutoff.isoformat(),
            "end_time": start_time.isoformat(),
            "summary": {
                "tasks_started": task_started,
                "tasks_completed": task_completed,
                "tasks_succeeded": task_succeeded,
                "tasks_failed": task_failed,
                "success_rate": task_succeeded / task_completed if task_completed > 0 else 0.0,
                "avg_duration_seconds": avg_duration
            },
            "fixes": {
                "attempts": fix_attempts,
                "succeeded": fix_succeeded,
                "success_rate": fix_succeeded / fix_attempts if fix_attempts > 0 else 0.0
            },
            "agent_performance": agent_performance,
            "error_distribution": error_dist,
            "top_errors": dict(self.get_top_errors(5))
        }
        
        return report
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """ダッシュボード用データを生成"""
        now = datetime.now()
        
        # 複数期間のレポートを生成
        hourly_report = self.generate_report(ReportPeriod.HOURLY, now)
        daily_report = self.generate_report(ReportPeriod.DAILY, now)
        weekly_report = self.generate_report(ReportPeriod.WEEKLY, now)
        
        # 時系列データ（過去24時間）
        cutoff = now - timedelta(hours=24)
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff]
        
        # 1時間ごとの集計
        hourly_buckets = defaultdict(lambda: {"tasks": 0, "errors": 0, "fixes": 0})
        
        for metric in recent_metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            
            if metric.name == "task_completed":
                hourly_buckets[hour_key]["tasks"] += 1
            elif metric.name == "fix_attempt":
                hourly_buckets[hour_key]["fixes"] += 1
            elif "error" in metric.name:
                hourly_buckets[hour_key]["errors"] += 1
        
        # 時系列データを整形
        time_series = []
        for hour in sorted(hourly_buckets.keys()):
            time_series.append({
                "timestamp": hour.isoformat(),
                "tasks": hourly_buckets[hour]["tasks"],
                "errors": hourly_buckets[hour]["errors"],
                "fixes": hourly_buckets[hour]["fixes"]
            })
        
        # 全エージェントのパフォーマンス
        all_agents_perf = self.get_all_agents_performance()
        agent_summary = {}
        
        for agent_name, perf in all_agents_perf.items():
            agent_summary[agent_name] = {
                "total_tasks": perf.total_count,
                "success_rate": round(perf.success_rate * 100, 2),
                "avg_duration": round(perf.avg_duration, 2),
                "status": self._get_agent_status(perf)
            }
        
        return {
            "overview": {
                "hourly": hourly_report["summary"],
                "daily": daily_report["summary"],
                "weekly": weekly_report["summary"]
            },
            "time_series": time_series,
            "agents": agent_summary,
            "errors": {
                "distribution": self.get_error_distribution(),
                "top_5": dict(self.get_top_errors(5))
            },
            "fixes": {
                "overall_success_rate": round(self.get_fix_success_rate() * 100, 2),
                "by_type": {
                    fix_type: {
                        "attempted": stats["attempted"],
                        "success_rate": round(
                            (stats["succeeded"] / stats["attempted"] * 100) 
                            if stats["attempted"] > 0 else 0, 2
                        )
                    }
                    for fix_type, stats in self.fix_stats.items()
                }
            },
            "active_tasks": len(self.active_tasks),
            "generated_at": now.isoformat()
        }
    
    def export_metrics(self, filepath: Optional[str] = None) -> str:
        """
        メトリクスをJSONファイルにエクスポート
        
        Args:
            filepath: 出力ファイルパス（Noneの場合は自動生成）
        
        Returns:
            出力ファイルパス
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.storage_dir / f"metrics_{timestamp}.json"
        
        data = {
            "metrics": [m.to_dict() for m in self.metrics],
            "agent_stats": dict(self.agent_stats),
            "error_stats": dict(self.error_stats),
            "fix_stats": dict(self.fix_stats),
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metrics exported to {filepath}")
        
        return str(filepath)
    
    def import_metrics(self, filepath: str):
        """メトリクスをJSONファイルからインポート"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # メトリクスを復元
        for m_data in data.get("metrics", []):
            metric = MetricEntry(
                name=m_data["name"],
                value=m_data["value"],
                type=MetricType(m_data["type"]),
                timestamp=datetime.fromisoformat(m_data["timestamp"]),
                tags=m_data.get("tags", {})
            )
            self.metrics.append(metric)
        
        # 統計データを復元
        self.agent_stats.update(data.get("agent_stats", {}))
        self.error_stats.update(data.get("error_stats", {}))
        self.fix_stats.update(data.get("fix_stats", {}))
        
        logger.info(f"Metrics imported from {filepath}")
    
    def _percentile(self, sorted_data: List[float], percentile: int) -> float:
        """パーセンタイルを計算"""
        if not sorted_data:
            return 0.0
        
        index = (len(sorted_data) - 1) * percentile / 100
        lower = int(index)
        upper = lower + 1
        
        if upper >= len(sorted_data):
            return sorted_data[-1]
        
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
    
    def _get_agent_status(self, perf: PerformanceStats) -> str:
        """エージェントのステータスを判定"""
        if perf.total_count == 0:
            return "idle"
        
        if perf.success_rate >= 0.95:
            return "excellent"
        elif perf.success_rate >= 0.80:
            return "good"
        elif perf.success_rate >= 0.60:
            return "fair"
        else:
            return "poor"
    
    def clear_old_metrics(self, days: int = 30):
        """古いメトリクスをクリア"""
        cutoff = datetime.now() - timedelta(days=days)
        
        original_count = len(self.metrics)
        self.metrics = [m for m in self.metrics if m.timestamp >= cutoff]
        
        cleared_count = original_count - len(self.metrics)
        logger.info(f"Cleared {cleared_count} old metrics (older than {days} days)")
    
    def get_summary(self) -> Dict[str, Any]:
        """簡易サマリーを取得"""
        total_tasks = sum(stats["tasks_processed"] for stats in self.agent_stats.values())
        total_succeeded = sum(stats["tasks_succeeded"] for stats in self.agent_stats.values())
        total_failed = sum(stats["tasks_failed"] for stats in self.agent_stats.values())
        
        overall_success_rate = total_succeeded / total_tasks if total_tasks > 0 else 0.0
        
        return {
            "total_tasks": total_tasks,
            "total_succeeded": total_succeeded,
            "total_failed": total_failed,
            "overall_success_rate": round(overall_success_rate * 100, 2),
            "active_agents": len(self.agent_stats),
            "total_metrics": len(self.metrics),
            "unique_errors": len(self.error_stats),
            "fix_types": len(self.fix_stats)
        }


# 使用例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    collector = MetricsCollectorAgent()
    
    # タスク実行をシミュレート
    collector.start_task("task-1", "LocalFixAgent")
    import time
    time.sleep(0.5)
    collector.end_task("task-1", "LocalFixAgent", success=True)
    
    collector.start_task("task-2", "CloudFixAgent")
    time.sleep(1.0)
    collector.end_task("task-2", "CloudFixAgent", success=False, error_type="SyntaxError")
    
    # 修正試行を記録
    collector.record_fix_attempt("local", success=True, duration=2.5, error_type="ImportError")
    collector.record_fix_attempt("cloud", success=False, duration=5.0, error_type="AttributeError")
    
    # レポート生成
    daily_report = collector.generate_report(ReportPeriod.DAILY)
    print("\n=== Daily Report ===")
    print(json.dumps(daily_report, indent=2))
    
    # ダッシュボードデータ生成
    dashboard = collector.generate_dashboard_data()
    print("\n=== Dashboard Data ===")
    print(json.dumps(dashboard, indent=2))
    
    # サマリー
    summary = collector.get_summary()
    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))
    
    # エクスポート
    export_path = collector.export_metrics()
    print(f"\nMetrics exported to: {export_path}")

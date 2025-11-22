"""
Enhanced Observer System

強化版オブザーバーシステム

このパッケージは、システム全体の依存関係を監視し、
健全性をチェックする機能を提供します。

主要コンポーネント:
    - StaticDependencyAnalyzer: 静的依存関係解析
    - ExecutionTracer: 実行時トレース
    - SystemGraphDB: グラフデータベース
    - DependencyGraphBuilder: グラフ構築
    - HealthChecker: ヘルスチェック
    - AlertManager: アラート管理
    - ImpactAnalyzer: 影響範囲分析
    - EnhancedObserverOrchestrator: 統括制御
"""

__version__ = "1.0.0"
__author__ = "gemini_AI_Agent Team"

from .alert_manager import AlertManager
from .graph_builder import DependencyGraphBuilder
from .graph_db import SystemGraphDB
from .health_checker import HealthChecker
from .impact_analyzer import ImpactAnalyzer
from .orchestrator import EnhancedObserverOrchestrator
# 主要クラスをインポート
from .static_analyzer import StaticDependencyAnalyzer
from .tracer import ExecutionTracer, trace, tracer

__all__ = [
    "StaticDependencyAnalyzer",
    "ExecutionTracer",
    "tracer",
    "trace",
    "SystemGraphDB",
    "DependencyGraphBuilder",
    "HealthChecker",
    "AlertManager",
    "ImpactAnalyzer",
    "EnhancedObserverOrchestrator",
]

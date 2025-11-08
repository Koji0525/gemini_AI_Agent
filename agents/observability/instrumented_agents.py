"""
Instrumented Agents - OpenTelemetry計装エージェント

【Phase 1.1: 既存エージェントのインストゥルメンテーション】
既存エージェントを非侵襲的にラップし、トレース情報を収集
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from datetime import datetime

from agents.observability.opentelemetry_config import (TracingDecorator,
                                                       get_otel_config)

logger = logging.getLogger(__name__)


class InstrumentedPMAgent:
    """PMAgent計装ラッパー"""

    def __init__(self, pm_agent):
        self.pm_agent = pm_agent
        self.otel_config = get_otel_config()
        self.decorator = TracingDecorator(self.otel_config)
        print("✅ PMAgent計装完了")

    def create_task(self, *args, **kwargs):
        @self.decorator.trace_method("PMAgent.create_task")
        def _create_task():
            return self.pm_agent.create_task(*args, **kwargs)

        return _create_task()

    def decompose_task(self, *args, **kwargs):
        @self.decorator.trace_method("PMAgent.decompose_task")
        def _decompose_task():
            return self.pm_agent.decompose_task(*args, **kwargs)

        return _decompose_task()

    def __getattr__(self, name):
        return getattr(self.pm_agent, name)


class InstrumentedTaskExecutor:
    """TaskExecutor計装ラッパー"""

    def __init__(self, task_executor):
        self.task_executor = task_executor
        self.otel_config = get_otel_config()
        self.decorator = TracingDecorator(self.otel_config)
        print("✅ TaskExecutor計装完了")

    def execute_task(self, *args, **kwargs):
        @self.decorator.trace_method("TaskExecutor.execute_task")
        def _execute_task():
            start_time = datetime.now()
            result = self.task_executor.execute_task(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            print(f"📊 タスク実行時間: {duration:.2f}秒")
            return result

        return _execute_task()

    def __getattr__(self, name):
        return getattr(self.task_executor, name)


class InstrumentedReviewAgent:
    """ReviewAgent計装ラッパー"""

    def __init__(self, review_agent):
        self.review_agent = review_agent
        self.otel_config = get_otel_config()
        self.decorator = TracingDecorator(self.otel_config)
        print("✅ ReviewAgent計装完了")

    def review_result(self, *args, **kwargs):
        @self.decorator.trace_method("ReviewAgent.review_result")
        def _review_result():
            return self.review_agent.review_result(*args, **kwargs)

        return _review_result()

    def __getattr__(self, name):
        return getattr(self.review_agent, name)


def instrument_agents(orchestrator):
    """オーケストレーターのエージェントを計装"""
    instrumented_count = 0

    try:
        if hasattr(orchestrator, "pm_agent") and orchestrator.pm_agent:
            orchestrator.pm_agent = InstrumentedPMAgent(orchestrator.pm_agent)
            instrumented_count += 1

        if hasattr(orchestrator, "task_executor") and orchestrator.task_executor:
            orchestrator.task_executor = InstrumentedTaskExecutor(orchestrator.task_executor)
            instrumented_count += 1

        if hasattr(orchestrator, "review_agent") and orchestrator.review_agent:
            orchestrator.review_agent = InstrumentedReviewAgent(orchestrator.review_agent)
            instrumented_count += 1

        print(f"✅ {instrumented_count}個のエージェントを計装しました")

    except Exception as e:
        print(f"❌ エージェント計装エラー: {e}")

    return instrumented_count


if __name__ == "__main__":
    print("�� 計装エージェントテスト")

    class DummyPMAgent:
        def create_task(self, task_name):
            print(f"タスク作成: {task_name}")
            return {"task_id": "123", "name": task_name}

    pm_agent = DummyPMAgent()
    instrumented_pm = InstrumentedPMAgent(pm_agent)
    result = instrumented_pm.create_task("test_task")
    print(f"結果: {result}")

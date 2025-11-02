"""
task_executor package

TaskCoordinatorと各種専門Executorを提供
"""

# 基本TaskExecutorは直接インポート
try:
    # プロジェクトルートのtask_executor.pyからインポート
    import sys
    from pathlib import Path

    # プロジェクトルートを追加
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from task_executor import TaskExecutor as BaseTaskExecutor

    TaskExecutor = BaseTaskExecutor

except ImportError:
    # フォールバック: シンプルなダミークラス
    class TaskExecutor:
        def __init__(self, sheets_manager, output_dir="agent_outputs"):
            self.sheets_manager = sheets_manager
            self.output_dir = output_dir

        async def execute_single_task(self, browser, task):
            """ダミー実装"""
            return True


# TaskCoordinatorは常にインポート可能
try:
    from task_executor.task_coordinator import TaskCoordinator
except ImportError:
    TaskCoordinator = None

__all__ = ["TaskExecutor", "TaskCoordinator"]

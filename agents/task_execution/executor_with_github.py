"""
GitH連携付きTaskExecutor
既存のEnhancedTaskExecutorV2を拡張（破壊的変更なし）
"""
from agents.task_execution.enhanced_executor_v2 import EnhancedTaskExecutorV2
from agents.github_integration.auto_committer import AutoCommitter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskExecutorWithGitHub(EnhancedTaskExecutorV2):
    """GitHub自動コミット機能付きTaskExecutor"""
    
    def __init__(self, knowledge_manager=None, auto_commit=True):
        super().__init__(knowledge_manager)
        self.auto_commit = auto_commit
        self.committer = AutoCommitter() if auto_commit else None
    
    def execute_task_with_details(self, task):
        """タスク実行 + 自動コミット"""
        # 親クラスのメソッドを呼び出し（既存機能）
        result = super().execute_task_with_details(task)
        
        # 成功時のみ自動コミット（新機能）
        if self.auto_commit and result.get('status') == 'completed':
            logger.info("📤 自動コミット開始...")
            
            commit_result = self.committer.commit_task_results(
                task_id=task.get('task_id'),
                task_description=task.get('description'),
                output_files=result.get('output_files', []),
                quality_score=result.get('quality_score', 0)
            )
            
            if commit_result['success']:
                logger.info(f"✅ 自動コミット成功: {commit_result['commit_hash'][:8]}")
                result['git_commit'] = commit_result['commit_hash']
                result['git_pushed'] = commit_result['pushed']
            else:
                logger.warning(f"⚠️ 自動コミット失敗: {commit_result['message']}")
        
        return result

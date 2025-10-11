# fix_agents/fix_agent.py
"""
修正エージェントの基底クラス
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseFixAgent(ABC):
    """
    修正エージェントの基底クラス
    
    すべての修正エージェント（Local, Cloud）の共通インターフェース
    """
    
    def __init__(
        self,
        command_monitor=None,
        wp_tester=None,
        **kwargs
    ):
        """
        初期化
        
        Args:
            command_monitor: CommandMonitorAgent
            wp_tester: WordPressTester
            **kwargs: その他のオプション
        """
        self.cmd_monitor = command_monitor
        self.wp_tester = wp_tester
        
        # 統計情報
        self.stats = {
            "total_fixes": 0,
            "successful_fixes": 0,
            "failed_fixes": 0
        }
        
        self.agent_name = self.__class__.__name__
        logger.info(f"✅ {self.agent_name} 初期化")
    
    @abstractmethod
    async def execute_bug_fix_task(self, bug_fix_task):
        """
        バグ修正タスクを実行（サブクラスで実装）
        
        Args:
            bug_fix_task: BugFixTask
            
        Returns:
            FixResult: 修正結果
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        success_rate = 0.0
        if self.stats["total_fixes"] > 0:
            success_rate = self.stats["successful_fixes"] / self.stats["total_fixes"]
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "agent_name": self.agent_name
        }
    
    def _create_failed_result(
        self,
        task_id: str,
        error_message: str,
        start_time: datetime
    ):
        """失敗結果を作成"""
        from data_models import FixResult
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return FixResult(
            task_id=task_id,
            success=False,
            modified_files=[],
            generated_code="",
            test_passed=False,
            execution_time=execution_time,
            error_message=error_message,
            confidence_score=0.0
        )


# エイリアス（互換性のため）
LocalFixAgent = BaseFixAgent
CloudFixAgent = BaseFixAgent
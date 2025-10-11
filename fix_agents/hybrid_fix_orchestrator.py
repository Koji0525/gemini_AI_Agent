# hybrid_fix_orchestrator.py
"""
ハイブリチE��修正オーケストレーター
ローカルとクラウド修正を統括管琁E
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from data_models import BugFixTask, FixResult, ErrorContextModel
from .local_fix_agent import LocalFixAgent
from cloud_fix_agent import CloudFixAgent
from error_classifier import ErrorClassifier

logger = logging.getLogger(__name__)


class FixStrategy(Enum):
    """修正戦略"""
    LOCAL_ONLY = "local_only"          # ローカルのみ
    CLOUD_ONLY = "cloud_only"          # クラウド�Eみ
    LOCAL_FIRST = "local_first"        # ローカル優允E
    CLOUD_FIRST = "cloud_first"        # クラウド優允E
    PARALLEL = "parallel"              # 並列実衁E
    ADAPTIVE = "adaptive"              # 適応的選抁E


class HybridFixOrchestrator:
    """
    ハイブリチE��修正オーケストレーター
    
    機�E:
    - エラー刁E��とルーチE��ング
    - ローカル/クラウド修正の選抁E
    - フォールバック戦略
    - 並列実行管琁E
    - 統計情報の収集
    """
    
    def __init__(
        self,
        local_agent: LocalFixAgent,
        cloud_agent: CloudFixAgent,
        error_classifier: Optional[ErrorClassifier] = None,
        default_strategy: FixStrategy = FixStrategy.ADAPTIVE
    ):
        """
        初期匁E
        
        Args:
            local_agent: ローカル修正エージェンチE
            cloud_agent: クラウド修正エージェンチE
            error_classifier: エラー刁E��器
            default_strategy: チE��ォルト戦略
        """
        self.local_agent = local_agent
        self.cloud_agent = cloud_agent
        self.error_classifier = error_classifier or ErrorClassifier()
        self.default_strategy = default_strategy
        
        # 統計情報
        self.stats = {
            "total_tasks": 0,
            "local_fixes": 0,
            "cloud_fixes": 0,
            "hybrid_fixes": 0,
            "successful_fixes": 0,
            "failed_fixes": 0,
            "avg_execution_time": 0.0,
            "strategy_usage": {strategy.value: 0 for strategy in FixStrategy}
        }
        
        # 修正履歴
        self.fix_history = []
        
        logger.info(f"✁EHybridFixOrchestrator 初期化完亁E(戦略={default_strategy.value})")
    
    async def execute_fix_task(
        self, 
        bug_fix_task: BugFixTask,
        strategy: Optional[FixStrategy] = None
    ) -> FixResult:
        """
        修正タスクを実衁E
        
        Args:
            bug_fix_task: バグ修正タスク
            strategy: 修正戦略�E�省略時�EチE��ォルト！E
            
        Returns:
            FixResult: 修正結果
        """
        start_time = datetime.now()
        task_id = bug_fix_task.task_id
        
        self.stats["total_tasks"] += 1
        
        # 戦略の決宁E
        selected_strategy = strategy or self.default_strategy
        
        # 適応的戦略の場合、エラー刁E��に基づぁE��決宁E
        if selected_strategy == FixStrategy.ADAPTIVE:
            selected_strategy = await self._select_adaptive_strategy(bug_fix_task.error_context)
        
        self.stats["strategy_usage"][selected_strategy.value] += 1
        
        logger.info("=" * 80)
        logger.info(f"🎯 ハイブリチE��修正開姁E {task_id}")
        logger.info(f"📊 選択戦略: {selected_strategy.value}")
        logger.info("=" * 80)
        
        try:
            # 戦略に応じた実衁E
            if selected_strategy == FixStrategy.LOCAL_ONLY:
                result = await self._execute_local_only(bug_fix_task)
                
            elif selected_strategy == FixStrategy.CLOUD_ONLY:
                result = await self._execute_cloud_only(bug_fix_task)
                
            elif selected_strategy == FixStrategy.LOCAL_FIRST:
                result = await self._execute_local_first(bug_fix_task)
                
            elif selected_strategy == FixStrategy.CLOUD_FIRST:
                result = await self._execute_cloud_first(bug_fix_task)
                
            elif selected_strategy == FixStrategy.PARALLEL:
                result = await self._execute_parallel(bug_fix_task)
                
            else:
                result = await self._execute_local_first(bug_fix_task)
            
            # 統計情報の更新
            if result.success:
                self.stats["successful_fixes"] += 1
            else:
                self.stats["failed_fixes"] += 1
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_avg_execution_time(execution_time)
            
            # 履歴に追加
            self.fix_history.append({
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "strategy": selected_strategy.value,
                "success": result.success,
                "execution_time": execution_time,
                "agent_used": result.agent_used if hasattr(result, 'agent_used') else "unknown"
            })
            
            logger.info(f"{'✁E if result.success else '❁E} 修正{'成功' if result.success else '失敁E}: {task_id} ({execution_time:.2f}私E")
            
            return result
            
        except Exception as e:
            logger.error(f"💥 修正実行エラー: {e}", exc_info=True)
            self.stats["failed_fixes"] += 1
            
            return FixResult(
                task_id=task_id,
                success=False,
                modified_files=[],
                generated_code="",
                test_passed=False,
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def _select_adaptive_strategy(self, error_context: ErrorContextModel) -> FixStrategy:
        """
        エラーコンチE��ストに基づぁE��適応的に戦略を選抁E
        
        Args:
            error_context: エラーコンチE��スチE
            
        Returns:
            FixStrategy: 選択された戦略
        """
        # エラー刁E��E
        classification = self.error_classifier.classify(error_context)
        
        complexity = classification.get("complexity", "medium")
        error_type = classification.get("error_type", "unknown")
        confidence = classification.get("confidence", 0.5)
        
        logger.info(f"📊 エラー刁E��E 褁E��度={complexity}, タイチE{error_type}, 信頼度={confidence:.2f}")
        
        # 褁E��度に基づく戦略選抁E
        if complexity == "simple":
            # 単純なエラーはローカルで迁E��に処琁E
            return FixStrategy.LOCAL_FIRST
            
        elif complexity == "medium":
            # 中程度の褁E��さ�Eローカル優先、失敗時クラウチE
            if confidence > 0.7:
                return FixStrategy.LOCAL_FIRST
            else:
                return FixStrategy.CLOUD_FIRST
                
        else:  # complex
            # 褁E��なエラーは最初からクラウチE
            if error_type in ["design_flaw", "architectural", "multi_file"]:
                return FixStrategy.CLOUD_ONLY
            else:
                return FixStrategy.CLOUD_FIRST
    
    async def _execute_local_only(self, bug_fix_task: BugFixTask) -> FixResult:
        """ローカルのみで実衁E""
        logger.info("💻 ローカル修正実衁E)
        self.stats["local_fixes"] += 1
        result = await self.local_agent.execute_bug_fix_task(bug_fix_task)
        result.agent_used = "local"
        return result
    
    async def _execute_cloud_only(self, bug_fix_task: BugFixTask) -> FixResult:
        """クラウド�Eみで実衁E""
        logger.info("☁E��Eクラウド修正実衁E)
        self.stats["cloud_fixes"] += 1
        result = await self.cloud_agent.execute_bug_fix_task(bug_fix_task)
        result.agent_used = "cloud"
        return result
    
    async def _execute_local_first(self, bug_fix_task: BugFixTask) -> FixResult:
        """ローカル優先、失敗時クラウドにフォールバック"""
        logger.info("💻 ローカル修正を試衁E)
        self.stats["local_fixes"] += 1
        
        local_result = await self.local_agent.execute_bug_fix_task(bug_fix_task)
        
        if local_result.success and local_result.confidence_score >= 0.7:
            logger.info("✁Eローカル修正成功")
            local_result.agent_used = "local"
            return local_result
        
        logger.warning("⚠�E�Eローカル修正不十刁E��クラウドにフォールバック")
        logger.info("☁E��Eクラウド修正実衁E)
        self.stats["cloud_fixes"] += 1
        self.stats["hybrid_fixes"] += 1
        
        cloud_result = await self.cloud_agent.execute_bug_fix_task(bug_fix_task)
        cloud_result.agent_used = "hybrid_local_then_cloud"
        
        return cloud_result
    
    async def _execute_cloud_first(self, bug_fix_task: BugFixTask) -> FixResult:
        """クラウド優先、失敗時ローカルにフォールバック"""
        logger.info("☁E��Eクラウド修正を試衁E)
        self.stats["cloud_fixes"] += 1
        
        cloud_result = await self.cloud_agent.execute_bug_fix_task(bug_fix_task)
        
        if cloud_result.success:
            logger.info("✁Eクラウド修正成功")
            cloud_result.agent_used = "cloud"
            return cloud_result
        
        logger.warning("⚠�E�Eクラウド修正失敗、ローカルにフォールバック")
        logger.info("💻 ローカル修正実衁E)
        self.stats["local_fixes"] += 1
        self.stats["hybrid_fixes"] += 1
        
        local_result = await self.local_agent.execute_bug_fix_task(bug_fix_task)
        local_result.agent_used = "hybrid_cloud_then_local"
        
        return local_result
    
    async def _execute_parallel(self, bug_fix_task: BugFixTask) -> FixResult:
        """ローカルとクラウドを並列実行し、最良の結果を選抁E""
        logger.info("🔀 並列修正実行（ローカル & クラウド！E)
        self.stats["local_fixes"] += 1
        self.stats["cloud_fixes"] += 1
        self.stats["hybrid_fixes"] += 1
        
        # 並列実衁E
        results = await asyncio.gather(
            self.local_agent.execute_bug_fix_task(bug_fix_task),
            self.cloud_agent.execute_bug_fix_task(bug_fix_task),
            return_exceptions=True
        )
        
        local_result, cloud_result = results
        
        # エラーハンドリング
        if isinstance(local_result, Exception):
            logger.error(f"❁Eローカル並列実行エラー: {local_result}")
            local_result = None
        
        if isinstance(cloud_result, Exception):
            logger.error(f"❁Eクラウド並列実行エラー: {cloud_result}")
            cloud_result = None
        
        # 最良の結果を選抁E
        best_result = self._select_best_result(local_result, cloud_result)
        
        if best_result:
            best_result.agent_used = "parallel"
            logger.info(f"✁E並列実行完亁E��最良結果を選択（エージェンチE{best_result.agent_used}�E�E)
            return best_result
        else:
            # 両方失敁E
            logger.error("❁E並列実行失敗（両エージェント失敗！E)
            return FixResult(
                task_id=bug_fix_task.task_id,
                success=False,
                modified_files=[],
                generated_code="",
                test_passed=False,
                execution_time=0.0,
                error_message="Both local and cloud agents failed",
                agent_used="parallel_failed"
            )
    
    def _select_best_result(
        self, 
        local_result: Optional[FixResult], 
        cloud_result: Optional[FixResult]
    ) -> Optional[FixResult]:
        """
        2つの結果から最良のも�Eを選抁E
        
        Args:
            local_result: ローカル結果
            cloud_result: クラウド結果
            
        Returns:
            Optional[FixResult]: 最良の結果
        """
        # どちらかがNoneの場吁E
        if local_result is None:
            return cloud_result
        if cloud_result is None:
            return local_result
        
        # 両方成功の場合、信頼度で比輁E
        if local_result.success and cloud_result.success:
            local_score = local_result.confidence_score or 0.5
            cloud_score = cloud_result.confidence_score or 0.5
            
            if cloud_score > local_score:
                logger.info(f"☁E��Eクラウド結果を選択（信頼度: {cloud_score:.2f} > {local_score:.2f}�E�E)
                return cloud_result
            else:
                logger.info(f"💻 ローカル結果を選択（信頼度: {local_score:.2f} >= {cloud_score:.2f}�E�E)
                return local_result
        
        # どちらか一方のみ成功
        if local_result.success:
            logger.info("💻 ローカル結果を選択（ローカルのみ成功�E�E)
            return local_result
        if cloud_result.success:
            logger.info("☁E��Eクラウド結果を選択（クラウド�Eみ成功�E�E)
            return cloud_result
        
        # 両方失敗�E場合、信頼度が高い方
        local_score = local_result.confidence_score or 0.0
        cloud_score = cloud_result.confidence_score or 0.0
        
        return cloud_result if cloud_score > local_score else local_result
    
    def _update_avg_execution_time(self, execution_time: float):
        """平坁E��行時間を更新"""
        total = self.stats["total_tasks"]
        current_avg = self.stats["avg_execution_time"]
        self.stats["avg_execution_time"] = (current_avg * (total - 1) + execution_time) / total
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取征E""
        success_rate = 0.0
        if self.stats["total_tasks"] > 0:
            success_rate = self.stats["successful_fixes"] / self.stats["total_tasks"]
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "local_agent_stats": self.local_agent.get_stats(),
            "cloud_agent_stats": self.cloud_agent.get_stats()
        }
    
    def print_stats(self):
        """統計情報を表示"""
        stats = self.get_stats()
        
        print("\n" + "=" * 80)
        print("📊 ハイブリチE��修正オーケストレーター 統計情報")
        print("=" * 80)
        print(f"総タスク数: {stats['total_tasks']}")
        print(f"成功数: {stats['successful_fixes']} ({stats['success_rate']:.1%})")
        print(f"失敗数: {stats['failed_fixes']}")
        print(f"平坁E��行時閁E {stats['avg_execution_time']:.2f}私E)
        print(f"\nローカル修正: {stats['local_fixes']}囁E)
        print(f"クラウド修正: {stats['cloud_fixes']}囁E)
        print(f"ハイブリチE��修正: {stats['hybrid_fixes']}囁E)
        print("\n戦略使用状況E")
        for strategy, count in stats['strategy_usage'].items():
            print(f"  - {strategy}: {count}囁E)
        print("=" * 80 + "\n")
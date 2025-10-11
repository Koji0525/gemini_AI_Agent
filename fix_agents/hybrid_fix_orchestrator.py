# hybrid_fix_orchestrator.py
"""
繝上う繝悶Μ繝・ラ菫ｮ豁｣繧ｪ繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｿ繝ｼ
繝ｭ繝ｼ繧ｫ繝ｫ縺ｨ繧ｯ繝ｩ繧ｦ繝我ｿｮ豁｣繧堤ｵｱ諡ｬ邂｡逅・
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from data_models import BugFixTask, FixResult, ErrorContextModel
from .local_fix_agent import LocalFixAgent
from .cloud_fix_agent import CloudFixAgent
from .error_classifier import ErrorClassifier

logger = logging.getLogger(__name__)


class FixStrategy(Enum):
    """菫ｮ豁｣謌ｦ逡･"""
    LOCAL_ONLY = "local_only"          # 繝ｭ繝ｼ繧ｫ繝ｫ縺ｮ縺ｿ
    CLOUD_ONLY = "cloud_only"          # 繧ｯ繝ｩ繧ｦ繝峨・縺ｿ
    LOCAL_FIRST = "local_first"        # 繝ｭ繝ｼ繧ｫ繝ｫ蜆ｪ蜈・
    CLOUD_FIRST = "cloud_first"        # 繧ｯ繝ｩ繧ｦ繝牙━蜈・
    PARALLEL = "parallel"              # 荳ｦ蛻怜ｮ溯｡・
    ADAPTIVE = "adaptive"              # 驕ｩ蠢懃噪驕ｸ謚・


class HybridFixOrchestrator:
    """
    繝上う繝悶Μ繝・ラ菫ｮ豁｣繧ｪ繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｿ繝ｼ
    
    讖溯・:
    - 繧ｨ繝ｩ繝ｼ蛻・｡槭→繝ｫ繝ｼ繝・ぅ繝ｳ繧ｰ
    - 繝ｭ繝ｼ繧ｫ繝ｫ/繧ｯ繝ｩ繧ｦ繝我ｿｮ豁｣縺ｮ驕ｸ謚・
    - 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ謌ｦ逡･
    - 荳ｦ蛻怜ｮ溯｡檎ｮ｡逅・
    - 邨ｱ險域ュ蝣ｱ縺ｮ蜿朱寔
    """
    
    def __init__(
        self,
        local_agent: LocalFixAgent,
        cloud_agent: CloudFixAgent,
        error_classifier: Optional[ErrorClassifier] = None,
        default_strategy: FixStrategy = FixStrategy.ADAPTIVE
    ):
        """
        蛻晄悄蛹・
        
        Args:
            local_agent: 繝ｭ繝ｼ繧ｫ繝ｫ菫ｮ豁｣繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝・
            cloud_agent: 繧ｯ繝ｩ繧ｦ繝我ｿｮ豁｣繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝・
            error_classifier: 繧ｨ繝ｩ繝ｼ蛻・｡槫勣
            default_strategy: 繝・ヵ繧ｩ繝ｫ繝域姶逡･
        """
        self.local_agent = local_agent
        self.cloud_agent = cloud_agent
        self.error_classifier = error_classifier or ErrorClassifier()
        self.default_strategy = default_strategy
        
        # 邨ｱ險域ュ蝣ｱ
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
        
        # 菫ｮ豁｣螻･豁ｴ
        self.fix_history = []
        
        logger.info(f"笨・HybridFixOrchestrator 蛻晄悄蛹門ｮ御ｺ・(謌ｦ逡･={default_strategy.value})")
    
    async def execute_fix_task(
        self, 
        bug_fix_task: BugFixTask,
        strategy: Optional[FixStrategy] = None
    ) -> FixResult:
        """
        菫ｮ豁｣繧ｿ繧ｹ繧ｯ繧貞ｮ溯｡・
        
        Args:
            bug_fix_task: 繝舌げ菫ｮ豁｣繧ｿ繧ｹ繧ｯ
            strategy: 菫ｮ豁｣謌ｦ逡･・育怐逡･譎ゅ・繝・ヵ繧ｩ繝ｫ繝茨ｼ・
            
        Returns:
            FixResult: 菫ｮ豁｣邨先棡
        """
        start_time = datetime.now()
        task_id = bug_fix_task.task_id
        
        self.stats["total_tasks"] += 1
        
        # 謌ｦ逡･縺ｮ豎ｺ螳・
        selected_strategy = strategy or self.default_strategy
        
        # 驕ｩ蠢懃噪謌ｦ逡･縺ｮ蝣ｴ蜷医√お繝ｩ繝ｼ蛻・梵縺ｫ蝓ｺ縺･縺・※豎ｺ螳・
        if selected_strategy == FixStrategy.ADAPTIVE:
            selected_strategy = await self._select_adaptive_strategy(bug_fix_task.error_context)
        
        self.stats["strategy_usage"][selected_strategy.value] += 1
        
        logger.info("=" * 80)
        logger.info(f"識 繝上う繝悶Μ繝・ラ菫ｮ豁｣髢句ｧ・ {task_id}")
        logger.info(f"投 驕ｸ謚樊姶逡･: {selected_strategy.value}")
        logger.info("=" * 80)
        
        try:
            # 謌ｦ逡･縺ｫ蠢懊§縺溷ｮ溯｡・
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
            
            # 邨ｱ險域ュ蝣ｱ縺ｮ譖ｴ譁ｰ
            if result.success:
                self.stats["successful_fixes"] += 1
            else:
                self.stats["failed_fixes"] += 1
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_avg_execution_time(execution_time)
            
            # 螻･豁ｴ縺ｫ霑ｽ蜉
            self.fix_history.append({
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "strategy": selected_strategy.value,
                "success": result.success,
                "execution_time": execution_time,
                "agent_used": result.agent_used if hasattr(result, 'agent_used') else "unknown"
            })
            
            logger.info(f"{'笨・ if result.success else '笶・} 菫ｮ豁｣{'謌仙粥' if result.success else '螟ｱ謨・}: {task_id} ({execution_time:.2f}遘・")
            
            return result
            
        except Exception as e:
            logger.error(f"徴 菫ｮ豁｣螳溯｡後お繝ｩ繝ｼ: {e}", exc_info=True)
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
        繧ｨ繝ｩ繝ｼ繧ｳ繝ｳ繝・く繧ｹ繝医↓蝓ｺ縺･縺・※驕ｩ蠢懃噪縺ｫ謌ｦ逡･繧帝∈謚・
        
        Args:
            error_context: 繧ｨ繝ｩ繝ｼ繧ｳ繝ｳ繝・く繧ｹ繝・
            
        Returns:
            FixStrategy: 驕ｸ謚槭＆繧後◆謌ｦ逡･
        """
        # 繧ｨ繝ｩ繝ｼ蛻・｡・
        classification = self.error_classifier.classify(error_context)
        
        complexity = classification.get("complexity", "medium")
        error_type = classification.get("error_type", "unknown")
        confidence = classification.get("confidence", 0.5)
        
        logger.info(f"投 繧ｨ繝ｩ繝ｼ蛻・｡・ 隍・尅蠎ｦ={complexity}, 繧ｿ繧､繝・{error_type}, 菫｡鬆ｼ蠎ｦ={confidence:.2f}")
        
        # 隍・尅蠎ｦ縺ｫ蝓ｺ縺･縺乗姶逡･驕ｸ謚・
        if complexity == "simple":
            # 蜊倡ｴ斐↑繧ｨ繝ｩ繝ｼ縺ｯ繝ｭ繝ｼ繧ｫ繝ｫ縺ｧ霑・溘↓蜃ｦ逅・
            return FixStrategy.LOCAL_FIRST
            
        elif complexity == "medium":
            # 荳ｭ遞句ｺｦ縺ｮ隍・尅縺輔・繝ｭ繝ｼ繧ｫ繝ｫ蜆ｪ蜈医∝､ｱ謨玲凾繧ｯ繝ｩ繧ｦ繝・
            if confidence > 0.7:
                return FixStrategy.LOCAL_FIRST
            else:
                return FixStrategy.CLOUD_FIRST
                
        else:  # complex
            # 隍・尅縺ｪ繧ｨ繝ｩ繝ｼ縺ｯ譛蛻昴°繧峨け繝ｩ繧ｦ繝・
            if error_type in ["design_flaw", "architectural", "multi_file"]:
                return FixStrategy.CLOUD_ONLY
            else:
                return FixStrategy.CLOUD_FIRST
    
    async def _execute_local_only(self, bug_fix_task: BugFixTask) -> FixResult:
        """繝ｭ繝ｼ繧ｫ繝ｫ縺ｮ縺ｿ縺ｧ螳溯｡・""
        logger.info("捗 繝ｭ繝ｼ繧ｫ繝ｫ菫ｮ豁｣螳溯｡・)
        self.stats["local_fixes"] += 1
        result = await self.local_agent.execute_bug_fix_task(bug_fix_task)
        result.agent_used = "local"
        return result
    
    async def _execute_cloud_only(self, bug_fix_task: BugFixTask) -> FixResult:
        """繧ｯ繝ｩ繧ｦ繝峨・縺ｿ縺ｧ螳溯｡・""
        logger.info("笘・ｸ・繧ｯ繝ｩ繧ｦ繝我ｿｮ豁｣螳溯｡・)
        self.stats["cloud_fixes"] += 1
        result = await self.cloud_agent.execute_bug_fix_task(bug_fix_task)
        result.agent_used = "cloud"
        return result
    
    async def _execute_local_first(self, bug_fix_task: BugFixTask) -> FixResult:
        """繝ｭ繝ｼ繧ｫ繝ｫ蜆ｪ蜈医∝､ｱ謨玲凾繧ｯ繝ｩ繧ｦ繝峨↓繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ"""
        logger.info("捗 繝ｭ繝ｼ繧ｫ繝ｫ菫ｮ豁｣繧定ｩｦ陦・)
        self.stats["local_fixes"] += 1
        
        local_result = await self.local_agent.execute_bug_fix_task(bug_fix_task)
        
        if local_result.success and local_result.confidence_score >= 0.7:
            logger.info("笨・繝ｭ繝ｼ繧ｫ繝ｫ菫ｮ豁｣謌仙粥")
            local_result.agent_used = "local"
            return local_result
        
        logger.warning("笞・・繝ｭ繝ｼ繧ｫ繝ｫ菫ｮ豁｣荳榊香蛻・√け繝ｩ繧ｦ繝峨↓繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ")
        logger.info("笘・ｸ・繧ｯ繝ｩ繧ｦ繝我ｿｮ豁｣螳溯｡・)
        self.stats["cloud_fixes"] += 1
        self.stats["hybrid_fixes"] += 1
        
        cloud_result = await self.cloud_agent.execute_bug_fix_task(bug_fix_task)
        cloud_result.agent_used = "hybrid_local_then_cloud"
        
        return cloud_result
    
    async def _execute_cloud_first(self, bug_fix_task: BugFixTask) -> FixResult:
        """繧ｯ繝ｩ繧ｦ繝牙━蜈医∝､ｱ謨玲凾繝ｭ繝ｼ繧ｫ繝ｫ縺ｫ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ"""
        logger.info("笘・ｸ・繧ｯ繝ｩ繧ｦ繝我ｿｮ豁｣繧定ｩｦ陦・)
        self.stats["cloud_fixes"] += 1
        
        cloud_result = await self.cloud_agent.execute_bug_fix_task(bug_fix_task)
        
        if cloud_result.success:
            logger.info("笨・繧ｯ繝ｩ繧ｦ繝我ｿｮ豁｣謌仙粥")
            cloud_result.agent_used = "cloud"
            return cloud_result
        
        logger.warning("笞・・繧ｯ繝ｩ繧ｦ繝我ｿｮ豁｣螟ｱ謨励√Ο繝ｼ繧ｫ繝ｫ縺ｫ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ")
        logger.info("捗 繝ｭ繝ｼ繧ｫ繝ｫ菫ｮ豁｣螳溯｡・)
        self.stats["local_fixes"] += 1
        self.stats["hybrid_fixes"] += 1
        
        local_result = await self.local_agent.execute_bug_fix_task(bug_fix_task)
        local_result.agent_used = "hybrid_cloud_then_local"
        
        return local_result
    
    async def _execute_parallel(self, bug_fix_task: BugFixTask) -> FixResult:
        """繝ｭ繝ｼ繧ｫ繝ｫ縺ｨ繧ｯ繝ｩ繧ｦ繝峨ｒ荳ｦ蛻怜ｮ溯｡後＠縲∵怙濶ｯ縺ｮ邨先棡繧帝∈謚・""
        logger.info("楳 荳ｦ蛻嶺ｿｮ豁｣螳溯｡鯉ｼ医Ο繝ｼ繧ｫ繝ｫ & 繧ｯ繝ｩ繧ｦ繝会ｼ・)
        self.stats["local_fixes"] += 1
        self.stats["cloud_fixes"] += 1
        self.stats["hybrid_fixes"] += 1
        
        # 荳ｦ蛻怜ｮ溯｡・
        results = await asyncio.gather(
            self.local_agent.execute_bug_fix_task(bug_fix_task),
            self.cloud_agent.execute_bug_fix_task(bug_fix_task),
            return_exceptions=True
        )
        
        local_result, cloud_result = results
        
        # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ
        if isinstance(local_result, Exception):
            logger.error(f"笶・繝ｭ繝ｼ繧ｫ繝ｫ荳ｦ蛻怜ｮ溯｡後お繝ｩ繝ｼ: {local_result}")
            local_result = None
        
        if isinstance(cloud_result, Exception):
            logger.error(f"笶・繧ｯ繝ｩ繧ｦ繝我ｸｦ蛻怜ｮ溯｡後お繝ｩ繝ｼ: {cloud_result}")
            cloud_result = None
        
        # 譛濶ｯ縺ｮ邨先棡繧帝∈謚・
        best_result = self._select_best_result(local_result, cloud_result)
        
        if best_result:
            best_result.agent_used = "parallel"
            logger.info(f"笨・荳ｦ蛻怜ｮ溯｡悟ｮ御ｺ・∵怙濶ｯ邨先棡繧帝∈謚橸ｼ医お繝ｼ繧ｸ繧ｧ繝ｳ繝・{best_result.agent_used}・・)
            return best_result
        else:
            # 荳｡譁ｹ螟ｱ謨・
            logger.error("笶・荳ｦ蛻怜ｮ溯｡悟､ｱ謨暦ｼ井ｸ｡繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥､ｱ謨暦ｼ・)
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
        2縺､縺ｮ邨先棡縺九ｉ譛濶ｯ縺ｮ繧ゅ・繧帝∈謚・
        
        Args:
            local_result: 繝ｭ繝ｼ繧ｫ繝ｫ邨先棡
            cloud_result: 繧ｯ繝ｩ繧ｦ繝臥ｵ先棡
            
        Returns:
            Optional[FixResult]: 譛濶ｯ縺ｮ邨先棡
        """
        # 縺ｩ縺｡繧峨°縺君one縺ｮ蝣ｴ蜷・
        if local_result is None:
            return cloud_result
        if cloud_result is None:
            return local_result
        
        # 荳｡譁ｹ謌仙粥縺ｮ蝣ｴ蜷医∽ｿ｡鬆ｼ蠎ｦ縺ｧ豈碑ｼ・
        if local_result.success and cloud_result.success:
            local_score = local_result.confidence_score or 0.5
            cloud_score = cloud_result.confidence_score or 0.5
            
            if cloud_score > local_score:
                logger.info(f"笘・ｸ・繧ｯ繝ｩ繧ｦ繝臥ｵ先棡繧帝∈謚橸ｼ井ｿ｡鬆ｼ蠎ｦ: {cloud_score:.2f} > {local_score:.2f}・・)
                return cloud_result
            else:
                logger.info(f"捗 繝ｭ繝ｼ繧ｫ繝ｫ邨先棡繧帝∈謚橸ｼ井ｿ｡鬆ｼ蠎ｦ: {local_score:.2f} >= {cloud_score:.2f}・・)
                return local_result
        
        # 縺ｩ縺｡繧峨°荳譁ｹ縺ｮ縺ｿ謌仙粥
        if local_result.success:
            logger.info("捗 繝ｭ繝ｼ繧ｫ繝ｫ邨先棡繧帝∈謚橸ｼ医Ο繝ｼ繧ｫ繝ｫ縺ｮ縺ｿ謌仙粥・・)
            return local_result
        if cloud_result.success:
            logger.info("笘・ｸ・繧ｯ繝ｩ繧ｦ繝臥ｵ先棡繧帝∈謚橸ｼ医け繝ｩ繧ｦ繝峨・縺ｿ謌仙粥・・)
            return cloud_result
        
        # 荳｡譁ｹ螟ｱ謨励・蝣ｴ蜷医∽ｿ｡鬆ｼ蠎ｦ縺碁ｫ倥＞譁ｹ
        local_score = local_result.confidence_score or 0.0
        cloud_score = cloud_result.confidence_score or 0.0
        
        return cloud_result if cloud_score > local_score else local_result
    
    def _update_avg_execution_time(self, execution_time: float):
        """蟷ｳ蝮・ｮ溯｡梧凾髢薙ｒ譖ｴ譁ｰ"""
        total = self.stats["total_tasks"]
        current_avg = self.stats["avg_execution_time"]
        self.stats["avg_execution_time"] = (current_avg * (total - 1) + execution_time) / total
    
    def get_stats(self) -> Dict[str, Any]:
        """邨ｱ險域ュ蝣ｱ繧貞叙蠕・""
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
        """邨ｱ險域ュ蝣ｱ繧定｡ｨ遉ｺ"""
        stats = self.get_stats()
        
        print("\n" + "=" * 80)
        print("投 繝上う繝悶Μ繝・ラ菫ｮ豁｣繧ｪ繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｿ繝ｼ 邨ｱ險域ュ蝣ｱ")
        print("=" * 80)
        print(f"邱上ち繧ｹ繧ｯ謨ｰ: {stats['total_tasks']}")
        print(f"謌仙粥謨ｰ: {stats['successful_fixes']} ({stats['success_rate']:.1%})")
        print(f"螟ｱ謨玲焚: {stats['failed_fixes']}")
        print(f"蟷ｳ蝮・ｮ溯｡梧凾髢・ {stats['avg_execution_time']:.2f}遘・)
        print(f"\n繝ｭ繝ｼ繧ｫ繝ｫ菫ｮ豁｣: {stats['local_fixes']}蝗・)
        print(f"繧ｯ繝ｩ繧ｦ繝我ｿｮ豁｣: {stats['cloud_fixes']}蝗・)
        print(f"繝上う繝悶Μ繝・ラ菫ｮ豁｣: {stats['hybrid_fixes']}蝗・)
        print("\n謌ｦ逡･菴ｿ逕ｨ迥ｶ豕・")
        for strategy, count in stats['strategy_usage'].items():
            print(f"  - {strategy}: {count}蝗・)
        print("=" * 80 + "\n")

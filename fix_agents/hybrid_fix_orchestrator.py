# hybrid_fix_orchestrator.py
"""
郢昜ｸ翫≧郢晄じﾎ懃ｹ昴・繝ｩ闖ｫ・ｮ雎・ｽ｣郢ｧ・ｪ郢晢ｽｼ郢ｧ・ｱ郢ｧ・ｹ郢晏現ﾎ樒ｹ晢ｽｼ郢ｧ・ｿ郢晢ｽｼ
郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ邵ｺ・ｨ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｿ・ｮ雎・ｽ｣郢ｧ蝣､・ｵ・ｱ隲｡・ｬ驍ゑｽ｡騾・・
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
    """闖ｫ・ｮ雎・ｽ｣隰鯉ｽｦ騾｡・･"""
    LOCAL_ONLY = "local_only"          # 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ邵ｺ・ｮ邵ｺ・ｿ
    CLOUD_ONLY = "cloud_only"          # 郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晏ｳｨ繝ｻ邵ｺ・ｿ
    LOCAL_FIRST = "local_first"        # 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ陷・ｽｪ陷医・
    CLOUD_FIRST = "cloud_first"        # 郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晉甥笏∬怦繝ｻ
    PARALLEL = "parallel"              # 闕ｳ・ｦ陋ｻ諤懶ｽｮ貅ｯ・｡繝ｻ
    ADAPTIVE = "adaptive"              # 鬩包ｽｩ陟｢諛・飭鬩包ｽｸ隰壹・


class HybridFixOrchestrator:
    """
    郢昜ｸ翫≧郢晄じﾎ懃ｹ昴・繝ｩ闖ｫ・ｮ雎・ｽ｣郢ｧ・ｪ郢晢ｽｼ郢ｧ・ｱ郢ｧ・ｹ郢晏現ﾎ樒ｹ晢ｽｼ郢ｧ・ｿ郢晢ｽｼ
    
    隶匁ｺｯ繝ｻ:
    - 郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ陋ｻ繝ｻ・｡讒ｭ竊堤ｹ晢ｽｫ郢晢ｽｼ郢昴・縺・ｹ晢ｽｳ郢ｧ・ｰ
    - 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ/郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｿ・ｮ雎・ｽ｣邵ｺ・ｮ鬩包ｽｸ隰壹・
    - 郢晁ｼ斐°郢晢ｽｼ郢晢ｽｫ郢晁・繝｣郢ｧ・ｯ隰鯉ｽｦ騾｡・･
    - 闕ｳ・ｦ陋ｻ諤懶ｽｮ貅ｯ・｡讙趣ｽｮ・｡騾・・
    - 驍ｨ・ｱ髫ｪ蝓溘Η陜｣・ｱ邵ｺ・ｮ陷ｿ譛ｱ蟇・
    """
    
    def __init__(
        self,
        local_agent: LocalFixAgent,
        cloud_agent: CloudFixAgent,
        error_classifier: Optional[ErrorClassifier] = None,
        default_strategy: FixStrategy = FixStrategy.ADAPTIVE
    ):
        """
        陋ｻ譎・ｄ陋ｹ繝ｻ
        
        Args:
            local_agent: 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ闖ｫ・ｮ雎・ｽ｣郢ｧ・ｨ郢晢ｽｼ郢ｧ・ｸ郢ｧ・ｧ郢晢ｽｳ郢昴・
            cloud_agent: 郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｿ・ｮ雎・ｽ｣郢ｧ・ｨ郢晢ｽｼ郢ｧ・ｸ郢ｧ・ｧ郢晢ｽｳ郢昴・
            error_classifier: 郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ陋ｻ繝ｻ・｡讒ｫ蜍｣
            default_strategy: 郢昴・繝ｵ郢ｧ・ｩ郢晢ｽｫ郢晏沺蟋ｶ騾｡・･
        """
        self.local_agent = local_agent
        self.cloud_agent = cloud_agent
        self.error_classifier = error_classifier or ErrorClassifier()
        self.default_strategy = default_strategy
        
        # 驍ｨ・ｱ髫ｪ蝓溘Η陜｣・ｱ
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
        
        # 闖ｫ・ｮ雎・ｽ｣陞ｻ・･雎・ｽｴ
        self.fix_history = []
        
        logger.info(f"隨ｨ繝ｻHybridFixOrchestrator 陋ｻ譎・ｄ陋ｹ髢・ｮ蠕｡・ｺ繝ｻ(隰鯉ｽｦ騾｡・･={default_strategy.value})")
    
    async def execute_fix_task(
        self, 
        bug_fix_task: BugFixTask,
        strategy: Optional[FixStrategy] = None
    ) -> FixResult:
        """
        闖ｫ・ｮ雎・ｽ｣郢ｧ・ｿ郢ｧ・ｹ郢ｧ・ｯ郢ｧ雋橸ｽｮ貅ｯ・｡繝ｻ
        
        Args:
            bug_fix_task: 郢晁・縺定将・ｮ雎・ｽ｣郢ｧ・ｿ郢ｧ・ｹ郢ｧ・ｯ
            strategy: 闖ｫ・ｮ雎・ｽ｣隰鯉ｽｦ騾｡・･繝ｻ閧ｲ諤宣｡・･隴弱ｅ繝ｻ郢昴・繝ｵ郢ｧ・ｩ郢晢ｽｫ郢晁肩・ｼ繝ｻ
            
        Returns:
            FixResult: 闖ｫ・ｮ雎・ｽ｣驍ｨ蜈域｣｡
        """
        start_time = datetime.now()
        task_id = bug_fix_task.task_id
        
        self.stats["total_tasks"] += 1
        
        # 隰鯉ｽｦ騾｡・･邵ｺ・ｮ雎趣ｽｺ陞ｳ繝ｻ
        selected_strategy = strategy or self.default_strategy
        
        # 鬩包ｽｩ陟｢諛・飭隰鯉ｽｦ騾｡・･邵ｺ・ｮ陜｣・ｴ陷ｷ蛹ｻﾂ竏壹♀郢晢ｽｩ郢晢ｽｼ陋ｻ繝ｻ譴ｵ邵ｺ・ｫ陜難ｽｺ邵ｺ・･邵ｺ繝ｻ窶ｻ雎趣ｽｺ陞ｳ繝ｻ
        if selected_strategy == FixStrategy.ADAPTIVE:
            selected_strategy = await self._select_adaptive_strategy(bug_fix_task.error_context)
        
        self.stats["strategy_usage"][selected_strategy.value] += 1
        
        logger.info("=" * 80)
        logger.info(f"﨟櫁ｭ・郢昜ｸ翫≧郢晄じﾎ懃ｹ昴・繝ｩ闖ｫ・ｮ雎・ｽ｣鬮｢蜿･・ｧ繝ｻ {task_id}")
        logger.info(f"﨟樊兜 鬩包ｽｸ隰壽ｨ雁ｧｶ騾｡・･: {selected_strategy.value}")
        logger.info("=" * 80)
        
        try:
            # 隰鯉ｽｦ騾｡・･邵ｺ・ｫ陟｢諛環ｧ邵ｺ貅ｷ・ｮ貅ｯ・｡繝ｻ
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
            
            # 驍ｨ・ｱ髫ｪ蝓溘Η陜｣・ｱ邵ｺ・ｮ隴厄ｽｴ隴・ｽｰ
            if result.success:
                self.stats["successful_fixes"] += 1
            else:
                self.stats["failed_fixes"] += 1
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_avg_execution_time(execution_time)
            
            # 陞ｻ・･雎・ｽｴ邵ｺ・ｫ髴托ｽｽ陷会｣ｰ
            self.fix_history.append({
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "strategy": selected_strategy.value,
                "success": result.success,
                "execution_time": execution_time,
                "agent_used": result.agent_used if hasattr(result, 'agent_used') else "unknown"
            })
            
            logger.info(f"{'隨ｨ繝ｻ if result.success else '隨ｶ繝ｻ} 闖ｫ・ｮ雎・ｽ｣{'隰御ｻ咏ｲ･' if result.success else '陞滂ｽｱ隰ｨ繝ｻ}: {task_id} ({execution_time:.2f}驕倥・")
            
            return result
            
        except Exception as e:
            logger.error(f"﨟槫ｾｴ 闖ｫ・ｮ雎・ｽ｣陞ｳ貅ｯ・｡蠕後♀郢晢ｽｩ郢晢ｽｼ: {e}", exc_info=True)
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
        郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ郢ｧ・ｳ郢晢ｽｳ郢昴・縺冗ｹｧ・ｹ郢晏現竊楢搏・ｺ邵ｺ・･邵ｺ繝ｻ窶ｻ鬩包ｽｩ陟｢諛・飭邵ｺ・ｫ隰鯉ｽｦ騾｡・･郢ｧ蟶昶・隰壹・
        
        Args:
            error_context: 郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ郢ｧ・ｳ郢晢ｽｳ郢昴・縺冗ｹｧ・ｹ郢昴・
            
        Returns:
            FixStrategy: 鬩包ｽｸ隰壽ｧｭ・・ｹｧ蠕娯螺隰鯉ｽｦ騾｡・･
        """
        # 郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ陋ｻ繝ｻ・｡繝ｻ
        classification = self.error_classifier.classify(error_context)
        
        complexity = classification.get("complexity", "medium")
        error_type = classification.get("error_type", "unknown")
        confidence = classification.get("confidence", 0.5)
        
        logger.info(f"﨟樊兜 郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ陋ｻ繝ｻ・｡繝ｻ 髫阪・蟆・趣ｽｦ={complexity}, 郢ｧ・ｿ郢ｧ・､郢昴・{error_type}, 闖ｫ・｡鬯・ｽｼ陟趣ｽｦ={confidence:.2f}")
        
        # 髫阪・蟆・趣ｽｦ邵ｺ・ｫ陜難ｽｺ邵ｺ・･邵ｺ荵怜ｧｶ騾｡・･鬩包ｽｸ隰壹・
        if complexity == "simple":
            # 陷雁｡・ｴ譁絶・郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ邵ｺ・ｯ郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ邵ｺ・ｧ髴代・ﾂ貅倪・陷・ｽｦ騾・・
            return FixStrategy.LOCAL_FIRST
            
        elif complexity == "medium":
            # 闕ｳ・ｭ驕槫唱・ｺ・ｦ邵ｺ・ｮ髫阪・蟆・ｸｺ霈斐・郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ陷・ｽｪ陷亥現ﾂ竏晢ｽ､・ｱ隰ｨ邇ｲ蜃ｾ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢昴・
            if confidence > 0.7:
                return FixStrategy.LOCAL_FIRST
            else:
                return FixStrategy.CLOUD_FIRST
                
        else:  # complex
            # 髫阪・蟆・ｸｺ・ｪ郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ邵ｺ・ｯ隴崢陋ｻ譏ｴﾂｰ郢ｧ蟲ｨ縺醍ｹ晢ｽｩ郢ｧ・ｦ郢昴・
            if error_type in ["design_flaw", "architectural", "multi_file"]:
                return FixStrategy.CLOUD_ONLY
            else:
                return FixStrategy.CLOUD_FIRST
    
    async def _execute_local_only(self, bug_fix_task: BugFixTask) -> FixResult:
        """郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ邵ｺ・ｮ邵ｺ・ｿ邵ｺ・ｧ陞ｳ貅ｯ・｡繝ｻ""
        logger.info("﨟樊漉 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ闖ｫ・ｮ雎・ｽ｣陞ｳ貅ｯ・｡繝ｻ)
        self.stats["local_fixes"] += 1
        result = await self.local_agent.execute_bug_fix_task(bug_fix_task)
        result.agent_used = "local"
        return result
    
    async def _execute_cloud_only(self, bug_fix_task: BugFixTask) -> FixResult:
        """郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晏ｳｨ繝ｻ邵ｺ・ｿ邵ｺ・ｧ陞ｳ貅ｯ・｡繝ｻ""
        logger.info("隨倥・・ｸ繝ｻ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｿ・ｮ雎・ｽ｣陞ｳ貅ｯ・｡繝ｻ)
        self.stats["cloud_fixes"] += 1
        result = await self.cloud_agent.execute_bug_fix_task(bug_fix_task)
        result.agent_used = "cloud"
        return result
    
    async def _execute_local_first(self, bug_fix_task: BugFixTask) -> FixResult:
        """郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ陷・ｽｪ陷亥現ﾂ竏晢ｽ､・ｱ隰ｨ邇ｲ蜃ｾ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晏ｳｨ竊鍋ｹ晁ｼ斐°郢晢ｽｼ郢晢ｽｫ郢晁・繝｣郢ｧ・ｯ"""
        logger.info("﨟樊漉 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ闖ｫ・ｮ雎・ｽ｣郢ｧ螳夲ｽｩ・ｦ髯ｦ繝ｻ)
        self.stats["local_fixes"] += 1
        
        local_result = await self.local_agent.execute_bug_fix_task(bug_fix_task)
        
        if local_result.success and local_result.confidence_score >= 0.7:
            logger.info("隨ｨ繝ｻ郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ闖ｫ・ｮ雎・ｽ｣隰御ｻ咏ｲ･")
            local_result.agent_used = "local"
            return local_result
        
        logger.warning("隨橸｣ｰ繝ｻ繝ｻ郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ闖ｫ・ｮ雎・ｽ｣闕ｳ讎企ｦ呵崕繝ｻﾂ竏壹￠郢晢ｽｩ郢ｧ・ｦ郢晏ｳｨ竊鍋ｹ晁ｼ斐°郢晢ｽｼ郢晢ｽｫ郢晁・繝｣郢ｧ・ｯ")
        logger.info("隨倥・・ｸ繝ｻ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｿ・ｮ雎・ｽ｣陞ｳ貅ｯ・｡繝ｻ)
        self.stats["cloud_fixes"] += 1
        self.stats["hybrid_fixes"] += 1
        
        cloud_result = await self.cloud_agent.execute_bug_fix_task(bug_fix_task)
        cloud_result.agent_used = "hybrid_local_then_cloud"
        
        return cloud_result
    
    async def _execute_cloud_first(self, bug_fix_task: BugFixTask) -> FixResult:
        """郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晉甥笏∬怦蛹ｻﾂ竏晢ｽ､・ｱ隰ｨ邇ｲ蜃ｾ郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ邵ｺ・ｫ郢晁ｼ斐°郢晢ｽｼ郢晢ｽｫ郢晁・繝｣郢ｧ・ｯ"""
        logger.info("隨倥・・ｸ繝ｻ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｿ・ｮ雎・ｽ｣郢ｧ螳夲ｽｩ・ｦ髯ｦ繝ｻ)
        self.stats["cloud_fixes"] += 1
        
        cloud_result = await self.cloud_agent.execute_bug_fix_task(bug_fix_task)
        
        if cloud_result.success:
            logger.info("隨ｨ繝ｻ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｿ・ｮ雎・ｽ｣隰御ｻ咏ｲ･")
            cloud_result.agent_used = "cloud"
            return cloud_result
        
        logger.warning("隨橸｣ｰ繝ｻ繝ｻ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｿ・ｮ雎・ｽ｣陞滂ｽｱ隰ｨ蜉ｱﾂ竏墅溽ｹ晢ｽｼ郢ｧ・ｫ郢晢ｽｫ邵ｺ・ｫ郢晁ｼ斐°郢晢ｽｼ郢晢ｽｫ郢晁・繝｣郢ｧ・ｯ")
        logger.info("﨟樊漉 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ闖ｫ・ｮ雎・ｽ｣陞ｳ貅ｯ・｡繝ｻ)
        self.stats["local_fixes"] += 1
        self.stats["hybrid_fixes"] += 1
        
        local_result = await self.local_agent.execute_bug_fix_task(bug_fix_task)
        local_result.agent_used = "hybrid_cloud_then_local"
        
        return local_result
    
    async def _execute_parallel(self, bug_fix_task: BugFixTask) -> FixResult:
        """郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ邵ｺ・ｨ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晏ｳｨ・定叉・ｦ陋ｻ諤懶ｽｮ貅ｯ・｡蠕鯉ｼ邵ｲ竏ｵ諤呎ｿｶ・ｯ邵ｺ・ｮ驍ｨ蜈域｣｡郢ｧ蟶昶・隰壹・""
        logger.info("﨟樊･ｳ 闕ｳ・ｦ陋ｻ蠍ｺ・ｿ・ｮ雎・ｽ｣陞ｳ貅ｯ・｡魃会ｽｼ蛹ｻﾎ溽ｹ晢ｽｼ郢ｧ・ｫ郢晢ｽｫ & 郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢昜ｼ夲ｽｼ繝ｻ)
        self.stats["local_fixes"] += 1
        self.stats["cloud_fixes"] += 1
        self.stats["hybrid_fixes"] += 1
        
        # 闕ｳ・ｦ陋ｻ諤懶ｽｮ貅ｯ・｡繝ｻ
        results = await asyncio.gather(
            self.local_agent.execute_bug_fix_task(bug_fix_task),
            self.cloud_agent.execute_bug_fix_task(bug_fix_task),
            return_exceptions=True
        )
        
        local_result, cloud_result = results
        
        # 郢ｧ・ｨ郢晢ｽｩ郢晢ｽｼ郢昜ｸ莞ｦ郢晏ｳｨﾎ懃ｹ晢ｽｳ郢ｧ・ｰ
        if isinstance(local_result, Exception):
            logger.error(f"隨ｶ繝ｻ郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ闕ｳ・ｦ陋ｻ諤懶ｽｮ貅ｯ・｡蠕後♀郢晢ｽｩ郢晢ｽｼ: {local_result}")
            local_result = None
        
        if isinstance(cloud_result, Exception):
            logger.error(f"隨ｶ繝ｻ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｸ・ｦ陋ｻ諤懶ｽｮ貅ｯ・｡蠕後♀郢晢ｽｩ郢晢ｽｼ: {cloud_result}")
            cloud_result = None
        
        # 隴崢豼ｶ・ｯ邵ｺ・ｮ驍ｨ蜈域｣｡郢ｧ蟶昶・隰壹・
        best_result = self._select_best_result(local_result, cloud_result)
        
        if best_result:
            best_result.agent_used = "parallel"
            logger.info(f"隨ｨ繝ｻ闕ｳ・ｦ陋ｻ諤懶ｽｮ貅ｯ・｡謔滂ｽｮ蠕｡・ｺ繝ｻﾂ竏ｵ諤呎ｿｶ・ｯ驍ｨ蜈域｣｡郢ｧ蟶昶・隰壽ｩｸ・ｼ蛹ｻ縺顔ｹ晢ｽｼ郢ｧ・ｸ郢ｧ・ｧ郢晢ｽｳ郢昴・{best_result.agent_used}繝ｻ繝ｻ)
            return best_result
        else:
            # 闕ｳ・｡隴・ｽｹ陞滂ｽｱ隰ｨ繝ｻ
            logger.error("隨ｶ繝ｻ闕ｳ・ｦ陋ｻ諤懶ｽｮ貅ｯ・｡謔滂ｽ､・ｱ隰ｨ證ｦ・ｼ莠包ｽｸ・｡郢ｧ・ｨ郢晢ｽｼ郢ｧ・ｸ郢ｧ・ｧ郢晢ｽｳ郢昜ｺ･・､・ｱ隰ｨ證ｦ・ｼ繝ｻ)
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
        2邵ｺ・､邵ｺ・ｮ驍ｨ蜈域｣｡邵ｺ荵晢ｽ芽ｭ崢豼ｶ・ｯ邵ｺ・ｮ郢ｧ繧・・郢ｧ蟶昶・隰壹・
        
        Args:
            local_result: 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ驍ｨ蜈域｣｡
            cloud_result: 郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晁・・ｵ蜈域｣｡
            
        Returns:
            Optional[FixResult]: 隴崢豼ｶ・ｯ邵ｺ・ｮ驍ｨ蜈域｣｡
        """
        # 邵ｺ・ｩ邵ｺ・｡郢ｧ蟲ｨﾂｰ邵ｺ蜷孃ne邵ｺ・ｮ陜｣・ｴ陷ｷ繝ｻ
        if local_result is None:
            return cloud_result
        if cloud_result is None:
            return local_result
        
        # 闕ｳ・｡隴・ｽｹ隰御ｻ咏ｲ･邵ｺ・ｮ陜｣・ｴ陷ｷ蛹ｻﾂ竏ｽ・ｿ・｡鬯・ｽｼ陟趣ｽｦ邵ｺ・ｧ雎育｢托ｽｼ繝ｻ
        if local_result.success and cloud_result.success:
            local_score = local_result.confidence_score or 0.5
            cloud_score = cloud_result.confidence_score or 0.5
            
            if cloud_score > local_score:
                logger.info(f"隨倥・・ｸ繝ｻ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晁・・ｵ蜈域｣｡郢ｧ蟶昶・隰壽ｩｸ・ｼ莠包ｽｿ・｡鬯・ｽｼ陟趣ｽｦ: {cloud_score:.2f} > {local_score:.2f}繝ｻ繝ｻ)
                return cloud_result
            else:
                logger.info(f"﨟樊漉 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ驍ｨ蜈域｣｡郢ｧ蟶昶・隰壽ｩｸ・ｼ莠包ｽｿ・｡鬯・ｽｼ陟趣ｽｦ: {local_score:.2f} >= {cloud_score:.2f}繝ｻ繝ｻ)
                return local_result
        
        # 邵ｺ・ｩ邵ｺ・｡郢ｧ蟲ｨﾂｰ闕ｳﾂ隴・ｽｹ邵ｺ・ｮ邵ｺ・ｿ隰御ｻ咏ｲ･
        if local_result.success:
            logger.info("﨟樊漉 郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ驍ｨ蜈域｣｡郢ｧ蟶昶・隰壽ｩｸ・ｼ蛹ｻﾎ溽ｹ晢ｽｼ郢ｧ・ｫ郢晢ｽｫ邵ｺ・ｮ邵ｺ・ｿ隰御ｻ咏ｲ･繝ｻ繝ｻ)
            return local_result
        if cloud_result.success:
            logger.info("隨倥・・ｸ繝ｻ郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晁・・ｵ蜈域｣｡郢ｧ蟶昶・隰壽ｩｸ・ｼ蛹ｻ縺醍ｹ晢ｽｩ郢ｧ・ｦ郢晏ｳｨ繝ｻ邵ｺ・ｿ隰御ｻ咏ｲ･繝ｻ繝ｻ)
            return cloud_result
        
        # 闕ｳ・｡隴・ｽｹ陞滂ｽｱ隰ｨ蜉ｱ繝ｻ陜｣・ｴ陷ｷ蛹ｻﾂ竏ｽ・ｿ・｡鬯・ｽｼ陟趣ｽｦ邵ｺ遒・ｽｫ蛟･・櫁ｭ・ｽｹ
        local_score = local_result.confidence_score or 0.0
        cloud_score = cloud_result.confidence_score or 0.0
        
        return cloud_result if cloud_score > local_score else local_result
    
    def _update_avg_execution_time(self, execution_time: float):
        """陝ｷ・ｳ陜ｮ繝ｻ・ｮ貅ｯ・｡譴ｧ蜃ｾ鬮｢阮呻ｽ定ｭ厄ｽｴ隴・ｽｰ"""
        total = self.stats["total_tasks"]
        current_avg = self.stats["avg_execution_time"]
        self.stats["avg_execution_time"] = (current_avg * (total - 1) + execution_time) / total
    
    def get_stats(self) -> Dict[str, Any]:
        """驍ｨ・ｱ髫ｪ蝓溘Η陜｣・ｱ郢ｧ雋槫徐陟輔・""
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
        """驍ｨ・ｱ髫ｪ蝓溘Η陜｣・ｱ郢ｧ螳夲ｽ｡・ｨ驕会ｽｺ"""
        stats = self.get_stats()
        
        print("\n" + "=" * 80)
        print("﨟樊兜 郢昜ｸ翫≧郢晄じﾎ懃ｹ昴・繝ｩ闖ｫ・ｮ雎・ｽ｣郢ｧ・ｪ郢晢ｽｼ郢ｧ・ｱ郢ｧ・ｹ郢晏現ﾎ樒ｹ晢ｽｼ郢ｧ・ｿ郢晢ｽｼ 驍ｨ・ｱ髫ｪ蝓溘Η陜｣・ｱ")
        print("=" * 80)
        print(f"驍ｱ荳翫■郢ｧ・ｹ郢ｧ・ｯ隰ｨ・ｰ: {stats['total_tasks']}")
        print(f"隰御ｻ咏ｲ･隰ｨ・ｰ: {stats['successful_fixes']} ({stats['success_rate']:.1%})")
        print(f"陞滂ｽｱ隰ｨ邇ｲ辟・ {stats['failed_fixes']}")
        print(f"陝ｷ・ｳ陜ｮ繝ｻ・ｮ貅ｯ・｡譴ｧ蜃ｾ鬮｢繝ｻ {stats['avg_execution_time']:.2f}驕倥・)
        print(f"\n郢晢ｽｭ郢晢ｽｼ郢ｧ・ｫ郢晢ｽｫ闖ｫ・ｮ雎・ｽ｣: {stats['local_fixes']}陜励・)
        print(f"郢ｧ・ｯ郢晢ｽｩ郢ｧ・ｦ郢晄・・ｿ・ｮ雎・ｽ｣: {stats['cloud_fixes']}陜励・)
        print(f"郢昜ｸ翫≧郢晄じﾎ懃ｹ昴・繝ｩ闖ｫ・ｮ雎・ｽ｣: {stats['hybrid_fixes']}陜励・)
        print("\n隰鯉ｽｦ騾｡・･闖ｴ・ｿ騾包ｽｨ霑･・ｶ雎輔・")
        for strategy, count in stats['strategy_usage'].items():
            print(f"  - {strategy}: {count}陜励・)
        print("=" * 80 + "\n")

"""
修正版SelfLearningPipeline v2 - 互換性問題解決
"""

import os
import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
from agents.self_healing.pattern_extractor import PatternExtractor
from agents.self_healing.decision_support_system import DecisionSupportSystem
from agents.self_healing.logging.log_integrator_fixed import LogIntegratorFixed
from agents.self_healing.logging.context_logger import ContextLogger


class SelfLearningPipelineFixedV2:
    def __init__(self, sheets_manager, knowledge_base_manager):
        self.sheets_manager = sheets_manager
        self.kb_manager = knowledge_base_manager

        # 修正版コンポーネントを使用
        self.log_integrator = LogIntegratorFixed(self.sheets_manager)
        self.pattern_extractor = PatternExtractor(self.log_integrator)
        self.decision_system = DecisionSupportSystem()
        self.context_logger = ContextLogger(self.sheets_manager)

        print("✅ SelfLearningPipelineFixedV2 初期化完了")

    async def run_learning_cycle(self):
        """学習サイクルを実行 - 互換性確保版"""
        try:
            # ログ収集
            logs = await self.log_integrator.load_all_logs()

            # パターン抽出
            patterns = await self.pattern_extractor.extract(logs)

            # ナレッジ更新
            await self.kb_manager.update(patterns)

            # 修正戦略生成
            strategies = await self.decision_system.decide(patterns)

            print(f"✅ 学習サイクル完了: {len(strategies)}個の戦略を生成")
            return strategies

        except Exception as e:
            print(f"❌ 学習サイクルエラー: {e}")
            import traceback

            traceback.print_exc()
            return []

    async def learn_from_error(self, error_result):
        """エラーから学習"""
        try:
            await self.log_integrator.integrate_logs([error_result])
            return True
        except Exception as e:
            print(f"❌ エラー学習失敗: {e}")
            return False

"""
修正版SelfLearningPipeline - 既存機能を維持
"""

import os
import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
from agents.self_healing.pattern_extractor import PatternExtractor
from agents.self_healing.decision_support_system import DecisionSupportSystem
from agents.self_healing.logging.log_integrator import LogIntegrator  # 既存のモジュールを使用


class SelfLearningPipelineFixed:
    def __init__(self, sheets_manager, knowledge_base_manager):
        self.sheets_manager = sheets_manager
        self.kb_manager = knowledge_base_manager

        # 既存のコンポーネントを正しく初期化
        self.log_integrator = LogIntegrator()
        self.pattern_extractor = PatternExtractor(self.log_integrator)  # LogIntegratorを渡す
        self.decision_system = DecisionSupportSystem()

        print("✅ SelfLearningPipelineFixed 初期化完了")

    async def run_learning_cycle(self):
        """学習サイクルを実行 - 既存ロジックを維持"""
        try:
            # 既存のログ収集メソッドを使用
            logs = await self.log_integrator.load_all_logs()

            # パターン抽出
            patterns = await self.pattern_extractor.extract(logs)

            # ナレッジ更新
            await self.kb_manager.update(patterns)

            # 修正戦略生成
            strategies = await self.decision_system.decide(patterns)

            return strategies

        except Exception as e:
            print(f"❌ 学習サイクルエラー: {e}")
            return []

    async def learn_from_error(self, error_result):
        """エラーから学習 - 既存機能を維持"""
        try:
            # エラーログを記録
            await self.log_integrator.integrate_logs([error_result])
            return True
        except Exception as e:
            print(f"❌ エラー学習失敗: {e}")
            return False

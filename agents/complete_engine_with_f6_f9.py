"""
CompleteEngine（F6/F9統合版）
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.complete_engine_with_strict_quality import CompleteEngineWithStrictQuality
from agents.f6_dynamic_task_generator import F6DynamicTaskGenerator
from agents.f9_human_interface import F9HumanInterface

class CompleteEngineWithF6F9(CompleteEngineWithStrictQuality):
    """CompleteEngine（F6/F9統合版）"""
    
    def __init__(self):
        super().__init__()
        self.f6_generator = F6DynamicTaskGenerator(self.sheets)
        self.f9_interface = F9HumanInterface(self.sheets)
        
    def run_full_integration_cycle_with_f6_f9(self, goal_id=None, limit=1):
        """統合フロー（F6/F9対応版）"""
        print("\n" + "=" * 80)
        print("🚀 完全統合フロー開始（F6/F9対応版）")
        print("=" * 80)
        
        # F9: 人間指示チェック（最優先）
        instructions = self.f9_interface.check_human_instructions()
        if instructions:
            self.f9_interface.process_instructions(instructions)
        
        # F1: タスク可用性チェック
        result = self.run_full_integration_cycle_fixed(goal_id, limit)
        
        # 実行結果を確認
        if not result.get('success'):
            return result
        
        # F6: 品質不合格タスクの処理
        # TODO: 各タスクの品質評価結果を取得
        # 簡易版として、最後に実行したタスクをチェック
        
        return result


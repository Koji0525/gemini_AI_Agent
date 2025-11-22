"""
CompleteEngine（厳格品質評価統合版）
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.complete_engine_ultimate_fixed import CompleteEngineUltimateFixed
from tools.strict_quality_evaluator import StrictQualityEvaluator

class CompleteEngineWithStrictQuality(CompleteEngineUltimateFixed):
    """CompleteEngine（厳格品質評価統合版）"""
    
    def __init__(self):
        super().__init__()
        self.strict_evaluator = StrictQualityEvaluator()
        
    def execute_task_with_strict_quality(self, task):
        """タスク実行（厳格品質評価付き）"""
        print(f"\n{'=' * 80}")
        print(f"🚀 タスク実行: {task['task_id']}")
        print('=' * 80)
        
        # タスク実行
        result = self.execute_task(task)
        
        # 成果物ディレクトリを特定
        output_dir = self._find_output_dir(task['task_id'])
        
        if output_dir:
            # 厳格品質評価
            quality_result = self.strict_evaluator.evaluate_task_output(
                task['task_id'],
                output_dir
            )
            
            # 結果を統合
            result['strict_quality'] = quality_result
            result['quality_score_strict'] = quality_result['score'] * 10  # 100点満点に変換
            result['usability'] = quality_result['usability']
            
            # 合否判定
            if quality_result['score'] >= 7.0:
                print("\n✅ 品質評価: 合格（実用化レベル）")
                result['status'] = 'completed'
            else:
                print(f"\n❌ 品質評価: 不合格（{quality_result['usability']}）")
                result['status'] = 'failed'
                result['retry_needed'] = True
        else:
            print("\n❌ 成果物ディレクトリが見つかりません")
            result['quality_score_strict'] = 0
            result['status'] = 'failed'
            result['retry_needed'] = True
        
        return result
    
    def _find_output_dir(self, task_id: str) -> str:
        """成果物ディレクトリを検索"""
        import os
        
        base_dirs = [
            'agent_outputs/implementation',
            'agent_outputs/design',
            'agent_outputs/testing',
            'agent_outputs/documentation'
        ]
        
        for base_dir in base_dirs:
            if not os.path.exists(base_dir):
                continue
            
            for entry in os.listdir(base_dir):
                entry_path = os.path.join(base_dir, entry)
                if os.path.isdir(entry_path):
                    # タスクIDが含まれているか確認
                    if task_id.split('_')[0] in entry:
                        return entry_path
        
        return None


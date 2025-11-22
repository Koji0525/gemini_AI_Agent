"""
QualityFeedbackLoop v2
品質不合格時の自動改善と再実行
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.strict_quality_evaluator import StrictQualityEvaluator
from agents.task_executor_enhanced_v3 import TaskExecutorEnhancedV3

class QualityFeedbackLoopV2:
    """品質フィードバックループ v2"""
    
    MAX_RETRY = 3
    PASS_THRESHOLD = 7.0
    
    def __init__(self):
        self.evaluator = StrictQualityEvaluator()
        self.executor = TaskExecutorEnhancedV3()
        
    def execute_with_quality_assurance(self, task: dict) -> dict:
        """品質保証付きタスク実行"""
        print(f"\n{'=' * 80}")
        print(f"🔄 QualityFeedbackLoop: {task['task_id']}")
        print('=' * 80)
        
        retry_count = 0
        previous_failure = None
        
        # 戦略リスト
        strategies = [
            TaskExecutorEnhancedV3.STRATEGY_DETAILED,
            TaskExecutorEnhancedV3.STRATEGY_STEP_BY_STEP,
            TaskExecutorEnhancedV3.STRATEGY_CONCISE
        ]
        
        while retry_count < self.MAX_RETRY:
            print(f"\n【実行 {retry_count + 1}/{self.MAX_RETRY}】")
            
            # 戦略を選択
            strategy = strategies[retry_count]
            
            try:
                # タスク実行
                exec_result = self.executor.execute_task_with_strategy(
                    task,
                    strategy=strategy,
                    previous_failure=previous_failure,
                    retry_count=retry_count
                )
                
                # 品質評価
                quality_result = self.evaluator.evaluate_task_output(
                    task['task_id'],
                    exec_result['output_path']
                )
                
                score = quality_result['score']
                
                print(f"\n📊 品質評価結果: {score:.1f}/10点")
                print(f"   実用性: {quality_result['usability']}")
                
                # 合格判定
                if score >= self.PASS_THRESHOLD:
                    print(f"\n✅ 品質合格！（{score:.1f}/10点）")
                    return {
                        'success': True,
                        'score': score,
                        'output_path': exec_result['output_path'],
                        'retry_count': retry_count,
                        'quality': quality_result
                    }
                else:
                    print(f"\n⚠️  品質不合格（{score:.1f}/10点 < {self.PASS_THRESHOLD}点）")
                    
                    # 改善提案を生成
                    previous_failure = self._generate_improvement_suggestions(
                        quality_result
                    )
                    
                    print(f"\n📝 改善提案:\n{previous_failure}")
                    
                    retry_count += 1
                    
            except Exception as e:
                print(f"\n❌ 実行エラー: {e}")
                import traceback
                traceback.print_exc()
                previous_failure = f"エラーが発生しました: {str(e)}"
                retry_count += 1
        
        # 最大リトライ回数到達
        print(f"\n❌ 最大リトライ回数到達（{self.MAX_RETRY}回）")
        return {
            'success': False,
            'score': 0,
            'retry_count': retry_count,
            'reason': '品質基準を満たせませんでした'
        }
    
    def _generate_improvement_suggestions(self, quality_result: dict) -> str:
        """改善提案を生成"""
        evaluation = quality_result['evaluation']
        
        suggestions = []
        
        # 行数不足
        if evaluation['total_lines'] < 300:
            suggestions.append(
                f"❌ 行数不足: {evaluation['total_lines']}行 < 300行\n"
                f"   → より詳細な実装を追加してください\n"
                f"   → メインファイルを150行以上に拡張\n"
                f"   → サブモジュールを追加（各50行以上）"
            )
        
        # サイズ不足
        if evaluation['total_bytes'] < 5000:
            suggestions.append(
                f"❌ サイズ不足: {evaluation['total_bytes']}バイト < 5000バイト\n"
                f"   → より多くのコードと説明を追加"
            )
        
        # コードファイル不足
        if evaluation['code_files'] < 2:
            suggestions.append(
                f"❌ コードファイル不足: {evaluation['code_files']}個 < 2個\n"
                f"   → メインファイルとサポートファイルを作成"
            )
        
        # ドキュメント不足
        if evaluation['doc_files'] < 2:
            suggestions.append(
                f"❌ ドキュメント不足: {evaluation['doc_files']}個 < 2個\n"
                f"   → README.mdとAPI仕様書を作成"
            )
        
        # README.md なし
        if not evaluation['has_readme']:
            suggestions.append(
                f"❌ README.md なし\n"
                f"   → 詳細な使用方法を記載したREADME.mdを作成（100行以上）"
            )
        
        return "\n\n".join(suggestions)


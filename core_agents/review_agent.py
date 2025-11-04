"""
Review Agent - タスク実行結果の品質評価を担当
"""

import asyncio
from typing import Dict, Any, List
import logging

class ReviewAgent:
    """
    タスク実行結果を評価し、品質スコアを付与するエージェント
    
    責務:
    - タスク実行結果の品質評価
    - 0-10点の品質スコア付与
    - 改善提案の生成
    - 評価失敗時の適切なフォールバック処理
    """
    
    def __init__(self, sheets_manager=None):
        """
        ReviewAgentの初期化
        
        Args:
            sheets_manager: スプレッドシート管理オブジェクト（オプション）
        """
        self.sheets_manager = sheets_manager
        self.logger = logging.getLogger(__name__)
        
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク結果を評価して品質スコアを返す
        
        Args:
            context: 評価コンテキストを含む辞書
                - task_id: タスクID
                - task_name: タスク名  
                - task_description: タスク説明
                - result: 実行結果
                - agent_name: 使用エージェント
                - timestamp: 評価時間
                
        Returns:
            dict: 品質評価結果
                - quality_score: 0-10のスコア
                - evaluation: 評価コメント
                - status: 評価状態
                - improvement_suggestions: 改善提案（リスト）
        """
        try:
            # 必須フィールドのバリデーション
            if not context or not isinstance(context, dict):
                return self._create_fallback_response(
                    "評価コンテキストが不正な形式です",
                    "invalid_context"
                )
            
            if not context.get('task_name'):
                return self._create_fallback_response(
                    "タスク名が取得できないため中間評価",
                    "missing_task_name"
                )
            
            # 結果データの検証
            result = context.get('result', {})
            if not result or not isinstance(result, dict):
                return self._create_fallback_response(
                    "実行結果が不正な形式です",
                    "invalid_result"
                )
            
            # 評価コンテキストの抽出
            task_name = context.get('task_name', '不明なタスク')
            task_description = context.get('task_description', '')
            agent_name = context.get('agent_name', '不明なエージェント')
            output = result.get('output', '')
            status = result.get('status', 'unknown')
            
            self.logger.info(f"評価開始: {task_name} (エージェント: {agent_name})")
            
            # 品質スコアの計算
            quality_score = self._calculate_quality_score(
                task_name, output, status, agent_name
            )
            
            # 評価コメントの生成
            evaluation_comment = self._generate_evaluation_comment(
                quality_score, task_name, output
            )
            
            # 改善提案の生成
            improvement_suggestions = self._generate_improvement_suggestions(
                quality_score, output, task_name
            )
            
            # 評価状態の決定
            evaluation_status = self._determine_evaluation_status(quality_score)
            
            response = {
                'quality_score': quality_score,
                'evaluation': evaluation_comment,
                'status': evaluation_status,
                'improvement_suggestions': improvement_suggestions,
                'task_name': task_name,
                'agent_name': agent_name
            }
            
            self.logger.info(f"評価完了: {task_name} - スコア: {quality_score}/10")
            
            return response
            
        except Exception as e:
            # 評価失敗時のフォールバック
            self.logger.error(f"評価処理中にエラーが発生: {str(e)}")
            
            return self._create_fallback_response(
                f"評価処理中にエラーが発生: {str(e)}",
                "evaluation_error"
            )
    
    def _calculate_quality_score(self, task_name: str, output: str, 
                               status: str, agent_name: str) -> int:
        """
        品質スコアを計算する（0-10点）
        
        Args:
            task_name: タスク名
            output: 出力内容
            status: 実行ステータス
            agent_name: エージェント名
            
        Returns:
            int: 0-10の品質スコア
        """
        base_score = 7  # デフォルトスコア
        
        # 出力内容の分析
        if output:
            # 出力の長さによる調整
            if len(output.strip()) > 200:
                base_score += 1  # 詳細な出力は高評価
            elif len(output.strip()) < 10:
                base_score -= 1  # 短すぎる出力は低評価
            
            # キーワード分析
            positive_keywords = ['success', 'complete', 'done', 'finished', '成功']
            negative_keywords = ['error', 'fail', 'failed', 'exception', 'エラー']
            
            output_lower = output.lower()
            
            for keyword in positive_keywords:
                if keyword in output_lower:
                    base_score += 1
                    break
                    
            for keyword in negative_keywords:
                if keyword in output_lower:
                    base_score -= 2
                    break
        
        # ステータスによる調整
        status_scores = {
            'completed': 2,
            'success': 2,
            'partial': 0,
            'failed': -2,
            'error': -3,
            'timeout': -2
        }
        
        base_score += status_scores.get(status, 0)
        
        # エージェント種別による調整（経験則）
        if 'gemini' in agent_name.lower():
            base_score += 0  # 標準
        elif 'human' in agent_name.lower():
            base_score += 1  # 人間の介入は高品質と仮定
        
        # スコアを0-10の範囲に収める
        final_score = max(0, min(10, base_score))
        
        return final_score
    
    def _generate_evaluation_comment(self, score: int, task_name: str, 
                                   output: str) -> str:
        """
        評価コメントを生成する
        
        Args:
            score: 品質スコア
            task_name: タスク名
            output: 出力内容
            
        Returns:
            str: 評価コメント
        """
        if score >= 9:
            return f"優れた成果: {task_name} - 高品質な出力が得られました"
        elif score >= 7:
            return f"良好な成果: {task_name} - 期待通りの結果です"
        elif score >= 5:
            return f"改善の余地あり: {task_name} - 基本的な要件は満たしています"
        elif score >= 3:
            return f"要改善: {task_name} - 重要な要素が不足しています"
        else:
            return f"不合格: {task_name} - 根本的な見直しが必要です"
    
    def _generate_improvement_suggestions(self, score: int, output: str, 
                                        task_name: str) -> List[str]:
        """
        改善提案を生成する
        
        Args:
            score: 品質スコア
            output: 出力内容
            task_name: タスク名
            
        Returns:
            List[str]: 改善提案のリスト
        """
        suggestions = []
        
        if score < 7:
            if len(output.strip()) < 50:
                suggestions.append("出力をもう少し詳細に記述してください")
            
            if 'error' in output.lower() or 'fail' in output.lower():
                suggestions.append("エラー内容を具体的に分析し、解決策を提示してください")
            
            if score < 5:
                suggestions.append("タスクの要件を再確認してください")
                suggestions.append("別のアプローチを検討してください")
        
        # 高得点の場合もさらなる改善提案
        if score >= 8:
            suggestions.append("この調子で高品質な作業を継続してください")
        
        # デフォルト提案（スコアに関係なく）
        if not suggestions:
            suggestions.append("現在のアプローチを継続してください")
        
        return suggestions
    
    def _determine_evaluation_status(self, score: int) -> str:
        """
        評価状態を決定する
        
        Args:
            score: 品質スコア
            
        Returns:
            str: 評価状態
        """
        if score >= 7:
            return "accepted"
        elif score >= 5:
            return "needs_minor_improvement"
        elif score >= 3:
            return "needs_major_improvement"
        else:
            return "rejected"
    
    def _create_fallback_response(self, message: str, error_type: str) -> Dict[str, Any]:
        """
        評価失敗時のフォールバックレスポンスを作成
        
        Args:
            message: エラーメッセージ
            error_type: エラータイプ
            
        Returns:
            dict: フォールバックレスポンス
        """
        self.logger.warning(f"評価フォールバック: {error_type} - {message}")
        
        return {
            'quality_score': 5,  # 0点ではなく中間値
            'evaluation': message,
            'status': error_type,
            'improvement_suggestions': [
                "評価システムに問題が発生しました",
                "手動での確認を推奨します"
            ],
            'task_name': '評価エラー',
            'agent_name': 'ReviewAgent'
        }
    
    async def batch_evaluate(self, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        複数のタスク結果を一括評価
        
        Args:
            contexts: 評価コンテキストのリスト
            
        Returns:
            List[Dict]: 評価結果のリスト
        """
        tasks = [self.evaluate(context) for context in contexts]
        return await asyncio.gather(*tasks)
    
    def get_evaluation_stats(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        評価統計を計算
        
        Args:
            evaluations: 評価結果のリスト
            
        Returns:
            Dict: 統計情報
        """
        if not evaluations:
            return {
                'total_count': 0,
                'average_score': 0,
                'score_distribution': {},
                'acceptance_rate': 0
            }
        
        scores = [e.get('quality_score', 0) for e in evaluations]
        statuses = [e.get('status', 'unknown') for e in evaluations]
        
        return {
            'total_count': len(evaluations),
            'average_score': sum(scores) / len(scores),
            'score_distribution': {
                'excellent_9_10': len([s for s in scores if s >= 9]),
                'good_7_8': len([s for s in scores if 7 <= s < 9]),
                'fair_5_6': len([s for s in scores if 5 <= s < 7]),
                'poor_3_4': len([s for s in scores if 3 <= s < 5]),
                'failed_0_2': len([s for s in scores if s < 3])
            },
            'acceptance_rate': len([s for s in statuses if s == 'accepted']) / len(statuses) * 100
        }

# 単体テスト用
if __name__ == "__main__":
    async def test_review_agent():
        """ReviewAgentのテスト"""
        agent = ReviewAgent()
        
        # テストケース
        test_cases = [
            {
                'task_name': 'コード生成タスク',
                'task_description': 'Pythonスクリプトを生成',
                'result': {
                    'output': '正常にコードが生成されました。すべてのテストに合格しています。',
                    'status': 'completed'
                },
                'agent_name': 'GeminiAgent'
            },
            {
                'task_name': 'データ分析タスク', 
                'result': {
                    'output': 'エラーが発生しました',
                    'status': 'error'
                },
                'agent_name': 'DataAgent'
            },
            {
                'task_name': None,  # 異常系
                'result': None
            }
        ]
        
        print("=== ReviewAgent テスト開始 ===")
        
        for i, context in enumerate(test_cases):
            print(f"\n--- テストケース {i+1} ---")
            result = await agent.evaluate(context)
            print(f"スコア: {result.get('quality_score')}")
            print(f"評価: {result.get('evaluation')}")
            print(f"状態: {result.get('status')}")
            print(f"改善提案: {result.get('improvement_suggestions')}")
        
        print("\n=== テスト完了 ===")
    
    # テスト実行
    asyncio.run(test_review_agent())

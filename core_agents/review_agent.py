"""
ReviewAgent: タスク実行結果の品質評価
品質スコア（1-10）を算出し、フィードバックを提供
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ReviewAgent:
    """タスク実行結果をレビューし、品質スコアを算出"""
    
    def __init__(self, sheets_wrapper):
        self.sheets = sheets_wrapper
        self.review_criteria = {
            'completeness': 0.3,    # 完成度
            'correctness': 0.3,     # 正確性
            'efficiency': 0.2,      # 効率性
            'maintainability': 0.2  # 保守性
        }
        logger.info("✅ ReviewAgent を初期化しました")
    
    async def review_task(self, task_result: Dict[str, Any]) -> Dict[str, Any]:
        """タスク実行結果をレビュー"""
        try:
            logger.info(f"🔍 タスクレビュー開始: {task_result.get('task_id', 'N/A')}")
            
            # 各基準でスコアリング
            scores = {
                'completeness': self._score_completeness(task_result),
                'correctness': self._score_correctness(task_result),
                'efficiency': self._score_efficiency(task_result),
                'maintainability': self._score_maintainability(task_result)
            }
            
            # 重み付け合計スコア
            total_score = sum(
                score * self.review_criteria[criterion]
                for criterion, score in scores.items()
            )
            
            # フィードバック生成
            feedback = self._generate_feedback(scores, total_score)
            
            review_result = {
                'task_id': task_result.get('task_id', 'N/A'),
                'quality_score': round(total_score, 2),
                'detailed_scores': scores,
                'feedback': feedback,
                'reviewed_at': datetime.now().isoformat(),
                'needs_rework': total_score < 7.0
            }
            
            logger.info(f"✅ レビュー完了: スコア {total_score:.2f}/10")
            return review_result
            
        except Exception as e:
            logger.error(f"❌ レビューエラー: {e}")
            return {
                'task_id': task_result.get('task_id', 'N/A'),
                'quality_score': 5.0,
                'error': str(e)
            }
    
    def _score_completeness(self, task_result: Dict[str, Any]) -> float:
        """完成度スコア（1-10）"""
        status = task_result.get('status', 'unknown')
        output = task_result.get('output', '')
        
        score = 5.0  # ベーススコア
        
        if status == 'completed':
            score += 3.0
        elif status == 'partial':
            score += 1.0
        
        if output and len(output) > 100:
            score += 2.0
        elif output:
            score += 1.0
        
        return min(10.0, score)
    
    def _score_correctness(self, task_result: Dict[str, Any]) -> float:
        """正確性スコア（1-10）"""
        errors = task_result.get('errors', [])
        warnings = task_result.get('warnings', [])
        
        score = 10.0
        
        # エラー・警告でペナルティ
        score -= len(errors) * 2.0
        score -= len(warnings) * 0.5
        
        return max(1.0, score)
    
    def _score_efficiency(self, task_result: Dict[str, Any]) -> float:
        """効率性スコア（1-10）"""
        execution_time = task_result.get('execution_time', 0)
        
        if execution_time == 0:
            return 7.0  # デフォルト
        
        # 実行時間による評価（秒単位）
        if execution_time < 10:
            return 10.0
        elif execution_time < 30:
            return 8.0
        elif execution_time < 60:
            return 6.0
        elif execution_time < 120:
            return 4.0
        else:
            return 2.0
    
    def _score_maintainability(self, task_result: Dict[str, Any]) -> float:
        """保守性スコア（1-10）"""
        # ログの有無、エラーハンドリングなどで評価
        has_logs = bool(task_result.get('logs'))
        has_error_handling = 'error' not in task_result or task_result.get('error_handled', False)
        
        score = 5.0
        
        if has_logs:
            score += 3.0
        if has_error_handling:
            score += 2.0
        
        return score
    
    def _generate_feedback(self, scores: Dict[str, float], total_score: float) -> List[str]:
        """フィードバック生成"""
        feedback = []
        
        if total_score >= 9.0:
            feedback.append("🎉 優秀な品質です！")
        elif total_score >= 7.0:
            feedback.append("✅ 良好な品質です")
        else:
            feedback.append("⚠️ 改善が必要です")
        
        # 各項目の詳細フィードバック
        for criterion, score in scores.items():
            if score < 7.0:
                if criterion == 'completeness':
                    feedback.append(f"- 完成度が低い（{score:.1f}/10）：タスクを完全に完了させてください")
                elif criterion == 'correctness':
                    feedback.append(f"- 正確性に問題（{score:.1f}/10）：エラーや警告を解消してください")
                elif criterion == 'efficiency':
                    feedback.append(f"- 効率性が低い（{score:.1f}/10）：実行時間を短縮してください")
                elif criterion == 'maintainability':
                    feedback.append(f"- 保守性が低い（{score:.1f}/10）：ログやエラーハンドリングを追加してください")
        
        return feedback


class QualityFeedbackLoop:
    """品質フィードバックループ：低品質タスクを自動再実行"""
    
    def __init__(self, review_agent, task_executor):
        self.review_agent = review_agent
        self.task_executor = task_executor
        self.max_retry = 3
        logger.info("✅ QualityFeedbackLoop を初期化しました")
    
    async def process_task_with_feedback(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タスク実行 → レビュー → 必要に応じて再実行"""
        retry_count = 0
        
        while retry_count < self.max_retry:
            logger.info(f"🔄 タスク実行試行 {retry_count + 1}/{self.max_retry}")
            
            # タスク実行
            result = await self.task_executor.execute_single_task(task)
            
            # レビュー
            review = await self.review_agent.review_task(result)
            
            # 品質判定
            if review['quality_score'] >= 7.0:
                logger.info(f"✅ 品質基準クリア: {review['quality_score']:.2f}/10")
                return {**result, 'review': review, 'retry_count': retry_count}
            
            logger.warning(f"⚠️ 品質不足: {review['quality_score']:.2f}/10")
            logger.info(f"📋 フィードバック: {review['feedback']}")
            
            # 改善策を適用してリトライ
            task = self._apply_improvements(task, review)
            retry_count += 1
        
        # 最大リトライ到達
        logger.error(f"❌ 品質基準未達（{self.max_retry}回リトライ）")
        return {
            **result,
            'review': review,
            'retry_count': retry_count,
            'quality_failed': True
        }
    
    def _apply_improvements(self, task: Dict[str, Any], review: Dict[str, Any]) -> Dict[str, Any]:
        """レビューフィードバックに基づいてタスクを改善"""
        improved_task = task.copy()
        
        # フィードバックから改善点を抽出
        scores = review.get('detailed_scores', {})
        
        if scores.get('completeness', 10) < 7.0:
            improved_task['priority'] = 'high'
            improved_task['notes'] = 'タスクを完全に完了させる'
        
        if scores.get('correctness', 10) < 7.0:
            improved_task['validation'] = 'strict'
        
        return improved_task

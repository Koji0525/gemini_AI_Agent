"""
レビューオーケストレーター - 複数エージェントの連携管理
"""
import asyncio
from typing import Dict, List, Optional

class ReviewOrchestrator:
    """レビューエージェントのオーケストレーター"""
    
    def __init__(self, browser):
        self.browser = browser
        from review_agents.specialized_reviewers import (
            ContentReviewAgent, 
            TechnicalFeasibilityReviewer, 
            WordPressImplementationReviewer
        )
        self.content_reviewer = ContentReviewAgent(browser)
        self.tech_reviewer = TechnicalFeasibilityReviewer(browser)
        self.wp_reviewer = WordPressImplementationReviewer(browser)
        
        # レビューエージェントのマッピング
        self.reviewer_mapping = {
            'content_quality': self.content_reviewer.review_content_quality,
            'technical_feasibility': self.tech_reviewer.review_technical_feasibility,
            'wordpress_implementation': self.wp_reviewer.review_wordpress_implementation
        }
    
    async def select_reviewers(self, task_description: str, output: str) -> List[str]:
        """タスクに適したレビューエージェントを選択"""
        description_lower = task_description.lower()
        output_lower = output.lower()
        
        selected_reviewers = ['content_quality']  # 常にコンテンツ品質レビュー
        
        # 技術的内容の検出
        tech_keywords = ['実装', '開発', 'コード', '技術', 'システム', 'API', 'データベース']
        if any(keyword in description_lower for keyword in tech_keywords):
            selected_reviewers.append('technical_feasibility')
        
        # WordPress関連の検出
        wp_keywords = ['wordpress', 'wp', 'プラグイン', 'テーマ', 'カスタム投稿', 'ACF', 'ユーザーロール']
        if any(keyword in description_lower or keyword in output_lower for keyword in wp_keywords):
            selected_reviewers.append('wordpress_implementation')
        
        # 出力内容に基づく追加選択
        if 'function' in output_lower or 'class' in output_lower or 'コード' in output_lower:
            if 'technical_feasibility' not in selected_reviewers:
                selected_reviewers.append('technical_feasibility')
        
        print(f"🎯 選択されたレビューエージェント: {selected_reviewers}")
        return selected_reviewers
    
    async def execute_reviews(self, task_description: str, output: str, 
                           specific_reviewers: List[str] = None) -> Dict:
        """選択されたレビューエージェントを実行"""
        try:
            # レビューアーを選択
            if specific_reviewers:
                reviewers_to_run = specific_reviewers
            else:
                reviewers_to_run = await self.select_reviewers(task_description, output)
            
            print(f"🔍 {len(reviewers_to_run)}件のレビューを実行中...")
            
            # 並列でレビュー実行
            review_tasks = []
            for reviewer_type in reviewers_to_run:
                if reviewer_type in self.reviewer_mapping:
                    review_func = self.reviewer_mapping[reviewer_type]
                    task = review_func(task_description, output)
                    review_tasks.append(task)
            
            # すべてのレビューを実行
            review_results = await asyncio.gather(*review_tasks, return_exceptions=True)
            
            # 結果を整理
            valid_reviews = []
            for i, result in enumerate(review_results):
                reviewer_type = reviewers_to_run[i]
                if isinstance(result, Exception):
                    print(f"❌ {reviewer_type} レビューエラー: {result}")
                    valid_reviews.append({
                        "reviewer_type": reviewer_type,
                        "score": 5,
                        "error": str(result),
                        "status": "failed"
                    })
                else:
                    result["status"] = "completed"
                    valid_reviews.append(result)
            
            # 総合評価を計算
            final_score = self._calculate_final_score(valid_reviews)
            overall_rating = self._get_overall_rating(final_score)
            
            return {
                "success": True,
                "final_score": final_score,
                "overall_rating": overall_rating,
                "reviewers_used": reviewers_to_run,
                "detailed_reviews": valid_reviews,
                "summary": self._generate_summary(valid_reviews, final_score)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"レビューオーケストレーションエラー: {e}",
                "final_score": 5,
                "overall_rating": "エラー"
            }
    
    def _calculate_final_score(self, reviews: List[Dict]) -> float:
        """レビュー結果から最終スコアを計算"""
        if not reviews:
            return 5.0
        
        valid_scores = []
        weights = {
            'content_quality': 1.0,
            'technical_feasibility': 0.8,
            'wordpress_implementation': 0.9
        }
        
        for review in reviews:
            if review.get('status') == 'completed' and 'score' in review:
                reviewer_type = review.get('reviewer_type')
                weight = weights.get(reviewer_type, 0.5)
                valid_scores.append(review['score'] * weight)
        
        if not valid_scores:
            return 5.0
        
        weighted_avg = sum(valid_scores) / sum(weights.get(r.get('reviewer_type'), 0.5) 
                                            for r in reviews if r.get('status') == 'completed')
        return round(weighted_avg, 1)
    
    def _get_overall_rating(self, score: float) -> str:
        """スコアから総合評価を決定"""
        if score >= 9.0:
            return "優秀"
        elif score >= 7.5:
            return "良好"
        elif score >= 6.0:
            return "平均"
        elif score >= 4.0:
            return "要改善"
        else:
            return "不合格"
    
    def _generate_summary(self, reviews: List[Dict], final_score: float) -> str:
        """レビュー結果のサマリーを生成"""
        summary = f"総合評価: {final_score}/10\n\n"
        
        # 各レビューアーの結果
        for review in reviews:
            if review.get('status') == 'completed':
                reviewer_type = review.get('reviewer_type', 'unknown')
                score = review.get('score', 0)
                
                summary += f"【{reviewer_type}】\n"
                summary += f"スコア: {score}/10\n"
                
                # 改善点があれば表示
                improvements = review.get('improvements_needed') or review.get('technical_issues') or review.get('wordpress_issues')
                if improvements and len(improvements) > 0 and improvements[0] != "特筆すべき技術的問題は見つかりませんでした":
                    summary += "主な改善点:\n"
                    for i, issue in enumerate(improvements[:3], 1):
                        summary += f"  {i}. {issue}\n"
                
                summary += "\n"
        
        return summary
    
    async def get_detailed_quality_evaluation(self, reviews_result: Dict) -> str:
        """詳細な品質評価テキストを生成"""
        if not reviews_result.get('success'):
            return "レビュー処理に失敗しました"
        
        final_score = reviews_result['final_score']
        overall_rating = reviews_result['overall_rating']
        detailed_reviews = reviews_result['detailed_reviews']
        
        evaluation = f"総合品質評価: {final_score}/10 ({overall_rating})\n\n"
        
        for review in detailed_reviews:
            if review.get('status') == 'completed':
                reviewer_type = review.get('reviewer_type')
                score = review.get('score')
                
                evaluation += f"=== {reviewer_type} レビュー ===\n"
                evaluation += f"スコア: {score}/10\n"
                
                # 長所
                strengths = review.get('strengths', [])
                if strengths:
                    evaluation += "✅ 長所:\n"
                    for strength in strengths[:2]:
                        evaluation += f"  • {strength}\n"
                
                # 改善点
                improvements = (review.get('improvements_needed') or 
                              review.get('technical_issues') or 
                              review.get('wordpress_issues', []))
                if improvements and improvements[0] != "特筆すべき技術的問題は見つかりませんでした":
                    evaluation += "❌ 改善点:\n"
                    for improvement in improvements[:3]:
                        evaluation += f"  • {improvement}\n"
                
                # 評価根拠
                rationale = review.get('rationale')
                if rationale and rationale != ["レビュー処理中にエラーが発生"]:
                    evaluation += f"📊 評価根拠: {rationale[0] if isinstance(rationale, list) else rationale}\n"
                
                evaluation += "\n"
        
        return evaluation


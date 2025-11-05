"""
品質スコア評価のヘルパークラス
ReviewAgentの簡易版
"""

class QualityScorer:
    """品質スコア評価"""
    
    @staticmethod
    def score_task_output(output, task_description):
        """タスク出力の品質スコアを計算"""
        if not output:
            return 0, "出力なし"
        
        # 簡易的なスコアリングロジック
        score = 7  # 基本スコア
        description = "合格"
        
        # 出力の長さチェック
        output_str = str(output)
        if len(output_str) > 100:
            score += 1
            description = "十分な出力"
        
        # エラーの有無
        if "error" in output_str.lower() or "failed" in output_str.lower():
            score -= 2
            description = "エラーあり"
        
        # 成功の明示
        if "success" in output_str.lower() or "completed" in output_str.lower():
            score += 1
            description = "成功"
        
        # スコアの範囲制限
        score = max(0, min(10, score))
        
        return score, description


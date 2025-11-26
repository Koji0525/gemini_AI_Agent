#!/usr/bin/env python3
"""
フィードバック生成システム

目的: Criticエージェントの評価結果を、実行可能な改善提案に変換

変換例:
- 「詳細度が低い」→ 「以下の3つの具体例を追加してください: 1) ..., 2) ..., 3) ...」
- 「構造性が低い」→ 「以下の見出し構造を使用してください: ## 概要, ## 分析, ## 結論」
"""

from typing import Dict, List

class FeedbackGenerator:
    """
    フィードバック生成システム
    
    責務:
    - 評価結果を実行可能な改善提案に変換
    - 優先度付け
    - 具体的な例示
    """
    
    def __init__(self):
        """初期化"""
        pass
    
    def generate_actionable_feedback(
        self,
        scores: Dict[str, int],
        original_feedback: str
    ) -> str:
        """
        実行可能なフィードバックを生成
        
        Args:
            scores: カテゴリ別スコア
            original_feedback: Criticからの元フィードバック
        
        Returns:
            実行可能なフィードバック文字列
        """
        suggestions = []
        
        # スコアが低いカテゴリに対して提案生成
        if scores.get('completeness', 25) < 20:
            suggestions.append(self._suggest_completeness())
        
        if scores.get('accuracy', 25) < 20:
            suggestions.append(self._suggest_accuracy())
        
        if scores.get('detail', 25) < 20:
            suggestions.append(self._suggest_detail())
        
        if scores.get('structure', 25) < 20:
            suggestions.append(self._suggest_structure())
        
        # フィードバック統合
        feedback = "# 改善提案（優先度順）\n\n"
        for i, suggestion in enumerate(suggestions, 1):
            feedback += f"## {i}. {suggestion['title']}\n\n"
            feedback += f"{suggestion['description']}\n\n"
            if 'examples' in suggestion:
                feedback += "**例:**\n"
                for example in suggestion['examples']:
                    feedback += f"- {example}\n"
                feedback += "\n"
        
        # 元のフィードバックも追加
        feedback += f"---\n\n**Criticからの詳細評価:**\n{original_feedback}\n"
        
        return feedback
    
    def _suggest_completeness(self) -> Dict:
        """完全性の改善提案"""
        return {
            'title': '完全性の向上',
            'description': '以下の要素を追加して、完全な分析にしてください：',
            'examples': [
                '背景情報: なぜこのトピックが重要か',
                'データ収集方法: どのようにデータを集めたか',
                '制約事項: 分析の限界や前提条件',
                '今後の課題: 次に取り組むべきこと'
            ]
        }
    
    def _suggest_accuracy(self) -> Dict:
        """正確性の改善提案"""
        return {
            'title': '正確性の向上',
            'description': 'データの信頼性を高めるため、以下を追加してください：',
            'examples': [
                '出典の明記: 「〜によると」「〜のデータでは」',
                '検証方法: どのように正確性を確認したか',
                '更新日時: データの鮮度を示す',
                '信頼区間: 数値の誤差範囲を記載'
            ]
        }
    
    def _suggest_detail(self) -> Dict:
        """詳細度の改善提案"""
        return {
            'title': '詳細度の向上',
            'description': '抽象的な表現を具体的にしてください：',
            'examples': [
                '「大きく変動した」→「3%上昇し、52週ぶりの高値」',
                '「多くの企業」→「Fortune 500の78%（390社）」',
                '「最近」→「2025年11月26日時点」',
                '具体例を3つ以上追加'
            ]
        }
    
    def _suggest_structure(self) -> Dict:
        """構造性の改善提案"""
        return {
            'title': '構造性の向上',
            'description': '以下の構造を使って整理してください：',
            'examples': [
                '見出し: # 大見出し、## 中見出し、### 小見出し',
                '箇条書き: - 項目1、- 項目2',
                '表: | 項目 | 値 | を使った比較表',
                '図: グラフや図解の追加（プレースホルダーでも可）'
            ]
        }

# ========================================
# テスト
# ========================================
if __name__ == "__main__":
    print("="*60)
    print("💬 フィードバック生成システム テスト")
    print("="*60)
    
    generator = FeedbackGenerator()
    
    # テストスコア
    test_scores = {
        'completeness': 15,
        'accuracy': 18,
        'detail': 12,
        'structure': 10
    }
    
    # フィードバック生成
    feedback = generator.generate_actionable_feedback(
        scores=test_scores,
        original_feedback="全体的に改善の余地があります。"
    )
    
    print("\n生成されたフィードバック:")
    print("="*60)
    print(feedback)
    print("="*60)
    print("\n✅ テスト完了")

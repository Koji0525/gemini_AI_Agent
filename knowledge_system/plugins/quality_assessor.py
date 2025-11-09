#!/usr/bin/env python3
from knowledge_system.core.plugin_base import BasePlugin

class QualityassessorPlugin(BasePlugin):
    """ナレッジ品質評価プラグイン"""
    
    def execute(self, title, content, tags, category):
        """ナレッジの品質を評価"""
        score = 0
        
        # タイトルの長さ
        if len(title) >= 10:
            score += 20
        
        # 内容の長さ
        if len(content) >= 50:
            score += 30
        
        # タグの存在
        if tags and len(tags.split(',')) >= 2:
            score += 20
        
        # カテゴリの適切さ
        if category != 'general':
            score += 30
        
        quality_level = "高" if score >= 80 else "中" if score >= 60 else "低"
        
        return {
            'score': score,
            'level': quality_level,
            'feedback': self._generate_feedback(score, title, content, tags, category)
        }
    
    def _generate_feedback(self, score, title, content, tags, category):
        """品質フィードバックを生成"""
        feedback = []
        
        if len(title) < 10:
            feedback.append("タイトルをもう少し具体的にすると検索されやすくなります")
        
        if len(content) < 50:
            feedback.append("内容を充実させるとより役立つナレッジになります")
        
        if not tags or len(tags.split(',')) < 2:
            feedback.append("タグを追加すると検索精度が向上します")
        
        if category == 'general':
            feedback.append("具体的なカテゴリを設定すると整理しやすくなります")
        
        return feedback if feedback else ["良好な品質です"]

# テスト
if __name__ == "__main__":
    plugin = QualityassessorPlugin()
    result = plugin.execute(
        "テストタイトル",
        "これはテスト内容です。十分な長さがあるか確認します。",
        "テスト,品質",
        "technology"
    )
    print(f"品質評価結果: {result}")

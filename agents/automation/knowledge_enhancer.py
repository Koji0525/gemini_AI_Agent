"""
ナレッジ高品質化エンジン
Gemini APIを使って実践的なナレッジに変換
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.gemini_api import GeminiAPI
from tools.knowledge_templates import get_template

class KnowledgeEnhancer:
    """ナレッジ高品質化エンジン"""
    
    def __init__(self):
        self.gemini = GeminiAPI()
    
    def enhance_knowledge(self, raw_content: str, task_context: dict) -> dict:
        """
        生のコンテンツを実践的なナレッジに変換
        
        Args:
            raw_content: 生のコンテンツ
            task_context: タスクコンテキスト（task_id, output_path, quality_scoreなど）
        
        Returns:
            enhanced_knowledge: 高品質化されたナレッジ
        """
        
        # Geminiプロンプト構築
        prompt = self._build_enhancement_prompt(raw_content, task_context)
        
        # Gemini APIで高品質化
        enhanced_content = self.gemini.generate_content(prompt)
        
        # 品質チェック
        quality_score = self._assess_quality(enhanced_content)
        
        return {
            'content': enhanced_content,
            'quality_score': quality_score,
            'original_content': raw_content,
            'enhanced_at': datetime.now().isoformat()
        }
    
    def _build_enhancement_prompt(self, raw_content: str, context: dict) -> str:
        """高品質化プロンプト構築"""
        
        prompt = f"""
あなたは優秀な技術ドキュメントライターです。
以下の生のコンテンツを、後で使える実践的なナレッジに変換してください。

# 生のコンテンツ
{raw_content}

# タスクコンテキスト
- タスクID: {context.get('task_id', 'unknown')}
- 品質スコア: {context.get('quality_score', 0)}/10
- 出力パス: {context.get('output_path', 'unknown')}

# 変換要件

## 必須要素
1. **問題・課題**: どんな問題を解決するのか？
2. **解決策**: どうやって解決するのか？
3. **コード例**: 実際に使えるコード（最も重要な部分のみ）
4. **使用場面**: どんな時に使うのか？
5. **学び**: このナレッジから何を学べるか？

## フォーマット
````markdown
# [タイトル]

## 📋 概要
簡潔な説明（1-2行）

## ❓ 問題・課題
具体的な問題の説明

## ✅ 解決策
解決方法の説明

## 💡 実装方法

### 主要コード
```python
# 最も重要な部分のみ（10-30行）
def example():
    pass
```

### 説明
コードの説明

## 🎯 使用場面
- 場面1: ...
- 場面2: ...

## 🎓 学び
このナレッジから得られる重要な学び

## 🔗 関連知識
- 関連技術1
- 関連技術2
````

## 重要な指針
- **実践的**: 後で実際に使えること
- **簡潔**: 無駄な情報は省く
- **コード優先**: 説明よりコード例を重視
- **再利用可能**: コピペですぐ使える
- **検索可能**: キーワードを適切に含める

変換後のMarkdownを出力してください。
"""
        
        return prompt
    
    def _assess_quality(self, content: str) -> float:
        """品質評価"""
        
        quality_criteria = {
            'has_problem': '問題' in content or '課題' in content,
            'has_solution': '解決' in content,
            'has_code': '```' in content,
            'has_use_case': '使用' in content or '場面' in content,
            'has_learning': '学び' in content or 'ポイント' in content,
            'sufficient_length': len(content) > 500,
            'has_structure': '##' in content
        }
        
        score = sum(quality_criteria.values()) / len(quality_criteria) * 10
        
        return round(score, 1)
    
    def batch_enhance(self, knowledge_list: list) -> list:
        """一括高品質化"""
        
        enhanced_list = []
        
        for knowledge in knowledge_list:
            try:
                enhanced = self.enhance_knowledge(
                    knowledge['content'],
                    knowledge.get('context', {})
                )
                enhanced_list.append(enhanced)
            except Exception as e:
                print(f"  ⚠️  高品質化エラー: {e}")
                continue
        
        return enhanced_list


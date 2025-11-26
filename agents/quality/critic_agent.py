#!/usr/bin/env python3
"""
Criticエージェント（批評家エージェント）

目的: タスク実行結果を批評的に評価し、具体的な改善提案を生成
モデル: Gemini 2.0 Flash（高速・低コスト）

品質評価基準（100点満点）:
- 完全性 (25点): すべての要件を満たしているか
- 正確性 (25点): データが正確で検証可能か
- 詳細度 (25点): 具体例や数値が豊富か
- 構造性 (25点): 見出しや箇条書きで整理されているか
"""

import json
import os
from typing import Dict, List, Tuple
from pathlib import Path

# Gemini APIインポート
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️  google-generativeai がインストールされていません")

class CriticAgent:
    """
    批評家エージェント
    
    責務:
    - タスク実行結果の品質評価（0-100点）
    - 具体的な改善提案の生成
    - 強み・弱みの分析
    
    使用例:
        critic = CriticAgent()
        
        score, feedback = critic.evaluate(
            task_result={
                'description': '金融市場分析',
                'output': 'レポート内容...'
            }
        )
    """
    
    # 品質評価基準
    QUALITY_RUBRIC = {
        'completeness': {
            'name': '完全性',
            'max_score': 25,
            'criteria': {
                25: 'すべての要件を満たし、追加情報も提供',
                15: '主要な要件は満たすが、一部不足',
                10: '部分的に要件を満たす',
                5: 'ほとんど要件を満たしていない'
            }
        },
        'accuracy': {
            'name': '正確性',
            'max_score': 25,
            'criteria': {
                25: 'データが正確で出典が明記されている',
                15: 'データはあるが検証が不十分',
                10: 'データの正確性が疑わしい',
                5: 'データがないか明らかに間違い'
            }
        },
        'detail': {
            'name': '詳細度',
            'max_score': 25,
            'criteria': {
                25: '具体例、数値、図表が豊富',
                15: 'いくつかの具体例あり',
                10: '抽象的な説明のみ',
                5: '非常に曖昧'
            }
        },
        'structure': {
            'name': '構造性',
            'max_score': 25,
            'criteria': {
                25: '見出し、箇条書き、図表で整理',
                15: '見出しのみ使用',
                10: '段落のみ',
                5: '構造がない'
            }
        }
    }
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        初期化
        
        Args:
            model_name: 使用するGeminiモデル
        """
        self.model_name = model_name
        self.model = None
        
        # Gemini API初期化
        if GENAI_AVAILABLE:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ Criticエージェント初期化: {model_name}")
            else:
                print("⚠️  GEMINI_API_KEY が設定されていません")
        
        # ダミーモード（API未設定時）
        self.dummy_mode = self.model is None
        if self.dummy_mode:
            print("🤖 ダミーモードで動作します")
    
    def evaluate(
        self,
        task_result: Dict,
        task_requirements: Dict = None
    ) -> Tuple[int, str]:
        """
        タスク実行結果を評価
        
        Args:
            task_result: タスク実行結果
            task_requirements: タスク要件（オプション）
        
        Returns:
            (品質スコア, フィードバック文字列)
        """
        if self.dummy_mode:
            return self._dummy_evaluate(task_result)
        
        # Gemini APIで評価
        return self._evaluate_with_gemini(task_result, task_requirements)
    
    def _evaluate_with_gemini(
        self,
        task_result: Dict,
        task_requirements: Dict = None
    ) -> Tuple[int, str]:
        """
        Gemini APIを使って評価
        
        Args:
            task_result: タスク実行結果
            task_requirements: タスク要件
        
        Returns:
            (品質スコア, フィードバック)
        """
        # プロンプト構築
        prompt = self._build_evaluation_prompt(task_result, task_requirements)
        
        try:
            # Gemini API呼び出し
            response = self.model.generate_content(prompt)
            
            # レスポンスをパース
            score, feedback = self._parse_gemini_response(response.text)
            
            return score, feedback
            
        except Exception as e:
            print(f"⚠️  Gemini API エラー: {e}")
            return self._dummy_evaluate(task_result)
    
    def _build_evaluation_prompt(
        self,
        task_result: Dict,
        task_requirements: Dict = None
    ) -> str:
        """評価プロンプトを構築"""
        
        prompt = f"""
あなたは厳格な品質評価者です。以下のタスク実行結果を客観的に評価してください。

# 評価基準（100点満点）

1. **完全性（25点）**
   - すべての要件を満たしているか
   - 25点: すべて満たし追加情報も提供
   - 15点: 主要な要件は満たすが一部不足
   - 10点: 部分的に要件を満たす
   - 5点: ほとんど満たしていない

2. **正確性（25点）**
   - データが正確で検証可能か
   - 25点: 正確で出典が明記
   - 15点: データはあるが検証不十分
   - 10点: 正確性が疑わしい
   - 5点: データがないか明らかに間違い

3. **詳細度（25点）**
   - 具体例や数値が豊富か
   - 25点: 具体例、数値、図表が豊富
   - 15点: いくつかの具体例あり
   - 10点: 抽象的な説明のみ
   - 5点: 非常に曖昧

4. **構造性（25点）**
   - 見出しや箇条書きで整理されているか
   - 25点: 見出し、箇条書き、図表で整理
   - 15点: 見出しのみ使用
   - 10点: 段落のみ
   - 5点: 構造がない

# タスク実行結果
```
{json.dumps(task_result, indent=2, ensure_ascii=False)}
```

# 出力形式

以下のJSON形式で出力してください：
```json
{{
  "total_score": 85,
  "scores": {{
    "completeness": 20,
    "accuracy": 22,
    "detail": 23,
    "structure": 20
  }},
  "feedback": "以下の点を改善してください：\\n1. データの出典を明記\\n2. 具体例を3つ追加\\n3. 図表を使って可視化",
  "strengths": ["構造が整理されている", "主要なポイントを網羅"],
  "weaknesses": ["具体例が少ない", "出典がない"]
}}
```

厳しく評価してください。80点以上は本当に優れた成果物のみです。
"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Tuple[int, str]:
        """Geminiのレスポンスをパース"""
        try:
            # JSONブロックを抽出
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                score = data.get('total_score', 0)
                feedback = data.get('feedback', '')
                
                return score, feedback
            else:
                # JSONが見つからない場合
                return 60, response_text
                
        except Exception as e:
            print(f"⚠️  レスポンスパースエラー: {e}")
            return 60, response_text
    
    def _dummy_evaluate(self, task_result: Dict) -> Tuple[int, str]:
        """
        ダミー評価（API未設定時）
        
        実際の実装では、出力の長さや構造を簡易分析
        """
        output = task_result.get('output', '')
        
        # 簡易評価ロジック
        score = 60  # ベーススコア
        
        # 長さによる加点
        if len(output) > 500:
            score += 5
        if len(output) > 1000:
            score += 5
        
        # 構造による加点（見出しや箇条書き）
        if '#' in output or '-' in output:
            score += 5
        
        # 数値による加点
        import re
        numbers = re.findall(r'\d+', output)
        if len(numbers) > 5:
            score += 5
        
        feedback = f"""
【ダミー評価モード】

現在のスコア: {score}点

改善提案:
1. より具体的な数値やデータを追加してください
2. 見出しや箇条書きを使って構造化してください
3. 出典や根拠を明記してください
4. 図表や可視化を追加してください

このメッセージはGemini APIが未設定のため表示されています。
GEMINI_API_KEYを設定すると、AIによる詳細な評価が可能になります。
"""
        
        return score, feedback
    
    def get_rubric(self) -> Dict:
        """評価基準を取得"""
        return self.QUALITY_RUBRIC

# ========================================
# テスト
# ========================================
if __name__ == "__main__":
    print("="*60)
    print("🤔 Criticエージェント テスト")
    print("="*60)
    
    # インスタンス作成
    critic = CriticAgent()
    
    # テストタスク結果
    test_result = {
        'description': '金融市場分析レポート作成',
        'output': '''
# 金融市場分析レポート

## 概要
2025年11月の金融市場は、AI技術の進展により大きな変動がありました。

## 主要な動き
- 株式市場: S&P 500が3%上昇
- 為替市場: ドル円が145円から148円に
- 債券市場: 10年債利回りが4.2%に

## 今後の見通し
引き続き注視が必要です。
'''
    }
    
    # 評価実行
    print("\n📊 評価実行中...")
    score, feedback = critic.evaluate(test_result)
    
    print(f"\n✅ 評価完了")
    print(f"\n品質スコア: {score}点")
    print(f"\nフィードバック:\n{feedback}")
    
    print("\n" + "="*60)
    print("✅ テスト完了")
    print("="*60)

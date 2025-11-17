#!/usr/bin/env python3
"""
AI駆動型コード生成
Claude APIを使って実際に動くコードを生成
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

import os
from anthropic import Anthropic
from typing import Dict, Any


class AICodeGenerator:
    """Claude APIを使った高品質コード生成"""
    
    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = Anthropic(api_key=api_key)
    
    def generate_code(self, task_id: str, filename: str, details: Dict[str, Any]) -> str:
        """
        詳細情報からClaude APIで高品質コードを生成
        """
        prompt = f"""あなたはPythonコード生成の専門家です。以下の要件に基づいて、実際に動作する高品質なPythonコードを生成してください。

# タスク情報
タスクID: {task_id}
ファイル名: {filename}

# 目的
{details['purpose']}

# 実装内容
{details['overview']}

# 成功基準
{details['success_criteria']}

# コンテキスト情報
{details['context']}

# 生成要件
1. 実際に動作するコードを生成（スケルトンではなく実装を含める）
2. 成功基準を満たすために必要なメソッドをすべて実装
3. 適切なエラーハンドリングを含める
4. 詳細なdocstringを記述
5. type hintsを使用
6. 100-150行程度の充実したコード

# 出力形式
Pythonコードのみを出力してください。説明文は不要です。
コードブロックのマークダウン記法（```python）も不要です。
"""
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            code = response.content[0].text
            
            # マークダウンのコードブロックを除去
            if code.startswith('```python'):
                code = code.split('```python')[1]
                code = code.split('```')[0]
            elif code.startswith('```'):
                code = code.split('```')[1]
                code = code.split('```')[0]
            
            return code.strip()
        
        except Exception as e:
            print(f"⚠️ API呼び出しエラー: {e}")
            print(f"   フォールバック: テンプレートベース生成")
            return self._generate_fallback_code(task_id, filename, details)
    
    def _generate_fallback_code(self, task_id: str, filename: str, details: Dict) -> str:
        """APIエラー時のフォールバック"""
        class_name = ''.join(word.capitalize() for word in filename.replace('.py', '').split('_'))
        
        return f'''#!/usr/bin/env python3
"""
{filename}
タスクID: {task_id}

目的: {details['purpose']}
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')


class {class_name}:
    """
    {details['purpose']}
    """
    
    def __init__(self):
        """初期化"""
        pass
    
    def execute(self):
        """メイン処理"""
        # TODO: 実装
        pass


if __name__ == '__main__':
    instance = {class_name}()
    instance.execute()
'''


if __name__ == '__main__':
    # テスト
    generator = AICodeGenerator()
    
    test_details = {
        'purpose': '自己修復機能の基盤を実装',
        'overview': 'エラーパターン5個を定義し、自動修復ロジックを実装',
        'success_criteria': '5エラーパターン定義、修復ロジック実装、修復成功率80%以上',
        'context': '既存TaskExecutor、エラーログ、修復戦略DB'
    }
    
    code = generator.generate_code('475', 'self_healing_engine.py', test_details)
    print(code)
    print(f"\n生成コード行数: {len(code.splitlines())}")

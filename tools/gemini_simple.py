"""
シンプルなGemini APIラッパー
"""

import os
import google.generativeai as genai

class GeminiSimple:
    """シンプルなGemini APIクライアント"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY環境変数が設定されていません")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate(self, prompt: str, max_retries: int = 3) -> str:
        """テキスト生成"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  ⚠️  リトライ ({attempt + 1}/{max_retries})")
                    continue
                else:
                    raise e


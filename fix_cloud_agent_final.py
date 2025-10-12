#!/usr/bin/env python3
"""CloudFixAgent の API キー読み込みを修正"""
from pathlib import Path

file = Path('fix_agents/cloud_fix_agent.py')
content = file.read_text()

# _init_api_client の前に .env 読み込みを追加
old_init = '''    def _init_api_client(self):
        """APIクライアントを初期化"""
        if self.api_provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)'''

new_init = '''    def _init_api_client(self):
        """APIクライアントを初期化"""
        # .env から API キーを読み込む
        import os
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # API キーが設定されていない場合は環境変数から取得
        if not self.api_key:
            self.api_key = os.getenv('OPENAI_API_KEY')
        
        if self.api_provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)'''

if old_init in content:
    content = content.replace(old_init, new_init)
    file.write_text(content)
    print("✅ CloudFixAgent の API キー読み込みを追加")
else:
    print("⚠️ 該当箇所が見つかりません")

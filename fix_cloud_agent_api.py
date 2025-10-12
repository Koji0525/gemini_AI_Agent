#!/usr/bin/env python3
from pathlib import Path

file = Path('fix_agents/cloud_fix_agent.py')
content = file.read_text()

# API キー取得部分を強化
old_init = '''    def _init_api_client(self):
        """API クライアントの初期化"""
        if not self.api_key:
            raise ValueError("API キーが設定されていません")
        
        self.client = openai.OpenAI(api_key=self.api_key)'''

new_init = '''    def _init_api_client(self):
        """API クライアントの初期化"""
        import os
        from dotenv import load_dotenv
        
        # .env ファイルから再読み込み
        load_dotenv(override=True)
        
        # API キーの取得（優先順位: 引数 > 環境変数 > .env）
        if not self.api_key:
            self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY が設定されていません")
        
        self.client = openai.OpenAI(api_key=self.api_key)'''

if old_init in content:
    content = content.replace(old_init, new_init)
    file.write_text(content)
    print("✅ CloudFixAgent の API キー読み込みを強化")
else:
    print("⚠️ 該当箇所が見つかりません")

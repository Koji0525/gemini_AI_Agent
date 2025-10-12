#!/usr/bin/env python3
"""Claude API 接続テスト"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import anthropic
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY が設定されていません")
        exit(1)
    
    print(f"🔑 APIキー: {api_key[:15]}...")
    print("🔄 Claude API に接続中...")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # テストメッセージ
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": "こんにちは。接続テストです。簡潔に応答してください。"
        }]
    )
    
    print("✅ 接続成功！")
    print(f"応答: {message.content[0].text}")
    
except Exception as e:
    print(f"❌ エラー: {e}")

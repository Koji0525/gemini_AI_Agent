#!/usr/bin/env python3
"""
ReviewAgent の Gemini 初期化を修正
"""
import os
from pathlib import Path

# review_agent.py を確認
review_agent_path = Path('review_agent.py')

if not review_agent_path.exists():
    print("❌ review_agent.py が見つかりません")
    exit(1)

# 内容を読み込む
with open(review_agent_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Gemini API key の設定箇所を探す
print("🔍 Gemini 初期化コードを確認中...")

# __init__ メソッドを探す
import re
init_match = re.search(r'def __init__\(self\):.*?(?=\n    def |\n\nclass |\Z)', content, re.DOTALL)

if init_match:
    print("✅ __init__ メソッドを発見")
    print("\n📝 初期化コード:")
    print(init_match.group()[:500])
    print("...")
    
    # GEMINI_API_KEY の確認
    if 'GEMINI_API_KEY' in content:
        print("\n✅ GEMINI_API_KEY が参照されています")
        
        # 環境変数が設定されているか確認
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            print(f"✅ 環境変数 GEMINI_API_KEY: 設定済み（{len(api_key)}文字）")
        else:
            print("❌ 環境変数 GEMINI_API_KEY: 未設定")
            print("\n💡 修正方法:")
            print("   export GEMINI_API_KEY='your_api_key_here'")
            print("   または")
            print("   echo 'export GEMINI_API_KEY=\"your_key\"' >> ~/.bashrc")
    
    # send_prompt メソッドを探す
    if 'send_prompt' in content:
        print("\n✅ send_prompt メソッドが存在します")
        
        # self.ai または self.gemini_client などの初期化を確認
        ai_patterns = ['self.ai =', 'self.gemini', 'self.client =', 'GeminiClient']
        found_patterns = []
        for pattern in ai_patterns:
            if pattern in content:
                found_patterns.append(pattern)
        
        if found_patterns:
            print(f"✅ AI クライアント初期化: {', '.join(found_patterns)}")
        else:
            print("⚠️ AI クライアント初期化が見つかりません")
    else:
        print("⚠️ send_prompt メソッドが見つかりません")

print("\n" + "=" * 80)
print("📋 推奨修正:")
print("=" * 80)
print("1. GEMINI_API_KEY 環境変数を設定")
print("2. review_agent.py の __init__ で self.ai を初期化")
print("3. send_prompt が self.ai を参照していることを確認")

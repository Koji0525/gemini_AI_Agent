#!/usr/bin/env python3
"""Claude API 自動化システムのセットアップ"""
import os
from pathlib import Path

print("🤖 Claude API 自動化システム セットアップ")
print("=" * 60)

# 1. Anthropic SDK の確認/インストール
try:
    import anthropic
    print("✅ Anthropic SDK インストール済み")
except ImportError:
    print("📦 Anthropic SDK をインストール中...")
    os.system("pip install anthropic")
    print("✅ インストール完了")

# 2. .env に ANTHROPIC_API_KEY を追加
env_file = Path('.env')
env_content = env_file.read_text() if env_file.exists() else ""

if 'ANTHROPIC_API_KEY' not in env_content:
    print("\n⚠️  ANTHROPIC_API_KEY が .env に見つかりません")
    print("既に環境変数に設定されているか確認します...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"✅ 環境変数から取得: {api_key[:10]}...")
        # .env に追加
        with open('.env', 'a') as f:
            f.write(f"\n\n# Claude API\nANTHROPIC_API_KEY={api_key}\n")
        print("✅ .env に追加しました")
    else:
        print("\n❌ ANTHROPIC_API_KEY が見つかりません")
        print("設定方法:")
        print("  1. https://console.anthropic.com/ でAPIキーを取得")
        print("  2. .env に追加: ANTHROPIC_API_KEY=sk-ant-...")
else:
    print("✅ ANTHROPIC_API_KEY は既に設定済み")

print("\n" + "=" * 60)
print("✅ セットアップ完了")
print("\n次のステップ:")
print("  python test_claude_api.py  # 接続テスト")

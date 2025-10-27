#!/bin/bash

# 既存の .env を確認
if [ -f .env ]; then
    echo "📝 .env ファイルが存在します。更新します..."
else
    echo "📝 新しい .env ファイルを作成します..."
fi

# APIキーを追加（既存の環境変数から）
cat >> .env << ENVEOF

# API Keys
OPENAI_API_KEY=${OPENAI_API_KEY}
GEMINI_API_KEY=${GEMINI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# Browser Settings
BROWSER_DATA_DIR=browser_data
ENVEOF

echo "✅ .env ファイルを更新しました"
cat .env

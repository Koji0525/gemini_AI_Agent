#!/bin/bash
echo "🔍 緊急診断"
echo "="

echo "1. 最新ログ確認:"
if [ -f "logs/unified_conversation.log" ]; then
    echo "📋 unified_conversation.log:"
    tail -50 logs/unified_conversation.log
else
    echo "❌ ログファイルなし"
fi

echo ""
echo "2. 最新Claude応答:"
latest_response=$(ls -t claude_response_*.txt 2>/dev/null | head -1)
if [ -n "$latest_response" ]; then
    echo "📄 $latest_response:"
    cat "$latest_response"
else
    echo "❌ 応答ファイルなし"
fi

echo ""
echo "3. プロセス確認:"
ps aux | grep -E "python.*claude|python.*web_dashboard" | grep -v grep

echo ""
echo "4. API接続テスト:"
python test_claude_api.py

echo ""
echo "5. カスタム指示ファイル:"
if [ -f "CUSTOM_INSTRUCTION.txt" ]; then
    echo "✅ 存在:"
    cat CUSTOM_INSTRUCTION.txt
else
    echo "❌ なし"
fi

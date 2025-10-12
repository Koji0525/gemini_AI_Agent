#!/bin/bash
echo "=" 
echo "🧪 完全フローテスト"
echo "="

# 1. 古いプロセスを停止
echo "🛑 古いプロセスを停止..."
pkill -f web_dashboard
pkill -f claude_unified

# 2. ログをクリア
echo "🗑️ ログをクリア..."
mkdir -p logs
> logs/unified_conversation.log
> logs/unified_debug.log

# 3. テスト用カスタム指示を作成
echo "📝 テスト用カスタム指示を作成..."
cat > CUSTOM_INSTRUCTION.txt << 'INSTRUCTION'
プロジェクトのファイル構造を確認して、以下を実行してください：
1. README.mdが存在するか確認
2. logs/ディレクトリのファイル数をカウント
3. 実行結果を簡潔に報告
INSTRUCTION

echo "✅ カスタム指示ファイル作成完了"
cat CUSTOM_INSTRUCTION.txt
echo ""

# 4. 統合エージェントを直接実行（デバッグ）
echo "🚀 統合エージェントを直接実行..."
python claude_unified_agent.py

echo ""
echo "=" 
echo "📊 実行結果"
echo "="

# 5. ログ確認
echo "📋 会話ログ（最新20行）:"
tail -20 logs/unified_conversation.log

echo ""
echo "🐛 デバッグログ（最新10行）:"
tail -10 logs/unified_debug.log

echo ""
echo "📁 生成されたファイル:"
ls -lt claude_response_*.txt 2>/dev/null | head -3

echo ""
echo "=" 
echo "✅ テスト完了"
echo "="

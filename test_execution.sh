#!/bin/bash
echo "🧪 実行テスト開始"
echo "現在時刻: $(date '+%H:%M:%S')"
echo ""

# 1. カスタム指示ファイル作成
echo "📝 カスタム指示作成..."
cat > CUSTOM_INSTRUCTION.txt << 'INSTRUCTION'
簡単なテスト: 
ls -la README.md
echo "テスト完了"
INSTRUCTION

echo "✅ カスタム指示ファイル作成完了"
ls -la CUSTOM_INSTRUCTION.txt

# 2. 直接実行
echo ""
echo "🚀 claude_unified_agent_fixed.py を直接実行..."
python claude_unified_agent_fixed.py

# 3. 結果確認
echo ""
echo "📊 結果確認:"
echo "最新ログ:"
tail -10 logs/unified_conversation.log

echo ""
echo "カスタム指示ファイル:"
ls -la CUSTOM_INSTRUCTION.txt 2>/dev/null || echo "❌ 削除済み（正常）"

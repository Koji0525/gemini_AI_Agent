#!/bin/bash
# 安全なスクリプト実行フレームワーク v1.0
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "�� 安全実行フレームワーク起動"

execute_step() {
    local step_name="$1"
    local script_content="$2"
    
    echo "▶️  実行: $step_name"
    
    # 一時ファイルを作成
    local temp_script="/tmp/step_$$.py"
    echo "import sys" > "$temp_script"
    echo "sys.path.insert(0, '/workspaces/gemini_AI_Agent')" >> "$temp_script"
    echo "$script_content" >> "$temp_script"
    
    # 実行
    if python3 "$temp_script"; then
        echo "✅ 成功: $step_name"
        rm -f "$temp_script"
        return 0
    else
        echo "❌ 失敗: $step_name"
        rm -f "$temp_script"
        return 1
    fi
}

# 使用例:
# execute_step "ナレッジ登録" "
# from mvp_v4.scripts.conversation_to_knowledge_v3 import ConversationKnowledgeExtractorV3
# extractor = ConversationKnowledgeExtractorV3()
# kb = extractor.extract_from_simple_format('テスト')
# if kb: extractor.save_knowledge(kb)
# "

echo "✅ フレームワーク準備完了"

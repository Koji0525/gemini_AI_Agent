#!/bin/bash
# ナレッジ登録スクリプト - コピペ途切れ防止版

echo "📝 ナレッジ登録システム V4"
echo "=========================="

if [ $# -eq 1 ]; then
    # ファイルから登録
    python3 mvp_v4/scripts/conversation_to_knowledge_v4.py "$1"
else
    # 対話式登録
    echo "ナレッジを入力してください（終了は Ctrl+D）:"
    python3 mvp_v4/scripts/conversation_to_knowledge_v4.py
fi

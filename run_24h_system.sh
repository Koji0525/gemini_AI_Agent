#!/bin/bash
echo "🕒 24時間自律開発システムを起動します..."
echo "📊 開始時刻: $(date)"

# 無限ループで実行（24時間継続）
while true; do
    echo "🔄 システム起動中..."
    python3 autonomous_development_orchestrator.py
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ 正常終了 - 再起動します"
    else
        echo "⚠️ 異常終了 (コード: $EXIT_CODE) - 10秒待機して再起動します"
        sleep 10
    fi
    
    echo "🔄 再起動処理中..."
    sleep 2
done

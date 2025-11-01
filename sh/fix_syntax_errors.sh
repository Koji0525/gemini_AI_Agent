#!/bin/bash
echo "🔧 構文エラーを修正します"

# complete_24h_system_plan.py の修正
echo "📦 complete_24h_system_plan.py を修正..."
if [ -f "complete_24h_system_plan.py" ]; then
    # 問題のある行を確認して修正
    sed -i '51s/.*/    "run": "詳細な実行コマンド",/' complete_24h_system_plan.py
    echo "✅ complete_24h_system_plan.py 修正完了"
fi

# create_integration_plan.py の修正
echo "📦 create_integration_plan.py を修正..."
if [ -f "create_integration_plan.py" ]; then
    # 問題のある行を確認して修正
    sed -i '48s/.*/    "run": "統合実行コマンド",/' create_integration_plan.py
    echo "✅ create_integration_plan.py 修正完了"
fi

echo "✅ 構文エラー修正完了"

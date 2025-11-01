#!/bin/bash
echo "🔧 YAML/JSON構文を修正します"

# complete_24h_system_plan.py の修正
if [ -f "complete_24h_system_plan.py" ]; then
    echo "📦 complete_24h_system_plan.py を修正..."
    # 51行目を安全に修正
    sed -i '51s/.*/    "run": "具体的な実行コマンドをここに記載",/' complete_24h_system_plan.py
fi

# create_integration_plan.py の修正
if [ -f "create_integration_plan.py" ]; then
    echo "📦 create_integration_plan.py を修正..."
    # 48行目を安全に修正
    sed -i '48s/.*/    "run": "統合テスト実行コマンド",/' create_integration_plan.py
fi

echo "✅ YAML/JSON構文修正完了"

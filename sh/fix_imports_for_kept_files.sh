#!/bin/bash
echo "🔧 インポートパスを修正します"

# 1. decision_support_system.py のインポート修正
echo "📦 decision_support_system.py のインポート修正..."
find . -name "*.py" -type f | grep -v "_ARCHIVE" | while read file; do
    if grep -q "from agents.decision_support.decision_support_system" "$file" 2>/dev/null; then
        sed -i 's/from agents.decision_support.decision_support_system/from agents.self_healing.logging.decision_support_system/g' "$file"
        echo "✅ $file: decision_support_system インポート修正"
    fi
done

# 2. retry_manager.py のインポート修正
echo "📦 retry_manager.py のインポート修正..."
find . -name "*.py" -type f | grep -v "_ARCHIVE" | while read file; do
    if grep -q "from agents.self_healing.core.retry_manager" "$file" 2>/dev/null; then
        sed -i 's/from agents.self_healing.core.retry_manager/from agents.self_healing.retry_manager/g' "$file"
        echo "✅ $file: retry_manager インポート修正"
    fi
done

echo "✅ インポートパス修正完了"

#!/bin/bash
# 重要なファイルがコミットされているか確認

IMPORTANT_PATTERNS=(
    "MD/*.md"
    "knowledge_system/database/*.db"
    "mvp_v4/knowledge/learned/*.json"
)

for pattern in "${IMPORTANT_PATTERNS[@]}"; do
    for file in $pattern; do
        if [[ -f "$file" ]]; then
            # Gitで追跡されているか確認
            if ! git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
                echo "⚠️  未追跡の重要ファイル: $file"
            fi
        fi
    done
done

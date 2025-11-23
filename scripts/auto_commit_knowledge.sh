#!/bin/bash
# ナレッジベースの自動コミット

TIMESTAMP=$(date +%Y%m%d_%H%M)
COMMIT_MSG="�� ナレッジ成長: 自動学習更新 ${TIMESTAMP}"

# 強制的に追加（.gitignoreを無視）
git add -f knowledge_system/database/knowledge.db
git add -f mvp_v4/knowledge/learned/auto_registered_knowledge.json

# 変更がある場合のみコミット
if git diff --staged --quiet; then
    echo "✅ ナレッジ変更なし"
else
    git commit -m "${COMMIT_MSG}"
    git push origin $(git branch --show-current)
    echo "✅ ナレッジ成長を記録: ${COMMIT_MSG}"
fi

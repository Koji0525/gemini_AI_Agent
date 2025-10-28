#!/bin/bash
echo "📊 GitHub Actionsワークフロー監視"
echo "=================================="
echo "現在のワークフロー一覧:"
find .github/workflows -name "*.yml" -exec basename {} \; | while read workflow; do
  echo "✅ $workflow"
done
echo ""
echo "🔄 最新の実行状況を確認するには:"
echo "gh run list --workflow=clean-cache.yml --limit=3"
echo ""
echo "📋 すべてのワークフローを表示:"
echo "gh workflow list"

#!/bin/bash
set -e

echo "🔍 GitHub Actions の状態を確認中..."

RESULT=$(gh run list --limit 1 --json conclusion,name,displayTitle,createdAt 2>/dev/null || echo "[]")

if [ "$RESULT" = "[]" ]; then
    echo "⚠️  GitHub CLI が未設定です"
    echo ""
    echo "📝 初回設定手順:"
    echo "   ターミナルで実行: gh auth login"
    exit 1
fi

CONCLUSION=$(echo "$RESULT" | jq -r '.[0].conclusion')
NAME=$(echo "$RESULT" | jq -r '.[0].name')
TITLE=$(echo "$RESULT" | jq -r '.[0].displayTitle')
CREATED=$(echo "$RESULT" | jq -r '.[0].createdAt')

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 最新のCI実行結果"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ワークフロー: $NAME"
echo "コミット: $TITLE"
echo "実行時刻: $CREATED"
echo ""

case "$CONCLUSION" in
    "success")
        echo "✅ 成功: すべてのチェックに合格しました"
        exit 0
        ;;
    "failure")
        echo "❌ 失敗: エラーが検出されました"
        echo ""
        echo "📋 詳細を確認:"
        echo "   gh run view --log"
        exit 1
        ;;
    "cancelled")
        echo "⚠️  キャンセル: 実行が中断されました"
        exit 0
        ;;
    *)
        echo "🔄 実行中: まだ完了していません"
        echo "   進捗確認: gh run watch"
        exit 0
        ;;
esac

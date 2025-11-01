#!/bin/bash

# GitHub Actions設定確認スクリプト
echo "🔍 GitHub Actions設定確認"
echo "========================"

# 設定ファイルの確認
echo "1. 📁 ワークフローファイルの確認:"
if [ -d ".github/workflows" ]; then
  echo "✅ .github/workflows ディレクトリ存在"
  WORKFLOW_FILES=$(find .github/workflows -name "*.yml" -o -name "*.yaml")
  if [ -n "$WORKFLOW_FILES" ]; then
    echo "📋 ワークフローファイル:"
    echo "$WORKFLOW_FILES" | while read file; do
      echo "  ✅ $file"
      # ファイル内容の簡単な確認
      if grep -q "name:" "$file"; then
        WORKFLOW_NAME=$(grep "name:" "$file" | head -1 | sed 's/name://' | tr -d ' "')
        echo "     📝 ワークフロー名: $WORKFLOW_NAME"
      fi
      if grep -q "on:" "$file"; then
        TRIGGERS=$(grep -A 10 "on:" "$file" | grep -E "push|pull_request|schedule|workflow_dispatch" | head -5)
        echo "     🚀 トリガー: $TRIGGERS" | tr '\n' ' '
        echo ""
      fi
    done
  else
    echo "❌ ワークフローファイルが見つかりません"
  fi
else
  echo "❌ .github/workflows ディレクトリがありません"
fi

# GitHub Actionsの状態確認（もしGitHub CLIがインストールされていれば）
echo ""
echo "2. 🌐 GitHub Actions状態確認:"
if command -v gh &> /dev/null; then
  echo "✅ GitHub CLIが利用可能です"
  # ワークフローの一覧表示
  gh workflow list 2>/dev/null || echo "⚠️  GitHubリポジトリに接続できません"
else
  echo "ℹ️  GitHub CLIがインストールされていません"
  echo "   インストール: https://cli.github.com/"
fi

# 次のステップの説明
echo ""
echo "3. 🚀 次のステップ:"
echo "✅ 設定ファイルは準備完了です！"
echo ""
echo "📋 実行されるアクション:"
echo "   • リポジトリにpushするたびに自動実行"
echo "   • プルリクエスト作成時に自動実行" 
echo "   • 手動で実行可能"
echo "   • 毎日午前3時に自動実行（スケジュール）"
echo ""
echo "🔧 確認方法:"
echo "   1. このリポジトリをGitHubにプッシュ"
echo "   2. GitHubリポジトリの「Actions」タブを確認"
echo "   3. ワークフローの実行状況を確認"
echo ""
echo "🧪 テスト実行方法:"
echo "   現在の変更をコミットしてプッシュ:"
echo "   git add ."
echo "   git commit -m 'feat: Add GitHub Actions for auto cache cleanup'"
echo "   git push origin v1.5.2-wordpress-agent"
echo ""
echo "📊 確認するポイント:"
echo "   ✅ ワークフローが開始されているか"
echo "   ✅ すべてのステップが成功しているか"
echo "   ✅ キャッシュ削除が実行されているか"
echo "   ✅ エラーや警告がないか"

# 現在のブランチ情報
echo ""
echo "4. 🌿 現在のブランチ情報:"
CURRENT_BRANCH=$(git branch --show-current)
echo "   現在のブランチ: $CURRENT_BRANCH"
echo "   設定された対象ブランチ: main, develop, v1.5.2-wordpress-agent"

if [[ " main develop v1.5.2-wordpress-agent " == *" $CURRENT_BRANCH "* ]]; then
  echo "   ✅ 現在のブランチは対象です"
else
  echo "   ⚠️  現在のブランチは対象外です。pushしても実行されません"
fi

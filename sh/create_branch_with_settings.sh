#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔧 ブランチ作成 + 全設定自動引き継ぎスクリプト
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 使用例: ./sh/create_branch_with_settings.sh v1.14.0-feature-name
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e  # エラーで停止

# 引数チェック
if [ -z "$1" ]; then
    echo "❌ エラー: ブランチ名を指定してください"
    echo "📝 使用例: ./sh/create_branch_with_settings.sh v1.14.0-feature-name"
    exit 1
fi

NEW_BRANCH=$1
BASE_BRANCH=${2:-main}  # デフォルトはmain

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 新ブランチ作成 + 設定引き継ぎ開始"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 ベースブランチ: $BASE_BRANCH"
echo "🆕 新ブランチ: $NEW_BRANCH"
echo ""

# STEP 1: ベースブランチから新ブランチを作成
echo "🔄 STEP 1: 新ブランチを作成中..."
git checkout $BASE_BRANCH
git pull origin $BASE_BRANCH
git checkout -b $NEW_BRANCH

echo "✅ 新ブランチ作成完了"
echo ""

# STEP 2: 必須設定ファイルをベースブランチから引き継ぐ
echo "📦 STEP 2: 設定ファイルを引き継ぎ中..."

# 引き継ぐファイル・フォルダのリスト
INHERIT_PATHS=(
    ".github/workflows/"
    ".env"
    ".gitignore"
    "configuration/"
    "scripts/clean_cache.sh"
    "tools/"
    "sh/"
    "requirements.txt"
)

for path in "${INHERIT_PATHS[@]}"; do
    if git ls-tree -r $BASE_BRANCH --name-only | grep -q "^$path"; then
        echo "  📄 引き継ぎ: $path"
        git checkout $BASE_BRANCH -- $path 2>/dev/null || echo "  ⚠️ スキップ: $path (存在しない)"
    else
        echo "  ℹ️ スキップ: $path (ベースブランチに存在しない)"
    fi
done

echo "✅ 設定ファイル引き継ぎ完了"
echo ""

# STEP 3: 変更をコミット
echo "💾 STEP 3: 変更をコミット中..."
git add .
git commit -m "🔧 $BASE_BRANCH から全設定を引き継ぎ (自動生成)" || echo "ℹ️ 変更なし、コミット不要"

echo "✅ コミット完了"
echo ""

# STEP 4: リモートにプッシュ
echo "🚀 STEP 4: リモートにプッシュ中..."
git push -u origin $NEW_BRANCH

echo "✅ プッシュ完了"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 ブランチ作成完了！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 現在のブランチ: $(git branch --show-current)"
echo "💡 次のステップ: コードを編集して開発を進めてください"
echo ""

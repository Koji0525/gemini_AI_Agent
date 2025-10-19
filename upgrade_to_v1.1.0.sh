#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "�� v1.1.0-integrated への移行"
echo "=========================================="

# ====================================================================
# STEP 1: 現在の変更を保存
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/5] 現在の変更を確認${NC}"
echo "=========================================="

echo "未コミットの変更:"
git status --short | head -20

echo ""
echo -e "${YELLOW}現在の変更をコミットしますか？ (y/n)${NC}"
read -p "> " commit_confirm

if [ "$commit_confirm" = "y" ]; then
    echo "コミットメッセージを入力:"
    read -p "> " commit_msg
    
    git add .
    git commit -m "$commit_msg"
    echo "✅ コミット完了"
fi

# ====================================================================
# STEP 2: 新しいブランチ作成
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/5] v1.1.0-integrated ブランチ作成${NC}"
echo "=========================================="

# 現在のブランチを確認
current_branch=$(git branch --show-current)
echo "現在のブランチ: $current_branch"

# v1.1.0-integrated ブランチが既に存在するか確認
if git show-ref --verify --quiet refs/heads/v1.1.0-integrated; then
    echo "⚠️  v1.1.0-integrated ブランチは既に存在します"
    echo "チェックアウトしますか？ (y/n)"
    read -p "> " checkout_confirm
    
    if [ "$checkout_confirm" = "y" ]; then
        git checkout v1.1.0-integrated
    fi
else
    # 新しいブランチを作成
    git checkout -b v1.1.0-integrated
    echo "✅ v1.1.0-integrated ブランチ作成完了"
fi

# ====================================================================
# STEP 3: バージョン情報更新
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/5] バージョン情報更新${NC}"
echo "=========================================="

# VERSION更新
echo "v1.1.0-integrated" > VERSION
echo "✅ VERSION更新: v1.1.0-integrated"

# CHANGELOG更新
cat > CHANGELOG.md << 'CHANGELOG'
# Changelog

## [1.1.0-integrated] - 2025-10-19

### Added
- ✨ 高度なフィードバックループシステム
- ✨ 複数タスク依存関係対応
- ✨ 失敗タスク自動再実行
- ✨ 品質評価システム
- ✨ ゴール達成度測定
- ✨ 実行履歴の深い分析

### Changed
- 🔧 フィードバックループの強化
- �� 依存関係解決の改善

### Planned
- 📝 学習メカニズム実装
- 📝 自動優先度調整

## [1.0.0-integrated] - 2025-10-19

### Added
- ✨ Google Sheets統合（タスク管理）
- ✨ Gemini AI統合（テキスト生成）
- ✨ WordPressエージェント統合
- ✨ タスク間の依存関係管理
- ✨ ハイブリッドストレージ（GitHub + Sheets）
- ✨ task_execution_log自動記録
- ✨ 優先度ベースのタスク実行
- ✨ レート制限機能（10秒間隔）

CHANGELOG

echo "✅ CHANGELOG.md更新完了"

# ====================================================================
# STEP 4: 開発環境確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 4/5] 開発環境確認${NC}"
echo "=========================================="

echo "Python バージョン:"
python3 --version

echo ""
echo "必要パッケージ確認:"
pip list | grep -E "playwright|gspread|google-auth" || echo "⚠️  一部パッケージ未インストール"

# ====================================================================
# STEP 5: 変更をコミット
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 5/5] バージョン更新をコミット${NC}"
echo "=========================================="

git add VERSION CHANGELOG.md
git commit -m "chore: bump version to v1.1.0-integrated" || echo "変更なし、またはコミット済み"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ v1.1.0-integrated 準備完了${NC}"
echo "=========================================="

echo ""
echo "現在のブランチ: $(git branch --show-current)"
echo "バージョン: $(cat VERSION)"

echo ""
echo "次のステップ:"
echo "  1. 新機能開発"
echo "  2. git push origin v1.1.0-integrated"


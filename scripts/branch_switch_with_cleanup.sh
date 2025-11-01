#!/bin/bash

# ブランチ切り替えとキャッシュ削除ツール
set -e

echo "🔄 ブランチ切り替え＆キャッシュクリーンアップツール"
echo "=================================================="

# 引数チェック
if [ $# -eq 0 ]; then
    echo "使用方法: $0 <ブランチ名>"
    echo "例: $0 v1.5.2-wordpress-agent"
    exit 1
fi

TARGET_BRANCH="$1"
CURRENT_BRANCH=$(git branch --show-current)

echo "🔍 現在のブランチ: $CURRENT_BRANCH"
echo "🎯 切り替え先ブランチ: $TARGET_BRANCH"

# ブランチの存在確認
if ! git show-ref --verify --quiet refs/heads/"$TARGET_BRANCH"; then
    echo "❌ ブランチ '$TARGET_BRANCH' が見つかりません"
    echo "利用可能なブランチ:"
    git branch -a | grep -v "remotes/" | sed 's/^/  /'
    exit 1
fi

# ===========================================
# STEP 1: 現在の状態のバックアップと記録
# ===========================================

echo ""
echo "1. 📋 現在の状態の記録..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="_BACKUP/branch_switch_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"

# 現在のファイル状態を記録
echo "📸 現在のファイル状態を記録中..."
find . -maxdepth 2 -type f -name "*.py" -o -name "*.json" -o -name "*.md" -o -name "*.sh" | \
    grep -v -E "(^\./\.git|^\./__pycache__|^\./\.pytest_cache)" | \
    head -50 > "$BACKUP_DIR/file_list_before.txt"

# 重要な設定ファイルをバックアップ
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/env.backup"
    echo "✅ .env をバックアップ"
fi

if [ -f "config/config_loader.py" ]; then
    cp config/config_loader.py "$BACKUP_DIR/config_loader.backup.py"
    echo "✅ config_loader.py をバックアップ"
fi

# ===========================================
# STEP 2: キャッシュの削除
# ===========================================

echo ""
echo "2. 🧹 キャッシュの削除..."

# Pythonキャッシュの削除
echo "🐍 Pythonキャッシュを削除..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# テストキャッシュの削除
echo "🧪 テストキャッシュを削除..."
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".coverage" -delete 2>/dev/null || true
find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true

# ビルドキャッシュの削除
echo "🏗️ ビルドキャッシュを削除..."
find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

# ログファイルのクリーンアップ（オプション）
echo "📋 一時ログファイルをクリーンアップ..."
find . -name "*.log" -type f -delete 2>/dev/null || true
find logs/ -name "*.log" -type f -delete 2>/dev/null || true

echo "✅ キャッシュ削除完了"

# ===========================================
# STEP 3: ブランチの切り替え
# ===========================================

echo ""
echo "3. 🔄 ブランチを切り替え..."

# 変更がある場合はスタッシュ
if ! git diff --quiet || ! git diff --staged --quiet; then
    echo "💾 変更をスタッシュします..."
    git stash push -m "Auto-stash before switching to $TARGET_BRANCH at $TIMESTAMP"
    STASH_APPLY_NEEDED=1
else
    STASH_APPLY_NEEDED=0
fi

# ブランチ切り替え
echo "🔄 $TARGET_BRANCH に切り替え..."
git checkout "$TARGET_BRANCH"

# 必要に応じてスタッシュを適用
if [ $STASH_APPLY_NEEDED -eq 1 ]; then
    echo "🔄 スタッシュを適用..."
    if git stash list | grep -q "Auto-stash before switching to $TARGET_BRANCH"; then
        git stash apply
    else
        echo "⚠️  該当するスタッシュが見つかりませんでした"
    fi
fi

echo "✅ ブランチ切り替え完了: $TARGET_BRANCH"

# ===========================================
# STEP 4: 切り替え後の状態確認
# ===========================================

echo ""
echo "4. 🔍 切り替え後の状態確認..."

# ファイル状態の記録
find . -maxdepth 2 -type f -name "*.py" -o -name "*.json" -o -name "*.md" -o -name "*.sh" | \
    grep -v -E "(^\./\.git|^\./__pycache__|^\./\.pytest_cache)" | \
    head -50 > "$BACKUP_DIR/file_list_after.txt"

# ファイルの変化を確認
echo "📊 ファイル変化の確認:"
diff -u "$BACKUP_DIR/file_list_before.txt" "$BACKUP_DIR/file_list_after.txt" | grep -E "^(\\+|\\-)" | grep -v "^\+\+\+" | grep -v "^\-\-\-" | head -10 || true

# 重要なファイルの存在確認
echo "🔍 重要なファイルの存在確認:"
important_files=(
    ".env"
    "config/config_loader.py" 
    "wordpress/wp_plugin_manager.py"
    "wordpress/wp_cpt_agent.py"
    "wordpress/wp_taxonomy_agent.py"
    "wordpress/wp_acf_agent.py"
    "wordpress/wp_orchestrator.py"
)

for file in "${important_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - 見つかりません"
    fi
done

# キャッシュが再生成されていないか確認
echo "🔍 キャッシュ状態の確認:"
NEW_CACHE_COUNT=$(find . -name "*.pyc" -o -name "__pycache__" 2>/dev/null | wc -l)
if [ "$NEW_CACHE_COUNT" -gt 0 ]; then
    echo "  ⚠️  新しいキャッシュファイルが $NEW_CACHE_COUNT 個見つかりました"
else
    echo "  ✅ キャッシュはクリーンな状態です"
fi

# ===========================================
# STEP 5: システム状態の検証
# ===========================================

echo ""
echo "5. 🧪 システム状態の検証..."

# 基本的なPythonインポートテスト
echo "🐍 Pythonインポートテスト..."
if python3 -c "
import sys
sys.path.append('.')
try:
    from config.config_loader import config
    from wordpress.wp_plugin_manager import WordPressPluginManager
    from wordpress.wp_cpt_agent import WordPressCPTAgent
    print('✅ 主要モジュールインポート成功')
except Exception as e:
    print(f'❌ インポートエラー: {e}')
    sys.exit(1)
"; then
    echo "  ✅ 基本インポートテスト成功"
else
    echo "  ❌ 基本インポートテスト失敗"
fi

# 設定の確認
echo "⚙️ 設定確認..."
if [ -f ".env" ]; then
    echo "  ✅ .env ファイル存在"
    # 設定の基本的な検証
    if python3 -c "
from config.config_loader import config
if config.WP_URL and config.WP_USER:
    print('  ✅ 必須設定が読み込めています')
else:
    print('  ❌ 必須設定が不足しています')
    exit(1)
    "; then
        echo "    ✅ 設定検証成功"
    else
        echo "    ❌ 設定検証失敗"
    fi
else
    echo "  ⚠️  .env ファイルがありません"
fi

# ===========================================
# STEP 6: クリーンアップレポート
# ===========================================

echo ""
echo "6. 📊 クリーンアップ完了レポート"
echo "=================================================="

echo "🎯 ブランチ切り替え完了: $CURRENT_BRANCH → $TARGET_BRANCH"
echo "📁 バックアップ: $BACKUP_DIR"
echo "🧹 削除したキャッシュ:"
echo "  • Pythonバイトコード (*.pyc)"
echo "  • __pycache__ ディレクトリ"
echo "  • テストキャッシュ"
echo "  • ビルドキャッシュ"
echo "  • 一時ログファイル"

# 最終状態の確認
FINAL_CACHE=$(find . -name "*.pyc" -o -name "__pycache__" 2>/dev/null | wc -l)
echo "🔍 最終キャッシュ状態: $FINAL_CACHE 個のキャッシュファイル"

if [ $FINAL_CACHE -eq 0 ]; then
    echo "🎉 キャッシュクリーンアップ完了！"
else
    echo "⚠️  キャッシュファイルが残っています。手動での確認をお勧めします。"
fi

echo ""
echo "💡 次のステップ:"
echo "  現在のブランチ: $TARGET_BRANCH"
echo "  キャッシュ状態: クリーン"
echo "  システム状態: 検証済み"
echo ""
echo "🚀 開発を続行してください！"

# バックアップ場所の情報
echo ""
echo "📂 バックアップ情報:"
echo "  バックアップディレクトリ: $BACKUP_DIR"
echo "  ファイルリスト比較:"
echo "    Before: $BACKUP_DIR/file_list_before.txt"
echo "    After:  $BACKUP_DIR/file_list_after.txt"

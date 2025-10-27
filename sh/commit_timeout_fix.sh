#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🧹 クリーンアップとコミット"
echo "=========================================="

# ====================================================================
# STEP 1: 一時ファイルを削除
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/3] 一時ファイル削除${NC}"
echo "=========================================="

# 削除するファイルパターン
rm -f check_*.sh 2>/dev/null || true
rm -f diagnose_*.sh 2>/dev/null || true
rm -f fix_*.sh 2>/dev/null || true
rm -f setup_*.sh 2>/dev/null || true
rm -f complete_*.sh 2>/dev/null || true
rm -f push_*.sh 2>/dev/null || true
rm -f clean_*.sh 2>/dev/null || true
rm -f cleanup_*.sh 2>/dev/null || true
rm -f *debug*.png *debug*.json 2>/dev/null || true

echo "✅ 一時ファイル削除完了"

# ====================================================================
# STEP 2: 重要なファイルのみステージング
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/3] 重要なファイルのみステージング${NC}"
echo "=========================================="

git add browser_control/browser_controller.py
git add docs/handover/v1.0.0_integrated_status.md
git add .gitignore

# 新規スクリプト
git add apply_timeout_fix.sh
git add test_timeout_fix.sh
git add commit_timeout_fix.sh

echo "✅ ステージング完了"
echo ""
echo "ステージングされたファイル:"
git diff --cached --name-only

# ====================================================================
# STEP 3: コミット
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/3] コミット${NC}"
echo "=========================================="

read -p "コミットしますか？ (y/n): " do_commit

if [ "$do_commit" = "y" ]; then
    git commit -m "fix: ブラウザタイムアウト問題の解決

🔧 主な変更:
- navigate_to_gemini にリトライ機能追加（最大3回）
- タイムアウトを段階的に増加（30秒→60秒→90秒）
- send_prompt にリトライ機能追加（最大2回）
- wait_until を domcontentloaded に変更（軽量化）

📝 テスト:
- 簡単なプロンプト送信テスト実装
- ウズベキスタンタスク再実行確認

📁 ドキュメント:
- v1.0.0統合ブランチの引き継ぎドキュメント作成"

    echo -e "${GREEN}✅ コミット完了${NC}"
    
    read -p "リモートにpushしますか？ (y/n): " do_push
    
    if [ "$do_push" = "y" ]; then
        git push origin v1.0.0-integrated
        echo -e "${GREEN}✅ push完了${NC}"
    fi
else
    echo "コミットをスキップしました"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 完了${NC}"
echo "=========================================="


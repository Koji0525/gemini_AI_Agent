#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "📦 レスポンス取得成功のコミット"
echo "=========================================="

# ====================================================================
# STEP 1: 重要なファイルをステージング
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/3] ステージング${NC}"
echo "=========================================="

git add browser_control/browser_controller.py
git add docs/handover/v1_development_summary.md
git add agent_outputs/test/improved_wait_test.md
git add .gitignore

# テストスクリプト
git add fix_wait_for_generation.sh
git add test_with_improved_wait.sh
git add test_stability_check.sh

echo "✅ ステージング完了"

# ====================================================================
# STEP 2: コミット
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/3] コミット${NC}"
echo "=========================================="

echo ""
echo "ステージングされたファイル:"
git diff --cached --name-only

echo ""
read -p "コミットしますか？ (y/n): " do_commit

if [ "$do_commit" = "y" ]; then
    git commit -m "feat: レスポンス取得機能完成 🎉

✅ 主な成果:
- wait_for_text_generation の完全実装
  - 50文字以上の実レスポンスを判定
  - テキスト長の安定を3回確認
  - 最大90秒待機

- レスポンス取得テスト成功
  - 574文字の完全なレスポンスを取得
  - ウズベキスタンM&Aポータルアウトライン生成成功

📊 テスト結果:
- プロンプト送信: 100% 成功
- レスポンス取得: 574文字取得
- ファイル保存: agent_outputs/test/ に保存成功

🎯 次のステップ:
- 安定性テスト（5回連続実行）
- Google Sheets 結果書き戻し実装"

    echo -e "${GREEN}✅ コミット完了${NC}"
    
    # ====================================================================
    # STEP 3: Push
    # ====================================================================
    echo ""
    echo -e "${BLUE}[STEP 3/3] Push${NC}"
    echo "=========================================="
    
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


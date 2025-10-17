#!/bin/bash
# 全段階を順番に実行

echo "🧹 プロジェクト全体整理"
echo "========================================"
echo ""
echo "実行する段階:"
echo "  1. 安全な削除（__pycache__, browser_data/）"
echo "  2. ROOT直下の整理"
echo "  3. .gitignore更新"
echo ""

read -p "全段階を実行しますか？ (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "キャンセルしました"
    echo ""
    echo "個別実行:"
    echo "  ./cleanup_step1_safe.sh"
    echo "  ./cleanup_step2_root.sh"
    echo "  ./cleanup_step3_gitignore.sh"
    exit 0
fi

# 段階1
./cleanup_step1_safe.sh
echo ""
echo "Press Enter to continue..."
read

# 段階2
./cleanup_step2_root.sh
echo ""
echo "Press Enter to continue..."
read

# 段階3
./cleanup_step3_gitignore.sh

echo ""
echo "========================================"
echo "🎉 全段階完了！"
echo "========================================"
echo ""
echo "📊 最終結果:"
find . -type f | wc -l
echo "ファイル"
echo ""
echo "📁 構造:"
echo "  ✅ core_agents/"
echo "  ✅ browser_control/"
echo "  ✅ scripts/"
echo "  ✅ _WIP/ ← テスト・一時ファイル"
echo "  ✅ _ARCHIVE/ ← 古いファイル"
echo ""

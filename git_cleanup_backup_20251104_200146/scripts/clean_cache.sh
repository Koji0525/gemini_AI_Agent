#!/bin/bash

# 包括的なキャッシュ削除スクリプト
echo "🧹 包括的なキャッシュクリーニング"
echo "=================================="

# 削除対象の定義
TARGETS=(
    "*.pyc"
    "__pycache__"
    ".pytest_cache"
    ".coverage"
    "htmlcov"
    "dist"
    "build"
    "*.egg-info"
    "*.log"
    ".mypy_cache"
    ".ruff_cache"
    ".vscode"
    ".idea"
)

# 各ターゲットの削除
TOTAL_REMOVED=0
for target in "${TARGETS[@]}"; do
    echo "🔍 $target を検索中..."
    COUNT=0
    SIZE=0
    
    # ファイル数のカウント
    if [[ $target == *"*"* ]]; then
        COUNT=$(find . -name "$target" -type f 2>/dev/null | wc -l)
        SIZE=$(find . -name "$target" -type f -exec du -ch {} + 2>/dev/null | grep total | cut -f1)
    else
        COUNT=$(find . -name "$target" -type d 2>/dev/null | wc -l)
        SIZE=$(find . -name "$target" -type d -exec du -sh {} + 2>/dev/null | awk '{sum+=$1} END {print sum "K"}')
    fi
    
    if [ "$COUNT" -gt 0 ]; then
        echo "🗑️  $target を削除中... ($COUNT 個, $SIZE)"
        
        # 削除実行
        if [[ $target == *"*"* ]]; then
            find . -name "$target" -type f -delete 2>/dev/null
        else
            find . -name "$target" -type d -exec rm -rf {} + 2>/dev/null
        fi
        
        TOTAL_REMOVED=$((TOTAL_REMOVED + COUNT))
    else
        echo "✅ $target: 見つかりませんでした"
    fi
done

# Pythonのコンパイル済みキャッシュの特別処理
echo "🐍 Pythonコンパイルキャッシュを確認..."
PYCACHE_DIRS=$(find . -path "*/__pycache__" -type d 2>/dev/null | wc -l)
if [ "$PYCACHE_DIRS" -gt 0 ]; then
    echo "🗑️  __pycache__ ディレクトリを削除中... ($PYCACHE_DIRS 個)"
    find . -path "*/__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    TOTAL_REMOVED=$((TOTAL_REMOVED + PYCACHE_DIRS))
fi

# 結果表示
echo ""
echo "�� クリーニング結果:"
echo "  🗑️  削除した項目数: $TOTAL_REMOVED"
echo "  🧹 キャッシュ状態: クリーン"

# 最終確認
REMAINING_CACHE=$(find . -name "*.pyc" -o -name "__pycache__" 2>/dev/null | wc -l)
if [ "$REMAINING_CACHE" -eq 0 ]; then
    echo "🎉 すべてのキャッシュが正常に削除されました！"
else
    echo "⚠️  キャッシュが $REMAINING_CACHE 個残っています"
    echo "🔍 残っているキャッシュ:"
    find . -name "*.pyc" -o -name "__pycache__" 2>/dev/null | head -10
fi

echo ""
echo "💡 ヒント:"
echo "  定期的なキャッシュ削除でパフォーマンスを向上させましょう"
echo "  ブランチ切り替え時は scripts/branch_switch_with_cleanup.sh を使用してください"

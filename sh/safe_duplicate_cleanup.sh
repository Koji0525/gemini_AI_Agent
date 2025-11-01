#!/bin/bash
echo "🔍 安全な重複ファイル整理スクリプト"

# アーカイブディレクトリ作成
ARCHIVE_DIR="_ARCHIVE/duplicate_files_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

echo "📝 インポート依存関係を確認しながら整理します..."

# 1. __init__.py はスキップ（パッケージファイルなので重複OK）
echo "✅ __init__.py はパッケージファイルのためスキップ"

# 2. uz-manda-portal 関連は別プロジェクトの可能性があるため確認
echo "🔍 uz-manda-portal 関連ファイルを調査..."
find . -path "*/uz-manda-portal/*" -name "*.py" | head -5

# 3. 各重要ファイルのインポート状況を確認してから整理
important_files=(
    "decision_support_system.py"
    "retry_manager.py" 
    "wp_plugin_manager.py"
)

for file in "${important_files[@]}"; do
    echo "=== $file の整理 ==="
    locations=($(find . -name "$file" -type f | grep -v "_ARCHIVE"))
    
    if [ ${#locations[@]} -gt 1 ]; then
        echo "⚠️  重複発見: ${#locations[@]}個"
        
        # 各ファイルのインポート状況を確認
        for location in "${locations[@]}"; do
            import_count=$(grep -r "from.*${file%.*}\|import.*${file%.*}" . --include="*.py" | grep -v "__pycache__" | grep -c "$location" || true)
            echo "  📍 $location → インポート数: $import_count"
        done
        
        # ここでユーザーに判断を仰ぐ
        echo "  🤔 どのファイルを保持しますか？(手動で判断してください)"
    fi
    echo ""
done

echo "✅ 調査完了。手動で安全に整理してください"
echo "📁 アーカイブ先: $ARCHIVE_DIR"

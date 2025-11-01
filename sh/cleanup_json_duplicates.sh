#!/bin/bash
echo "🔧 JSON重複ファイルを整理します"

# アーカイブディレクトリ作成
ARCHIVE_DIR="_ARCHIVE/json_duplicates_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

echo "📁 アーカイブ先: $ARCHIVE_DIR"

# 重複JSONファイルを検出して整理
echo "🔍 重複JSONファイルを検出..."
find . -name "*.json" -type f | sort | while read file; do
    filename=$(basename "$file")
    count=$(find . -name "$filename" -type f | wc -l)
    
    if [ $count -gt 1 ]; then
        echo "⚠️  重複: $filename ($count個)"
        
        # ファイルの重要度に基づいて整理
        case "$filename" in
            ".stylelintrc.json")
                # プロジェクトルートのものを保持
                if [[ "$file" != "./.stylelintrc.json" ]]; then
                    echo "  → アーカイブ: $file"
                    mv "$file" "$ARCHIVE_DIR/"
                fi
                ;;
            "01-evening.json"|"02-noon.json"|"01-display.json"|"02-subtitle.json")
                # configuration/ ディレクトリのものを保持
                if [[ "$file" != "./configuration/$filename" ]]; then
                    echo "  → アーカイブ: $file"
                    mv "$file" "$ARCHIVE_DIR/"
                fi
                ;;
            *)
                # その他の重複ファイルは詳細確認
                echo "  🔍 要確認: $file"
                ;;
        esac
    fi
done

echo "✅ JSON重複ファイル整理完了"

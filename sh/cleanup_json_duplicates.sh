#!/bin/bash
echo "🔍 JSON重複ファイル整理スクリプト"

# アーカイブディレクトリ作成
ARCHIVE_DIR="_ARCHIVE/duplicate_files_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

# 重複ファイルを検出して整理
find . -name "*.json" -type f | sort | while read file; do
    filename=$(basename "$file")
    count=$(find . -name "$filename" -type f | wc -l)
    if [ $count -gt 1 ]; then
        echo "⚠️  重複: $filename ($count個)"
        # 最新版以外をアーカイブ
        if [[ "$file" != "./$filename" && "$file" != "./configuration/$filename" ]]; then
            echo "  → アーカイブ: $file"
            mv "$file" "$ARCHIVE_DIR/"
        fi
    fi
done

echo "✅ 整理完了: $ARCHIVE_DIR に移動"

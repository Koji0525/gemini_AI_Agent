#!/bin/bash
# 段階2: ROOT直下のファイル整理

echo "🧹 段階2: ROOT直下の整理"
echo "========================================"

# _WIP, _ARCHIVE ディレクトリ作成
mkdir -p _WIP/scripts
mkdir -p _WIP/analysis
mkdir -p _ARCHIVE/old_scripts
mkdir -p _BACKUP/root_files

echo "✅ 整理用フォルダ作成完了"
echo ""

# 移動対象のパターン
echo "📦 移動対象:"
echo ""

# テストスクリプト
echo "🧪 テストスクリプト → _WIP/:"
test_files=(
    test_*.py
    check_*.py
    diagnose_*.py
    *_test.py
)

for pattern in "${test_files[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            echo "  - $file"
        fi
    done
done

echo ""
echo "🔧 修正・一時スクリプト → _WIP/scripts/:"
fix_files=(
    fix_*.py
    add_*.py
    organize_*.py
    create_*.py
    setup_*.py
    rebuild_*.py
)

for pattern in "${fix_files[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            echo "  - $file"
        fi
    done
done

echo ""
echo "📊 分析スクリプト → _WIP/analysis/:"
analysis_files=(
    analyze_*.py
    compare_*.py
    *_analysis.py
)

for pattern in "${analysis_files[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            echo "  - $file"
        fi
    done
done

echo ""
echo "🗄️ 古いバックアップファイル → _ARCHIVE/:"
old_files=(
    *.old
    *.backup
    *.orig
    *.rej
    *.before_*
    *_backup_*
)

for pattern in "${old_files[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            echo "  - $file"
        fi
    done
done

echo ""
read -p "これらのファイルを移動しますか？ (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "キャンセルしました"
    exit 0
fi

# 実行
echo ""
echo "📦 移動中..."

# テストスクリプト移動
for pattern in "${test_files[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            mv "$file" _WIP/ 2>/dev/null
        fi
    done
done

# 修正スクリプト移動
for pattern in "${fix_files[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            mv "$file" _WIP/scripts/ 2>/dev/null
        fi
    done
done

# 分析スクリプト移動
for pattern in "${analysis_files[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            mv "$file" _WIP/analysis/ 2>/dev/null
        fi
    done
done

# 古いファイル移動
for pattern in "${old_files[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            mv "$file" _ARCHIVE/old_scripts/ 2>/dev/null
        fi
    done
done

echo "✅ 移動完了"
echo ""
echo "========================================"
echo "✅ 段階2完了！"
echo ""
echo "📊 ROOT直下のファイル数:"
ls -1 | grep -E '\.py$|\.sh$' | wc -l
echo ""
echo "次: 段階3（.gitignore更新）"

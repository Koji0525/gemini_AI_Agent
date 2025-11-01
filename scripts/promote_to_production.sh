#!/bin/bash
# WIPで開発したファイルを本番環境に昇格

set -e

echo "========================================="
echo "🚀 WIP → 本番への昇格"
echo "========================================="

# 昇格対象ファイル
FILES_TO_PROMOTE=(
    "_WIP/pm_agent_automation.py:agents/pm_agent/automation.py"
    "_WIP/pm_agent_progress_monitor.py:agents/pm_agent/progress_monitor.py"
    "_WIP/pm_agent_task_registration.py:agents/pm_agent/task_registration.py"
    "_WIP/pm_agent_task_exporter.py:agents/pm_agent/task_exporter.py"
    "_WIP/pm_agent_enhanced/pm_agent_task_breakdown_gemini.py:agents/pm_agent/task_breakdown_gemini.py"
)

echo ""
echo "📋 昇格予定:"
for mapping in "${FILES_TO_PROMOTE[@]}"; do
    source="${mapping%%:*}"
    dest="${mapping##*:}"
    if [ -f "$source" ]; then
        echo "  ✅ $source → $dest"
    else
        echo "  ⚠️  $source （見つからない）"
    fi
done

echo ""
read -p "昇格を実行しますか？ (y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ キャンセルしました"
    exit 0
fi

echo ""
echo "========================================="
echo "🧪 昇格前テスト"
echo "========================================="

# 構文チェック
for mapping in "${FILES_TO_PROMOTE[@]}"; do
    source="${mapping%%:*}"
    if [ -f "$source" ]; then
        if python3 -m py_compile "$source" 2>/dev/null; then
            echo "  ✅ $source: 構文OK"
        else
            echo "  ❌ $source: 構文エラー"
            exit 1
        fi
    fi
done

echo ""
echo "========================================="
echo "📦 バックアップ作成"
echo "========================================="

BACKUP_DIR="_BACKUP/promotion_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for mapping in "${FILES_TO_PROMOTE[@]}"; do
    dest="${mapping##*:}"
    if [ -f "$dest" ]; then
        cp "$dest" "$BACKUP_DIR/$(basename $dest)"
        echo "  ✅ $(basename $dest) をバックアップ"
    fi
done

echo ""
echo "========================================="
echo "🚀 ファイル昇格実行"
echo "========================================="

for mapping in "${FILES_TO_PROMOTE[@]}"; do
    source="${mapping%%:*}"
    dest="${mapping##*:}"
    
    if [ -f "$source" ]; then
        # ディレクトリ作成
        mkdir -p "$(dirname $dest)"
        
        # コピー
        cp "$source" "$dest"
        echo "  ✅ $dest に昇格"
    fi
done

echo ""
echo "========================================="
echo "✅ 昇格完了！"
echo "========================================="
echo ""
echo "📁 バックアップ: $BACKUP_DIR"
echo ""
echo "🧪 次のステップ:"
echo "   1. 本番環境でテスト実行"
echo "   2. 問題なければコミット"
echo "   3. WIPファイルはそのまま保持（次回開発用）"
echo "========================================="

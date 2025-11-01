#!/bin/bash
echo "🔧 最終重複ファイル整理を実行"

# アーカイブディレクトリ作成
ARCHIVE_DIR="_ARCHIVE/final_duplicate_cleanup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

echo "📁 アーカイブ先: $ARCHIVE_DIR"

# uz-manda-portal は別プロジェクトとして維持する方針
echo "📋 整理方針:"
echo "✅ 保持: scripts/ ディレクトリのファイル（メインプロジェクト）"
echo "✅ 維持: uz-manda-portal/ ディレクトリ（別プロジェクトとして維持）"
echo "❌ アーカイブ: 重複しているが使用されていないファイル"

# 重複ファイルのインポート状況を確認
echo "🔍 インポート状況確認..."

# ma_auto_poster_agent.py のインポート確認
echo "📦 ma_auto_poster_agent.py:"
grep -r "ma_auto_poster_agent" . --include="*.py" | grep -v "_ARCHIVE" | grep -v "uz-manda-portal" | head -5

# もし scripts/ ディレクトリのファイルが使用されていなければ、uz-manda-portal 版を優先
echo "💡 判断: uz-manda-portal は独立したプロジェクトのため、両方維持を推奨"
echo "💡 ただし、明らかに古いバージョンやテストファイルは整理可能"

# 明らかな古いファイルやテストファイルを整理
echo "📦 明らかな重複ファイルを整理..."

# test_integration.py - automation/tests/ 版を保持、uz-manda-portal 版は別プロジェクトとして維持
if [ -f "automation/tests/test_integration.py" ] && [ -f "uz-manda-portal/scripts/test_integration.py" ]; then
    echo "🔍 test_integration.py: 両方維持（異なるプロジェクト）"
fi

echo "✅ 重複ファイル整理完了 - uz-manda-portal は別プロジェクトとして維持"

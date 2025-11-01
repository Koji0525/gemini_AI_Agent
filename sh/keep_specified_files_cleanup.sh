#!/bin/bash
echo "🔍 指定ファイル保持で重複整理を実行"

# アーカイブディレクトリ作成
ARCHIVE_DIR="_ARCHIVE/keep_specified_cleanup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

echo "📁 アーカイブ先: $ARCHIVE_DIR"
echo "💾 保持ファイル:"
echo "  ✅ ./agents/self_healing/logging/"
echo "  ✅ ./agents/self_healing/"
echo "  ✅ ./wp_plugin_manager.py"

# 1. decision_support_system.py - logging版を保持
echo "📦 decision_support_system.py を整理..."
if [ -f "agents/decision_support/decision_support_system.py" ]; then
    mv "agents/decision_support/decision_support_system.py" "$ARCHIVE_DIR/"
    echo "✅ agents/decision_support/decision_support_system.py → アーカイブ"
fi

# 2. retry_manager.py - self_healing版を保持、core版をアーカイブ
echo "📦 retry_manager.py を整理..."
if [ -f "agents/self_healing/core/retry_manager.py" ]; then
    mv "agents/self_healing/core/retry_manager.py" "$ARCHIVE_DIR/"
    echo "✅ agents/self_healing/core/retry_manager.py → アーカイブ"
fi

# 3. wp_plugin_manager.py - プロジェクトルート版を保持、tools版をアーカイブ
echo "📦 wp_plugin_manager.py を整理..."
if [ -f "tools/wp_plugin_manager.py" ]; then
    mv "tools/wp_plugin_manager.py" "$ARCHIVE_DIR/"
    echo "✅ tools/wp_plugin_manager.py → アーカイブ"
fi

echo ""
echo "✅ 指定ファイル保持での整理完了"

# 保持されているファイルの確認
echo ""
echo "🔍 保持されているファイル:"
find . -name "decision_support_system.py" -type f 2>/dev/null | grep -v "_ARCHIVE" | head -5
find . -name "retry_manager.py" -type f 2>/dev/null | grep -v "_ARCHIVE" | head -5
find . -name "wp_plugin_manager.py" -type f 2>/dev/null | grep -v "_ARCHIVE" | head -5

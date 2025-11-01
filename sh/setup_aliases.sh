#!/bin/bash
# 🔧 便利なエイリアスを設定
#
# 【エイリアス一覧】
# ✅ touch_smart    - スマートファイル作成
# ✅ fvm            - File Version Manager
# ✅ git_push       - Git自動プッシュ
# ✅ archive_old    - 古いバージョンアーカイブ
# ✅ check_dup      - 重複チェック

# エイリアス定義を ~/.bashrc に追加
cat >> ~/.bashrc << 'ALIASES'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 開発効率化エイリアス
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# スマートファイル作成（自動バージョンチェック）
alias touch_smart='python3 tools/smart_file_creator.py'

# File Version Manager（短縮形）
alias fvm='python3 tools/file_version_manager.py'

# Git自動プッシュ
alias git_push='python3 agents/git_agent/auto_commit_push_v04_optimized.py'

# 古いバージョンアーカイブ
alias archive_old='python3 tools/archive_old_versions.py'

# 重複チェック
alias check_dup='python3 tools/file_version_manager.py --check-duplicates --exclude-dirs _WIP _ARCHIVE _BACKUP'

ALIASES

echo "✅ エイリアスを ~/.bashrc に追加しました"
echo ""
echo "有効化するには以下を実行："
echo "  source ~/.bashrc"

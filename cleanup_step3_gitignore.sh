#!/bin/bash
# 段階3: .gitignore更新

echo "🧹 段階3: .gitignore更新"
echo "========================================"

# .gitignoreに追加すべき項目
cat >> .gitignore << 'GITIGNORE_EOF'

# ===== ブラウザ関連（自動生成） =====
browser_data/
*.pyc
__pycache__/
*.pyo
*.pyd

# ===== ログファイル =====
*.log
*.pid

# ===== 一時ファイル =====
*.tmp
*.temp
*.swp
*.swo
*~

# ===== バックアップファイル =====
*.backup
*.bak
*.old
*.orig
*.rej

# ===== OS関連 =====
.DS_Store
Thumbs.db

# ===== IDE関連 =====
.vscode/
.idea/
*.sublime-*

# ===== Python関連 =====
*.egg-info/
dist/
build/
.eggs/

# ===== 環境変数 =====
.env
.env.local

# ===== Playwright =====
playwright-report/
test-results/

# ===== その他 =====
node_modules/
*.db
*.db-journal
GITIGNORE_EOF

echo "✅ .gitignore更新完了"
echo ""
echo "追加した除外パターン:"
echo "  - browser_data/"
echo "  - __pycache__/"
echo "  - *.pyc"
echo "  - *.log, *.pid"
echo "  - *.backup, *.old"
echo "  - その他"
echo ""
echo "========================================"
echo "✅ 段階3完了！"

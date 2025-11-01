#!/bin/bash
echo "🔧 緊急問題診断"
cd /workspaces/gemini_AI_Agent || exit 1

# 1. サービスアカウントファイル確認
echo "=== サービスアカウントファイル ==="
ls -lh configuration/service_account.json 2>/dev/null || echo "❌ ファイルなし"

# 2. GoogleSheetsManagerのメソッド確認
echo ""
echo "=== GoogleSheetsManager メソッド ==="
python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from tools.sheets_manager import GoogleSheetsManager
methods = [m for m in dir(GoogleSheetsManager) if 'get' in m.lower() and not m.startswith('_')]
print('データ取得メソッド:')
for m in methods[:10]:
    print(f'  - {m}')
" 2>&1 | head -20

# 3. WordPress関連ファイル確認
echo ""
echo "=== WordPress関連ファイル ==="
find . -name "*wordpress*.py" -type f | grep -v __pycache__ | head -10

# 4. core_agentsの内容確認
echo ""
echo "=== core_agents ディレクトリ ==="
ls -la core_agents/*.py 2>/dev/null | awk '{print $9}'

# 5. .envファイル確認
echo ""
echo "=== 環境変数ファイル ==="
[ -f .env ] && echo "✅ .env あり" || echo "❌ .env なし"


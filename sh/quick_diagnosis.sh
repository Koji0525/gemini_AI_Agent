#!/bin/bash
# ====================================
# 【コピペ実行用】簡易診断スクリプト
# ====================================
# 
# 使い方: このファイル全体をコピーして
# GitHub Codespacesのターミナルに貼り付けて Enter
#

cd /workspaces/gemini_AI_Agent && \
echo "🔍 システム診断開始" && \
echo "==================" && \
echo "" && \
echo "📁 1. プロジェクト構造:" && \
pwd && \
echo "" && \
echo "📁 2. サービスアカウント:" && \
(ls -lh configuration/service_account.json && echo "✅ ファイル存在" || echo "❌ ファイル不在") && \
echo "" && \
echo "📁 3. .envファイル:" && \
([ -f .env ] && echo "✅ .env存在" || echo "❌ .env不在") && \
echo "" && \
echo "📁 4. core_agentsの内容:" && \
ls core_agents/*.py 2>/dev/null | wc -l | xargs -I {} echo "   {}個のPythonファイル" && \
ls core_agents/*.py 2>/dev/null | head -10 && \
echo "" && \
echo "📁 5. WordPress関連ファイル:" && \
find . -name "*wordpress*.py" -type f | grep -v __pycache__ | wc -l | xargs -I {} echo "   {}個のファイル" && \
find . -name "*wordpress*.py" -type f | grep -v __pycache__ | head -5 && \
echo "" && \
echo "🔧 6. GoogleSheetsManagerのメソッド確認:" && \
python3 << 'PYEND'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
try:
    from tools.sheets_manager import GoogleSheetsManager
    methods = [m for m in dir(GoogleSheetsManager) if not m.startswith('_')]
    get_methods = [m for m in methods if 'get' in m.lower() or 'read' in m.lower()]
    print(f"   全メソッド: {len(methods)}個")
    print(f"   データ取得系: {len(get_methods)}個")
    if get_methods:
        print("   主要メソッド:")
        for m in get_methods[:8]:
            print(f"      - {m}")
except Exception as e:
    print(f"   ❌ エラー: {e}")
PYEND
echo "" && \
echo "✅ 診断完了" && \
echo "" && \
echo "🎯 次のステップ:" && \
echo "   上記の結果をClaudeに共有してください"

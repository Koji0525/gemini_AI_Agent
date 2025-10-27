#!/bin/bash
# ====================================
# Phase 1: WordPress専門エージェント復活
# ====================================

echo "🔧 Phase 1: WordPress機能の緊急修復"
echo "===================================="

cd /workspaces/gemini_AI_Agent || exit 1

# ====
# 1. WordPress専門エージェントのインポートエラー確認
# ====
echo ""
echo "=== 1. WP専門エージェントのインポート状態確認 ==="
python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

# インポート可能なエージェントを確認
import importlib
import traceback

agents_to_check = [
    'core_agents.wordpress_cpt_agent',
    'core_agents.wordpress_acf_agent', 
    'core_agents.design_agent',
    'core_agents.review_agent'
]

print('📦 エージェントインポート状況:')
for agent_module in agents_to_check:
    try:
        mod = importlib.import_module(agent_module)
        print(f'  ✅ {agent_module}')
        # クラスの存在確認
        if hasattr(mod, 'WordPressCPTAgent'):
            print(f'     → WordPressCPTAgent クラス存在')
        if hasattr(mod, 'WordPressACFAgent'):
            print(f'     → WordPressACFAgent クラス存在')
    except Exception as e:
        print(f'  ❌ {agent_module}: {str(e)[:100]}')
        traceback.print_exc()
" 2>&1 | head -50

# ====
# 2. WordPress認証情報の確認
# ====
echo ""
echo "=== 2. WordPress認証情報の確認 ==="
python3 -c "
import sys
import os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

print('🔐 環境変数確認:')
wp_vars = ['WP_URL', 'WP_USER', 'WP_PASS', 'WORDPRESS_URL']
for var in wp_vars:
    value = os.environ.get(var, 'NOT SET')
    if value != 'NOT SET':
        masked = value[:10] + '***' if len(value) > 10 else '***'
        print(f'  {var}: {masked}')
    else:
        print(f'  ❌ {var}: 未設定')

print('')
print('📋 Sheets設定確認:')
try:
    from tools.sheets_manager import GoogleSheetsManager
    sheets_mgr = GoogleSheetsManager('1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s')
    
    # 設定シートから読み込み
    try:
        settings = sheets_mgr.get_all_records('settings')
        if settings:
            wp_settings = [s for s in settings if 'wp' in s.get('key', '').lower()]
            print(f'  WP関連設定: {len(wp_settings)}件')
            for setting in wp_settings[:5]:
                key = setting.get('key', 'N/A')
                value = setting.get('value', 'N/A')
                masked = value[:10] + '***' if len(str(value)) > 10 else '***'
                print(f'    {key}: {masked}')
        else:
            print('  ⚠️ settings シートが空、またはアクセス不可')
    except Exception as e:
        print(f'  ❌ settings シート読み込みエラー: {e}')
        
except Exception as e:
    print(f'❌ Sheets接続エラー: {e}')
" 2>&1 | head -50

# ====
# 3. TaskExecutorのWPエージェントルーティング確認
# ====
echo ""
echo "=== 3. TaskExecutorのWPエージェントルーティング確認 ==="
grep -n "wordpress_cpt\|wordpress_acf\|WordPressCPT\|WordPressACF" scripts/task_executor.py | head -20

# ====
# 4. 利用可能なWPエージェントファイルの確認
# ====
echo ""
echo "=== 4. WP専門エージェントファイルの存在確認 ==="
find . -name "*wordpress*agent*.py" -type f | grep -v "__pycache__" | grep -v "_BACKUP"

echo ""
echo "✅ Phase 1 診断完了"
echo "次のアクション: 検出された問題に基づいて修復を実行"

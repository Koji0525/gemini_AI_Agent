#!/bin/bash
# ====================================
# Phase 2: Gemini AI統合とタスク分解強化
# ====================================

echo "🤖 Phase 2: AI統合による品質向上"
echo "===================================="

cd /workspaces/gemini_AI_Agent || exit 1

# ====
# 1. 現在のタスク分解ロジック確認
# ====
echo ""
echo "=== 1. 現在のタスク分解ロジック（モック版）確認 ==="
echo "タスク分解ファイル:"
find . -name "*task_breakdown*.py" -type f | grep -v "__pycache__"

echo ""
echo "タスク分解メソッド:"
grep -n "def.*breakdown\|def.*decompose" core_agents/pm_agent.py 2>/dev/null | head -10

# ====
# 2. BrowserController統合状況の確認
# ====
echo ""
echo "=== 2. BrowserController統合状況 ==="
python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    from browser_control.browser_controller import BrowserController
    print('✅ BrowserController インポート成功')
    
    # 利用可能なメソッド確認
    import inspect
    methods = [m for m in dir(BrowserController) if not m.startswith('_')]
    print(f'📋 利用可能メソッド数: {len(methods)}')
    
    # Gemini関連メソッド
    gemini_methods = [m for m in methods if 'gemini' in m.lower() or 'prompt' in m.lower()]
    if gemini_methods:
        print('🎯 Gemini関連メソッド:')
        for method in gemini_methods[:10]:
            print(f'   - {method}')
    else:
        print('⚠️ Gemini関連メソッドが見つかりません')
        
except Exception as e:
    print(f'❌ BrowserController インポートエラー: {e}')
" 2>&1 | head -40

# ====
# 3. タスク分解品質の評価
# ====
echo ""
echo "=== 3. 現在のタスク分解品質評価 ==="
python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    from tools.sheets_manager import GoogleSheetsManager
    sheets_mgr = GoogleSheetsManager('1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s')
    
    # 最近のタスクを確認
    tasks = sheets_mgr.get_all_records('pm_tasks')
    print(f'📊 登録タスク総数: {len(tasks)}件')
    
    if tasks:
        recent_tasks = tasks[-5:]
        print('')
        print('📝 最近登録されたタスク（直近5件）:')
        for task in recent_tasks:
            task_id = task.get('task_id', 'N/A')
            title = task.get('task_title', 'N/A')
            agent_type = task.get('agent_type', 'N/A')
            dependencies = task.get('dependencies', 'N/A')
            
            # タスクの具体性を評価
            specificity = '具体的' if len(str(title)) > 30 else '抽象的'
            has_deps = '有' if dependencies and str(dependencies).strip() and dependencies != 'N/A' else '無'
            
            print(f'  🆔 {task_id}:')
            print(f'     タイトル: {str(title)[:60]}')
            print(f'     エージェント: {agent_type}')
            print(f'     依存関係: {has_deps}')
            print(f'     評価: {specificity}')
            print('')
            
except Exception as e:
    print(f'❌ タスク評価エラー: {e}')
" 2>&1 | head -60

# ====
# 4. Gemini AI統合プロンプトテスト
# ====
echo ""
echo "=== 4. Gemini AI統合のための準備確認 ==="
cat > /tmp/test_gemini_integration.py << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
import asyncio

async def test_gemini_for_task_breakdown():
    """タスク分解のためのGemini AI統合テスト"""
    try:
        from browser_control.browser_controller import BrowserController
        
        print("🤖 Gemini AI統合テスト開始")
        print("=" * 50)
        
        browser = BrowserController()
        await browser.initialize()
        print("✅ BrowserController初期化成功")
        
        # テスト用のプロジェクト目標
        test_goal = """
        WordPressサイトに「お客様の声」セクションを追加する。
        カスタム投稿タイプ「testimonials」を作成し、
        ACFで「顧客名」「評価（星5つ）」「コメント」フィールドを追加。
        """
        
        # タスク分解プロンプト
        prompt = f"""
あなたはプロジェクトマネージャーです。以下のプロジェクト目標を、
実行可能な具体的なタスクに分解してください。

目標: {test_goal}

各タスクは以下の形式で出力してください：
1. タスクタイトル（50文字以内）
2. 担当エージェント（wordpress_cpt, wordpress_acf, design, contentなど）
3. 詳細な説明
4. 依存タスク番号（あれば）

タスクリストを出力してください。
"""
        
        print("\n📤 Geminiにプロンプト送信中...")
        # Note: 実際のsend_promptメソッドはプロジェクトに依存
        # response = await browser.send_prompt(prompt)
        print("⚠️ send_promptメソッドの実装を確認する必要があります")
        
        await browser.cleanup()
        print("\n✅ テスト完了")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_for_task_breakdown())
PYTHON_SCRIPT

python3 /tmp/test_gemini_integration.py 2>&1 | head -50

echo ""
echo "✅ Phase 2 診断完了"
echo "次のアクション: Gemini AI統合の実装"

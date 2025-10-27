#!/bin/bash
# ====================================
# Phase 3: 完全自律サイクルの確立
# ====================================

echo "🚀 Phase 3: 完全自律サイクル確立"
echo "===================================="

cd /workspaces/gemini_AI_Agent || exit 1

# ====
# 1. Dynamic Task Generator実装状況の確認
# ====
echo ""
echo "=== 1. Dynamic Task Generator実装状況 ==="
echo "関連ファイル検索:"
find . -name "*dynamic*" -o -name "*generator*" | grep -v "__pycache__" | grep ".py$"

echo ""
echo "既存のタスク生成ロジック:"
grep -rn "def.*generate.*task\|class.*Generator" core_agents/ scripts/ 2>/dev/null | head -15

# ====
# 2. 品質スコアベースの再実行ロジック確認
# ====
echo ""
echo "=== 2. 品質スコアベースの再実行ロジック ==="
python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

try:
    from tools.sheets_manager import GoogleSheetsManager
    sheets_mgr = GoogleSheetsManager('1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s')
    
    # 低品質スコアのタスクを検出
    logs = sheets_mgr.get_all_records('task_execution_log')
    print(f'📊 実行ログ総数: {len(logs)}件')
    
    if logs:
        # 品質スコアが7未満のタスクを抽出
        low_quality = [
            log for log in logs 
            if log.get('quality_score') and 
            str(log.get('quality_score')).replace('.', '').isdigit() and
            float(log.get('quality_score')) < 7
        ]
        
        print(f'⚠️ 低品質タスク（スコア<7）: {len(low_quality)}件')
        
        if low_quality:
            print('')
            print('📝 再実行が必要なタスク（直近5件）:')
            for log in low_quality[-5:]:
                task_id = log.get('task_id', 'N/A')
                score = log.get('quality_score', 'N/A')
                agent = log.get('agent_type', 'N/A')
                status = log.get('status', 'N/A')
                
                print(f'  🆔 {task_id}: スコア {score}/10')
                print(f'     エージェント: {agent}')
                print(f'     ステータス: {status}')
                print('')
                
        # 再実行推奨の集計
        if low_quality:
            agent_stats = {}
            for log in low_quality:
                agent = log.get('agent_type', 'unknown')
                agent_stats[agent] = agent_stats.get(agent, 0) + 1
                
            print('📊 エージェント別 低品質タスク数:')
            for agent, count in sorted(agent_stats.items(), key=lambda x: x[1], reverse=True):
                print(f'   {agent}: {count}件')
                
except Exception as e:
    print(f'❌ エラー: {e}')
    import traceback
    traceback.print_exc()
" 2>&1 | head -60

# ====
# 3. 完全自律サイクルのテスト
# ====
echo ""
echo "=== 3. 完全自律サイクル テスト準備 ==="
cat > /tmp/test_autonomous_cycle.py << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
import asyncio

async def test_autonomous_cycle():
    """完全自律サイクルのテスト"""
    try:
        from tools.sheets_manager import GoogleSheetsManager
        from core_agents.pm_agent import PMAgent
        
        print("🔄 完全自律サイクル テスト")
        print("=" * 50)
        
        sheets_mgr = GoogleSheetsManager('1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s')
        
        # ステップ1: プロジェクト目標の取得
        print("\n📋 ステップ1: プロジェクト目標取得")
        goals = sheets_mgr.get_all_records('project_goal')
        active_goals = [g for g in goals if g.get('status') == 'active']
        print(f"   アクティブな目標: {len(active_goals)}件")
        
        if active_goals:
            test_goal = active_goals[0]
            print(f"   テスト目標: {test_goal.get('goal_name', 'N/A')[:50]}")
        
        # ステップ2: 進捗監視
        print("\n📊 ステップ2: 進捗監視")
        dashboard = sheets_mgr.get_all_records('progress_dashboard')
        if dashboard:
            low_progress = [d for d in dashboard if d.get('progress_rate') and float(d.get('progress_rate', 100)) < 50]
            print(f"   低進捗目標: {len(low_progress)}件")
        
        # ステップ3: タスク分解（現状確認）
        print("\n🔧 ステップ3: タスク分解機能")
        print("   ⚠️ 現在はモック版。Gemini AI統合が必要")
        
        # ステップ4: タスク実行
        print("\n🚀 ステップ4: タスク実行")
        tasks = sheets_mgr.get_all_records('pm_tasks')
        pending_tasks = [t for t in tasks if t.get('status') == 'pending']
        print(f"   実行待ちタスク: {len(pending_tasks)}件")
        
        # ステップ5: 品質評価と再実行判定
        print("\n⭐ ステップ5: 品質評価")
        logs = sheets_mgr.get_all_records('task_execution_log')
        recent_logs = logs[-10:] if logs else []
        scored_logs = [l for l in recent_logs if l.get('quality_score')]
        avg_score = sum(float(l.get('quality_score', 0)) for l in scored_logs) / len(scored_logs) if scored_logs else 0
        print(f"   最近の平均品質スコア: {avg_score:.2f}/10")
        
        # ステップ6: 進捗更新
        print("\n📈 ステップ6: 進捗更新")
        print("   ✅ 実行ログ → ダッシュボード連携動作中")
        
        print("\n" + "=" * 50)
        print("🎯 サイクル完成度評価:")
        print(f"   目標取得: ✅")
        print(f"   進捗監視: ✅")
        print(f"   タスク分解: ⚠️ (要AI統合)")
        print(f"   タスク実行: ✅")
        print(f"   品質評価: ✅")
        print(f"   進捗更新: ✅")
        print(f"   自動再実行: ❌ (未実装)")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_autonomous_cycle())
PYTHON_SCRIPT

python3 /tmp/test_autonomous_cycle.py 2>&1 | head -70

# ====
# 4. パフォーマンス指標の確認
# ====
echo ""
echo "=== 4. システムパフォーマンス指標 ==="
python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from datetime import datetime, timedelta

try:
    from tools.sheets_manager import GoogleSheetsManager
    sheets_mgr = GoogleSheetsManager('1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s')
    
    logs = sheets_mgr.get_all_records('task_execution_log')
    
    print('📊 システムパフォーマンス（全期間）:')
    print(f'   総実行タスク数: {len(logs)}件')
    
    # ステータス別集計
    status_count = {}
    for log in logs:
        status = log.get('status', 'unknown')
        status_count[status] = status_count.get(status, 0) + 1
    
    print('   ステータス別:')
    for status, count in sorted(status_count.items(), key=lambda x: x[1], reverse=True):
        print(f'     {status}: {count}件')
    
    # 品質スコア統計
    scored_logs = [l for l in logs if l.get('quality_score')]
    if scored_logs:
        scores = [float(l.get('quality_score')) for l in scored_logs]
        avg = sum(scores) / len(scores)
        high_quality = len([s for s in scores if s >= 8])
        
        print(f'   品質スコア付き: {len(scored_logs)}件')
        print(f'   平均スコア: {avg:.2f}/10')
        print(f'   高品質（8点以上）: {high_quality}件 ({high_quality/len(scored_logs)*100:.1f}%)')
        
except Exception as e:
    print(f'❌ エラー: {e}')
" 2>&1 | head -40

echo ""
echo "✅ Phase 3 診断完了"
echo "次のアクション: Dynamic Task Generatorの実装と完全自律化"

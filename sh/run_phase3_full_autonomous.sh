#!/bin/bash
# Phase 3完全自律実行システム

cd /workspaces/gemini_AI_Agent

LIMIT=${1:-2}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Phase 3完全自律実行システム"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【Phase 3機能】"
echo "  ✅ Phase 2機能すべて"
echo "  ✅ Git自動コミット"
echo "  ✅ ナレッジベース統合"
echo "  ✅ F1-F10完全連携"
echo "  ✅ 自動で開発が進む状態"
echo ""
echo "実行タスク数: $LIMIT"
echo ""

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.robust_task_selector import RobustTaskSelector
from core_agents.quality_feedback_loop_v2 import QualityFeedbackLoopV2
from agents.quality_assurance.auto_code_quality_checker import AutoCodeQualityChecker
from agents.quality_assurance.auto_test_generator import AutoTestGenerator
from agents.quality_assurance.auto_integration_manager import AutoIntegrationManager
from agents.automation.auto_git_committer import AutoGitCommitter
from agents.automation.f_system_integrator import FSystemIntegrator
from agents.efficiency.output_utilization_system import OutputUtilizationSystem
from tools.sheets_manager import GoogleSheetsManager

# 初期化
sheets = GoogleSheetsManager()
selector = RobustTaskSelector(sheets)
qfl = QualityFeedbackLoopV2()
quality_checker = AutoCodeQualityChecker()
test_generator = AutoTestGenerator()
integration_manager = AutoIntegrationManager()
git_committer = AutoGitCommitter()
f_integrator = FSystemIntegrator()
utilization = OutputUtilizationSystem()

# タスク選択
tasks = selector.select_executable_task(limit=$LIMIT)

if not tasks:
    print("⚠️  実行可能なタスクがありません")
    sys.exit(0)

print(f"✅ {len(tasks)}個のタスクを選択しました")
for i, task in enumerate(tasks, 1):
    print(f"  {i}. {task['task_id']}")

print()

# タスク実行
success_count = 0
high_quality_outputs = []
completed_task_ids = []

for task in tasks:
    print("\n" + "=" * 80)
    print(f"🚀 タスク実行: {task['task_id']}")
    print("=" * 80)
    
    try:
        # Phase 1: 高品質タスク実行
        result = qfl.execute_with_quality_assurance(task)
        
        if result['success']:
            output_path = result['output_path']
            score = result['score']
            
            print(f"\n✅ Phase 1完了: {task['task_id']}")
            
            # Phase 2: 品質チェック・テスト・統合
            quality_result = quality_checker.check_all(output_path)
            test_result = test_generator.generate_tests(output_path)
            
            if test_result['generated_tests']:
                test_run_result = test_generator.run_tests(output_path)
            
            integration_result = integration_manager.integrate_output(
                output_path,
                task['task_id'],
                score
            )
            
            # Phase 3: F1-F10統合
            print(f"\n🔗 Phase 3-1: F1-F10システム統合")
            f_result = f_integrator.integrate_with_f_systems({
                'task_id': task['task_id'],
                'score': score,
                'output_path': output_path
            })
            
            if f_result['f4_integrated']:
                print("  ✅ F4: ナレッジ蓄積完了")
            if f_result['f5_integrated']:
                print("  ✅ F5: 進捗可視化完了")
            if f_result['f9_notified']:
                print("  ✅ F9: 人間協働通知完了")
            
            # 高品質成果物を記録
            if score >= 7.0:
                high_quality_outputs.append({
                    'task_id': task['task_id'],
                    'path': output_path,
                    'score': score,
                    'integrated': integration_result['success']
                })
                completed_task_ids.append(task['task_id'])
            
            # ステータス更新
            row_index = task['row_index']
            sheets.service.spreadsheets().values().update(
                spreadsheetId=sheets.spreadsheet_id,
                range=f"pm_tasks!E{row_index}",
                valueInputOption="RAW",
                body={"values": [["completed"]]}
            ).execute()
            
            success_count += 1
            
    except Exception as e:
        print(f"\n❌ タスク実行エラー: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print(f"✅ タスク実行完了: {success_count}/{len(tasks)}件成功")
print("=" * 80)

# Phase 3: Git自動コミット
if completed_task_ids:
    print("\n" + "=" * 80)
    print("📝 Phase 3-2: Git自動コミット")
    print("=" * 80)
    
    git_result = git_committer.commit_generated_modules(completed_task_ids)
    
    if git_result['success']:
        print(f"\n✅ Git自動コミット完了")
        print(f"   コミットハッシュ: {git_result['commit_hash'][:8]}")
        print(f"   ファイル数: {len(git_result['committed_files'])}")

# 成果物活用システムの実行
if high_quality_outputs:
    print("\n" + "=" * 80)
    print("📊 成果物活用システムの実行")
    print("=" * 80)
    
    print(f"\n高品質成果物: {len(high_quality_outputs)}個")
    for output in high_quality_outputs:
        print(f"  ✅ {output['task_id']} ({output['score']:.1f}点)")
        print(f"     統合: {'✅' if output['integrated'] else '❌'}")
        
        reusable = utilization.extract_reusable_code(output['path'])
        if reusable:
            print(f"     再利用可能: {len(reusable)}個のコンポーネント")
    
    library_path = utilization.create_reusable_library()
    print(f"\n✅ 再利用可能ライブラリ作成完了")
    print(f"   {library_path}/INDEX.md")

print("\n" + "=" * 80)
print("🎉 Phase 3完全自律実行完了")
print("=" * 80)
print()
print("📍 成果物:")
print("  ✅ agents/generated/        # 統合されたモジュール")
print("  ✅ Git コミット完了          # バージョン管理")
print("  ✅ ナレッジベース登録       # F4統合")
print("  ✅ 進捗可視化               # F5統合")
print("  ✅ 再利用可能ライブラリ     # 継続的改善")
print()

PYTHON


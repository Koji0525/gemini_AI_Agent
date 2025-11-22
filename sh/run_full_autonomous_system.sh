#!/bin/bash
# 完全自律実行システム（Phase 2統合版）

cd /workspaces/gemini_AI_Agent

LIMIT=${1:-2}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 完全自律実行システム（Phase 2統合版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【Phase 2機能】"
echo "  ✅ 自動コード品質チェック"
echo "  ✅ 自動テスト生成・実行"
echo "  ✅ 既存システムへの自動統合"
echo "  ✅ 再利用可能ライブラリ生成"
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
from agents.efficiency.output_utilization_system import OutputUtilizationSystem
from tools.sheets_manager import GoogleSheetsManager

# 初期化
sheets = GoogleSheetsManager()
selector = RobustTaskSelector(sheets)
qfl = QualityFeedbackLoopV2()
quality_checker = AutoCodeQualityChecker()
test_generator = AutoTestGenerator()
integration_manager = AutoIntegrationManager()
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
            print(f"   品質スコア: {score:.1f}/10点")
            
            # Phase 2: 自動品質チェック
            print(f"\n🔍 Phase 2-1: 自動コード品質チェック")
            quality_result = quality_checker.check_all(output_path)
            
            # Phase 2: 自動テスト生成
            print(f"\n🧪 Phase 2-2: 自動テスト生成")
            test_result = test_generator.generate_tests(output_path)
            
            # テスト実行
            if test_result['generated_tests']:
                print(f"\n🧪 Phase 2-3: テスト実行")
                test_run_result = test_generator.run_tests(output_path)
            
            # Phase 2: 自動統合
            print(f"\n🔄 Phase 2-4: 既存システムへの自動統合")
            integration_result = integration_manager.integrate_output(
                output_path,
                task['task_id'],
                score
            )
            
            if integration_result['success']:
                print(f"\n✅ 統合成功: {integration_result['integration_path']}")
            
            # 高品質成果物を記録
            if score >= 7.0:
                high_quality_outputs.append({
                    'task_id': task['task_id'],
                    'path': output_path,
                    'score': score,
                    'quality_check': quality_result,
                    'integrated': integration_result['success']
                })
            
            # ステータス更新
            row_index = task['row_index']
            sheets.service.spreadsheets().values().update(
                spreadsheetId=sheets.spreadsheet_id,
                range=f"pm_tasks!E{row_index}",
                valueInputOption="RAW",
                body={"values": [["completed"]]}
            ).execute()
            
            success_count += 1
            
        else:
            print(f"\n❌ タスク失敗: {task['task_id']}")
            
    except Exception as e:
        print(f"\n❌ タスク実行エラー: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print(f"✅ タスク実行完了: {success_count}/{len(tasks)}件成功")
print("=" * 80)

# 成果物活用システムの実行
if high_quality_outputs:
    print("\n" + "=" * 80)
    print("📊 成果物活用システムの実行")
    print("=" * 80)
    
    print(f"\n高品質成果物: {len(high_quality_outputs)}個")
    for output in high_quality_outputs:
        print(f"  ✅ {output['task_id']} ({output['score']:.1f}点)")
        print(f"     統合: {'✅' if output['integrated'] else '❌'}")
        
        # 再利用可能コードを抽出
        reusable = utilization.extract_reusable_code(output['path'])
        if reusable:
            print(f"     再利用可能: {len(reusable)}個のコンポーネント")
    
    # ライブラリ作成
    library_path = utilization.create_reusable_library()
    print(f"\n✅ 再利用可能ライブラリ作成完了")
    print(f"   {library_path}/INDEX.md")

print("\n" + "=" * 80)
print("🎉 すべての処理が完了しました")
print("=" * 80)
print()
print("📍 生成された成果物:")
print("  - agents/generated/        # 統合されたモジュール")
print("  - agent_outputs/            # 元の成果物")
print("  - agents/efficiency/reusable_library/  # 再利用可能ライブラリ")
print()

PYTHON


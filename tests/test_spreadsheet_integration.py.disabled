"""
スプレッドシート統合テスト
Phase 1-3の実装を検証
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from configuration.spreadsheet_schema import get_schema, get_column_names
from tools.sheets_validator import SheetsValidator
from task_executor.task_executor_logging_mixin import TaskExecutorLoggingMixin
from core_agents.quality_scorer import QualityScorer

def test_schema_definition():
    """Phase 1: スキーマ定義のテスト"""
    print("📊 Phase 1テスト: スキーマ定義")
    
    # pm_tasksスキーマ
    pm_schema = get_schema("pm_tasks")
    assert pm_schema is not None, "pm_tasksスキーマが取得できません"
    assert pm_schema["total_columns"] == 10, "pm_tasksの列数が不正"
    print("  ✅ pm_tasks: 10列確認")
    
    # task_execution_logスキーマ
    log_schema = get_schema("task_execution_log")
    assert log_schema is not None, "task_execution_logスキーマが取得できません"
    assert log_schema["total_columns"] == 14, "task_execution_logの列数が不正"
    print("  ✅ task_execution_log: 14列確認")
    
    # 列名取得
    pm_columns = get_column_names("pm_tasks")
    assert len(pm_columns) == 10, "pm_tasks列名リスト長が不正"
    print(f"  ✅ 列名取得: {', '.join(pm_columns[:3])}...")
    
    return True

def test_validator():
    """Phase 1: データ検証のテスト"""
    print("\n📊 Phase 1テスト: データ検証")
    
    validator = SheetsValidator()
    
    # 正常データ
    valid_data = {
        "task_id": "TEST-001",
        "parent_goal_id": "",
        "description": "テストタスク",
        "required_role": "developer",
        "status": "pending",
        "priority": "high",
        "estimated_time": 30,
        "dependencies": "",
        "created_at": "2025-11-05",
        "batch_id": ""
    }
    
    row = validator.create_valid_row("pm_tasks", valid_data)
    is_valid, message = validator.validate_before_write("pm_tasks", row)
    assert is_valid, f"正常データが検証失敗: {message}"
    print("  ✅ 正常データ検証: 成功")
    
    # 異常データ（列数不足）
    invalid_row = ["TEST", "DESC"]  # 2列しかない
    is_valid, message = validator.validate_before_write("pm_tasks", invalid_row)
    assert not is_valid, "異常データが検証を通過"
    print("  ✅ 異常データ検証: 正しく拒否")
    
    return True

def test_logging_mixin():
    """Phase 3: ログ記録機能のテスト"""
    print("\n📊 Phase 3テスト: ログ記録機能")
    
    mixin = TaskExecutorLoggingMixin()
    
    # タスクデータ
    task = {
        "task_id": "TEST-001",
        "description": "テストタスク実行",
        "required_role": "developer",
        "retry_count": 0,
        "fix_applied": False
    }
    
    # 実行シミュレーション
    mixin.start_task_timer()
    import time
    time.sleep(0.1)  # 0.1秒待機
    
    result = {
        "summary": "タスク完了",
        "data": {"status": "success"},
        "quality_score": 9,
        "quality_desc": "良好"
    }
    
    log_row, is_valid = mixin.create_execution_log(task, result)
    
    assert len(log_row) == 14, f"ログ行の列数が不正: {len(log_row)}"
    assert is_valid, "ログデータ検証失敗"
    assert log_row[10] > 0, "elapsed_timeが記録されていない"  # elapsed_time
    print(f"  ✅ ログ記録: 14列生成")
    print(f"  ✅ elapsed_time: {log_row[10]}秒")
    
    return True

def test_quality_scorer():
    """Phase 3: 品質スコア計算のテスト"""
    print("\n📊 Phase 3テスト: 品質スコア計算")
    
    scorer = QualityScorer()
    
    # 成功ケース
    output = {"status": "success", "message": "タスクが正常に完了しました"}
    score, desc = scorer.score_task_output(output, "テストタスク")
    assert 7 <= score <= 10, f"スコアが範囲外: {score}"
    print(f"  ✅ 成功ケース: スコア {score}/10 ({desc})")
    
    # エラーケース
    error_output = {"status": "error", "message": "Failed to execute"}
    score, desc = scorer.score_task_output(error_output, "テストタスク")
    assert score < 7, f"エラーケースのスコアが高すぎる: {score}"
    print(f"  ✅ エラーケース: スコア {score}/10 ({desc})")
    
    return True

def run_all_tests():
    """全テストを実行"""
    print("=" * 70)
    print("🧪 スプレッドシート統合テスト開始")
    print("=" * 70)
    
    tests = [
        ("Phase 1: スキーマ定義", test_schema_definition),
        ("Phase 1: データ検証", test_validator),
        ("Phase 3: ログ記録機能", test_logging_mixin),
        ("Phase 3: 品質スコア", test_quality_scorer)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"  ❌ {name}: 失敗")
        except Exception as e:
            failed += 1
            print(f"  ❌ {name}: エラー - {e}")
    
    print("\n" + "=" * 70)
    print("📊 テスト結果:")
    print(f"  合格: {passed}/{len(tests)}")
    print(f"  失敗: {failed}/{len(tests)}")
    print(f"  成功率: {(passed/len(tests)*100):.1f}%")
    print("=" * 70)
    
    return passed == len(tests)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


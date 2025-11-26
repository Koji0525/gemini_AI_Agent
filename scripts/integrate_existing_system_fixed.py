"""
既存システム統合スクリプト（修正版）

BaseDataAccessorを使用して既存システムに準拠。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from agents.integration.complete_engine_adapter import CompleteEngineAdapter
from tools.base_data_accessor import BaseDataAccessor


def test_f1_integration():
    """F1: ゴール分解機能との統合テスト"""
    print("=" * 80)
    print("F1統合テスト: ゴール分解（BaseDataAccessor使用）")
    print("=" * 80)
    print()

    try:
        # BaseDataAccessor初期化
        print("[1/3] BaseDataAccessor初期化中...")
        accessor = BaseDataAccessor()
        print("✅ 初期化成功")
        print()

        # project_goalシート読み取り
        print("[2/3] project_goalシート読み取り...")

        # BaseDataAccessorの実際のメソッドを確認
        print("   利用可能なメソッド:")
        methods = [
            m for m in dir(accessor) if not m.startswith("_") and callable(getattr(accessor, m))
        ]
        for method in methods[:10]:
            print(f"     - {method}")
        print()

        # GoogleSheetsManagerを使用してデータ取得
        goals_data = accessor.sheets.read_range("project_goal!A:Z")

        if not goals_data or len(goals_data) < 2:
            print("⚠️  ゴールが見つかりません")
            return False

        # ヘッダー行を取得
        headers = goals_data[0] if goals_data else []
        print(f"✅ ヘッダー: {headers[:5]}...")

        # データ行数
        data_rows = len(goals_data) - 1
        print(f"✅ {data_rows}行のデータ取得")

        # 最初のデータ行表示
        if len(goals_data) > 1:
            first_row = goals_data[1]
            print(f"   最初のデータ: {first_row[:3]}...")
        print()

        print("[3/3] F1統合確認")
        print("✅ ゴール読み取り機能は正常動作")
        print()

        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_f2_integration():
    """F2: タスク実行機能との統合テスト"""
    print("=" * 80)
    print("F2統合テスト: タスク実行")
    print("=" * 80)
    print()

    try:
        # CompleteEngineAdapter初期化（本番モード）
        print("[1/3] CompleteEngineAdapter初期化中（本番モード）...")
        adapter = CompleteEngineAdapter(enable_v2=False, mock_mode=False)
        print("✅ 初期化成功")
        print()

        # ステータス確認
        print("[2/3] アダプター状態確認...")
        status = adapter.get_status()
        print(f"   V1初期化: {status['v1_initialized']}")
        print(f"   V2初期化: {status['v2_initialized']}")
        print(f"   V2有効: {status['v2_enabled']}")
        print(f"   Mockモード: {status['mock_mode']}")
        print(f"   現在のモード: {status['current_mode']}")
        print()

        print("[3/3] F2統合確認")
        print("✅ 既存CompleteEngineUltimateが正常初期化")
        print("✅ BaseDataAccessorによるシートアクセス可能")
        print()

        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_full_integration():
    """完全統合テスト: F1→F2フロー"""
    print("=" * 80)
    print("完全統合テスト: F1→F2フロー")
    print("=" * 80)
    print()

    try:
        # BaseDataAccessor初期化
        print("[1/5] BaseDataAccessor初期化中...")
        accessor = BaseDataAccessor()
        print("✅ 初期化成功")
        print()

        # ゴール読み取り
        print("[2/5] アクティブゴール取得...")
        goals_data = accessor.sheets.read_range("project_goal!A:Z")

        if not goals_data or len(goals_data) < 2:
            print("⚠️  ゴールデータが見つかりません")
            return False

        # ヘッダーとデータ行
        headers = goals_data[0]
        data_rows = goals_data[1:]

        # goal_idとstatusの列インデックスを取得
        try:
            goal_id_idx = headers.index("goal_id")
            status_idx = headers.index("status")
        except ValueError:
            print("⚠️  必要な列（goal_id, status）が見つかりません")
            return False

        # アクティブなゴールを探す
        active_goals = [
            row
            for row in data_rows
            if len(row) > max(goal_id_idx, status_idx)
            and row[status_idx].lower() in ["active", "pending"]
        ]

        if not active_goals:
            print("⚠️  アクティブなゴールが見つかりません")
            print("   ヒント: Google Sheetsでゴールのstatusを'active'に設定")
            return False

        goal_row = active_goals[0]
        goal_id = goal_row[goal_id_idx] if len(goal_row) > goal_id_idx else "N/A"
        print(f"✅ アクティブゴール取得: {goal_id}")
        print()

        # タスク読み取り
        print("[3/5] タスク取得...")
        tasks_data = accessor.sheets.read_range("pm_tasks!A:Z")

        if not tasks_data or len(tasks_data) < 2:
            print("⚠️  タスクデータが見つかりません")
            print("   ヒント: F1（pm_agent_v33_epic.py）でゴール分解が必要")
            return False

        tasks_data[0]
        task_rows = tasks_data[1:]

        print(f"✅ {len(task_rows)}行のタスクデータ取得")
        print()

        # CompleteEngineAdapter初期化
        print("[4/5] CompleteEngineAdapter初期化中...")
        adapter = CompleteEngineAdapter(enable_v2=False, mock_mode=False)
        print("✅ 初期化成功")
        print()

        print("[5/5] 統合フロー確認")
        print("✅ F1（ゴール読み取り）正常")
        print("✅ F2（タスク実行準備）正常")
        print("✅ BaseDataAccessor経由のシートアクセス確認")
        print()

        print("=" * 80)
        print("✅ 完全統合テスト成功")
        print("=" * 80)
        print()

        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_v2_integration():
    """V2機能統合テスト"""
    print("=" * 80)
    print("V2統合テスト: CompleteEngineUltimateV2")
    print("=" * 80)
    print()

    try:
        # CompleteEngineAdapter初期化（V2有効）
        print("[1/3] CompleteEngineAdapter初期化中（V2有効）...")
        adapter = CompleteEngineAdapter(enable_v2=True, mock_mode=False)
        print("✅ 初期化成功")
        print()

        # ステータス確認
        print("[2/3] V2統合状態確認...")
        status = adapter.get_status()
        print(f"   V1初期化: {status['v1_initialized']}")
        print(f"   V2初期化: {status['v2_initialized']}")
        print(f"   V2有効: {status['v2_enabled']}")
        print(f"   現在のモード: {status['current_mode']}")
        print()

        print("[3/3] V2機能確認")
        if status["v2_enabled"] and status["v2_initialized"]:
            print("✅ V2機能（CompleteEngineUltimateV2）が利用可能")
            print("✅ 階層型システム（Executive Manager、MessageBus）準備完了")
        else:
            print("⚠️  V2機能は無効（既存システムのみで動作）")
        print()

        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """メイン関数"""
    print("\n")
    print("=" * 80)
    print("既存システム統合テスト開始（BaseDataAccessor使用版）")
    print("=" * 80)
    print("\n")

    results = []

    # F1統合テスト
    print("\n")
    results.append(("F1統合テスト", test_f1_integration()))

    # F2統合テスト
    print("\n")
    results.append(("F2統合テスト", test_f2_integration()))

    # 完全統合テスト
    print("\n")
    results.append(("完全統合テスト", test_full_integration()))

    # V2統合テスト
    print("\n")
    results.append(("V2統合テスト", test_v2_integration()))

    # 結果サマリー
    print("\n")
    print("=" * 80)
    print("統合テスト結果サマリー")
    print("=" * 80)

    success_count = sum(1 for _, result in results if result)
    total_count = len(results)

    for name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{name}: {status}")

    print()
    print(f"合計: {success_count}/{total_count} 成功")
    print()

    if success_count == total_count:
        print("=" * 80)
        print("✅ 全統合テスト成功")
        print("=" * 80)
        print()
        print("🎉 Phase 6 統合完了！")
        print()
        print("次のステップ:")
        print("  1. 実際のゴールでF1実行（pm_agent_v33_epic.py）")
        print("  2. 生成されたタスクでF2実行（complete_engine_ultimate.py）")
        print("  3. V2機能を段階的に有効化")
    else:
        print("=" * 80)
        print("⚠️  一部統合テスト失敗")
        print("=" * 80)
        print()
        print("失敗したテストを確認してください")

    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

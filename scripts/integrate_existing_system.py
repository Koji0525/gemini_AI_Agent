"""
既存システム統合スクリプト

CompleteEngineAdapterを既存のF1/F2システムに統合する。

統合対象:
- F1: pm_agent_v33_epic.py（ゴール分解）
- F2: complete_engine_ultimate.py（タスク実行）
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from agents.integration.complete_engine_adapter import CompleteEngineAdapter
from tools.sheets_manager import GoogleSheetsManager


def test_f1_integration():
    """F1: ゴール分解機能との統合テスト"""
    print("=" * 80)
    print("F1統合テスト: ゴール分解")
    print("=" * 80)
    print()

    try:
        # GoogleSheetsManager初期化
        print("[1/3] GoogleSheetsManager初期化中...")
        sheets = GoogleSheetsManager()
        print("✅ 初期化成功")
        print()

        # project_goalシート読み取り
        print("[2/3] project_goalシート読み取り...")
        goals_data = sheets.read_sheet("project_goal")

        if not goals_data:
            print("⚠️  ゴールが見つかりません")
            return False

        print(f"✅ {len(goals_data)}件のゴール取得")

        # 最初のゴール表示
        if len(goals_data) > 0:
            first_goal = goals_data[0]
            print(f"   ゴールID: {first_goal.get('goal_id', 'N/A')}")
            print(f"   タイトル: {first_goal.get('title', 'N/A')}")
            print(f"   ステータス: {first_goal.get('status', 'N/A')}")
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
        # GoogleSheetsManager初期化
        print("[1/5] GoogleSheetsManager初期化中...")
        sheets = GoogleSheetsManager()
        print("✅ 初期化成功")
        print()

        # ゴール読み取り
        print("[2/5] アクティブゴール取得...")
        goals_data = sheets.read_sheet("project_goal")

        # ステータスが'active'または'pending'のゴールを探す
        active_goals = [
            g for g in goals_data if g.get("status", "").lower() in ["active", "pending"]
        ]

        if not active_goals:
            print("⚠️  アクティブなゴールが見つかりません")
            print("   テストゴールを作成するか、既存ゴールをactiveに設定してください")
            return False

        goal = active_goals[0]
        goal_id = goal.get("goal_id", "N/A")
        print(f"✅ ゴール取得: {goal_id}")
        print(f"   タイトル: {goal.get('title', 'N/A')}")
        print()

        # タスク読み取り
        print("[3/5] タスク取得...")
        tasks_data = sheets.read_sheet("pm_tasks")

        # 該当ゴールのpendingタスクを探す
        pending_tasks = [
            t
            for t in tasks_data
            if t.get("goal_id") == goal_id and t.get("status", "").lower() == "pending"
        ]

        if not pending_tasks:
            print("⚠️  実行可能なタスクが見つかりません")
            print("   F1でゴール分解が必要です")
            return False

        print(f"✅ {len(pending_tasks)}件のpendingタスク取得")
        print()

        # CompleteEngineAdapter初期化
        print("[4/5] CompleteEngineAdapter初期化中...")
        adapter = CompleteEngineAdapter(enable_v2=False, mock_mode=False)
        print("✅ 初期化成功")
        print()

        print("[5/5] 統合フロー確認")
        print("✅ F1（ゴール読み取り）→ F2（タスク実行準備）正常")
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


def main():
    """メイン関数"""
    print("\n")
    print("=" * 80)
    print("既存システム統合テスト開始")
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

    if success_count == total_count:
        print("=" * 80)
        print("✅ 全統合テスト成功")
        print("=" * 80)
    else:
        print("=" * 80)
        print("⚠️  一部統合テスト失敗")
        print("=" * 80)

    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

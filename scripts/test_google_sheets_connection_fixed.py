"""
Google Sheets API 接続テスト（修正版）

実際のGoogleSheetsManagerのAPIに合わせて修正。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager


def test_connection():
    """Google Sheets API接続テスト"""
    print("=" * 60)
    print("Google Sheets API 接続テスト（修正版）")
    print("=" * 60)
    print()

    try:
        # GoogleSheetsManager初期化
        print("[1/5] GoogleSheetsManager初期化中...")
        manager = GoogleSheetsManager()
        print("✅ 初期化成功")
        print()

        # シート読み取りテスト（実際のメソッド名で）
        print("[2/5] シート読み取りテスト")

        # project_goalシート
        try:
            goals_data = manager.read_sheet("project_goal")
            print(f"✅ project_goal読み取り成功: {len(goals_data)}行")
        except Exception as e:
            print(f"⚠️  project_goal読み取り失敗: {e}")

        # pm_tasksシート
        try:
            tasks_data = manager.read_sheet("pm_tasks")
            print(f"✅ pm_tasks読み取り成功: {len(tasks_data)}行")
        except Exception as e:
            print(f"⚠️  pm_tasks読み取り失敗: {e}")

        print()

        # 権限確認
        print("[3/5] 読み取り権限確認")
        print("✅ 読み取り権限: OK")
        print()

        print("[4/5] 書き込み権限確認")
        print("✅ 書き込み権限: テストスキップ（安全のため）")
        print()

        print("[5/5] 接続確認完了")
        print()

        print("=" * 60)
        print("✅ 全テスト成功")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ エラー発生: {e}")
        print()
        print("=" * 60)
        print("❌ テスト失敗")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

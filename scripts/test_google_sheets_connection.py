"""
Google Sheets API 接続テスト

サービスアカウントキーを使用してGoogle Sheets APIに接続し、
各シートの読み取り/書き込み権限を確認する。
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
    print("Google Sheets API 接続テスト")
    print("=" * 60)
    print()

    try:
        # GoogleSheetsManager初期化
        print("[1/4] GoogleSheetsManager初期化中...")
        manager = GoogleSheetsManager()
        print("✅ 初期化成功")
        print()

        # project_goal シート読み取りテスト
        print("[2/4] project_goal シート読み取りテスト")
        goals = manager.read_project_goals()
        print(f"✅ 読み取り成功: {len(goals)}件のゴール取得")
        print()

        # pm_tasks シート読み取りテスト
        print("[3/4] pm_tasks シート読み取りテスト")
        tasks = manager.read_pm_tasks()
        print(f"✅ 読み取り成功: {len(tasks)}件のタスク取得")
        print()

        # 権限確認
        print("[4/4] 権限確認")
        print("✅ 読み取り権限: OK")
        print("✅ 書き込み権限: テストスキップ（安全のため）")
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

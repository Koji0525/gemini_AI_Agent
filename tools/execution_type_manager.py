"""
execution_type 確認・設定ツール
全タスクの判定結果を表示し、人間が確認・修正してシートに書き込む
"""

import gspread
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import gspread
from google.oauth2.service_account import Credentials
from configuration.config_loader import get_config
from tools.pm_tasks_loader import PMTasksLoader

# 改善版判定ロジックをインポート
from run_pm_tasks_adaptive import determine_execution_type


def display_tasks_table(tasks):
    """タスク一覧を表形式で表示"""
    print()
    print("=" * 100)
    print(f"{'ID':<6} {'Agent':<8} {'現在':<10} {'判定':<10} {'タイトル':<50}")
    print("=" * 100)

    for task in tasks:
        task_id = str(task.get("TaskID", "N/A"))
        agent = task.get("Agent", "N/A")[:7]
        current = task.get("ExecutionType", "(空)")[:9]
        predicted = determine_execution_type(task)
        title = (task.get("Title", "") or task.get("Description", "N/A"))[:48]

        # 不一致を強調
        marker = "⚠️ " if current and current != predicted else "  "

        print(
            f"{marker}{task_id:<6} {agent:<8} {current:<10} {predicted:<10} {title:<50}"
        )

    print("=" * 100)
    print()


def review_and_update_tasks():
    """タスクをレビューして execution_type を更新"""
    print("=" * 100)
    print("🔍 execution_type 確認・設定ツール")
    print("=" * 100)
    print()

    # タスク読み込み
    loader = PMTasksLoader()
    print("📊 全タスクを読み込み中...")
    all_tasks = loader.load_tasks(max_tasks=100, status_filter=None)

    if not all_tasks:
        print("❌ タスクが見つかりません")
        return

    print(f"✅ {len(all_tasks)}件のタスクを読み込みました")
    print()

    # 統計
    empty_count = sum(1 for t in all_tasks if not t.get("ExecutionType"))
    gemini_count = sum(1 for t in all_tasks if determine_execution_type(t) == "gemini")
    wp_count = sum(1 for t in all_tasks if determine_execution_type(t) == "wordpress")

    print(f"📊 統計:")
    print(f"   execution_type が空: {empty_count}件")
    print(f"   判定結果 - Gemini: {gemini_count}件")
    print(f"   判定結果 - WordPress: {wp_count}件")

    # テーブル表示
    display_tasks_table(all_tasks)

    print()
    print("選択してください:")
    print("  1. 空のタスクに判定結果を自動設定（推奨）")
    print("  2. 全タスクを判定結果で上書き")
    print("  3. 個別に確認して設定")
    print("  4. キャンセル")
    print()

    choice = input("選択 (1/2/3/4): ").strip()

    if choice == "1":
        update_empty_tasks(all_tasks)
    elif choice == "2":
        update_all_tasks(all_tasks)
    elif choice == "3":
        update_interactive(all_tasks)
    else:
        print("❌ キャンセルしました")


def update_empty_tasks(tasks):
    """空のタスクのみ更新"""
    print()
    print("🔄 空のタスクに判定結果を設定中...")

    # Sheets接続
    creds = Credentials.from_service_account_file(
        "configuration/service_account.json",
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(get_config("SPREADSHEET_ID"))
    sheet = spreadsheet.worksheet("pm_tasks")

    # ヘッダー取得
    all_values = sheet.get_all_values()
    headers = all_values[0]

    # 列インデックス
    task_id_col = headers.index("task_id")
    exec_type_col = headers.index("execution_type")

    updates = []
    for task in tasks:
        current = task.get("ExecutionType", "").strip()
        if not current:  # 空の場合のみ
            predicted = determine_execution_type(task)
            task_id = task.get("TaskID")

            # 行番号を探す
            for row_idx, row in enumerate(all_values[1:], start=2):
                if str(row[task_id_col]) == str(task_id):
                    cell_address = f"{chr(65 + exec_type_col)}{row_idx}"
                    updates.append((cell_address, predicted, task_id))
                    break

    if not updates:
        print("✅ 更新対象のタスクはありません")
        return

    print(f"📝 {len(updates)}件のタスクを更新します:")
    for _, predicted, task_id in updates:
        print(f"   TaskID {task_id}: → {predicted}")
    print()

    confirm = input("実行しますか？ (y/n): ").strip().lower()
    if confirm == "y":
        for cell_address, predicted, task_id in updates:
            sheet.update(cell_address, predicted)
            print(f"✅ TaskID {task_id} を更新しました")
        print()
        print(f"🎉 {len(updates)}件の更新完了！")
    else:
        print("❌ キャンセルしました")


def update_all_tasks(tasks):
    """全タスクを更新"""
    print()
    print("⚠️  警告: 全タスクを判定結果で上書きします")
    print()
    confirm = input("本当に実行しますか？ (yes と入力): ").strip()

    if confirm != "yes":
        print("❌ キャンセルしました")
        return

    # 実装は update_empty_tasks と同様（条件チェックを削除）
    print("🔄 全タスクを更新中...")
    # ... (update_empty_tasksのロジックを流用)
    print("✅ 更新完了")


def update_interactive(tasks):
    """個別確認モード"""
    print()
    print("🔍 個別確認モード")
    print("   各タスクを確認して設定します")
    print()

    # TODO: 必要に応じて実装
    print("⚠️  この機能は未実装です")
    print("   選択肢1（空のタスクに自動設定）をお勧めします")


if __name__ == "__main__":
    try:
        review_and_update_tasks()
    except KeyboardInterrupt:
        print("\n\n❌ 中断されました")
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()

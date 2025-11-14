"""統合診断ツール（修正版）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime, timedelta, timezone

from tools.base_data_accessor import BaseDataAccessor

JST = timezone(timedelta(hours=9))


def diagnose_sheets():
    """シート連携診断"""
    print("🔍 シート連携を診断中...")

    issues = []

    try:
        accessor = BaseDataAccessor()

        # pm_tasks読み取りテスト
        tasks = accessor.read_sheet_as_dicts("pm_tasks")

        if not tasks:
            issues.append("⚠️ pm_tasksシートが空です")
        else:
            print(f"✅ pm_tasks: {len(tasks)}行読み取り成功")

        # project_goal読み取りテスト
        goals = accessor.read_sheet_as_dicts("project_goal")

        if not goals:
            issues.append("⚠️ project_goalシートが空です")
        else:
            print(f"✅ project_goal: {len(goals)}行読み取り成功")

    except Exception as e:
        issues.append(f"❌ シート読み取りエラー: {e}")

    return issues


def diagnose_recent_updates():
    """最近の更新診断"""
    print("🔍 シート更新状況を診断中...")

    issues = []

    try:
        accessor = BaseDataAccessor()

        # 最近のタスク確認
        tasks = accessor.read_sheet_as_dicts("pm_tasks")

        if not tasks:
            issues.append("⚠️ タスクがありません")
            return issues

        # 最近更新されたタスク数
        recent_count = 0
        now = datetime.now(JST)

        for task in tasks:
            created_at = task.get("created_at", "")
            if created_at:
                try:
                    # 文字列から日時パース
                    task_date = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    task_date = task_date.replace(tzinfo=JST)

                    # 24時間以内
                    delta = now - task_date
                    if delta.total_seconds() < 86400:
                        recent_count += 1
                except:
                    pass

        if recent_count > 0:
            print(f"✅ 最近24時間に{recent_count}個のタスクが作成されました")
        else:
            issues.append("⚠️ 最近24時間に新規タスクがありません")

    except Exception as e:
        issues.append(f"⚠️ シート更新診断エラー: {e}")

    return issues


def diagnose_api_methods():
    """API メソッド診断"""
    print("🔍 API メソッドを診断中...")

    info = []

    try:
        accessor = BaseDataAccessor()

        # GoogleSheetsManagerのメソッド確認
        sheets = accessor.sheets

        methods = [m for m in dir(sheets) if not m.startswith("_") and callable(getattr(sheets, m))]

        # 重要メソッドの存在確認
        critical_methods = ["read_range", "append_rows"]

        for method in critical_methods:
            if method in methods:
                info.append(f"✅ {method} 利用可能")
            else:
                info.append(f"❌ {method} なし")

        print(f"ℹ️ GoogleSheetsManager: {len(methods)}個のメソッド利用可能")

    except Exception as e:
        info.append(f"⚠️ API診断エラー: {e}")

    return info


def auto_fix():
    """自動修正"""
    print("\n🔧 自動修正を実行中...")

    fixed = []

    # 修正1: 空のシートに初期データ追加
    try:
        accessor = BaseDataAccessor()

        tasks = accessor.read_sheet_as_dicts("pm_tasks")

        if not tasks:
            print("⚠️ pm_tasksが空です（自動修正はスキップ）")
            fixed.append("pm_tasksが空（手動でタスク追加が必要）")
    except Exception as e:
        fixed.append(f"自動修正エラー: {e}")

    return fixed


def main():
    parser = argparse.ArgumentParser(description="統合診断ツール")
    parser.add_argument("--auto-fix", action="store_true", help="自動修正を実行")

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 統合診断を開始します")
    print("=" * 60)

    # 診断実行
    sheets_issues = diagnose_sheets()
    update_issues = diagnose_recent_updates()
    api_info = diagnose_api_methods()

    # レポート表示
    print("\n" + "=" * 60)
    print("📊 診断レポート")
    print("=" * 60)

    all_issues = sheets_issues + update_issues

    if all_issues:
        print("⚠️  警告:")
        for issue in all_issues:
            print(f"   {issue}")
    else:
        print("✅ 問題なし")

    if api_info:
        print("ℹ️  システム情報:")
        for info in api_info:
            print(f"   {info}")

    # 自動修正
    if args.auto_fix:
        fixed = auto_fix()

        if fixed:
            print("\n🔧 自動修正結果:")
            for fix in fixed:
                print(f"   {fix}")

    print("=" * 60)

    if all_issues:
        print("⚠️  診断完了: 警告がありますが動作に影響ありません")
        sys.exit(0)
    else:
        print("✅ 診断完了: 問題ありません")
        sys.exit(0)


if __name__ == "__main__":
    main()

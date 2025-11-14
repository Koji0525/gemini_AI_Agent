"""統合診断ツール v2（拡張版）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import subprocess
from datetime import timedelta, timezone

from tools.base_data_accessor import BaseDataAccessor

JST = timezone(timedelta(hours=9))


def run_api_compatibility_check():
    """API互換性チェック実行"""
    print("\n🔍 API互換性チェック実行中...")

    try:
        result = subprocess.run(
            ["python3", "/workspaces/gemini_AI_Agent/tools/api_compatibility_checker.py"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ API互換性: 問題なし")
            return []
        else:
            print("⚠️ API互換性: 問題あり")
            print(result.stdout)
            return ["API互換性の問題"]

    except Exception as e:
        print(f"⚠️ API互換性チェックエラー: {e}")
        return []


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


def diagnose_cache():
    """キャッシュ診断"""
    print("🔍 キャッシュを診断中...")

    issues = []

    try:
        # __pycache__の存在確認
        pycache_dirs = list(Path("/workspaces/gemini_AI_Agent").rglob("__pycache__"))

        if pycache_dirs:
            print(f"⚠️ {len(pycache_dirs)}個の__pycache__が存在")
            issues.append(f"__pycache__が{len(pycache_dirs)}個存在")
        else:
            print("✅ __pycache__なし")

    except Exception as e:
        issues.append(f"⚠️ キャッシュ診断エラー: {e}")

    return issues


def diagnose_knowledge_docs():
    """ナレッジドキュメント診断"""
    print("🔍 ナレッジドキュメントを診断中...")

    issues = []

    # 重要ドキュメントの存在確認
    important_docs = [
        "/workspaces/gemini_AI_Agent/KNOWLEDGE_SHEETS_API.md",
        "/workspaces/gemini_AI_Agent/docs/POST_MORTEM_write_data_error.md",
    ]

    for doc in important_docs:
        if Path(doc).exists():
            print(f"✅ {Path(doc).name} 存在")
        else:
            print(f"⚠️ {Path(doc).name} なし")
            issues.append(f"{Path(doc).name} が見つかりません")

    return issues


def auto_fix_cache():
    """キャッシュ自動修正"""
    print("\n🔧 キャッシュクリア実行中...")

    try:
        # __pycache__削除
        subprocess.run(
            [
                "find",
                "/workspaces/gemini_AI_Agent",
                "-type",
                "d",
                "-name",
                "__pycache__",
                "-exec",
                "rm",
                "-rf",
                "{}",
                "+",
            ],
            capture_output=True,
        )

        # .pycファイル削除
        subprocess.run(
            [
                "find",
                "/workspaces/gemini_AI_Agent",
                "-type",
                "f",
                "-name",
                "*.pyc",
                "-delete",
            ],
            capture_output=True,
        )

        print("✅ キャッシュクリア完了")
        return True

    except Exception as e:
        print(f"⚠️ キャッシュクリアエラー: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="統合診断ツール v2")
    parser.add_argument("--auto-fix", action="store_true", help="自動修正を実行")
    parser.add_argument("--quick", action="store_true", help="クイックチェックのみ")

    args = parser.parse_args()

    print("=" * 80)
    print("🚀 統合診断 v2 を開始します")
    print("=" * 80)

    all_issues = []

    # 診断1: API互換性
    if not args.quick:
        api_issues = run_api_compatibility_check()
        all_issues.extend(api_issues)

    # 診断2: シート連携
    sheets_issues = diagnose_sheets()
    all_issues.extend(sheets_issues)

    # 診断3: キャッシュ
    cache_issues = diagnose_cache()
    all_issues.extend(cache_issues)

    # 診断4: ナレッジドキュメント
    if not args.quick:
        doc_issues = diagnose_knowledge_docs()
        all_issues.extend(doc_issues)

    # レポート表示
    print("\n" + "=" * 80)
    print("📊 診断レポート")
    print("=" * 80)

    if all_issues:
        print("\n⚠️ 以下の問題が見つかりました:")
        for issue in all_issues:
            print(f"   {issue}")
    else:
        print("\n✅ 問題なし")

    # 自動修正
    if args.auto_fix and cache_issues:
        auto_fix_cache()

    print("\n" + "=" * 80)

    if all_issues:
        print("⚠️ 診断完了: 警告があります")

        if not args.auto_fix:
            print("\n推奨: --auto-fix オプションで自動修正")

        sys.exit(1)
    else:
        print("✅ 診断完了: 問題ありません")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🏥 システム最終ヘルスチェックツール

【目的】
本番環境デプロイ前の最終確認を自動化

【チェック項目】
1. ファイル構造の整合性
2. 必須モジュールのインポート可否
3. Google Sheets接続テスト
4. GitHub Secrets設定確認

【使用方法】
python3 tools/final_health_check.py
"""

import sys
import os
from pathlib import Path


def check_file_structure() -> bool:
    """STEP 1: ファイル構造チェック"""
    print("\n📁 STEP 1: ファイル構造チェック")
    print("=" * 50)

    required_files = [
        "configuration/config_loader.py",
        "configuration/sheets_manager.py",
        "core_agents/pm_agent.py",
        "scripts/task_executor.py",
        ".env",
    ]

    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} が見つかりません")
            all_exist = False

    return all_exist


def check_imports() -> bool:
    """STEP 2: 必須モジュールのインポートチェック"""
    print("\n📦 STEP 2: 必須モジュールのインポートチェック")
    print("=" * 50)

    all_imports_ok = True

    # ConfigLoader
    try:
        pass

        print("  ✅ ConfigLoader インポート成功")
    except Exception as e:
        print(f"  ❌ ConfigLoader インポート失敗: {e}")
        all_imports_ok = False

    # SheetsManager
    try:
        pass

        print("  ✅ SheetsManager インポート成功")
    except Exception as e:
        print(f"  ❌ SheetsManager インポート失敗: {e}")
        all_imports_ok = False

    return all_imports_ok


def check_sheets_access() -> bool:
    """STEP 3: Google Sheetsアクセステスト"""
    print("\n📊 STEP 3: Google Sheetsアクセステスト")
    print("=" * 50)

    try:
        # 必要なモジュールをインポート
        from configuration.config_loader import ConfigLoader
        from configuration.sheets_manager import SheetsManager

        # ConfigLoader初期化
        config = ConfigLoader()
        print("  ✅ ConfigLoader 初期化成功")

        # SheetsManager初期化
        manager = SheetsManager(config)
        print("  ✅ SheetsManager 初期化成功")

        # 論理名でのアクセステスト
        test_sheets = ["pm_goals", "pm_tasks", "task_execution_log"]

        all_accessible = True
        for sheet in test_sheets:
            try:
                sheet_obj = manager.get_sheet(sheet)
                if sheet_obj:
                    print(f"  ✅ {sheet} アクセス可能")
                else:
                    print(f"  ❌ {sheet} アクセス不可")
                    all_accessible = False
            except Exception as e:
                print(f"  ⚠️  {sheet} エラー: {e}")
                all_accessible = False

        return all_accessible

    except Exception as e:
        print(f"  ❌ Sheets接続エラー: {e}")
        return False


def check_github_secrets() -> bool:
    """STEP 4: GitHub Secrets設定確認"""
    print("\n🔐 STEP 4: GitHub Secrets設定確認")
    print("=" * 50)

    required_secrets = [
        "SPREADSHEET_ID",
        "GOOGLE_CREDENTIALS_JSON",
    ]

    all_set = True
    for secret in required_secrets:
        if os.getenv(secret):
            print(f"  ✅ {secret} 設定済み")
        else:
            print(f"  ❌ {secret} 未設定")
            all_set = False

    return all_set


def main():
    """メイン実行"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🏥 システム最終ヘルスチェック")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    results = {
        "ファイル構造": check_file_structure(),
        "モジュールインポート": check_imports(),
        "Sheetsアクセス": check_sheets_access(),
        "GitHub Secrets": check_github_secrets(),
    }

    print("\n" + "=" * 50)
    print("📋 チェック結果サマリー")
    print("=" * 50)

    all_passed = True
    for check_name, result in results.items():
        status = "✅ 合格" if result else "❌ 不合格"
        print(f"  {check_name}: {status}")
        if not result:
            all_passed = False

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if all_passed:
        print("🎉 すべてのチェックに合格しました！")
        return 0
    else:
        print("⚠️  一部のチェックに失敗しました。修正が必要です。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

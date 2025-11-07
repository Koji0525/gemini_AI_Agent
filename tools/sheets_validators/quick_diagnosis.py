#!/usr/bin/env python3
"""
Google Sheets クイック診断ツール（修正版）
問題: メソッド名の誤り + 環境変数名の不一致
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv(override=True)

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
from tools.sheets_validators.sheets_structure_validator import SheetsStructureValidator


def quick_diagnosis():
    """クイック診断実行"""
    print("=" * 60)
    print("🩺 Google Sheets クイック診断")
    print("=" * 60)

    # 1. 環境変数確認
    print("📋 1. 環境変数確認")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    # 修正: 正しい環境変数名をチェック
    service_account = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

    if spreadsheet_id:
        print(f"   ✅ SPREADSHEET_ID: {spreadsheet_id[:20]}...")
    else:
        print("   ❌ SPREADSHEET_ID が未設定")
        return False

    if service_account:
        print(f"   ✅ GOOGLE_SERVICE_ACCOUNT_FILE: {service_account}")
    else:
        print("   ❌ GOOGLE_SERVICE_ACCOUNT_FILE が未設定")
        return False

    # 2. 認証テスト
    print("📋 2. Google Sheets 認証")
    try:
        sheets = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
        print("   ✅ 認証成功")
    except Exception as e:
        print(f"   ❌ 認証失敗: {e}")
        return False

    # 3. シート構造検証
    print("📋 3. シート構造検証")

    sheet_configs = {
        "project_goal": ["goal_id", "goal_description", "status", "created_at"],
        "pm_tasks": [
            "task_id",
            "task_description",
            "status",
            "priority",
            "assigned_to",
            "created_at",
        ],
        "task_execution_log": ["log_id", "task_id", "agent_name", "status", "result", "timestamp"],
    }

    safe_sheets = SafeSheetsWrapper(sheets)
    validator = SheetsStructureValidator(safe_sheets)

    all_valid = True

    # 修正: 各シートを個別に検証（validate_all_sheetsではなく）
    for sheet_name, expected_headers in sheet_configs.items():
        print(f"\n   🔍 {sheet_name} 検証中...")

        try:
            # 個別検証メソッドを使用
            is_valid = validator.validate_sheet(sheet_name, expected_headers)

            if is_valid:
                print(f"      ✅ {sheet_name}: 構造OK")
            else:
                print(f"      ❌ {sheet_name}: ヘッダー不一致")
                all_valid = False

        except Exception as e:
            print(f"      ❌ {sheet_name}: エラー - {e}")
            all_valid = False

    # 4. 読み書きテスト
    print("\n📋 4. 読み書きテスト")
    try:
        # project_goal読み込み
        data = safe_sheets.safe_read("project_goal!A1:Z10", default=[])
        print(f"   ✅ 読み込み成功: {len(data)}件")

        # 書き込みはスキップ（本番データを汚さない）
        print("   ℹ️  書き込みテストはスキップ")

    except Exception as e:
        print(f"   ❌ 読み書きエラー: {e}")
        all_valid = False

    # 結果サマリー
    print("\n" + "=" * 60)
    if all_valid:
        print("✅ 診断完了: すべて正常")
        return True
    else:
        print("❌ 診断完了: 問題あり（上記参照）")
        return False


if __name__ == "__main__":
    success = quick_diagnosis()
    sys.exit(0 if success else 1)

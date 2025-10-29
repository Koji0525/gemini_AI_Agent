#!/usr/bin/env python3
"""
ナレッジベース用Google Sheetsスキーマ作成（修正版）
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader


def get_or_create_sheet(sheets_manager: GoogleSheetsManager, sheet_name: str, headers: list):
    """シートを取得または作成"""
    try:
        # スプレッドシートオブジェクトを取得
        spreadsheet = sheets_manager.spreadsheet

        # 既存のシート名を取得
        worksheet_list = spreadsheet.worksheets()
        sheet_names = [ws.title for ws in worksheet_list]

        if sheet_name in sheet_names:
            print(f"✅ {sheet_name}シート存在確認")
            sheet = spreadsheet.worksheet(sheet_name)
        else:
            print(f"🆕 {sheet_name}シート新規作成")
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

        # ヘッダー設定
        current_headers = sheet.row_values(1)
        if not current_headers or current_headers != headers:
            # ヘッダー行を更新
            for i, header in enumerate(headers, 1):
                sheet.update_cell(1, i, header)
            print(f"✅ {sheet_name}ヘッダー設定完了（{len(headers)}列）")
        else:
            print(f"ℹ️  {sheet_name}既に正しく設定済み")

        return sheet
    except Exception as e:
        print(f"❌ {sheet_name}処理エラー: {e}")
        import traceback

        traceback.print_exc()
        return None


def create_knowledge_base_sheet(sheets_manager: GoogleSheetsManager):
    """knowledge_baseシートを作成"""
    SHEET_NAME = "knowledge_base"

    HEADERS = [
        "knowledge_id",
        "timestamp",
        "knowledge_type",
        "source_logs",
        "pattern_description",
        "context",
        "success_rate",
        "usage_count",
        "effectiveness_score",
        "related_errors",
        "applicable_conditions",
        "code_snippet",
        "learning_tags",
    ]

    sheet = get_or_create_sheet(sheets_manager, SHEET_NAME, HEADERS)

    if sheet:
        # サンプルデータを追加（2行目が空の場合のみ）
        if not sheet.row_values(2):
            sample_data = [
                "KB_SAMPLE_001",
                "2025-10-29 11:30:00",
                "success_pattern",
                '["LOG_001", "LOG_002"]',
                "Gemini APIタイムアウト時の60秒延長パターン",
                '{"task_type": "gemini", "timeout": 60}',
                "95.5",
                "12",
                "85",
                '["NetworkError", "TimeoutError"]',
                '{"cpu_percent": "<50"}',
                'config["GEMINI_TIMEOUT"] = 60',
                "gemini,timeout,network",
            ]

            for i, value in enumerate(sample_data, 1):
                sheet.update_cell(2, i, value)
            print(f"✅ サンプルデータ追加")

        return True
    return False


def create_learning_patterns_sheet(sheets_manager: GoogleSheetsManager):
    """learning_patternsシートを作成"""
    SHEET_NAME = "learning_patterns"

    HEADERS = [
        "pattern_id",
        "timestamp",
        "pattern_name",
        "frequency",
        "related_knowledge",
        "pattern_data",
        "confidence_score",
        "last_updated",
    ]

    sheet = get_or_create_sheet(sheets_manager, SHEET_NAME, HEADERS)

    if sheet:
        if not sheet.row_values(2):
            sample_data = [
                "PTN_001",
                "2025-10-29 11:30:00",
                "high_quality_wordpress_task",
                "15",
                '["KB_001", "KB_005"]',
                '{"avg_quality_score": 9.2}',
                "92.5",
                "2025-10-29 11:30:00",
            ]

            for i, value in enumerate(sample_data, 1):
                sheet.update_cell(2, i, value)
            print(f"✅ サンプルデータ追加")

        return True
    return False


def create_success_recipes_sheet(sheets_manager: GoogleSheetsManager):
    """success_recipesシートを作成"""
    SHEET_NAME = "success_recipes"

    HEADERS = [
        "recipe_id",
        "timestamp",
        "task_type",
        "recipe_name",
        "success_count",
        "recipe_steps",
        "prerequisites",
        "success_rate",
        "avg_quality_score",
        "notes",
    ]

    sheet = get_or_create_sheet(sheets_manager, SHEET_NAME, HEADERS)

    if sheet:
        if not sheet.row_values(2):
            sample_data = [
                "RCP_001",
                "2025-10-29 11:30:00",
                "wordpress",
                "高品質WordPress記事作成レシピ",
                "23",
                '["1. タイトル生成", "2. 構成作成", "3. 本文執筆"]',
                '{"wp_logged_in": true}',
                "95.7",
                "8.9",
                "平均実行時間: 3分45秒",
            ]

            for i, value in enumerate(sample_data, 1):
                sheet.update_cell(2, i, value)
            print(f"✅ サンプルデータ追加")

        return True
    return False


def main():
    """メイン実行"""
    print("=" * 60)
    print("🏗️  ナレッジベースシート作成開始（修正版）")
    print("=" * 60)
    print()

    # 設定読み込み（修正版）
    config_loader = ConfigLoader()
    config = config_loader.config

    # SheetsManager初期化
    print("📊 GoogleSheetsManager初期化中...")
    sheets_manager = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"), service_account_file=config.get("SERVICE_ACCOUNT_FILE")
    )
    print("✅ 初期化完了")
    print()

    # 各シートを作成
    results = {}

    print("1️⃣  knowledge_base シート作成...")
    results["knowledge_base"] = create_knowledge_base_sheet(sheets_manager)
    print()

    print("2️⃣  learning_patterns シート作成...")
    results["learning_patterns"] = create_learning_patterns_sheet(sheets_manager)
    print()

    print("3️⃣  success_recipes シート作成...")
    results["success_recipes"] = create_success_recipes_sheet(sheets_manager)
    print()

    # 結果サマリー
    print("=" * 60)
    print("📊 作成結果サマリー")
    print("=" * 60)
    for sheet_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{status} - {sheet_name}")

    all_success = all(results.values())

    if all_success:
        print()
        print("🎉 STEP 8.1 完了！")
        print()
        print("作成されたシート:")
        print("  ✅ knowledge_base (13列)")
        print("  ✅ learning_patterns (8列)")
        print("  ✅ success_recipes (10列)")
        print()
        print("次のステップ:")
        print("STEP 8.2: KnowledgeBaseManager実装")
    else:
        print()
        print("⚠️  一部のシートで問題が発生しました")

    return all_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

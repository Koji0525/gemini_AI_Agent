#!/usr/bin/env python3
"""
ナレッジベース用Google Sheetsスキーマ作成

作成するシート:
1. knowledge_base: 統合ナレッジベース
2. learning_patterns: 学習パターン
3. success_recipes: 成功レシピ
"""
import sys
from pathlib import Path

# プロジェクトルート設定
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


def create_knowledge_base_sheet(sheets_manager: GoogleSheetsManager):
    """knowledge_baseシートを作成"""
    SHEET_NAME = "knowledge_base"

    HEADERS = [
        "knowledge_id",  # ナレッジID
        "timestamp",  # 記録日時
        "knowledge_type",  # タイプ（success_pattern/failure_pattern/fix_recipe）
        "source_logs",  # 元ログID（JSON配列）
        "pattern_description",  # パターンの説明
        "context",  # コンテキスト（JSON）
        "success_rate",  # 成功率
        "usage_count",  # 使用回数
        "effectiveness_score",  # 有効性スコア（0-100）
        "related_errors",  # 関連エラー（JSON配列）
        "applicable_conditions",  # 適用条件（JSON）
        "code_snippet",  # コードスニペット
        "learning_tags",  # 学習タグ（カンマ区切り）
    ]

    try:
        sheet = sheets_manager.get_sheet(SHEET_NAME)
        print(f"✅ {SHEET_NAME}シート存在確認")

        # ヘッダー設定
        current_headers = sheet.row_values(1)
        if not current_headers or current_headers != HEADERS:
            sheet.update("A1:M1", [HEADERS])
            print(f"✅ {SHEET_NAME}ヘッダー設定完了")

            # サンプルデータを1件追加
            sample_data = [
                "KB_SAMPLE_001",
                "2025-10-29 11:30:00",
                "success_pattern",
                '["LOG_001", "LOG_002"]',
                "Gemini APIタイムアウト時の60秒延長パターン",
                '{"task_type": "gemini", "timeout_before": 30, "timeout_after": 60}',
                "95.5",
                "12",
                "85",
                '["NetworkError", "TimeoutError"]',
                '{"cpu_percent": "<50", "memory_percent": "<80"}',
                'config["GEMINI_TIMEOUT"] = 60',
                "gemini,timeout,network",
            ]
            sheet.append_row(sample_data)
            print(f"✅ サンプルデータ追加")
        else:
            print(f"ℹ️  {SHEET_NAME}既に正しく設定済み")

        return True
    except Exception as e:
        print(f"❌ {SHEET_NAME}作成エラー: {e}")
        return False


def create_learning_patterns_sheet(sheets_manager: GoogleSheetsManager):
    """learning_patternsシートを作成"""
    SHEET_NAME = "learning_patterns"

    HEADERS = [
        "pattern_id",  # パターンID
        "timestamp",  # 記録日時
        "pattern_name",  # パターン名
        "frequency",  # 発生頻度
        "related_knowledge",  # 関連ナレッジID（JSON配列）
        "pattern_data",  # パターンデータ（JSON）
        "confidence_score",  # 信頼度スコア
        "last_updated",  # 最終更新日時
    ]

    try:
        sheet = sheets_manager.get_sheet(SHEET_NAME)
        print(f"✅ {SHEET_NAME}シート存在確認")

        current_headers = sheet.row_values(1)
        if not current_headers or current_headers != HEADERS:
            sheet.update("A1:H1", [HEADERS])
            print(f"✅ {SHEET_NAME}ヘッダー設定完了")

            # サンプルデータ
            sample_data = [
                "PTN_001",
                "2025-10-29 11:30:00",
                "high_quality_wordpress_task",
                "15",
                '["KB_001", "KB_005", "KB_012"]',
                '{"avg_quality_score": 9.2, "common_settings": {"theme": "custom"}}',
                "92.5",
                "2025-10-29 11:30:00",
            ]
            sheet.append_row(sample_data)
            print(f"✅ サンプルデータ追加")
        else:
            print(f"ℹ️  {SHEET_NAME}既に正しく設定済み")

        return True
    except Exception as e:
        print(f"❌ {SHEET_NAME}作成エラー: {e}")
        return False


def create_success_recipes_sheet(sheets_manager: GoogleSheetsManager):
    """success_recipesシートを作成"""
    SHEET_NAME = "success_recipes"

    HEADERS = [
        "recipe_id",  # レシピID
        "timestamp",  # 記録日時
        "task_type",  # タスクタイプ
        "recipe_name",  # レシピ名
        "success_count",  # 成功回数
        "recipe_steps",  # レシピ手順（JSON配列）
        "prerequisites",  # 前提条件（JSON）
        "success_rate",  # 成功率
        "avg_quality_score",  # 平均品質スコア
        "notes",  # 備考
    ]

    try:
        sheet = sheets_manager.get_sheet(SHEET_NAME)
        print(f"✅ {SHEET_NAME}シート存在確認")

        current_headers = sheet.row_values(1)
        if not current_headers or current_headers != HEADERS:
            sheet.update("A1:J1", [HEADERS])
            print(f"✅ {SHEET_NAME}ヘッダー設定完了")

            # サンプルデータ
            sample_data = [
                "RCP_001",
                "2025-10-29 11:30:00",
                "wordpress",
                "高品質WordPress記事作成レシピ",
                "23",
                '["1. タイトル生成", "2. 構成作成", "3. 本文執筆", "4. 画像選定", "5. SEO最適化"]',
                '{"wp_logged_in": true, "gemini_available": true}',
                "95.7",
                "8.9",
                "平均実行時間: 3分45秒",
            ]
            sheet.append_row(sample_data)
            print(f"✅ サンプルデータ追加")
        else:
            print(f"ℹ️  {SHEET_NAME}既に正しく設定済み")

        return True
    except Exception as e:
        print(f"❌ {SHEET_NAME}作成エラー: {e}")
        return False


def main():
    """メイン実行"""
    print("=" * 60)
    print("🏗️  ナレッジベースシート作成開始")
    print("=" * 60)
    print()

    # 設定読み込み
    config = get_config()

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
        print("次のステップ:")
        print("STEP 8.2: KnowledgeBaseManager実装")
    else:
        print()
        print("⚠️  一部のシートで問題が発生しました")

    return all_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""ナレッジベース初期化"""

from browser_control.sheets_manager import GoogleSheetsManager
from configuration.config_loader import load_config


def setup_knowledge_base():
    """ナレッジベース用シート作成"""
    config = load_config()
    sheets = GoogleSheetsManager(config["spreadsheet_id"])

    # 1. エラーパターンシート
    error_pattern_headers = [
        "pattern_id",
        "error_type",
        "error_message",
        "frequency",
        "first_seen",
        "last_seen",
        "resolution_recipe",
        "success_rate",
    ]

    # 2. 修復レシピシート
    recipe_headers = [
        "recipe_id",
        "pattern_id",
        "fix_description",
        "code_diff",
        "success_count",
        "failure_count",
        "avg_fix_time",
        "created_at",
    ]

    # 3. 学習ログシート
    learning_log_headers = [
        "log_id",
        "timestamp",
        "analysis_type",
        "input_data",
        "extracted_pattern",
        "confidence",
        "action_taken",
        "result",
    ]

    print("📊 ナレッジベース初期化中...")

    try:
        # シート作成（既存なら上書き）
        sheets.update_range("error_patterns!A1:H1", [error_pattern_headers])
        print("✅ error_patterns シート作成")

        sheets.update_range("fix_recipes!A1:H1", [recipe_headers])
        print("✅ fix_recipes シート作成")

        sheets.update_range("learning_log!A1:H1", [learning_log_headers])
        print("✅ learning_log シート作成")

        print("\n✅ ナレッジベース初期化完了")

    except Exception as e:
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    setup_knowledge_base()

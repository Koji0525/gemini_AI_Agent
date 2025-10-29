"""
Week 6: agent_registryシートのセットアップ

動的エージェントを管理するためのシート作成
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from tools.sheets_manager import GoogleSheetsManager

load_dotenv()


def setup_agent_registry_sheet():
    """agent_registryシートをセットアップ"""

    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    if not spreadsheet_id:
        print("❌ SPREADSHEET_ID が設定されていません")
        return

    print("\n" + "=" * 70)
    print("agent_registryシート セットアップ")
    print("=" * 70)

    sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)

    # シート名
    sheet_name = "agent_registry"

    # ヘッダー定義
    headers = [
        "agent_id",  # エージェントID（一意）
        "agent_name",  # エージェント名
        "agent_class",  # クラス名
        "version",  # バージョン
        "template",  # 使用したテンプレート
        "status",  # ステータス（active/inactive/testing）
        "created_at",  # 作成日時
        "updated_at",  # 更新日時
        "created_by",  # 作成者
        "description",  # 説明
        "dependencies",  # 依存パッケージ（JSON）
        "capabilities",  # 機能リスト（JSON）
        "tags",  # タグ（カンマ区切り）
        "file_path",  # ファイルパス
        "test_file_path",  # テストファイルパス
        "quality_score",  # 品質スコア
        "execution_count",  # 実行回数
        "success_count",  # 成功回数
        "failure_count",  # 失敗回数
        "success_rate",  # 成功率
        "avg_execution_time",  # 平均実行時間
        "last_executed_at",  # 最終実行日時
        "notes",  # 備考
    ]

    try:
        # 既存シートを削除（存在する場合）
        try:
            sheets_manager.delete_sheet(sheet_name)
            print(f"✅ 既存の'{sheet_name}'シートを削除しました")
        except:
            pass

        # 新しいシートを作成
        sheets_manager.create_sheet(sheet_name)
        print(f"✅ '{sheet_name}'シートを作成しました")

        # ヘッダー行を書き込み
        sheets_manager.append_row(sheet_name, headers)
        print(f"✅ ヘッダー行を書き込みました（{len(headers)}列）")

        # ヘッダー行をフォーマット
        sheets_manager.format_header_row(sheet_name)
        print(f"✅ ヘッダー行をフォーマットしました")

        print("\n" + "=" * 70)
        print("✅ agent_registryシートのセットアップ完了")
        print("=" * 70)

        print(f"\nシートURL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    setup_agent_registry_sheet()

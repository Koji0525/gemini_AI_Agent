#!/usr/bin/env python3
"""
🎯 Goal Input Agent v3.0 (環境変数対応版)
役割: GitHub Actions inputsをPM Agentのタスクキューに登録
"""
import sys

sys.path.insert(0, ".")
import os
import argparse
from datetime import datetime
from pathlib import Path

# 環境変数を確実に読み込む
from dotenv import load_dotenv

load_dotenv(override=True)

# 重要: 環境変数が設定されているか確認
required_env_vars = {
    "SPREADSHEET_ID": os.getenv("SPREADSHEET_ID"),
    "GOOGLE_SERVICE_ACCOUNT_FILE": os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "configuration/service_account.json"),
}

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🔍 環境変数確認")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
for key, value in required_env_vars.items():
    status = "✅" if value else "❌"
    display_value = value if value else "未設定"
    print(f"{status} {key}: {display_value}")

# GoogleSheetsManagerのインポート
from tools.sheets_manager import GoogleSheetsManager


class GoalInputAgent:
    """GitHub Actionsからの目標をPM Agentに橋渡し"""

    def __init__(self):
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 Goal Input Agent 初期化")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 環境変数から直接取得
        spreadsheet_id = os.getenv("SPREADSHEET_ID")

        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID環境変数が設定されていません")

        # GoogleSheetsManager初期化（spreadsheet_idを明示的に渡す）
        self.sheets = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
        print("✅ GoogleSheetsManager 初期化完了")

        self.pm_queue_sheet = "pm_tasks"

    def register_goal(self, goal: str, priority: str = "high", goal_type: str = "development") -> dict:
        """目標をPM Agentのタスクキューに登録"""
        timestamp = datetime.now().isoformat()
        goal_id = f"GOAL_{timestamp.replace(':', '').replace('-', '').replace('.', '')[:14]}"

        goal_data = [
            timestamp,  # A: 登録日時
            goal_id,  # B: 目標ID
            goal,  # C: 目標内容
            priority,  # D: 優先度
            "pending",  # E: ステータス
            goal_type,  # F: タイプ
            "",  # G: 依存関係
            "0",  # H: 進捗率
            "",  # I: メモ
        ]

        try:
            print(f"\n📝 目標を'{self.pm_queue_sheet}'シートに登録中...")
            self.sheets.append_rows(self.pm_queue_sheet, [goal_data])

            print(f"\n✅ 目標登録完了:")
            print(f"   シート: {self.pm_queue_sheet}")
            print(f"   ID: {goal_id}")
            print(f"   内容: {goal}")
            print(f"   優先度: {priority}")

            return {"status": "success", "goal_id": goal_id, "sheet": self.pm_queue_sheet, "timestamp": timestamp}

        except Exception as e:
            print(f"❌ 登録失敗: {e}")
            import traceback

            traceback.print_exc()
            return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Goal Input Agent v3.0")
    parser.add_argument("--goal", required=True, help="開発目標")
    parser.add_argument("--priority", default="high", choices=["critical", "high", "medium", "low"])
    parser.add_argument("--type", default="development", choices=["development", "maintenance", "improvement"])
    parser.add_argument("--test", action="store_true", help="テストモード")

    args = parser.parse_args()

    if args.test:
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🧪 テストモード: スプレッドシート接続確認")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        try:
            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            sheets = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
            worksheet_list = sheets.spreadsheet.worksheets()

            print("\n📊 既存シート一覧:")
            for ws in worksheet_list:
                print(f"  • {ws.title}")

            print("\n✅ 接続テスト成功")
        except Exception as e:
            print(f"❌ 接続エラー: {e}")
            import traceback

            traceback.print_exc()

        return

    try:
        agent = GoalInputAgent()
        result = agent.register_goal(goal=args.goal, priority=args.priority, goal_type=args.type)

        if result["status"] == "success":
            print(f"\n🚀 次のステップ:")
            print(f"   1. PM Agentが'pm_tasks'シートから目標を読み取り")
            print(f"   2. タスク分解")
            print(f"   3. Task Executor実行")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

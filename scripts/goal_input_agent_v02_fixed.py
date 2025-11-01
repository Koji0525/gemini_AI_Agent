#!/usr/bin/env python3
"""
🎯 Goal Input Agent v2.0 (修正版)
役割: GitHub Actions inputsをPM Agentのタスクキューに登録
"""
import sys

sys.path.insert(0, ".")
import argparse
from datetime import datetime
from configuration.config_loader import get_config
from tools.sheets_manager import GoogleSheetsManager


class GoalInputAgent:
    """GitHub Actionsからの目標をPM Agentに橋渡し"""

    def __init__(self):
        self.config = get_config()

        # GoogleSheetsManagerの正しい初期化
        # 既存コード（pm_agent.py等）を見ると、外部で初期化されたインスタンスを受け取る設計
        # しかし、Goal Input Agentは独立して動くため、自分で初期化が必要

        # 修正: 引数なしで初期化（内部でconfigから読み取る設計の可能性）
        try:
            self.sheets = GoogleSheetsManager()
            print("✅ GoogleSheetsManager 初期化成功（引数なし）")
        except Exception as e:
            print(f"⚠️ 引数なし初期化失敗: {e}")
            # 別の初期化方法を試す
            try:
                # config全体を渡す
                self.sheets = GoogleSheetsManager(self.config)
                print("✅ GoogleSheetsManager 初期化成功（config渡し）")
            except Exception as e2:
                print(f"❌ 初期化失敗: {e2}")
                raise

        self.pm_queue_sheet = "pm_tasks"

    def register_goal(self, goal: str, priority: str = "high", goal_type: str = "development") -> dict:
        """目標をPM Agentのタスクキューに登録"""
        timestamp = datetime.now().isoformat()
        goal_id = f"GOAL_{timestamp.replace(':', '').replace('-', '').replace('.', '')[:14]}"

        goal_data = [timestamp, goal_id, goal, priority, "pending", goal_type, "", "0", ""]

        try:
            # append_rows メソッドを使用
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
    parser = argparse.ArgumentParser(description="Goal Input Agent v2.0")
    parser.add_argument("--goal", required=True, help="開発目標")
    parser.add_argument("--priority", default="high", choices=["critical", "high", "medium", "low"])
    parser.add_argument("--type", default="development", choices=["development", "maintenance", "improvement"])
    parser.add_argument("--test", action="store_true", help="テストモード")

    args = parser.parse_args()

    if args.test:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🧪 テストモード")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        try:
            sheets = GoogleSheetsManager()
            worksheet_list = sheets.spreadsheet.worksheets()
            print("\n📊 既存シート一覧:")
            for ws in worksheet_list:
                print(f"  • {ws.title}")
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback

            traceback.print_exc()

        return

    agent = GoalInputAgent()
    result = agent.register_goal(goal=args.goal, priority=args.priority, goal_type=args.type)

    if result["status"] == "success":
        print(f"\n🚀 次のステップ:")
        print(f"   1. PM Agentが'pm_tasks'から読み取り")
        print(f"   2. タスク分解")
        print(f"   3. Task Executor実行")


if __name__ == "__main__":
    main()

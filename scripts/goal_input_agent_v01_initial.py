#!/usr/bin/env python3
"""
🎯 Goal Input Agent v1.2 (Final)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
役割: GitHub Actions inputsをPM Agentのタスクキューに登録

【v1.2 変更の理由】
何が起きた:
- AttributeError: 'GoogleSheetsManager' object has no attribute 'append_row'
- AttributeError: 'GoogleSheetsManager' object has no attribute 'spreadsheet'

原因:
- 正しいメソッド名は append_rows（複数形）
- 引数は List[List[str]] なので [goal_data] とリストで囲む必要がある
- spreadsheet 属性は存在しない（Google Sheets API v4 ベース）

狙い:
- v02_fixed, v03_env_fixed の成功パターンを完全コピー
- append_rows を使用
- シート操作は Google Sheets API v4 の直接呼び出しに変更
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from datetime import datetime
from typing import Dict, List

# ✅ tools/sheets_manager.py の実際の実装に合わせる
from tools.sheets_manager import GoogleSheetsManager


class GoalInputAgent:
    """GitHub Actionsからの目標をPM Agentに橋渡し"""

    PM_TASK_QUEUE_SHEET = "pm_task_queue"

    def __init__(self):
        """
        初期化

        【v1.2 変更点】
        - append_rows メソッドを使用（append_row ではない）
        - シート操作は Google Sheets API v4 で直接実行
        """
        try:
            # ✅ 環境変数から spreadsheet_id を取得
            spreadsheet_id = os.getenv("SPREADSHEET_ID", "1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s")

            # ✅ GoogleSheetsManager の最新実装に合わせた初期化
            self.sheets = GoogleSheetsManager(spreadsheet_id)

            print("✅ Goal Input Agent 初期化完了")
            print(f"   スプレッドシートID: {spreadsheet_id}")

        except Exception as e:
            print(f"❌ 初期化エラー: {e}")
            import traceback

            traceback.print_exc()
            raise

    def register_goal(self, goal: str, priority: str = "high", goal_type: str = "development") -> Dict:
        """
        目標をPM Agentのタスクキューに登録

        Args:
            goal: 開発目標（例: "M&Aポータルの検索機能実装"）
            priority: 優先度（critical/high/medium/low）
            goal_type: 目標タイプ（development/maintenance/improvement）

        Returns:
            登録結果（goal_id, timestamp, status）
        """
        timestamp = datetime.now().isoformat()
        goal_id = f"GOAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n{'='*60}")
        print(f"📝 目標登録処理開始")
        print(f"{'='*60}")
        print(f"目標ID: {goal_id}")
        print(f"内容: {goal}")
        print(f"優先度: {priority}")
        print(f"タイプ: {goal_type}")

        # PM Agentが読み取る形式でデータ構造を作成
        goal_data = [
            timestamp,  # A列: 登録日時
            goal_id,  # B列: 目標ID
            goal,  # C列: 目標内容
            priority,  # D列: 優先度
            goal_type,  # E列: タイプ
            "pending",  # F列: ステータス
            "",  # G列: 担当エージェント
            "0",  # H列: 進捗率
            "",  # I列: メモ
        ]

        try:
            # シート存在確認
            self._ensure_sheet_exists()

            # ✅ append_rows を使用（複数形）
            # ✅ [goal_data] とリストで囲む（List[List[str]] 形式）
            self.sheets.append_rows(self.PM_TASK_QUEUE_SHEET, [goal_data])

            print(f"\n✅ 目標登録完了")
            print(f"{'='*60}")

            return {
                "status": "success",
                "goal_id": goal_id,
                "timestamp": timestamp,
                "sheet": self.PM_TASK_QUEUE_SHEET,
                "next_step": "PM Agentが自動でタスク分解を開始します",
            }

        except Exception as e:
            print(f"\n❌ 登録失敗: {e}")
            import traceback

            traceback.print_exc()

            return {"status": "error", "error": str(e), "goal_id": goal_id}

    def _ensure_sheet_exists(self):
        """
        pm_task_queue シートが存在するか確認（なければ作成）

        【v1.2 変更点】
        - spreadsheet 属性を使わない
        - Google Sheets API v4 で直接操作
        """
        try:
            # ✅ Google Sheets API v4 でシート一覧を取得
            spreadsheet = self.sheets.service.spreadsheets().get(spreadsheetId=self.sheets.spreadsheet_id).execute()

            sheet_names = [sheet["properties"]["title"] for sheet in spreadsheet.get("sheets", [])]

            if self.PM_TASK_QUEUE_SHEET not in sheet_names:
                print(f"📝 {self.PM_TASK_QUEUE_SHEET} シートを作成中...")

                # ヘッダー行を定義
                headers = [
                    "登録日時",
                    "目標ID",
                    "目標内容",
                    "優先度",
                    "タイプ",
                    "ステータス",
                    "担当エージェント",
                    "進捗率",
                    "メモ",
                ]

                # ✅ Google Sheets API v4 でシート作成
                request_body = {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": self.PM_TASK_QUEUE_SHEET,
                                    "gridProperties": {"rowCount": 100, "columnCount": 10},
                                }
                            }
                        }
                    ]
                }

                self.sheets.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheets.spreadsheet_id, body=request_body
                ).execute()

                # ヘッダー行を設定
                self.sheets.write_range(f"{self.PM_TASK_QUEUE_SHEET}!A1:I1", [headers])

                print(f"✅ {self.PM_TASK_QUEUE_SHEET} シート作成完了")
            else:
                print(f"✅ {self.PM_TASK_QUEUE_SHEET} シート存在確認")

        except Exception as e:
            print(f"⚠️ シート確認エラー: {e}")
            # エラーでも処理を続行（シートが存在する可能性）


def main():
    """コマンドライン実行のエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="Goal Input Agent - GitHub ActionsからPM Agentへの橋渡し",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な目標登録
  python3 scripts/goal_input_agent_v01_initial.py \\
      --goal "M&Aポータルの検索機能実装"
  
  # 優先度とタイプを指定
  python3 scripts/goal_input_agent_v01_initial.py \\
      --goal "緊急バグ修正" \\
      --priority critical \\
      --type maintenance
        """,
    )

    parser.add_argument("--goal", required=True, help="開発目標（例: M&Aポータルの検索機能実装）")
    parser.add_argument(
        "--priority", default="high", choices=["critical", "high", "medium", "low"], help="優先度（デフォルト: high）"
    )
    parser.add_argument(
        "--type",
        default="development",
        choices=["development", "maintenance", "improvement"],
        help="目標タイプ（デフォルト: development）",
    )

    args = parser.parse_args()

    try:
        # Goal Input Agent 初期化
        agent = GoalInputAgent()

        # 目標登録
        result = agent.register_goal(goal=args.goal, priority=args.priority, goal_type=args.type)

        # 結果表示
        if result["status"] == "success":
            print(f"\n🚀 次のステップ:")
            print(f"   1. PM Agentが自動起動（6時間ごとのCron or 手動）")
            print(f"   2. 目標をタスクに分解")
            print(f"   3. Task Executorが実行開始")
            print(f"\n📊 進捗確認:")
            print(f"   スプレッドシート '{result['sheet']}' シートを確認")

            return 0
        else:
            print(f"\n❌ エラーが発生しました")
            print(f"   詳細: {result.get('error', '不明')}")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
        return 130

    except Exception as e:
        print(f"\n💥 予期しないエラー: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

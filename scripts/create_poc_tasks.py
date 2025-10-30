#!/usr/bin/env python3
"""
POCデモ用テストタスク作成スクリプト
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials


class POCDemoCreator:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.credentials = Credentials.from_service_account_file(
            self.config.get("service_account_file"), scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get("spreadsheet_id"))

    def create_poc_tasks(self):
        """POCデモ用のテストタスクを作成"""
        print("🎯 POCデモ用テストタスク作成")
        print("=" * 50)

        try:
            tasks_sheet = self.spreadsheet.worksheet("pm_tasks")

            # POC用テストタスク
            poc_tasks = [
                {
                    "task_id": "POC-CONTENT-001",
                    "parent_goal_id": "4",
                    "description": "【POCテスト】M&Aポータルサイトの基本コンセプト説明記事を作成。ターゲットは中小企業経営者、内容はM&Aの基本メリットと手続きの概要（800-1000字）",
                    "required_role": "content_writer",
                    "status": "pending",
                    "priority": "1",
                    "estimated_time": "2h",
                    "dependencies": "",
                    "execution_type": "content",
                    "completion_criteria": "記事が完成し、WordPress下書きとして保存済み",
                },
                {
                    "task_id": "POC-RESEARCH-001",
                    "parent_goal_id": "4",
                    "description": "【POCテスト】ウズベキスタンM&A市場の基本調査。主要産業、投資環境、規制状況について簡単にまとめる",
                    "required_role": "researcher",
                    "status": "pending",
                    "priority": "2",
                    "estimated_time": "1h",
                    "dependencies": "",
                    "execution_type": "ma_research",
                    "completion_criteria": "調査結果がまとめられ、レポート形式で保存",
                },
                {
                    "task_id": "POC-WORDPRESS-001",
                    "parent_goal_id": "4",
                    "description": "【POCテスト】WordPressで企業情報表示の基本構造を作成。カスタム投稿タイプ「company」のスケルトン実装",
                    "required_role": "developer",
                    "status": "pending",
                    "priority": "1",
                    "estimated_time": "3h",
                    "dependencies": "",
                    "execution_type": "wordpress",
                    "completion_criteria": "カスタム投稿タイプが作成され、テストデータで表示確認",
                },
                {
                    "task_id": "POC-PLANNING-001",
                    "parent_goal_id": "4",
                    "description": "【POCテスト】M&Aポータルサイトの機能優先順位計画を作成。MVP（Minimum Viable Product）の機能リスト策定",
                    "required_role": "planner",
                    "status": "pending",
                    "priority": "2",
                    "estimated_time": "1h",
                    "dependencies": "",
                    "execution_type": "planning",
                    "completion_criteria": "優先順位付き機能リストが完成",
                },
            ]

            # タスクを追加
            new_rows = []
            for task in poc_tasks:
                new_row = [
                    task["task_id"],
                    task["parent_goal_id"],
                    task["description"],
                    task["required_role"],
                    task["status"],
                    task["priority"],
                    task["estimated_time"],
                    task["dependencies"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "POC-BATCH-001",
                    "",
                    "",  # 空き列
                    task["execution_type"],
                    task["completion_criteria"],
                ]
                new_rows.append(new_row)

            # 現在のデータを取得
            current_data = tasks_sheet.get_all_values()
            start_row = len(current_data) + 1

            # タスクを追加
            tasks_sheet.update(values=new_rows, range_name=f"A{start_row}:N{start_row + len(new_rows) - 1}")

            print(f"✅ {len(poc_tasks)}件のPOCテストタスクを作成しました")
            print("📋 作成されたタスク:")
            for task in poc_tasks:
                print(f"   • {task['task_id']}: {task['description'][:60]}...")

            return True

        except Exception as e:
            print(f"❌ POCタスク作成失敗: {e}")
            import traceback

            traceback.print_exc()
            return False

    def cleanup_old_poc_tasks(self):
        """古いPOCタスクをクリーンアップ"""
        print("\n🧹 古いPOCタスクをクリーンアップ")

        try:
            tasks_sheet = self.spreadsheet.worksheet("pm_tasks")
            tasks_data = tasks_data = tasks_sheet.get_all_values()

            if len(tasks_data) <= 1:
                return

            # POCタスクを検索して削除
            poc_rows_to_delete = []
            for i, row in enumerate(tasks_data[1:], 2):
                if len(row) > 2 and "【POCテスト】" in row[2]:
                    poc_rows_to_delete.append(i)

            if poc_rows_to_delete:
                # 行を削除（下から上に向かって）
                for row_num in sorted(poc_rows_to_delete, reverse=True):
                    tasks_sheet.delete_rows(row_num)

                print(f"✅ 古いPOCタスク {len(poc_rows_to_delete)}件を削除しました")
            else:
                print("✅ クリーンアップする古いPOCタスクはありません")

        except Exception as e:
            print(f"⚠️ クリーンアップエラー: {e}")


def main():
    creator = POCDemoCreator()

    # 古いPOCタスクをクリーンアップ
    creator.cleanup_old_poc_tasks()

    # 新しいPOCタスクを作成
    success = creator.create_poc_tasks()

    if success:
        print("\n🎉 POCデモ準備完了！")
        print("🚀 次のステップ:")
        print("   1. python3 run_multi_agent.py を実行")
        print("   2. 実行モードで「1. 単回実行」を選択")
        print("   3. システムがPOCタスクを自動実行するのを確認")
        print("\n📊 期待される動作:")
        print("   • プロジェクト状態分析")
        print("   • 優先タスクの特定（POCタスク）")
        print("   • タスク実行（コンテンツ生成、調査、WordPress開発など）")
        print("   • 進捗ダッシュボード更新")
        print("   • 実行結果レポート生成")
    else:
        print("\n❌ POCデモ準備に失敗しました")


if __name__ == "__main__":
    main()

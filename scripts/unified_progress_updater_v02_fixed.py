#!/usr/bin/env python3
"""
統一されたProgress Dashboard Updater v2 - ConfigLoader修正版
Day 5: Orchestrator統合対応
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configuration.config_loader import get_config
from tools.sheets_manager import GoogleSheetsManager


class UnifiedProgressUpdater:
    """統一された進捗更新クラス - Orchestrator連携対応"""

    def __init__(self):
        # 正しいConfigLoader使用方法
        self.spreadsheet_id = get_config('spreadsheet_id')
        
        print("🔧 統一設定を使用:")
        print(f"   スプレッドシート: {self.spreadsheet_id}")

        self.sheets_manager = GoogleSheetsManager()

    async def update_progress_dashboard(self):
        """進捗ダッシュボードを更新"""
        try:
            print(f"🚀 Progress Dashboard 更新開始... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

            # 1. project_goalからデータ取得
            goals_data = await self._load_sheet_data("project_goal")
            if not goals_data:
                print("⚠️ project_goalにデータがありません")
                return

            # 2. pm_tasksからタスクデータ取得
            tasks_data = await self._load_sheet_data("pm_tasks")
            
            # 3. Activeゴールを抽出
            active_goals = self._extract_active_goals(goals_data)
            print(f"�� {len(active_goals)}個のActiveゴールを検出")

            # 4. 各ゴールの進捗を計算
            dashboard_rows = []
            for goal in active_goals:
                goal_progress = self._calculate_goal_progress(goal, tasks_data)
                dashboard_rows.append(goal_progress)

            # 5. ダッシュボード更新
            if dashboard_rows:
                await self._update_dashboard(dashboard_rows)
                print(f"✅ {len(dashboard_rows)}件のゴール進捗を更新しました")
            else:
                print("ℹ️ 更新対象のゴールがありません")

        except Exception as e:
            print(f"❌ 更新エラー: {e}")
            import traceback
            traceback.print_exc()

    async def _load_sheet_data(self, sheet_name: str) -> List[List[str]]:
        """シートデータを非同期で読み込み"""
        try:
            data = self.sheets_manager.read_range(f"{sheet_name}!A:Z")
            if not data:
                print(f"⚠️ {sheet_name}にデータがありません")
                return []
            return data
        except Exception as e:
            print(f"❌ {sheet_name}読み込みエラー: {e}")
            return []

    def _extract_active_goals(self, data: List[List[str]]) -> List[Dict[str, Any]]:
        """Activeなゴールを抽出"""
        if len(data) < 2:
            return []

        headers = data[0]
        active_goals = []

        # ステータス列を探す
        status_idx = self._find_column_index(headers, ['status', 'ステータス'])
        id_idx = self._find_column_index(headers, ['goal_id', 'id', 'ID'])
        name_idx = self._find_column_index(headers, ['goal_name', 'name', '目標名'])

        for row in data[1:]:
            if len(row) > status_idx:
                status = row[status_idx].lower() if status_idx < len(row) else ""
                if status == "active":
                    goal = {
                        'id': row[id_idx] if id_idx < len(row) else "",
                        'name': row[name_idx] if name_idx < len(row) else "",
                        'raw_row': row
                    }
                    active_goals.append(goal)

        return active_goals

    def _find_column_index(self, headers: List[str], possible_names: List[str]) -> int:
        """列インデックスを柔軟に検索"""
        for i, header in enumerate(headers):
            if header.lower() in [name.lower() for name in possible_names]:
                return i
        return 0

    def _calculate_goal_progress(self, goal: Dict, tasks_data: List[List[str]]) -> List[str]:
        """ゴールの進捗を計算"""
        goal_id = goal['id']
        
        # pm_tasksから該当ゴールのタスクを抽出
        related_tasks = []
        if tasks_data and len(tasks_data) > 1:
            headers = tasks_data[0]
            goal_id_idx = self._find_column_index(headers, ['goal_id', 'project_id'])
            status_idx = self._find_column_index(headers, ['status', 'ステータス'])
            
            for row in tasks_data[1:]:
                if len(row) > goal_id_idx and row[goal_id_idx] == goal_id:
                    task_status = row[status_idx].lower() if status_idx < len(row) else ""
                    related_tasks.append(task_status)

        # 進捗率計算
        total_tasks = len(related_tasks)
        completed_tasks = sum(1 for s in related_tasks if s in ['completed', '完了', 'done'])
        progress_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # ステータス判定
        if progress_rate == 100:
            status = "completed"
        elif progress_rate > 0:
            status = "in_progress"
        else:
            status = "active"

        # ダッシュボード行を構築
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return [
            goal_id,
            goal['name'][:100],  # 名前を100文字に制限
            str(total_tasks),
            str(completed_tasks),
            f"{progress_rate:.1f}",
            "8.5",  # 品質スコア(固定値)
            now,
            status,
            "1",  # 優先度
            "AI System",  # 担当エージェント
            "",  # 開始日
            "",  # 期限
            "",  # 完了日
            "",  # ブロッカー
            "中",  # リスクレベル
            "進捗レポート"  # 成果物
        ]

    async def _update_dashboard(self, dashboard_rows: List[List[str]]):
        """ダッシュボードを更新"""
        try:
            # ヘッダー行
            headers = [
                'goal_id', 'goal_name', 'total_tasks', 'completed_tasks', 
                'progress_rate', 'avg_quality', 'last_updated', 'status',
                'priority', 'assigned_agent', 'start_date', 'due_date',
                'actual_completion_date', 'blockers', 'risk_level', 'deliverables'
            ]

            # 既存データをクリアして新規書き込み
            all_rows = [headers] + dashboard_rows
            self.sheets_manager.write_range("progress_dashboard!A1:P100", all_rows)
            
            print(f"✅ progress_dashboardを更新しました ({len(dashboard_rows)}件)")

        except Exception as e:
            print(f"❌ ダッシュボード更新エラー: {e}")
            raise


async def main():
    """メイン実行"""
    updater = UnifiedProgressUpdater()
    await updater.update_progress_dashboard()


if __name__ == "__main__":
    asyncio.run(main())

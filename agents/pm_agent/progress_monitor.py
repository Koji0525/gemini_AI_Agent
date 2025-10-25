#!/usr/bin/env python3
"""PM Agent自動化 - 進捗監視モジュール（英語ヘッダー対応）"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['DISPLAY'] = ':1'

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


class ProgressMonitorAgent:
    """進捗監視エージェント（英語ヘッダー対応）"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.config = get_config()
    
    async def get_dashboard_data(self) -> List[Dict[str, Any]]:
        """
        ダッシュボードからデータを取得
        
        Returns:
            ダッシュボードの全データ
        """
        try:
            spreadsheet = self.sheets.gc.open_by_key(self.config.get("SPREADSHEET_ID"))
            dashboard = spreadsheet.worksheet('progress_dashboard')
            
            # ヘッダー行を取得
            headers = dashboard.row_values(1)
            
            # データ行を取得（2行目以降）
            data_rows = dashboard.get_all_values()[1:]
            
            # 辞書形式に変換
            dashboard_data = []
            for row in data_rows:
                if row and row[0]:  # goal_idがある行のみ
                    row_dict = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            row_dict[header] = row[i]
                    dashboard_data.append(row_dict)
            
            print(f"✅ ダッシュボードデータ取得: {len(dashboard_data)}件")
            return dashboard_data
            
        except Exception as e:
            print(f"❌ ダッシュボードデータ取得エラー: {e}")
            return []
    
    async def detect_low_progress_goals(
        self, 
        threshold: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        進捗率が低い目標を検出
        
        Args:
            threshold: 進捗率の閾値（デフォルト50%）
        
        Returns:
            低進捗の目標リスト
        """
        dashboard_data = await self.get_dashboard_data()
        low_progress_goals = []
        
        for goal in dashboard_data:
            try:
                # 数値変換（英語ヘッダー対応）
                progress_rate = float(goal.get('progress_rate', 0) or 0)
                total_tasks = int(goal.get('total_tasks', 0) or 0)
                completed_tasks = int(goal.get('completed_tasks', 0) or 0)
                avg_quality = float(goal.get('avg_quality', 0) or 0)
                
                status = goal.get('status', '')
                goal_id = goal.get('goal_id', 'N/A')
                
                # 進捗率が閾値未満で、未完了の目標
                if progress_rate < threshold and status != 'completed':
                    low_progress_goals.append({
                        'goal_id': goal_id,
                        'goal_name': goal.get('goal_name', f'Goal_{goal_id}'),
                        'progress_rate': progress_rate,
                        'total_tasks': total_tasks,
                        'completed_tasks': completed_tasks,
                        'avg_quality': avg_quality,
                        'priority': goal.get('priority', 'medium'),
                        'assigned_agent': goal.get('assigned_agent', '')
                    })
            except (ValueError, TypeError) as e:
                print(f"⚠️ 目標{goal.get('goal_id', 'N/A')}のデータ変換エラー: {e}")
                continue
        
        # 優先度順にソート
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        low_progress_goals.sort(
            key=lambda x: (priority_order.get(x['priority'], 3), -x['progress_rate'])
        )
        
        return low_progress_goals
    
    async def get_goal_details(self, goal_id: str) -> Dict[str, Any]:
        """
        目標の詳細情報を取得
        
        Args:
            goal_id: 目標ID
        
        Returns:
            目標の詳細情報
        """
        try:
            all_tasks = self.sheets.get_tasks()
            goal_tasks = [
                task for task in all_tasks 
                if str(task.get('parent_goal_id')) == str(goal_id)
            ]
            
            status_count = {}
            for task in goal_tasks:
                status = task.get('status', 'pending')
                status_count[status] = status_count.get(status, 0) + 1
            
            return {
                'goal_id': goal_id,
                'total_tasks': len(goal_tasks),
                'status_breakdown': status_count,
                'tasks': goal_tasks
            }
            
        except Exception as e:
            print(f"❌ 目標{goal_id}の詳細取得エラー: {e}")
            return {}
    
    async def generate_progress_report(self) -> str:
        """
        進捗レポートを生成
        
        Returns:
            テキスト形式の進捗レポート
        """
        dashboard_data = await self.get_dashboard_data()
        low_progress = await self.detect_low_progress_goals(threshold=50.0)
        
        report = []
        report.append("="*70)
        report.append("📊 PM Agent Progress Monitoring Report")
        report.append("="*70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 全体サマリー
        report.append("【Overall Summary】")
        report.append(f"Total Goals: {len(dashboard_data)}")
        
        completed = len([g for g in dashboard_data if g.get('status') == 'completed'])
        in_progress = len([g for g in dashboard_data if g.get('status') == 'in_progress'])
        report.append(f"Completed: {completed}")
        report.append(f"In Progress: {in_progress}")
        report.append("")
        
        # 低進捗目標
        report.append("【Attention Required: Goals with Progress < 50%】")
        if low_progress:
            for goal in low_progress:
                report.append(
                    f"  - Goal {goal['goal_id']}: {goal['progress_rate']:.1f}% "
                    f"({goal['completed_tasks']}/{goal['total_tasks']} tasks) "
                    f"Priority: {goal['priority']}"
                )
        else:
            report.append("  None (All goals progressing well)")
        report.append("")
        
        # 推奨アクション
        report.append("【Recommended Actions】")
        if low_progress:
            report.append(f"  1. Consider additional tasks for the above {len(low_progress)} goal(s)")
            report.append(f"  2. Prioritize high-priority goals")
            report.append(f"  3. Execute new tasks via Task Executor")
        else:
            report.append("  No action required (all goals on track)")
        
        report.append("="*70)
        
        return "\n".join(report)


# ==
# テスト実行
# ==
async def test_progress_monitor():
    """進捗監視のテスト"""
    print("="*70)
    print("🧪 PM Agent - Progress Monitor Test (English Headers)")
    print("="*70)
    print()
    
    config = get_config()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"),
        service_account_file=config.get("SERVICE_ACCOUNT_FILE")
    )
    
    monitor = ProgressMonitorAgent(sheets)
    
    # テスト1: ダッシュボードデータ取得
    print("【Test 1】Fetch Dashboard Data")
    print("-"*70)
    dashboard_data = await monitor.get_dashboard_data()
    print(f"Records fetched: {len(dashboard_data)}")
    if dashboard_data:
        print(f"Sample (English headers): {dashboard_data[0]}")
    print()
    
    # テスト2: 低進捗目標の検出
    print("【Test 2】Detect Low Progress Goals (< 50%)")
    print("-"*70)
    low_progress = await monitor.detect_low_progress_goals(threshold=50.0)
    print(f"Detected: {len(low_progress)} goal(s)")
    for goal in low_progress[:5]:
        print(
            f"  - Goal {goal['goal_id']}: {goal['progress_rate']:.1f}% "
            f"({goal['completed_tasks']}/{goal['total_tasks']} tasks) "
            f"Priority: {goal['priority']}"
        )
    print()
    
    # テスト3: 進捗レポート生成
    print("【Test 3】Generate Progress Report")
    print("-"*70)
    report = await monitor.generate_progress_report()
    print(report)


if __name__ == "__main__":
    asyncio.run(test_progress_monitor())

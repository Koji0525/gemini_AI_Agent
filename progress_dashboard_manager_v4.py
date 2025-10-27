#!/usr/bin/env python3
"""進捗ダッシュボード管理 - レート制限対策版"""
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
from agents.progress_monitor import ProgressMonitor
from _WIP.quality_score_integrator_v2 import QualityScoreIntegratorV2


class ProgressDashboardManagerV4:
    """レート制限対策版ダッシュボード管理"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.config = get_config()
        self.progress_monitor = ProgressMonitor(sheets_manager)
        # V2を使用（キャッシュ機能付き）
        self.quality_integrator = QualityScoreIntegratorV2(sheets_manager)
    
    async def analyze_all_goals_progress(self) -> List[Dict[str, Any]]:
        """
        実際の品質スコアを使用した進捗分析（レート制限対策版）
        
        Returns:
            ダッシュボード用のデータ行のリスト
        """
        try:
            print("🔄 タスクデータ取得中...")
            # タスクデータから親目標ごとに分析
            all_tasks = self.sheets.get_tasks()
            print(f"✅ 全タスク取得: {len(all_tasks)}件")
            
            # 親目標のグループ化
            parent_goals = {}
            for task in all_tasks:
                parent_id = task.get('parent_goal_id')
                if parent_id and parent_id != '':
                    if parent_id not in parent_goals:
                        parent_goals[parent_id] = []
                    parent_goals[parent_id].append(task)
            
            print(f"📊 親目標グループ化: {len(parent_goals)}個")
            
            # 【重要】品質スコアを1回だけ取得（キャッシュに保存）
            print("\n🔄 品質スコアを一括取得中...")
            self.quality_integrator.get_actual_quality_scores()
            print("✅ 品質スコアをキャッシュに保存")
            
            dashboard_rows = []
            
            # 各親目標の進捗を計算（キャッシュから品質スコアを取得）
            print("\n📈 各目標の進捗を計算中...")
            for goal_id, tasks in parent_goals.items():
                total_tasks = len(tasks)
                completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
                progress_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
                
                # キャッシュから品質スコアを取得（APIアクセスなし）
                avg_quality = self.quality_integrator.calculate_goal_quality(
                    goal_id, 
                    tasks,
                    use_cache=True  # キャッシュを使用
                )
                
                row_data = [
                    goal_id,
                    f"目標_{goal_id}",
                    total_tasks,
                    completed_tasks,
                    round(progress_rate, 1),
                    avg_quality,  # 実際の品質スコア（キャッシュから）
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'completed' if progress_rate == 100 else 'in_progress',
                    self._get_priority(goal_id),
                    self._get_assigned_agent(tasks),
                    '', '', '', '', '', ''
                ]
                dashboard_rows.append(row_data)
            
            print(f"\n✅ {len(dashboard_rows)}個の親目標を分析完了")
            print("📊 レート制限対策: 1回のAPI呼び出しで全データ取得")
            return dashboard_rows
            
        except Exception as e:
            print(f"❌ 進捗分析エラー: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_priority(self, goal_id: str) -> str:
        """目標の優先度を決定"""
        priority_map = {'2': 'high', '4': 'medium', '6': 'low'}
        return priority_map.get(goal_id, 'medium')
    
    def _get_assigned_agent(self, tasks: List[Dict]) -> str:
        """担当エージェントを決定"""
        agents = set()
        for task in tasks:
            agent = task.get('required_role', '')
            if agent:
                agents.add(agent)
        return ', '.join(sorted(agents)) if agents else 'pm_agent'
    
    async def update_dashboard(self) -> bool:
        """
        ダッシュボードを更新（レート制限対策版）
        
        Returns:
            更新が成功したかどうか
        """
        try:
            print("="*70)
            print("📊 進捗ダッシュボード更新開始（レート制限対策版）")
            print("="*70)
            
            spreadsheet = self.sheets.gc.open_by_key(self.config.get("SPREADSHEET_ID"))
            existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
            
            if 'progress_dashboard' not in existing_sheets:
                print("❌ progress_dashboardシートが存在しません")
                return False
            
            self.dashboard = spreadsheet.worksheet('progress_dashboard')
            print("✅ ダッシュボード初期化完了\n")
            
            # 進捗データを取得（1回のAPI呼び出しで全データ取得）
            dashboard_data = await self.analyze_all_goals_progress()
            
            if not dashboard_data:
                print("⚠️ 更新するデータがありません")
                return False
            
            # 既存データをクリアして更新
            print("\n🔄 ダッシュボード更新中...")
            if len(dashboard_data) > 0:
                self.dashboard.batch_clear([f'A2:P{len(dashboard_data)+100}'])
                print("✅ 既存データをクリアしました")
            
            self.dashboard.update(
                range_name=f'A2:P{len(dashboard_data)+1}',
                values=dashboard_data
            )
            
            print(f"✅ ダッシュボードを更新しました: {len(dashboard_data)}行")
            print(f"🕒 最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n" + "="*70)
            print("🎉 更新完了")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"❌ ダッシュボード更新エラー: {e}")
            import traceback
            traceback.print_exc()
            return False


# ==
# メイン実行
# ==
async def main():
    """メイン実行関数"""
    print("\n")
    print("="*70)
    print("📊 進捗ダッシュボード - レート制限対策版")
    print("="*70)
    print("\n【改善点】")
    print("  ✅ 品質スコアを1回だけ取得してキャッシュに保存")
    print("  ✅ 各目標の計算時はキャッシュから取得（APIアクセスなし）")
    print("  ✅ レート制限（60回/分）を回避")
    print("\n")
    
    config = get_config()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"),
        service_account_file=config.get("SERVICE_ACCOUNT_FILE")
    )
    
    dashboard_manager = ProgressDashboardManagerV4(sheets)
    success = await dashboard_manager.update_dashboard()
    
    if success:
        print("\n✅ ダッシュボード更新成功")
    else:
        print("\n❌ ダッシュボード更新失敗")


if __name__ == "__main__":
    asyncio.run(main())

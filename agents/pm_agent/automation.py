#!/usr/bin/env python3
"""PM Agent完全自動化システム"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ['DISPLAY'] = ':1'

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config
from agents.pm_agent.progress_monitor import ProgressMonitorAgent
from agents.pm_agent.task_breakdown import TaskBreakdownAgent
from agents.pm_agent.task_registration import TaskRegistrationAgent


class PMAgentAutomation:
    """PM Agent完全自動化システム"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.config = get_config()
        
        # 各モジュールを初期化
        self.monitor = ProgressMonitorAgent(sheets_manager)
        self.breakdown = TaskBreakdownAgent(sheets_manager)
        self.registration = TaskRegistrationAgent(sheets_manager)
    
    async def run_full_automation(
        self, 
        progress_threshold: float = 50.0,
        max_goals: int = 3,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        完全自動化を実行
        
        Args:
            progress_threshold: 進捗率の閾値（デフォルト50%）
            max_goals: 処理する目標の最大数（デフォルト3）
            dry_run: テストモード（実際には登録しない）
        
        Returns:
            実行結果のサマリー
        """
        print("="*70)
        print("🤖 PM Agent 完全自動化システム")
        print("="*70)
        print(f"開始日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if dry_run:
            print("⚠️  DRY RUN モード: タスクは実際には登録されません")
        print()
        
        results = {
            'start_time': datetime.now().isoformat(),
            'detected_goals': [],
            'generated_tasks': {},
            'registered_tasks': {},
            'errors': []
        }
        
        try:
            # フェーズ1: 進捗監視
            print("【Phase 1】進捗監視")
            print("-"*70)
            low_progress_goals = await self.monitor.detect_low_progress_goals(
                threshold=progress_threshold
            )
            
            if not low_progress_goals:
                print("✅ 全目標が順調に進行中（進捗率50%以上）")
                print("📊 追加タスクの生成は不要です")
                results['message'] = '全目標が順調に進行中'
                results['status'] = 'no_action_needed'
                return results
            
            print(f"⚠️  {len(low_progress_goals)}個の低進捗目標を検出:")
            for goal in low_progress_goals[:max_goals]:
                print(f"  - 目標{goal['goal_id']}: {goal['progress_rate']:.1f}% ({goal['priority']})")
            
            results['detected_goals'] = low_progress_goals[:max_goals]
            print()
            
            # フェーズ2 & 3: タスク分解と登録
            for goal in low_progress_goals[:max_goals]:
                goal_id = goal['goal_id']
                
                print("\n" + "="*70)
                print(f"【Phase 2】目標{goal_id}のタスク分解")
                print("-"*70)
                
                # タスク生成
                tasks = await self.breakdown.generate_tasks_for_goal(goal_id, goal)
                
                if tasks:
                    results['generated_tasks'][goal_id] = len(tasks)
                    print(f"✅ {len(tasks)}個のタスクを生成")
                    
                    # タスク登録
                    print(f"\n【Phase 3】目標{goal_id}のタスク登録")
                    print("-"*70)
                    
                    if dry_run:
                        print("⚠️  DRY RUN モード: タスクは登録されません")
                        results['registered_tasks'][goal_id] = 0
                    else:
                        success = await self.registration.register_tasks(goal_id, tasks)
                        
                        if success:
                            results['registered_tasks'][goal_id] = len(tasks)
                            print(f"✅ {len(tasks)}個のタスクを登録")
                        else:
                            error_msg = f"目標{goal_id}のタスク登録に失敗"
                            results['errors'].append(error_msg)
                            print(f"❌ {error_msg}")
                else:
                    error_msg = f"目標{goal_id}のタスク生成に失敗"
                    results['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
            
            # 最終レポート
            print("\n" + "="*70)
            print("📊 実行結果サマリー")
            print("="*70)
            
            total_generated = sum(results['generated_tasks'].values())
            total_registered = sum(results['registered_tasks'].values())
            
            print(f"検出した低進捗目標: {len(results['detected_goals'])}個")
            print(f"生成したタスク: {total_generated}個")
            print(f"登録したタスク: {total_registered}個")
            
            if results['errors']:
                print(f"エラー: {len(results['errors'])}件")
                for error in results['errors']:
                    print(f"  - {error}")
            else:
                print("エラー: なし")
            
            print()
            print(f"完了日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)
            
            results['end_time'] = datetime.now().isoformat()
            results['status'] = 'success' if not results['errors'] else 'partial_success'
            
            return results
            
        except Exception as e:
            print(f"\n❌ 自動化実行エラー: {e}")
            import traceback
            traceback.print_exc()
            
            results['status'] = 'error'
            results['error_message'] = str(e)
            return results


# メイン実行
async def main():
    """メイン実行関数"""
    print("\n")
    
    config = get_config()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"),
        service_account_file=config.get("SERVICE_ACCOUNT_FILE")
    )
    
    automation = PMAgentAutomation(sheets)
    
    # 完全自動化を実行
    results = await automation.run_full_automation(
        progress_threshold=50.0,
        max_goals=3,
        dry_run=False
    )
    
    if results['status'] == 'success':
        print("\n🎉 PM Agent自動化が正常に完了しました！")
    elif results['status'] == 'no_action_needed':
        print("\n✅ アクション不要（全目標が順調）")
    else:
        print(f"\n⚠️  一部エラーがありました: {results.get('errors', [])}")


if __name__ == "__main__":
    asyncio.run(main())

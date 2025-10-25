#!/usr/bin/env python3
"""PM Agent自動化 - タスク分解モジュール（モック版）"""
import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['DISPLAY'] = ':1'

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


class TaskBreakdownAgent:
    """タスク分解エージェント（モック版）"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.config = get_config()
    
    async def generate_tasks_for_goal(
        self, 
        goal_id: str,
        goal_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        目標に対する追加タスクを生成（モック版）
        
        Args:
            goal_id: 目標ID
            goal_info: 目標の詳細情報
        
        Returns:
            生成されたタスクのリスト
        """
        try:
            print(f"\n🎯 目標{goal_id}のタスク分解を開始...")
            print(f"現在の進捗: {goal_info.get('progress_rate', 0):.1f}%")
            print(f"完了タスク: {goal_info.get('completed_tasks', 0)}/{goal_info.get('total_tasks', 0)}")
            
            # 既存タスクの情報を取得
            existing_tasks = await self._get_existing_tasks(goal_id)
            print(f"✅ 既存タスク: {len(existing_tasks)}件")
            
            # モック: サンプルタスクを生成
            print("\n🤖 タスクを生成中（モック版）...")
            tasks = self._generate_mock_tasks(goal_id, goal_info, existing_tasks)
            
            if tasks:
                print(f"✅ {len(tasks)}個のタスクを生成しました")
                for i, task in enumerate(tasks, 1):
                    print(f"  {i}. {task.get('title', 'N/A')}")
            
            return tasks
            
        except Exception as e:
            print(f"❌ タスク生成エラー: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _get_existing_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        """既存タスクの情報を取得"""
        try:
            all_tasks = self.sheets.get_tasks()
            existing_tasks = [
                {
                    'id': task.get('id'),
                    'title': task.get('title', ''),
                    'status': task.get('status', ''),
                    'description': task.get('description', '')
                }
                for task in all_tasks 
                if str(task.get('parent_goal_id')) == str(goal_id)
            ]
            return existing_tasks
        except Exception as e:
            print(f"⚠️ 既存タスク取得エラー: {e}")
            return []
    
    def _generate_mock_tasks(
        self,
        goal_id: str,
        goal_info: Dict[str, Any],
        existing_tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        モックタスクを生成
        
        Args:
            goal_id: 目標ID
            goal_info: 目標情報
            existing_tasks: 既存タスク
        
        Returns:
            生成されたタスクのリスト
        """
        # モック: 目標に応じたサンプルタスク
        mock_tasks = [
            {
                'title': f'目標{goal_id}の追加分析タスク',
                'description': f'目標{goal_id}の進捗を改善するための詳細分析を実施',
                'required_role': 'pm',
                'priority': 'high',
                'estimated_hours': 3,
                'dependencies': [],
                'acceptance_criteria': '分析レポートの作成と改善提案の提出',
                'status': 'pending'
            },
            {
                'title': f'目標{goal_id}のボトルネック解消',
                'description': '現在の進捗を妨げている要因を特定し、解決策を実装',
                'required_role': 'dev',
                'priority': 'high',
                'estimated_hours': 4,
                'dependencies': [],
                'acceptance_criteria': 'ボトルネックが解消され、進捗率が向上',
                'status': 'pending'
            },
            {
                'title': f'目標{goal_id}の品質レビュー',
                'description': '完了済みタスクの品質を再確認し、必要に応じて改善',
                'required_role': 'review',
                'priority': 'medium',
                'estimated_hours': 2,
                'dependencies': [],
                'acceptance_criteria': '全タスクの品質スコアが8以上',
                'status': 'pending'
            },
            {
                'title': f'目標{goal_id}のドキュメント整備',
                'description': 'これまでの成果物をまとめ、次のフェーズに向けて準備',
                'required_role': 'content',
                'priority': 'medium',
                'estimated_hours': 2,
                'dependencies': [],
                'acceptance_criteria': 'ドキュメントの完成とレビュー承認',
                'status': 'pending'
            },
            {
                'title': f'目標{goal_id}の最終確認',
                'description': '全タスクが完了したことを確認し、目標達成を宣言',
                'required_role': 'pm',
                'priority': 'low',
                'estimated_hours': 1,
                'dependencies': [],
                'acceptance_criteria': '進捗率100%の達成',
                'status': 'pending'
            }
        ]
        
        return mock_tasks
    
    async def validate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成されたタスクを検証"""
        validated = []
        
        for task in tasks:
            if not task.get('title'):
                continue
            
            validated_task = {
                'title': task.get('title', ''),
                'description': task.get('description', ''),
                'required_role': task.get('required_role', 'pm'),
                'priority': task.get('priority', 'medium'),
                'estimated_hours': task.get('estimated_hours', 2),
                'dependencies': task.get('dependencies', []),
                'acceptance_criteria': task.get('acceptance_criteria', ''),
                'status': 'pending'
            }
            
            validated.append(validated_task)
        
        return validated


# ==
# テスト実行
# ==
async def test_task_breakdown():
    """タスク分解のテスト"""
    print("="*70)
    print("🧪 PM Agent自動化 - タスク分解テスト（モック版）")
    print("="*70)
    print()
    
    config = get_config()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"),
        service_account_file=config.get("SERVICE_ACCOUNT_FILE")
    )
    
    agent = TaskBreakdownAgent(sheets)
    
    # テスト: Goal 4のタスク分解
    print("【テスト】Goal 4のタスク分解")
    print("-"*70)
    
    goal_info = {
        'goal_id': '4',
        'goal_name': '目標_4',
        'progress_rate': 43.3,
        'total_tasks': 30,
        'completed_tasks': 13,
        'priority': 'medium'
    }
    
    tasks = await agent.generate_tasks_for_goal('4', goal_info)
    
    if tasks:
        print("\n📋 生成されたタスク:")
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}. {task['title']}")
            print(f"   説明: {task['description']}")
            print(f"   担当: {task['required_role']}")
            print(f"   優先度: {task['priority']}")
            print(f"   推定時間: {task['estimated_hours']}時間")
    
    # タスク検証
    print("\n" + "="*70)
    print("【タスク検証】")
    print("-"*70)
    validated = await agent.validate_tasks(tasks)
    print(f"✅ {len(validated)}個のタスクが検証済み")
    
    print("\n✅ テスト完了")


if __name__ == "__main__":
    asyncio.run(test_task_breakdown())

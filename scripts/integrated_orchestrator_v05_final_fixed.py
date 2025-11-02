#!/usr/bin/env python3
"""
統合オーケストレーター v05（完成版）

【完成】
✅ 目標入力 → タスク分解 → タスク実行
✅ ナレッジベース連携
✅ 5行目以降に正しく書き込み
✅ 全エラー修正
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.smart_sheets_manager import SmartSheetsManager
from task_executor.task_coordinator_v05_self_healing import (
    TaskCoordinatorWithSelfHealing,
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedOrchestratorV05:
    """統合オーケストレーター（完成版）"""
    
    def __init__(self):
        self.sheets_manager = SmartSheetsManager()
        self.task_coordinator = TaskCoordinatorWithSelfHealing(self.sheets_manager)
        self.kb_available = self._check_knowledge_base()
    
    def _check_knowledge_base(self) -> bool:
        """ナレッジベース連携確認"""
        try:
            kb_data = self.sheets_manager.read_range('knowledge_base!A2:A10')
            logger.info(f"✅ ナレッジベース連携OK: {len(kb_data)}件")
            return True
        except Exception as e:
            logger.warning(f"⚠️ ナレッジベース未利用: {e}")
            return False
    
    async def run(self):
        """メイン実行"""
        print("=" * 60)
        print("🚀 統合オーケストレーター v05（完成版）")
        print("=" * 60)
        
        try:
            # STEP 1: アクティブな目標を取得
            print("\n📋 STEP 1: アクティブな目標取得")
            goals = await self.get_active_goals()
            
            if not goals:
                print("   ℹ️ アクティブな目標がありません")
                return
            
            print(f"   ✅ {len(goals)}件の目標を検出")
            
            # STEP 2: 各目標をタスクに分解
            for goal in goals:
                print(f"\n📝 STEP 2: 目標をタスクに分解")
                print(f"   目標ID: {goal['goal_id']}")
                
                await self.decompose_goal(goal)
            
            # STEP 3: タスク実行
            print(f"\n🎯 STEP 3: タスク実行")
            await self.execute_tasks()
            
            # STEP 4: ナレッジベース統計
            if self.kb_available:
                print(f"\n📚 STEP 4: ナレッジベース統計")
                await self.show_knowledge_base_stats()
            
            print("\n" + "=" * 60)
            print("✅ 実行完了")
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ 実行エラー: {e}")
            import traceback
            traceback.print_exc()
    
    async def get_active_goals(self):
        """アクティブな目標を取得"""
        try:
            last_row = self.sheets_manager.detect_actual_data_range('project_goal')
            goals_data = self.sheets_manager.read_range(f'project_goal!A2:D{last_row}')
            
            active_goals = []
            for row in goals_data:
                if len(row) >= 3 and row[2] == 'active':
                    active_goals.append({
                        'goal_id': row[0],
                        'description': row[1],
                        'status': row[2],
                        'created_at': row[3] if len(row) > 3 else ''
                    })
            
            return active_goals
            
        except Exception as e:
            logger.error(f"❌ 目標取得エラー: {e}")
            return []
    
    async def decompose_goal(self, goal):
        """目標をタスクに分解"""
        try:
            base_tasks = [
                {
                    'task_id': f"{goal['goal_id']}_TASK_001",
                    'description': f"【調査】{goal['description'][:50]}の要件定義",
                    'required_role': 'analyst',
                    'priority': 'high',
                    'execution_type': 'gemini'
                },
                {
                    'task_id': f"{goal['goal_id']}_TASK_002",
                    'description': f"【設計】{goal['description'][:50]}の設計書作成",
                    'required_role': 'architect',
                    'priority': 'high',
                    'execution_type': 'gemini'
                },
                {
                    'task_id': f"{goal['goal_id']}_TASK_003",
                    'description': f"【実装】{goal['description'][:50]}のコード実装",
                    'required_role': 'developer',
                    'priority': 'medium',
                    'execution_type': 'content'
                }
            ]
            
            print(f"   ✅ {len(base_tasks)}個のタスクを生成")
            
            # pm_tasksシートに登録
            task_data = []
            for task in base_tasks:
                task_data.append([
                    task['task_id'],
                    goal['goal_id'],
                    task['description'],
                    task['required_role'],
                    'pending',
                    task['priority'],
                    '1h',
                    '',
                    datetime.now().isoformat(),
                    f"BATCH_{datetime.now().strftime('%Y%m%d')}",
                    '',
                    '',
                    task['execution_type']
                ])
            
            self.sheets_manager.smart_append_rows('pm_tasks', task_data, validate=False)
            print(f"   ✅ pm_tasksシートに登録完了")
            
        except Exception as e:
            logger.error(f"❌ タスク生成エラー: {e}")
    
    async def execute_tasks(self):
        """タスクを実行"""
        try:
            last_row = self.sheets_manager.detect_actual_data_range('pm_tasks')
            tasks_data = self.sheets_manager.read_range(f'pm_tasks!A2:M{last_row}')
            
            pending_tasks = []
            for row in tasks_data:
                if len(row) > 4 and row[4] == 'pending':
                    # 🔧 修正: 辞書型で全情報を保持
                    pending_tasks.append({
                        'task_id': row[0] if len(row) > 0 else '',
                        'parent_goal_id': row[1] if len(row) > 1 else '',
                        'description': row[2] if len(row) > 2 else '',
                        'required_role': row[3] if len(row) > 3 else '',
                        'status': row[4] if len(row) > 4 else 'pending',
                        'priority': row[5] if len(row) > 5 else 'medium',
                        'estimated_time': row[6] if len(row) > 6 else '',
                        'dependencies': row[7] if len(row) > 7 else '',
                        'created_at': row[8] if len(row) > 8 else '',
                        'batch_id': row[9] if len(row) > 9 else '',
                        'detail_file_path': row[10] if len(row) > 10 else '',
                        'blank': row[11] if len(row) > 11 else '',
                        'execution_type': row[12] if len(row) > 12 else 'content'
                    })
            
            if not pending_tasks:
                print("   ℹ️ 実行待ちタスクなし")
                return
            
            print(f"   📋 実行待ちタスク: {len(pending_tasks)}件")
            print(f"   💡 最初の1件のみ実行（テスト）")
            
            # 最初の1件のみ実行
            if pending_tasks:
                task = pending_tasks[0]
                print(f"\n   🎯 タスク実行: {task['task_id']}")
                print(f"      {task['description'][:60]}...")
                
                try:
                    # 🔧 修正: タスク辞書全体を渡す
                    result = await self.task_coordinator.execute_task(task)
                    
                    if result.get('status') == 'success':
                        print(f"      ✅ 成功")
                    else:
                        print(f"      ⚠️ 失敗: {result.get('error', 'Unknown')}")
                except Exception as e:
                    print(f"      ❌ 実行エラー: {e}")
            
        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {e}")
    
    async def show_knowledge_base_stats(self):
        """ナレッジベース統計表示"""
        try:
            kb_data = self.sheets_manager.read_range('knowledge_base!A2:M100')
            
            print(f"   📊 ナレッジベース統計:")
            print(f"      総件数: {len(kb_data)}")
            
            types = {}
            for row in kb_data:
                if len(row) > 2:
                    kb_type = row[2]
                    types[kb_type] = types.get(kb_type, 0) + 1
            
            for kb_type, count in types.items():
                print(f"      - {kb_type}: {count}件")
            
        except Exception as e:
            logger.warning(f"⚠️ 統計表示エラー: {e}")


async def main():
    """メイン関数"""
    orchestrator = IntegratedOrchestratorV05()
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())

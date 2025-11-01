#!/usr/bin/env python3
"""
🎯 Goal Input Agent v1.0
役割: GitHub Actions inputsをPM Agentのタスクキューに登録

連携先:
- 入力: GitHub Actions workflow_dispatch inputs
- 出力: PM Agent (`pm_tasks`シート)
- 依存: SheetsManager, ConfigLoader
"""
import sys
sys.path.insert(0, '.')
import argparse
from datetime import datetime
from configuration.config_loader import load_config
from core_agents.sheets_manager import SheetsManager

class GoalInputAgent:
    """GitHub Actionsからの目標をPM Agentに橋渡し"""
    
    def __init__(self):
        self.config = load_config()
        self.sheets = SheetsManager(
            credentials_path=self.config['credentials_path'],
            spreadsheet_id=self.config['spreadsheet_id']
        )
        self.pm_queue_sheet = 'pm_task_queue'  # PM Agentの入力シート
    
    def register_goal(self, goal: str, priority: str = 'high', 
                     goal_type: str = 'development') -> dict:
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
        goal_id = f"GOAL_{timestamp.replace(':', '').replace('-', '')[:14]}"
        
        # PM Agentが読み取る形式でシートに登録
        goal_data = [
            timestamp,           # A列: 登録日時
            goal_id,            # B列: 目標ID
            goal,               # C列: 目標内容
            priority,           # D列: 優先度
            goal_type,          # E列: タイプ
            'pending',          # F列: ステータス
            '',                 # G列: 担当エージェント（PM Agentが設定）
            '',                 # H列: 進捗率（0-100）
            ''                  # I列: メモ
        ]
        
        try:
            self.sheets.append_row(self.pm_queue_sheet, goal_data)
            print(f"✅ 目標登録完了:")
            print(f"   ID: {goal_id}")
            print(f"   内容: {goal}")
            print(f"   優先度: {priority}")
            
            return {
                'status': 'success',
                'goal_id': goal_id,
                'timestamp': timestamp,
                'next_step': 'PM Agentが自動でタスク分解を開始します'
            }
        
        except Exception as e:
            print(f"❌ 登録失敗: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

def main():
    parser = argparse.ArgumentParser(
        description='Goal Input Agent - GitHub ActionsからPM Agentへの橋渡し'
    )
    parser.add_argument('--goal', required=True, help='開発目標')
    parser.add_argument('--priority', default='high', 
                       choices=['critical', 'high', 'medium', 'low'])
    parser.add_argument('--type', default='development',
                       choices=['development', 'maintenance', 'improvement'])
    
    args = parser.parse_args()
    
    agent = GoalInputAgent()
    result = agent.register_goal(
        goal=args.goal,
        priority=args.priority,
        goal_type=args.type
    )
    
    if result['status'] == 'success':
        print(f"\n🚀 次のステップ:")
        print(f"   1. PM Agentが自動起動（6時間ごとのCron or 手動）")
        print(f"   2. 目標をタスクに分解")
        print(f"   3. Task Executorが実行開始")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🎯 Goal Input Agent v1.0
役割: GitHub Actions inputsをproject_goalシートに登録
      PM Agentが自動でタスクに分解する
"""
import sys
sys.path.insert(0, '.')
import argparse
from datetime import datetime
from configuration.config_loader import get_config
from tools.sheets_manager import GoogleSheetsManager

class GoalInputAgent:
    """GitHub Actionsからの目標をproject_goalシートに登録"""
    
    def __init__(self):
        self.spreadsheet_id = get_config('SPREADSHEET_ID')
        self.sheets = GoogleSheetsManager(spreadsheet_id=self.spreadsheet_id)
        self.project_goal_sheet = 'project_goal'  # PM Agentが読み取るシート
    
    def register_goal(self, goal: str, priority: str = 'high') -> dict:
        """
        目標をproject_goalシートに登録
        PM Agentがstatus='active'の目標を自動で読み取り、タスク分解する
        
        Args:
            goal: 開発目標
            priority: 優先度（未使用だがproject_goalシートには優先度列がない）
        
        Returns:
            登録結果
        """
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        # 既存のproject_goalシートの構造に合わせる
        # ヘッダー: ['goal_id', 'goal_description', 'status', 'created_at']
        
        try:
            # 最新のgoal_idを取得して+1
            existing_data = self.sheets.read_range(self.project_goal_sheet)
            
            if existing_data and len(existing_data) > 1:
                # 最後の行からgoal_idを取得
                last_goal_id = 0
                for row in existing_data[1:]:
                    if row and row[0]:  # goal_id列が存在
                        try:
                            last_goal_id = max(last_goal_id, int(row[0]))
                        except (ValueError, IndexError):
                            continue
                
                new_goal_id = last_goal_id + 1
            else:
                new_goal_id = 1
            
            # project_goalシートの形式に合わせてデータ作成
            goal_data = [
                str(new_goal_id),    # A列: goal_id
                goal,                # B列: goal_description
                'active',            # C列: status（PM Agentがこれを読み取る）
                timestamp            # D列: created_at
            ]
            
            self.sheets.append_rows(self.project_goal_sheet, [goal_data])
            
            print(f"✅ 目標登録完了:")
            print(f"   Goal ID: {new_goal_id}")
            print(f"   内容: {goal}")
            print(f"   ステータス: active")
            print(f"   登録日: {timestamp}")
            
            return {
                'status': 'success',
                'goal_id': new_goal_id,
                'timestamp': timestamp,
                'next_step': 'PM Agentが自動でタスク分解（次回実行時）'
            }
        
        except Exception as e:
            print(f"❌ 登録失敗: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'error': str(e)
            }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--goal', required=True, help='開発目標')
    parser.add_argument('--priority', default='high', 
                       choices=['critical', 'high', 'medium', 'low'],
                       help='優先度（参考情報）')
    
    args = parser.parse_args()
    
    agent = GoalInputAgent()
    result = agent.register_goal(goal=args.goal, priority=args.priority)
    
    if result['status'] == 'success':
        print(f"\n🚀 次のステップ:")
        print(f"   1. PM Agentが自動起動（手動 or Cron）")
        print(f"   2. project_goalから目標読み取り")
        print(f"   3. pm_tasksにタスク分解")
        print(f"   4. Task Executorが実行")

if __name__ == "__main__":
    main()

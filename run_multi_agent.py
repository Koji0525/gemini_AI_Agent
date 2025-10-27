#!/usr/bin/env python3
"""
🏃‍♂️ マルチエージェント自動実行システム - メイン実行ファイル
"""

import os
import sys
import asyncio
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pm_agent import ProjectManagerAgent
from configuration.config_loader import ConfigLoader

class MultiAgentRunner:
    def __init__(self):
        self.config = ConfigLoader()
        self.pm_agent = ProjectManagerAgent()
    
    async def run_automation_cycle(self):
        """自動化サイクルを実行"""
        print("🚀 マルチエージェント自動実行システム起動")
        print("=" * 60)
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. プロジェクト状態を分析
            print("\n📊 ステップ1: プロジェクト状態分析")
            project_status = await self.pm_agent.analyze_project_status()
            
            if not project_status:
                print("❌ プロジェクト分析に失敗しました")
                return False
            
            # 2. 優先タスクを特定
            print("\n🎯 ステップ2: 優先タスク特定")
            priority_tasks = await self.pm_agent.identify_priority_tasks()
            
            # 3. タスク実行
            print("\n⚡ ステップ3: タスク実行")
            execution_results = await self.pm_agent.execute_priority_tasks(priority_tasks)
            
            # 4. 進捗更新
            print("\n📈 ステップ4: 進捗更新")
            await self.pm_agent.update_progress_dashboard()
            
            # 5. 結果レポート
            print("\n📋 ステップ5: 結果レポート生成")
            await self.pm_agent.generate_execution_report(execution_results)
            
            print(f"\n✅ 自動実行完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
            
        except Exception as e:
            print(f"❌ 自動実行エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_single_cycle(self):
        """単一サイクルを実行（非同期ラッパー）"""
        return asyncio.run(self.run_automation_cycle())

def main():
    """メイン実行関数"""
    runner = MultiAgentRunner()
    
    print("�� 実行モード選択:")
    print("   1. 単回実行")
    print("   2. 自動監視モード")
    
    choice = input("選択 (1 or 2): ").strip()
    
    if choice == "1":
        success = runner.run_single_cycle()
        if success:
            print("🏆 単回実行が正常に完了しました")
        else:
            print("❌ 単回実行に失敗しました")
    
    elif choice == "2":
        print("🔧 自動監視モードは開発中です")
        print("💡 現在は単回実行を推奨します")
        runner.run_single_cycle()
    
    else:
        print("❌ 無効な選択です")

if __name__ == "__main__":
    main()

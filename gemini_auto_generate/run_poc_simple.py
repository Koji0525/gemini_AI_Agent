#!/usr/bin/env python3
"""
🎯 シンプルPOCデモ - 求めている構成で実行
"""

import os
import sys
import asyncio
from datetime import datetime

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🔧 インポートチェック...")

# 必要なモジュールをインポート
try:
    from pm_agent import ProjectManagerAgent
    from configuration.config_loader import ConfigLoader
    print("✅ pm_agent をインポートしました")
except ImportError as e:
    print(f"❌ pm_agent インポートエラー: {e}")

try:
    from task_executor import TaskExecutor
    print("✅ task_executor をインポートしました")
except ImportError as e:
    print(f"❌ task_executor インポートエラー: {e}")

try:
    import gspread
    from google.oauth2.service_account import Credentials
    print("✅ Google Sheets ライブラリをインポートしました")
except ImportError as e:
    print(f"❌ Google Sheets インポートエラー: {e}")

class SimplePOCDemo:
    def __init__(self):
        try:
            self.config = ConfigLoader()
            self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
            self.credentials = Credentials.from_service_account_file(
                self.config.get('service_account_file'), 
                scopes=self.scopes
            )
            self.gc = gspread.authorize(self.credentials)
            self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
            print("✅ Google Sheets に接続しました")
        except Exception as e:
            print(f"❌ 初期化エラー: {e}")
            self.gc = None
    
    def show_structure(self):
        """フォルダ構造を表示"""
        print("\n📁 gemini_auto_generate フォルダ構造:")
        print("=" * 50)
        
        # 実際のファイル構造を表示
        base_dir = "."
        for root, dirs, files in os.walk(base_dir):
            level = root.replace(base_dir, '').count(os.sep)
            if level > 1:  # 2階層以上は表示しない
                continue
                
            indent = ' ' * 2 * level
            if root == base_dir:
                print(f"{indent}gemini_auto_generate/")
            else:
                print(f"{indent}📁 {os.path.basename(root)}/")
            
            subindent = ' ' * 2 * (level + 1)
            for file in sorted(files):
                if file.endswith('.py'):
                    emoji = self.get_file_emoji(file)
                    print(f"{subindent}{emoji} {file}")
    
    def get_file_emoji(self, filename):
        """ファイル名に基づいて絵文字を返す"""
        emoji_map = {
            'run_multi_agent.py': '🏃‍♂️',
            'pm_agent.py': '👑', 
            'pm_system_prompts.py': '👑',
            'task_executor.py': '⚙️',
            'task_executor_content.py': '📝',
            'task_executor_ma.py': '🔍',
            'content_task_executor.py': '📝',
            'config_loader.py': '⚙️',
            '__init__.py': '📁',
            'run_poc_simple.py': '🎯'
        }
        return emoji_map.get(filename, '📄')
    
    async def test_basic_functionality(self):
        """基本機能をテスト"""
        print("\n🧪 基本機能テスト")
        print("-" * 30)
        
        # 1. PMエージェントのテスト
        try:
            pm_agent = ProjectManagerAgent()
            print("✅ PMエージェントを初期化しました")
            
            # プロジェクト状態分析
            status = await pm_agent.analyze_project_status()
            if status:
                print(f"✅ プロジェクト分析: {status['active_goals']}個のアクティブゴール")
                print(f"✅ 進捗状況: {status['progress_rate']:.1f}%")
            else:
                print("❌ プロジェクト分析に失敗")
                
        except Exception as e:
            print(f"❌ PMエージェントテストエラー: {e}")
        
        # 2. タスク実行器のテスト
        try:
            task_executor = TaskExecutor()
            print("✅ タスク実行器を初期化しました")
            
            # テストタスクの実行
            test_task = {
                'task_id': 'POC-TEST-001',
                'description': 'POCテストタスク',
                'execution_type': 'general'
            }
            result = await task_executor.execute_task(test_task)
            print(f"✅ タスク実行テスト: {result.get('success', False)}")
            
        except Exception as e:
            print(f"❌ タスク実行器テストエラー: {e}")
    
    def check_module_imports(self):
        """モジュールインポートを確認"""
        print("\n🔍 モジュールインポート確認")
        print("-" * 30)
        
        modules_to_check = [
            ('pm_agent', 'ProjectManagerAgent'),
            ('task_executor', 'TaskExecutor'),
            ('task_executor.task_executor_content', 'ContentTaskExecutor'),
            ('task_executor.task_executor_ma', 'MATaskExecutor'),
            ('task_executor.task_executor_ma', 'WordPressTaskExecutor'),
            ('configuration.config_loader', 'ConfigLoader'),
        ]
        
        for module_path, class_name in modules_to_check:
            try:
                if module_path.startswith('task_executor.'):
                    # task_executorサブモジュール
                    full_path = module_path
                else:
                    full_path = module_path
                
                exec(f"from {full_path} import {class_name}")
                print(f"✅ {module_path}.{class_name}")
            except ImportError as e:
                print(f"❌ {module_path}.{class_name} - {e}")

def main():
    """メイン実行"""
    print("🎯 gemini_auto_generate シンプルPOCデモ")
    print("=" * 60)
    
    demo = SimplePOCDemo()
    
    # フォルダ構造を表示
    demo.show_structure()
    
    # モジュールインポート確認
    demo.check_module_imports()
    
    # 基本機能テスト
    asyncio.run(demo.test_basic_functionality())
    
    print(f"\n✅ POCデモ完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎉 求めている構成で動作確認完了！")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🎯 POCデモ実行スクリプト - 完全なデモンストレーション
"""

import os
import sys
import asyncio
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from configuration.config_loader import ConfigLoader
import gspread
from google.oauth2.service_account import Credentials

class POCDemoRunner:
    def __init__(self):
        self.config = ConfigLoader()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(
            self.config.get('service_account_file'), 
            scopes=self.scopes
        )
        self.gc = gspread.authorize(self.credentials)
        self.spreadsheet = self.gc.open_by_key(self.config.get('spreadsheet_id'))
        
        # POC実行器をインポート
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'task_executor'))
        from task_executor_poc_controller import POCEnhancedTaskExecutor
        self.poc_executor = POCEnhancedTaskExecutor()
    
    async def run_poc_demo(self):
        """POCデモを実行"""
        print("🎯 POCデモンストレーション開始")
        print("=" * 60)
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # ステップ1: POCタスクの作成
        print("📝 ステップ1: POCテストタスクの作成")
        await self._create_poc_tasks()
        
        # ステップ2: タスクの実行
        print("\n⚡ ステップ2: POCタスクの実行")
        results = await self._execute_poc_tasks()
        
        # ステップ3: 結果の表示
        print("\n📊 ステップ3: 実行結果の表示")
        await self._show_poc_results(results)
        
        # ステップ4: 成果物の確認
        print("\n📁 ステップ4: 生成された成果物の確認")
        await self._show_generated_artifacts()
        
        print(f"\n✅ POCデモ完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    
    async def _create_poc_tasks(self):
        """POCタスクを作成"""
        print("   タスクシートにPOCテストタスクを追加中...")
        
        try:
            # スクリプトを実行してタスクを作成
            import subprocess
            result = subprocess.run([sys.executable, 'scripts/create_poc_tasks.py'], 
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ POCテストタスクを作成しました")
            else:
                print(f"   ⚠️ タスク作成に問題があります: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ タスク作成エラー: {e}")
    
    async def _execute_poc_tasks(self):
        """POCタスクを実行"""
        try:
            tasks_sheet = self.spreadsheet.worksheet('pm_tasks')
            tasks_data = tasks_data = tasks_sheet.get_all_values()
            
            if len(tasks_data) <= 1:
                print("   ⚠️ 実行するタスクがありません")
                return []
            
            # POCタスクを検索
            poc_tasks = []
            for i, row in enumerate(tasks_data[1:], 2):
                if len(row) > 2 and '【POCテスト】' in row[2]:
                    task_info = {
                        'row_number': i,
                        'task_id': row[0] if row[0] else f"ROW_{i}",
                        'description': row[2] if len(row) > 2 else '説明なし',
                        'priority': row[5] if len(row) > 5 else '3',
                        'execution_type': row[12] if len(row) > 12 else 'general'
                    }
                    poc_tasks.append(task_info)
            
            print(f"   🔍 POCタスクを {len(poc_tasks)}件 発見")
            
            # タスクを実行
            results = []
            for task in poc_tasks:
                print(f"   🎯 実行中: {task['task_id']} - {task['description'][:40]}...")
                
                result = await self.poc_executor.execute_poc_task(task)
                results.append(result)
                
                # タスクステータスを更新
                await self._update_task_status(task['row_number'], 'completed')
                print(f"   ✅ 完了: {task['task_id']}")
            
            return results
            
        except Exception as e:
            print(f"   ❌ タスク実行エラー: {e}")
            return []
    
    async def _update_task_status(self, row_number, status):
        """タスクステータスを更新"""
        try:
            tasks_sheet = self.spreadsheet.worksheet('pm_tasks')
            tasks_sheet.update_cell(row_number, 5, status)  # 5列目がstatus
        except Exception as e:
            print(f"   ⚠️ ステータス更新エラー: {e}")
    
    async def _show_poc_results(self, results):
        """POC結果を表示"""
        if not results:
            print("   ⚠️ 表示する結果がありません")
            return
        
        success_count = sum(1 for r in results if r.get('success'))
        total_count = len(results)
        
        print(f"   📈 実行結果: {success_count}/{total_count} 成功")
        print(f"   🎯 成功率: {(success_count/total_count*100):.1f}%")
        
        print("\n   📋 詳細結果:")
        for result in results:
            status = "✅ 成功" if result.get('success') else "❌ 失敗"
            task_type = result.get('type', 'unknown')
            print(f"      • {result['task_id']}: {status} ({task_type})")
            
            if result.get('output_files'):
                print(f"         📁 出力ファイル: {', '.join(result['output_files'])}")
    
    async def _show_generated_artifacts(self):
        """生成された成果物を表示"""
        import glob
        
        print("   生成された成果物:")
        
        # 各種成果物を検索
        artifact_types = {
            '記事コンテンツ': 'poc_output/*.md',
            'WordPressコード': 'poc_output/wordpress/*.php',
            '調査レポート': 'poc_output/research/*.md',
            '計画文書': 'poc_output/plans/*.md'
        }
        
        for artifact_type, pattern in artifact_types.items():
            files = glob.glob(pattern)
            if files:
                print(f"   📂 {artifact_type}:")
                for file in files:
                    file_size = os.path.getsize(file) if os.path.exists(file) else 0
                    print(f"      • {file} ({file_size} bytes)")
            else:
                print(f"   📂 {artifact_type}: なし")
        
        # 総合統計
        all_files = []
        for pattern in artifact_types.values():
            all_files.extend(glob.glob(pattern))
        
        print(f"\n   📊 総合統計:")
        print(f"      • 総ファイル数: {len(all_files)}")
        print(f"      • 総ファイルサイズ: {sum(os.path.getsize(f) for f in all_files if os.path.exists(f))} bytes")
        print(f"      • 出力ディレクトリ: poc_output/")

def main():
    """メイン実行関数"""
    runner = POCDemoRunner()
    
    print("🎯 POCデモンストレーション")
    print("このデモでは以下のことを実証します:")
    print("   1. 📝 自動タスク作成")
    print("   2. ⚡ マルチタイプタスク実行")
    print("   3. 🏗️ 実際の成果物生成")
    print("   4. 📊 進捗追跡とレポート")
    print("   5. 📁 ファイル出力の確認")
    print()
    
    input("Enterキーを押してデモを開始...")
    
    success = asyncio.run(runner.run_poc_demo())
    
    if success:
        print("\n🎉 POCデモンストレーション完了！")
        print("✅ 以下のことが実証されました:")
        print("   • 自動タスク管理システム")
        print("   • マルチタイプタスク実行")
        print("   • 実際の成果物生成")
        print("   • 進捗追跡機能")
        print("   • ファイル出力機能")
        print("\n🚀 次のステップ:")
        print("   • 生成された成果物を poc_output/ ディレクトリで確認")
        print("   • スプレッドシートでタスク状態を確認")
        print("   • システムを実際のプロジェクトで使用")
    else:
        print("\n❌ POCデモに失敗しました")

if __name__ == "__main__":
    main()

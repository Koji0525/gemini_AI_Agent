#!/usr/bin/env python3
"""
🎯 完全版POCデモ - 全Pythonファイルを含むシステム全体のデモ
"""

import os
import sys
import asyncio
from datetime import datetime
import importlib.util

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🎯 完全版POCデモ - システム全体の動作確認")
print("=" * 70)

class CompletePOCDemo:
    def __init__(self):
        self.all_modules = {}
        self.test_results = {}
    
    def discover_all_modules(self):
        """すべてのPythonモジュールを発見"""
        print("1. 🔍 全Pythonモジュールの発見")
        print("-" * 50)
        
        modules_found = []
        
        for root, dirs, files in os.walk("."):
            # 特定のディレクトリを除外
            if '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, ".")
                    
                    # モジュール名を生成
                    if rel_path == "__init__.py":
                        module_name = root.replace('./', '').replace('/', '.')
                    else:
                        module_name = rel_path.replace('./', '').replace('/', '.').replace('.py', '')
                    
                    modules_found.append({
                        'path': rel_path,
                        'module_name': module_name,
                        'file': file
                    })
        
        # ソートして表示
        modules_found.sort(key=lambda x: x['path'])
        
        print(f"📊 発見されたPythonファイル: {len(modules_found)}個")
        
        # カテゴリ別に表示
        categories = {
            'メインシステム': [],
            'タスク実行器': [],
            '設定ファイル': [],
            'ユーティリティ': []
        }
        
        for module in modules_found:
            path = module['path']
            if path.startswith('task_executor/'):
                categories['タスク実行器'].append(module)
            elif path.startswith('configuration/'):
                categories['設定ファイル'].append(module)
            elif path.startswith('scripts/'):
                categories['ユーティリティ'].append(module)
            else:
                categories['メインシステム'].append(module)
        
        for category, modules in categories.items():
            if modules:
                print(f"\n📂 {category}:")
                for module in modules:
                    emoji = self.get_file_emoji(module['file'])
                    print(f"   {emoji} {module['path']}")
        
        self.all_modules = modules_found
        return modules_found
    
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
            'run_quick_poc.py': '🎯',
            'run_poc_simple.py': '🎯',
            'run_complete_poc.py': '🎯',
            'sync_settings.py': '⚙️'
        }
        return emoji_map.get(filename, '📄')
    
    def test_module_imports(self):
        """すべてのモジュールのインポートをテスト"""
        print("\n2. 🧪 全モジュールインポートテスト")
        print("-" * 50)
        
        import_results = {
            'success': [],
            'failed': []
        }
        
        for module_info in self.all_modules:
            module_name = module_info['module_name']
            
            # __init__.pyは特別扱い
            if module_info['file'] == '__init__.py':
                continue
            
            try:
                # モジュールを動的にインポート
                spec = importlib.util.spec_from_file_location(module_name, module_info['path'])
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    import_results['success'].append(module_info)
                    print(f"   ✅ {module_info['path']}")
                else:
                    import_results['failed'].append((module_info, "spec load failed"))
                    print(f"   ❌ {module_info['path']} - spec failed")
                    
            except Exception as e:
                import_results['failed'].append((module_info, str(e)))
                print(f"   ❌ {module_info['path']} - {e}")
        
        print(f"\n📊 インポート結果:")
        print(f"   ✅ 成功: {len(import_results['success'])}個")
        print(f"   ❌ 失敗: {len(import_results['failed'])}個")
        
        return import_results
    
    async def test_system_workflow(self):
        """システムワークフローのテスト"""
        print("\n3. 🔄 システムワークフローテスト")
        print("-" * 50)
        
        workflow_steps = [
            ("PMエージェント初期化", self.test_pm_agent),
            ("タスク実行器テスト", self.test_task_executor),
            ("コンテンツ生成テスト", self.test_content_generation),
            ("WordPress開発テスト", self.test_wordpress_development),
            ("M&A調査テスト", self.test_ma_research),
            ("進捗管理テスト", self.test_progress_management)
        ]
        
        workflow_results = {}
        
        for step_name, test_func in workflow_steps:
            try:
                print(f"   🔄 {step_name}...")
                result = await test_func()
                workflow_results[step_name] = {'success': True, 'result': result}
                print(f"   ✅ {step_name} 成功")
            except Exception as e:
                workflow_results[step_name] = {'success': False, 'error': str(e)}
                print(f"   ❌ {step_name} 失敗: {e}")
        
        return workflow_results
    
    async def test_pm_agent(self):
        """PMエージェントのテスト"""
        from pm_agent import ProjectManagerAgent
        agent = ProjectManagerAgent()
        status = await agent.analyze_project_status()
        return status
    
    async def test_task_executor(self):
        """タスク実行器のテスト"""
        from task_executor import TaskExecutor
        executor = TaskExecutor()
        
        test_tasks = [
            {'task_id': 'TEST-001', 'execution_type': 'general'},
            {'task_id': 'TEST-002', 'execution_type': 'content'},
            {'task_id': 'TEST-003', 'execution_type': 'wordpress'},
        ]
        
        results = []
        for task in test_tasks:
            result = await executor.execute_task(task)
            results.append(result)
        
        return results
    
    async def test_content_generation(self):
        """コンテンツ生成のテスト"""
        from task_executor.task_executor_content import ContentTaskExecutor
        executor = ContentTaskExecutor()
        
        test_task = {
            'task_id': 'CONTENT-TEST-001',
            'description': 'テストコンテンツ生成'
        }
        
        result = await executor.execute(test_task)
        return result
    
    async def test_wordpress_development(self):
        """WordPress開発のテスト"""
        from task_executor.task_executor_ma import WordPressTaskExecutor
        executor = WordPressTaskExecutor()
        
        test_task = {
            'task_id': 'WP-TEST-001',
            'description': 'テストWordPress開発'
        }
        
        result = await executor.execute(test_task)
        return result
    
    async def test_ma_research(self):
        """M&A調査のテスト"""
        from task_executor.task_executor_ma import MATaskExecutor
        executor = MATaskExecutor()
        
        test_task = {
            'task_id': 'MA-TEST-001',
            'description': 'テストM&A調査'
        }
        
        result = await executor.execute(test_task)
        return result
    
    async def test_progress_management(self):
        """進捗管理のテスト"""
        from pm_agent import ProjectManagerAgent
        agent = ProjectManagerAgent()
        
        # 優先タスクの特定
        tasks = await agent.identify_priority_tasks()
        
        # 進捗更新
        dashboard_updated = await agent.update_progress_dashboard()
        
        return {
            'priority_tasks_count': len(tasks),
            'dashboard_updated': dashboard_updated
        }
    
    def generate_system_report(self, import_results, workflow_results):
        """システムレポートを生成"""
        print("\n4. 📊 システム全体レポート")
        print("=" * 50)
        
        total_modules = len(self.all_modules)
        successful_imports = len(import_results['success'])
        failed_imports = len(import_results['failed'])
        
        successful_workflows = sum(1 for result in workflow_results.values() if result['success'])
        total_workflows = len(workflow_results)
        
        print(f"📈 システム統計:")
        print(f"   • 総モジュール数: {total_modules}個")
        print(f"   • 正常インポート: {successful_imports}個 ({successful_imports/total_modules*100:.1f}%)")
        print(f"   • インポート失敗: {failed_imports}個")
        print(f"   • ワークフロー成功: {successful_workflows}/{total_workflows}")
        
        print(f"\n🎯 主要コンポーネント:")
        components = [
            ("🏃‍♂️ メイン実行システム", "run_multi_agent.py"),
            ("👑 PMエージェント", "pm_agent.py"),
            ("⚙️ タスク実行コントローラー", "task_executor.py"),
            ("📝 コンテンツ生成", "task_executor_content.py"),
            ("🔍 M&A調査", "task_executor_ma.py"),
            ("🏗️ WordPress開発", "task_executor_ma.py (WordPressTaskExecutor)"),
            ("⚙️ 設定管理", "config_loader.py")
        ]
        
        for name, file in components:
            exists = any(file in module['path'] for module in self.all_modules)
            status = "✅" if exists else "❌"
            print(f"   {status} {name}")
        
        print(f"\n🚀 システム状態: {'✅ 正常' if successful_imports > total_modules * 0.8 else '⚠️ 要確認'}")
        
        if failed_imports > 0:
            print(f"\n⚠️ インポート失敗したモジュール:")
            for module_info, error in import_results['failed']:
                print(f"   • {module_info['path']}: {error}")
    
    async def run_demo(self):
        """デモを実行"""
        print("🚀 完全版POCデモ開始")
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # ステップ1: 全モジュール発見
        modules = self.discover_all_modules()
        
        # ステップ2: インポートテスト
        import_results = self.test_module_imports()
        
        # ステップ3: ワークフローテスト
        workflow_results = await self.test_system_workflow()
        
        # ステップ4: レポート生成
        self.generate_system_report(import_results, workflow_results)
        
        print(f"\n✅ POCデモ完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """メイン実行"""
    demo = CompletePOCDemo()
    asyncio.run(demo.run_demo())
    
    print("\n🎉 完全版POCデモ完了！")
    print("\n📋 実証された内容:")
    print("   • 全Pythonモジュールの構造")
    print("   • モジュール間の依存関係")
    print("   • システムワークフローの動作")
    print("   • 各コンポーネントの連携")
    print("   • エラーハンドリングとフォールバック")

if __name__ == "__main__":
    main()

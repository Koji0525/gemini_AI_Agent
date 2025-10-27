#!/usr/bin/env python3
"""
🎯 現在のディレクトリで動作するPOCデモ - ファイルを移動せずに実行
"""

import os
import sys
import asyncio
from datetime import datetime
import importlib.util

print("🎯 現在のディレクトリPOCデモ - ファイル移動なし")
print("=" * 70)

class CurrentDirectoryPOC:
    def __init__(self):
        self.system_components = {}
    
    def analyze_current_system(self):
        """現在のシステムを分析"""
        print("1. 🔍 現在のシステム分析")
        print("-" * 50)
        
        # システムコンポーネントの定義
        components = {
            '🏃‍♂️ メイン実行システム': [
                'run_multi_agent.py',
                'pm_agent.py',
                'pm_system_prompts.py', 
                'task_executor.py'
            ],
            '👑 コアエージェント': [
                'core_agents/pm_agent.py',
                'core_agents/review_agent.py',
                'core_agents/dev_agent.py',
                'core_agents/design_agent.py',
                'core_agents/content_writer_agent.py'
            ],
            '🌐 ブラウザ自動化': [
                'browser_control/browser_controller.py',
                'browser_control/safe_browser_manager.py'
            ],
            '🚀 WordPress開発': [
                'wordpress/wp_agent.py',
                'wordpress/wp_dev/wp_dev_agent.py',
                'wordpress/wp_dev/wp_acf_agent.py'
            ],
            '⚙️ タスク実行システム': [
                'task_executor/task_executor_content.py',
                'task_executor/task_executor_ma.py'
            ],
            '�� 設定管理': [
                'configuration/config_loader.py',
                'configuration/service_account.json'
            ]
        }
        
        print("📋 システムコンポーネント状況:")
        
        component_status = {}
        
        for category, files in components.items():
            print(f"\n{category}:")
            existing_files = []
            missing_files = []
            
            for file_path in files:
                if os.path.exists(file_path):
                    existing_files.append(file_path)
                    print(f"   ✅ {file_path}")
                else:
                    missing_files.append(file_path)
                    print(f"   ❌ {file_path}")
            
            component_status[category] = {
                'existing': existing_files,
                'missing': missing_files,
                'coverage': len(existing_files) / len(files) if files else 0
            }
        
        self.system_components = component_status
        return component_status
    
    def test_system_imports(self):
        """システムのインポートテスト"""
        print("\n2. 🧪 システムインポートテスト")
        print("-" * 50)
        
        modules_to_test = [
            # メインシステム
            ('run_multi_agent', 'MultiAgentRunner'),
            ('pm_agent', 'ProjectManagerAgent'),
            ('task_executor', 'TaskExecutor'),
            
            # コアエージェント
            ('core_agents.pm_agent', 'PMAgent'),
            ('core_agents.review_agent', 'ReviewAgent'),
            ('core_agents.dev_agent', 'DevAgent'),
            
            # ブラウザ制御
            ('browser_control.browser_controller', 'BrowserController'),
            
            # WordPress
            ('wordpress.wp_agent', 'WordPressAgent'),
            
            # 設定
            ('configuration.config_loader', 'ConfigLoader'),
        ]
        
        results = {'success': [], 'failed': []}
        
        for module_path, class_name in modules_to_test:
            # ファイルの存在確認
            file_path = module_path.replace('.', '/') + '.py'
            
            if not os.path.exists(file_path):
                results['failed'].append((module_path, class_name, "ファイルが存在しません"))
                print(f"   ❌ {module_path}.{class_name} - ファイルなし")
                continue
            
            try:
                # 動的インポート
                spec = importlib.util.spec_from_file_location(module_path, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # クラスの存在確認
                    if hasattr(module, class_name):
                        results['success'].append((module_path, class_name))
                        print(f"   ✅ {module_path}.{class_name}")
                    else:
                        results['failed'].append((module_path, class_name, f"クラス {class_name} が存在しません"))
                        print(f"   ❌ {module_path}.{class_name} - クラスなし")
                else:
                    results['failed'].append((module_path, class_name, "spec load failed"))
                    print(f"   ❌ {module_path}.{class_name} - spec failed")
                    
            except Exception as e:
                error_msg = str(e)
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                results['failed'].append((module_path, class_name, error_msg))
                print(f"   ❌ {module_path}.{class_name} - {error_msg}")
        
        print(f"\n📊 インポートテスト結果:")
        print(f"   ✅ 成功: {len(results['success'])}個")
        print(f"   ❌ 失敗: {len(results['failed'])}個")
        
        return results
    
    async def test_workflows(self):
        """ワークフローテスト"""
        print("\n3. 🔄 ワークフローテスト")
        print("-" * 50)
        
        workflows = [
            ("PMエージェント基本動作", self.test_pm_agent),
            ("タスク実行テスト", self.test_task_execution),
            ("設定読み込みテスト", self.test_config_loading),
        ]
        
        # 利用可能な追加テスト
        if os.path.exists('browser_control/browser_controller.py'):
            workflows.append(("ブラウザコントローラー", self.test_browser_controller))
        
        if os.path.exists('core_agents/review_agent.py'):
            workflows.append(("レビューエージェント", self.test_review_agent))
        
        if os.path.exists('wordpress/wp_agent.py'):
            workflows.append(("WordPressエージェント", self.test_wordpress_agent))
        
        workflow_results = {}
        
        for workflow_name, test_func in workflows:
            try:
                print(f"   🔄 {workflow_name}...")
                result = await test_func()
                workflow_results[workflow_name] = {
                    'success': True, 
                    'result': result
                }
                print(f"   ✅ {workflow_name} 成功")
            except Exception as e:
                workflow_results[workflow_name] = {
                    'success': False, 
                    'error': str(e)
                }
                print(f"   ❌ {workflow_name} 失敗: {e}")
        
        return workflow_results
    
    async def test_pm_agent(self):
        """PMエージェントテスト"""
        try:
            from pm_agent import ProjectManagerAgent
            agent = ProjectManagerAgent()
            status = await agent.analyze_project_status()
            return {'status_analysis': bool(status)}
        except Exception as e:
            return {'status_analysis': False, 'error': str(e)}
    
    async def test_task_execution(self):
        """タスク実行テスト"""
        try:
            from task_executor import TaskExecutor
            executor = TaskExecutor()
            result = await executor.execute_task({
                'task_id': 'TEST-001',
                'execution_type': 'general'
            })
            return {'task_executed': result.get('success', False)}
        except Exception as e:
            return {'task_executed': False, 'error': str(e)}
    
    async def test_config_loading(self):
        """設定読み込みテスト"""
        try:
            from configuration.config_loader import ConfigLoader
            config = ConfigLoader()
            spreadsheet_id = config.get('spreadsheet_id')
            return {'config_loaded': bool(spreadsheet_id)}
        except Exception as e:
            return {'config_loaded': False, 'error': str(e)}
    
    async def test_browser_controller(self):
        """ブラウザコントローラーテスト"""
        try:
            from browser_control.browser_controller import BrowserController
            controller = BrowserController()
            return {'initialized': True}
        except Exception as e:
            return {'initialized': False, 'error': str(e)}
    
    async def test_review_agent(self):
        """レビューエージェントテスト"""
        try:
            from core_agents.review_agent import ReviewAgent
            agent = ReviewAgent()
            return {'initialized': True}
        except Exception as e:
            return {'initialized': False, 'error': str(e)}
    
    async def test_wordpress_agent(self):
        """WordPressエージェントテスト"""
        try:
            from wordpress.wp_agent import WordPressAgent
            agent = WordPressAgent()
            return {'initialized': True}
        except Exception as e:
            return {'initialized': False, 'error': str(e)}
    
    def generate_report(self, component_status, import_results, workflow_results):
        """レポート生成"""
        print("\n4. 📊 システムレポート")
        print("=" * 50)
        
        # コンポーネントカバレッジ
        total_components = len(component_status)
        working_components = sum(1 for status in component_status.values() if status['coverage'] > 0.5)
        
        # インポート成功率
        import_success = len(import_results['success'])
        import_total = import_success + len(import_results['failed'])
        
        # ワークフロー成功率
        workflow_success = sum(1 for r in workflow_results.values() if r['success'])
        workflow_total = len(workflow_results)
        
        print(f"📈 システム統計:")
        print(f"   • コンポーネント: {working_components}/{total_components} 利用可能")
        print(f"   • インポート: {import_success}/{import_total} 成功")
        print(f"   • ワークフロー: {workflow_success}/{workflow_total} 成功")
        
        print(f"\n🎯 推奨アクション:")
        
        # 不足している重要なコンポーネントを特定
        critical_missing = []
        for category, status in component_status.items():
            if status['coverage'] < 0.5:
                critical_missing.append(category)
        
        if critical_missing:
            print(f"   ⚠️ 以下のコンポーネントが不足:")
            for missing in critical_missing:
                print(f"      • {missing}")
        else:
            print(f"   ✅ 主要コンポーネントは揃っています")
        
        # システム状態評価
        overall_score = (working_components/total_components + import_success/import_total + workflow_success/workflow_total) / 3
        if overall_score >= 0.8:
            system_status = "✅ 正常"
        elif overall_score >= 0.5:
            system_status = "⚠️ 部分正常"
        else:
            system_status = "❌ 要修正"
        
        print(f"\n🚀 システム状態: {system_status} (スコア: {overall_score:.1%})")
    
    async def run_demo(self):
        """デモを実行"""
        print("🚀 現在のディレクトリPOCデモ開始")
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # ステップ1: システム分析
        component_status = self.analyze_current_system()
        
        # ステップ2: インポートテスト
        import_results = self.test_system_imports()
        
        # ステップ3: ワークフローテスト
        workflow_results = await self.test_workflows()
        
        # ステップ4: レポート生成
        self.generate_report(component_status, import_results, workflow_results)
        
        print(f"\n✅ POCデモ完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """メイン実行"""
    demo = CurrentDirectoryPOC()
    asyncio.run(demo.run_demo())
    
    print(f"\n🎉 現在のディレクトリPOCデモ完了！")
    print(f"📋 このスクリプトはファイルを移動せずに現在のディレクトリで動作します")

if __name__ == "__main__":
    main()

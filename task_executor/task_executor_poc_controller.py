#!/usr/bin/env python3
"""
�� POCデモ用タスク実行コントローラー - 実際の成果物生成
"""

import asyncio
from datetime import datetime

class POCEnhancedTaskExecutor:
    """POC拡張タスク実行クラス"""
    
    def __init__(self):
        self.poc_executors = {
            'content': self._execute_poc_content,
            'wordpress': self._execute_poc_wordpress,
            'ma_research': self._execute_poc_research,
            'planning': self._execute_poc_planning
        }
    
    async def execute_poc_task(self, task_info):
        """POCタスクを実行"""
        execution_type = task_info.get('execution_type', 'general')
        executor = self.poc_executors.get(execution_type, self._execute_poc_general)
        
        try:
            print(f"      🎯 POC実行開始: {task_info['task_id']}")
            result = await executor(task_info)
            print(f"      ✅ POC実行完了: {task_info['task_id']}")
            return result
        except Exception as e:
            print(f"      ❌ POC実行エラー: {task_info['task_id']} - {e}")
            return {
                'task_id': task_info['task_id'],
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _execute_poc_content(self, task_info):
        """POCコンテンツタスクを実行"""
        from task_executor_poc import POCContentExecutor
        executor = POCContentExecutor()
        result = await executor.execute(task_info)
        
        return {
            'task_id': task_info['task_id'],
            'success': True,
            'type': 'poc_content',
            'result': result,
            'output_files': self._get_output_files('poc_output/*.md'),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _execute_poc_wordpress(self, task_info):
        """POC WordPressタスクを実行"""
        from task_executor_poc import POCWordPressExecutor
        executor = POCWordPressExecutor()
        result = await executor.execute(task_info)
        
        return {
            'task_id': task_info['task_id'],
            'success': True,
            'type': 'poc_wordpress',
            'result': result,
            'output_files': self._get_output_files('poc_output/wordpress/*.php'),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _execute_poc_research(self, task_info):
        """POC調査タスクを実行"""
        from task_executor_poc import POCResearchExecutor
        executor = POCResearchExecutor()
        result = await executor.execute(task_info)
        
        return {
            'task_id': task_info['task_id'],
            'success': True,
            'type': 'poc_research',
            'result': result,
            'output_files': self._get_output_files('poc_output/research/*.md'),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _execute_poc_planning(self, task_info):
        """POC計画タスクを実行"""
        print(f"      📋 POC計画作成: {task_info['task_id']}")
        
        # 計画作成のシミュレーション
        await asyncio.sleep(1)
        
        plan = {
            'mvp_features': [
                '企業情報登録機能',
                '基本検索機能',
                '問い合わせフォーム',
                '管理画面基本機能'
            ],
            'priority': '高',
            'estimated_timeline': '2-3週間',
            'required_resources': ['開発者1名', 'デザイナー1名']
        }
        
        # 計画ファイルの保存
        await self._save_plan_to_file(plan, task_info['task_id'])
        
        return {
            'task_id': task_info['task_id'],
            'success': True,
            'type': 'poc_planning',
            'result': plan,
            'output_files': self._get_output_files('poc_output/plans/*.md'),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _execute_poc_general(self, task_info):
        """POC一般タスクを実行"""
        print(f"      ⚙️ POC一般タスク: {task_info['task_id']}")
        
        await asyncio.sleep(0.5)
        
        return {
            'task_id': task_info['task_id'],
            'success': True,
            'type': 'poc_general',
            'result': {'message': 'POC一般タスクを実行しました'},
            'timestamp': datetime.now().isoformat()
        }
    
    async def _save_plan_to_file(self, plan, task_id):
        """計画をファイルに保存"""
        import os
        try:
            os.makedirs('poc_output/plans', exist_ok=True)
            
            filename = f"poc_output/plans/{task_id}_plan.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# MVP計画: {task_id}\n\n")
                f.write(f"作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## MVP機能\n")
                for feature in plan.get('mvp_features', []):
                    f.write(f"- {feature}\n")
                
                f.write(f"\n## 優先度: {plan.get('priority', '')}\n")
                f.write(f"## 推定期間: {plan.get('estimated_timeline', '')}\n")
                f.write(f"## 必要リソース: {', '.join(plan.get('required_resources', []))}\n")
            
            print(f"      💾 計画ファイル保存: {filename}")
            return True
            
        except Exception as e:
            print(f"      ⚠️ 計画ファイル保存エラー: {e}")
            return False
    
    def _get_output_files(self, pattern):
        """出力ファイルを取得"""
        import glob
        try:
            files = glob.glob(pattern)
            return [f.replace('\\', '/') for f in files]  # Windowsパスを統一
        except:
            return []

if __name__ == "__main__":
    # テスト実行
    async def test():
        executor = POCEnhancedTaskExecutor()
        
        test_task = {
            'task_id': 'POC-TEST-001',
            'description': 'テストタスク',
            'execution_type': 'content'
        }
        
        result = await executor.execute_poc_task(test_task)
        print(f"POCテスト結果: {result}")
    
    asyncio.run(test())

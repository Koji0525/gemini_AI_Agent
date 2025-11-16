"""
実用ツール生成版Executor v2.3
既存のサンプルコード生成から、実用ツール生成へ転換
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.task_execution.enhanced_executor_v2 import EnhancedTaskExecutorV2
from agents.context_analyzer.project_analyzer import ProjectContextAnalyzer, generate_practical_cli_tool
from pathlib import Path


class PracticalToolExecutor(EnhancedTaskExecutorV2):
    """実用ツール生成版Executor"""
    
    def __init__(self, knowledge_manager=None):
        super().__init__(knowledge_manager)
        self.analyzer = ProjectContextAnalyzer()
    
    def _execute_cli_task(self, task, task_dir):
        """CLI実装（実用ツール版）"""
        task_id = task.get('task_id')
        description = task.get('description')
        
        # プロジェクトコンテキストを活用して実用ツールを生成
        practical_tools = generate_practical_cli_tool(
            task_id,
            description,
            self.analyzer.context
        )
        
        output_files = []
        for filename, content in practical_tools.items():
            file_path = task_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            output_files.append(str(file_path))
        
        return {
            'summary': f'実用CLIツール（{len(practical_tools)}ファイル）を生成しました',
            'output_files': output_files,
            'execution_log': f'''実用ツール生成完了
  - task_cli.py: 実際のタスク管理に使用可能
  - README.md: 使用方法と効率化の説明
  
🚀 すぐに使えます！
   python agent_outputs/tasks/task_{task_id}/task_cli.py list-tasks'''
        }

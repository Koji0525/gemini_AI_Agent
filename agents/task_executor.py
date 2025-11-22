"""
タスク実行エンジン
新しいフォルダ名形式対応版
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.folder_name_formatter import format_folder_name, parse_task_info_from_sheet

class TaskExecutor:
    """タスク実行エンジン"""
    
    def __init__(self):
        self.output_base_dir = Path('/workspaces/gemini_AI_Agent/agents/generated')
        self.output_base_dir.mkdir(exist_ok=True)
        self.sequence_counter = {}
    
    def execute_task(self, task_data: dict) -> dict:
        """
        タスク実行
        
        Args:
            task_data: {
                'parent_goal_id': str,
                'task_id': str,
                'task_name': str,
                'description': str,
                ...
            }
        
        Returns:
            result: {
                'success': bool,
                'output_path': str,
                'folder_name': str,
                ...
            }
        """
        
        # タスク情報抽出
        parent_goal_id = task_data.get('parent_goal_id', '0')
        task_id = task_data.get('task_id', '0')
        task_name = task_data.get('task_name', task_data.get('title', 'unknown'))
        
        # 連番取得
        key = f"{parent_goal_id}_{task_id}_{task_name}"
        if key not in self.sequence_counter:
            self.sequence_counter[key] = 1
        else:
            self.sequence_counter[key] += 1
        
        sequence = self.sequence_counter[key]
        
        # フォルダ名生成
        folder_name = format_folder_name(
            parent_goal_id=parent_goal_id,
            task_id=task_id,
            task_name=task_name,
            sequence_number=sequence
        )
        
        # 出力パス
        output_path = self.output_base_dir / folder_name
        output_path.mkdir(exist_ok=True)
        
        print(f"📁 出力フォルダ: {folder_name}")
        
        # タスク実行（ここに実際のコード生成ロジック）
        # ...
        
        return {
            'success': True,
            'output_path': str(output_path),
            'folder_name': folder_name,
            'parent_goal_id': parent_goal_id,
            'task_id': task_id,
            'task_name': task_name,
            'sequence': sequence
        }


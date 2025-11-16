#!/usr/bin/env python3
"""
タスク詳細化インタビューシステム
既存のpm_agent_interview.pyをタスクレベルに適用
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from tools.sheets_manager import GoogleSheetsManager


class TaskInterviewer:
    """タスク詳細化インタビュー"""
    
    def __init__(self):
        self.sheets = GoogleSheetsManager()
        self.output_dir = Path("agent_outputs/tasks")
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """タスク情報を取得"""
        tasks = self.sheets.read_range('pm_tasks!A2:M1000')
        
        for row in tasks:
            if row[0] == task_id:
                return {
                    'task_id': row[0],
                    'parent_goal_id': row[1] if len(row) > 1 else '',
                    'description': row[2] if len(row) > 2 else '',
                    'required_role': row[3] if len(row) > 3 else ''
                }
        
        raise ValueError(f"タスク {task_id} が見つかりません")
    
    def conduct_interview(self, task_id: str) -> Dict[str, Any]:
        """詳細化インタビュー実施"""
        task = self.get_task(task_id)
        
        print(f"\n{'='*60}")
        print(f"タスク詳細化インタビュー")
        print(f"{'='*60}")
        print(f"\nタスクID: {task_id}")
        print(f"説明: {task['description']}")
        print(f"\n以下の質問に答えて、タスクを詳細化します。")
        print(f"（Enterのみで次へ、空白の質問はスキップ）\n")
        
        questions = {
            'target_users': {
                'q': '1. このツールは誰が使いますか？（例: 開発者、PM、自分自身）',
                'default': '開発者'
            },
            'primary_purpose': {
                'q': '2. このツールの主な目的は何ですか？（例: タスク管理を効率化、コード生成を自動化）',
                'default': ''
            },
            'key_features': {
                'q': '3. 必須機能TOP3を教えてください（例: 1. タスク一覧, 2. タスク実行, 3. 統計表示）',
                'default': ''
            },
            'input_data': {
                'q': '4. このツールは何をインプットとして受け取りますか？（例: タスクID、ファイルパス）',
                'default': ''
            },
            'output_data': {
                'q': '5. このツールは何をアウトプットしますか？（例: レポートファイル、実行結果）',
                'default': ''
            },
            'integration_points': {
                'q': '6. 既存のどのシステムと連携しますか？（例: Google Sheets, GitHub）',
                'default': ''
            },
            'performance_target': {
                'q': '7. パフォーマンス目標は？（例: 処理時間5秒以内、手動作業を10倍効率化）',
                'default': ''
            },
            'success_criteria': {
                'q': '8. 成功の判断基準は？（例: 全テストがパス、実際に使えて時間短縮できる）',
                'default': ''
            },
            'expected_files': {
                'q': '9. 期待される成果物ファイルは？（例: cli_tool.py, README.md, test_*.py）',
                'default': ''
            },
            'constraints': {
                'q': '10. 制約条件は？（例: Pythonのみ、外部API不使用、既存コードを壊さない）',
                'default': ''
            },
            'priority': {
                'q': '11. 優先度は？（high/medium/low）',
                'default': 'medium'
            },
            'estimated_time': {
                'q': '12. 実装にかかる予想時間は？（例: 2時間、1日）',
                'default': '2時間'
            }
        }
        
        answers = {
            'task_id': task_id,
            'original_description': task['description'],
            'interview_date': datetime.now().isoformat()
        }
        
        for key, meta in questions.items():
            response = input(f"\n{meta['q']}\n> ").strip()
            answers[key] = response if response else meta['default']
        
        return answers
    
    def save_interview(self, task_id: str, answers: Dict[str, Any]) -> Path:
        """インタビュー結果を保存"""
        task_dir = self.output_dir / f"task_{task_id}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"task_{task_id}_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = task_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(answers, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ インタビュー結果を保存: {filepath}")
        return filepath


def main():
    if len(sys.argv) < 2:
        print("使用方法: python task_interview.py <task_id>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    
    interviewer = TaskInterviewer()
    answers = interviewer.conduct_interview(task_id)
    filepath = interviewer.save_interview(task_id, answers)
    
    print(f"\n{'='*60}")
    print("次のステップ:")
    print(f"  python agents/task_requirements/task_requirements_generator.py {task_id}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

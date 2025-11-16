#!/usr/bin/env python3
"""
Google Sheetsベースのタスクインタビュー
使いやすさ重視版
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from tools.sheets_manager import GoogleSheetsManager


class TaskInterviewerSheets:
    """Google Sheetsベースのインタビュー"""
    
    SHEET_NAME = 'task_interviews'
    
    def __init__(self):
        self.sheets = GoogleSheetsManager()
        self._ensure_sheet_exists()
    
    def _ensure_sheet_exists(self):
        """task_interviewsシートが存在するか確認・作成"""
        try:
            # シートが存在するか確認
            self.sheets.read_range(f'{self.SHEET_NAME}!A1:A1')
        except Exception:
            # シートが存在しない場合は作成
            print(f"\n⚠️  {self.SHEET_NAME} シートが存在しません")
            print(f"以下のヘッダーでシートを作成してください:\n")
            print("A列: task_id")
            print("B列: target_users")
            print("C列: primary_purpose")
            print("D列: key_features")
            print("E列: input_data")
            print("F列: output_data")
            print("G列: integration_points")
            print("H列: performance_target")
            print("I列: success_criteria")
            print("J列: expected_files")
            print("K列: constraints")
            print("L列: priority")
            print("M列: estimated_time")
            print(f"\nまたは、以下のコマンドでテンプレートを生成:")
            print(f"  python agents/task_requirements/create_interview_sheet_template.py")
            sys.exit(1)
    
    def read_interview(self, task_id: str) -> Dict[str, Any]:
        """Sheetsからインタビュー結果を読み込み"""
        data = self.sheets.read_range(f'{self.SHEET_NAME}!A2:M1000')
        
        for row in data:
            if row[0] == task_id:
                return {
                    'task_id': row[0],
                    'target_users': row[1] if len(row) > 1 else '',
                    'primary_purpose': row[2] if len(row) > 2 else '',
                    'key_features': row[3] if len(row) > 3 else '',
                    'input_data': row[4] if len(row) > 4 else '',
                    'output_data': row[5] if len(row) > 5 else '',
                    'integration_points': row[6] if len(row) > 6 else '',
                    'performance_target': row[7] if len(row) > 7 else '',
                    'success_criteria': row[8] if len(row) > 8 else '',
                    'expected_files': row[9] if len(row) > 9 else '',
                    'constraints': row[10] if len(row) > 10 else '',
                    'priority': row[11] if len(row) > 11 else 'medium',
                    'estimated_time': row[12] if len(row) > 12 else '2時間',
                    'interview_date': datetime.now().isoformat()
                }
        
        raise ValueError(f"タスク {task_id} のインタビューデータが見つかりません")
    
    def save_to_json(self, task_id: str) -> Path:
        """Sheetsから読み込んでJSONに保存"""
        interview = self.read_interview(task_id)
        
        output_dir = Path("agent_outputs/tasks") / f"task_{task_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"task_{task_id}_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(interview, f, indent=2, ensure_ascii=False)
        
        print(f"✅ インタビュー結果をJSONに変換: {filepath}")
        return filepath


def main():
    if len(sys.argv) < 2:
        print("使用方法: python task_interview_sheets.py <task_id>")
        print("\n手順:")
        print("  1. Google Sheetsの task_interviews シートにデータを入力")
        print("  2. このスクリプトを実行してJSONに変換")
        sys.exit(1)
    
    task_id = sys.argv[1]
    
    interviewer = TaskInterviewerSheets()
    filepath = interviewer.save_to_json(task_id)
    
    print(f"\n{'='*60}")
    print("次のステップ:")
    print(f"  python agents/task_requirements/task_requirements_generator.py {task_id}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

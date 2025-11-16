#!/usr/bin/env python3
"""
JSONテンプレート生成システム
VSCodeで編集しやすいテンプレートを生成
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

import json
from pathlib import Path
from datetime import datetime

from tools.sheets_manager import GoogleSheetsManager


def generate_template(task_id: str) -> Path:
    """編集用JSONテンプレートを生成"""
    
    # タスク情報を取得
    sheets = GoogleSheetsManager()
    tasks = sheets.read_range('pm_tasks!A2:M1000')
    
    task_desc = ""
    for row in tasks:
        if row[0] == task_id:
            task_desc = row[2] if len(row) > 2 else ''
            break
    
    template = {
        "_instructions": {
            "ja": "このファイルをVSCodeで編集してください。編集後、保存して task_interview_from_json.py を実行します。",
            "en": "Edit this file in VSCode. After editing, save and run task_interview_from_json.py"
        },
        "task_id": task_id,
        "original_description": task_desc,
        "interview_date": datetime.now().isoformat(),
        
        "questions": {
            "target_users": {
                "question": "このツールは誰が使いますか？",
                "examples": ["開発者", "PM", "自分自身"],
                "answer": ""
            },
            "primary_purpose": {
                "question": "このツールの主な目的は何ですか？",
                "examples": ["タスク管理を効率化", "コード生成を自動化"],
                "answer": ""
            },
            "key_features": {
                "question": "必須機能TOP3を教えてください",
                "examples": ["1. タスク一覧", "2. タスク実行", "3. 統計表示"],
                "answer": ""
            },
            "input_data": {
                "question": "このツールは何をインプットとして受け取りますか？",
                "examples": ["タスクID", "ファイルパス"],
                "answer": ""
            },
            "output_data": {
                "question": "このツールは何をアウトプットしますか？",
                "examples": ["レポートファイル", "実行結果"],
                "answer": ""
            },
            "integration_points": {
                "question": "既存のどのシステムと連携しますか？",
                "examples": ["Google Sheets", "GitHub"],
                "answer": ""
            },
            "performance_target": {
                "question": "パフォーマンス目標は？",
                "examples": ["処理時間5秒以内", "手動作業を10倍効率化"],
                "answer": ""
            },
            "success_criteria": {
                "question": "成功の判断基準は？",
                "examples": ["全テストがパス", "実際に使えて時間短縮できる"],
                "answer": ""
            },
            "expected_files": {
                "question": "期待される成果物ファイルは？",
                "examples": ["cli_tool.py", "README.md", "test_*.py"],
                "answer": ""
            },
            "constraints": {
                "question": "制約条件は？",
                "examples": ["Pythonのみ", "外部API不使用", "既存コードを壊さない"],
                "answer": ""
            },
            "priority": {
                "question": "優先度は？",
                "examples": ["high", "medium", "low"],
                "answer": "medium"
            },
            "estimated_time": {
                "question": "実装にかかる予想時間は？",
                "examples": ["2時間", "1日"],
                "answer": "2時間"
            }
        }
    }
    
    # 保存
    output_dir = Path("agent_outputs/tasks") / f"task_{task_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    template_path = output_dir / f"task_{task_id}_interview_template.json"
    
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ テンプレート生成: {template_path}")
    print(f"\n次のステップ:")
    print(f"  1. VSCodeでファイルを開く:")
    print(f"     code {template_path}")
    print(f"  2. 各質問の 'answer' フィールドを編集")
    print(f"  3. 保存して実行:")
    print(f"     python agents/task_requirements/task_interview_from_json.py {task_id}")
    
    return template_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python task_interview_template.py <task_id>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    generate_template(task_id)

#!/usr/bin/env python3
"""
JSONテンプレートから読み込み
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

import json
from pathlib import Path
from datetime import datetime


def read_from_template(task_id: str) -> Path:
    """編集済みJSONテンプレートを読み込み"""
    
    task_dir = Path("agent_outputs/tasks") / f"task_{task_id}"
    template_path = task_dir / f"task_{task_id}_interview_template.json"
    
    if not template_path.exists():
        print(f"❌ テンプレートが見つかりません: {template_path}")
        print(f"まず以下を実行してください:")
        print(f"  python agents/task_requirements/task_interview_template.py {task_id}")
        sys.exit(1)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = json.load(f)
    
    # answersを抽出
    answers = {
        'task_id': template['task_id'],
        'original_description': template['original_description'],
        'interview_date': datetime.now().isoformat()
    }
    
    for key, data in template['questions'].items():
        answers[key] = data['answer']
    
    # 正式なインタビュー結果として保存
    result_path = task_dir / f"task_{task_id}_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(answers, f, indent=2, ensure_ascii=False)
    
    print(f"✅ インタビュー結果を保存: {result_path}")
    return result_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python task_interview_from_json.py <task_id>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    read_from_template(task_id)
    
    print(f"\n{'='*60}")
    print("次のステップ:")
    print(f"  python agents/task_requirements/task_requirements_generator.py {task_id}")
    print(f"{'='*60}")

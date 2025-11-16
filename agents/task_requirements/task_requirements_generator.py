#!/usr/bin/env python3
"""
タスク要件定義書自動生成
インタビュー結果から詳細な要件定義書を生成
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class TaskRequirementsGenerator:
    """タスク要件定義書生成"""
    
    def __init__(self):
        self.output_dir = Path("agent_outputs/tasks")
    
    def find_latest_interview(self, task_id: str) -> Path:
        """最新のインタビュー結果を検索"""
        task_dir = self.output_dir / f"task_{task_id}"
        
        if not task_dir.exists():
            raise FileNotFoundError(f"タスクディレクトリが見つかりません: {task_dir}")
        
        interview_files = sorted(task_dir.glob(f"task_{task_id}_interview_*.json"), reverse=True)
        
        if not interview_files:
            raise FileNotFoundError(f"インタビューファイルが見つかりません")
        
        return interview_files[0]
    
    def generate_requirements(self, task_id: str) -> Dict[str, Any]:
        """要件定義書を生成"""
        interview_path = self.find_latest_interview(task_id)
        
        with open(interview_path, 'r', encoding='utf-8') as f:
            interview = json.load(f)
        
        # 詳細な要件定義書を構築
        requirements = {
            'metadata': {
                'task_id': task_id,
                'original_description': interview.get('original_description'),
                'generated_at': datetime.now().isoformat(),
                'version': '1.0'
            },
            'overview': {
                'purpose': interview.get('primary_purpose'),
                'target_users': interview.get('target_users'),
                'priority': interview.get('priority'),
                'estimated_time': interview.get('estimated_time')
            },
            'functional_requirements': {
                'key_features': self._parse_key_features(interview.get('key_features', '')),
                'input': interview.get('input_data'),
                'output': interview.get('output_data'),
                'integration_points': interview.get('integration_points')
            },
            'non_functional_requirements': {
                'performance': interview.get('performance_target'),
                'constraints': interview.get('constraints')
            },
            'success_criteria': {
                'criteria': interview.get('success_criteria'),
                'expected_outputs': self._parse_expected_files(interview.get('expected_files', ''))
            },
            'subtasks': self._generate_subtasks(interview)
        }
        
        return requirements
    
    def _parse_key_features(self, features_str: str) -> list:
        """主要機能をパース"""
        if not features_str:
            return []
        
        # "1. 機能A, 2. 機能B" 形式をパース
        features = []
        for line in features_str.split(','):
            line = line.strip()
            if line:
                # "1. " などの番号を除去
                feature = line.split('.', 1)[-1].strip()
                features.append(feature)
        
        return features
    
    def _parse_expected_files(self, files_str: str) -> list:
        """期待ファイルをパース"""
        if not files_str:
            return []
        
        return [f.strip() for f in files_str.split(',') if f.strip()]
    
    def _generate_subtasks(self, interview: Dict[str, Any]) -> list:
        """サブタスクを生成"""
        key_features = self._parse_key_features(interview.get('key_features', ''))
        
        subtasks = []
        
        # Phase 1: 基盤実装
        subtasks.append({
            'phase': 'Phase 1: 基盤',
            'name': 'プロジェクト構造セットアップ',
            'purpose': '開発の基盤を整備',
            'success_criteria': '必要なディレクトリとファイルが作成されている',
            'expected_outputs': ['README.md', 'requirements.txt']
        })
        
        # Phase 2: 主要機能実装（キー機能ごと）
        for i, feature in enumerate(key_features, 1):
            subtasks.append({
                'phase': f'Phase 2: 主要機能 {i}',
                'name': f'{feature} の実装',
                'purpose': f'{feature}を実現する',
                'success_criteria': f'{feature}が動作する',
                'expected_outputs': [f'{feature.lower().replace(" ", "_")}.py']
            })
        
        # Phase 3: テスト
        subtasks.append({
            'phase': 'Phase 3: テスト',
            'name': 'テストスイート作成',
            'purpose': '品質を保証する',
            'success_criteria': '全テストがパス',
            'expected_outputs': ['test_suite.py']
        })
        
        # Phase 4: ドキュメント
        subtasks.append({
            'phase': 'Phase 4: ドキュメント',
            'name': 'ドキュメント整備',
            'purpose': '使用方法を明確にする',
            'success_criteria': 'README が完備されている',
            'expected_outputs': ['README.md', 'USAGE.md']
        })
        
        return subtasks
    
    def save_requirements(self, task_id: str, requirements: Dict[str, Any]) -> Path:
        """要件定義書を保存"""
        task_dir = self.output_dir / f"task_{task_id}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON形式
        json_path = task_dir / f"task_{task_id}_requirements.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(requirements, f, indent=2, ensure_ascii=False)
        
        # Markdown形式（読みやすい）
        md_path = task_dir / f"task_{task_id}_requirements.md"
        md_content = self._generate_markdown(requirements)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ 要件定義書を保存:")
        print(f"  - {json_path}")
        print(f"  - {md_path}")
        
        return json_path
    
    def _generate_markdown(self, req: Dict[str, Any]) -> str:
        """Markdown要件定義書を生成"""
        lines = []
        lines.append(f"# タスク要件定義書: {req['metadata']['task_id']}")
        lines.append(f"\n**生成日時**: {req['metadata']['generated_at']}")
        lines.append(f"\n## 📋 概要")
        lines.append(f"- **目的**: {req['overview']['purpose']}")
        lines.append(f"- **対象ユーザー**: {req['overview']['target_users']}")
        lines.append(f"- **優先度**: {req['overview']['priority']}")
        lines.append(f"- **予想時間**: {req['overview']['estimated_time']}")
        
        lines.append(f"\n## 🎯 機能要件")
        lines.append(f"### 主要機能")
        for feature in req['functional_requirements']['key_features']:
            lines.append(f"- {feature}")
        
        lines.append(f"\n### 入出力")
        lines.append(f"- **入力**: {req['functional_requirements']['input']}")
        lines.append(f"- **出力**: {req['functional_requirements']['output']}")
        
        lines.append(f"\n## ✅ 成功基準")
        lines.append(f"{req['success_criteria']['criteria']}")
        
        lines.append(f"\n### 期待成果物")
        for output in req['success_criteria']['expected_outputs']:
            lines.append(f"- {output}")
        
        lines.append(f"\n## 📊 サブタスク")
        for subtask in req['subtasks']:
            lines.append(f"\n### {subtask['phase']}: {subtask['name']}")
            lines.append(f"- **目的**: {subtask['purpose']}")
            lines.append(f"- **成功基準**: {subtask['success_criteria']}")
            lines.append(f"- **成果物**: {', '.join(subtask['expected_outputs'])}")
        
        return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("使用方法: python task_requirements_generator.py <task_id>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    
    generator = TaskRequirementsGenerator()
    requirements = generator.generate_requirements(task_id)
    filepath = generator.save_requirements(task_id, requirements)
    
    print(f"\n{'='*60}")
    print("次のステップ:")
    print(f"  python agents/task_requirements/task_executor_enhanced.py {task_id}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

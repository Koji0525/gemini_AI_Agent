"""
動作確認済みコード抽出システム
Phase 3で生成されたコードから「動作するコード」を抽出
"""

import sys
import os
from pathlib import Path
import re

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class WorkingCodeExtractor:
    """動作確認済みコード抽出"""
    
    def extract_working_knowledge(
        self,
        task_id: str,
        output_path: str,
        quality_score: float,
        test_results: dict
    ) -> dict:
        """
        動作確認済みコードからナレッジを抽出
        
        Returns:
            knowledge: {
                'title': タイトル,
                'problem': 解決した問題,
                'solution': 解決策,
                'working_code': 動作確認済みコード,
                'usage': 使い方,
                'lessons': 学んだこと
            }
        """
        
        output_dir = Path(output_path)
        
        # README読み込み
        readme_content = self._read_file(output_dir / 'README.md')
        
        # メインコード読み込み
        main_code = self._read_file(output_dir / 'main.py')
        
        # 問題と解決策を抽出
        problem = self._extract_problem(readme_content, task_id)
        solution = self._extract_solution(readme_content, main_code)
        
        # 動作確認済みコードを抽出（最も重要な部分）
        working_code = self._extract_core_code(main_code)
        
        # 使い方を抽出
        usage = self._extract_usage(output_dir / 'USAGE.md', readme_content)
        
        # 学びを生成
        lessons = self._generate_lessons(
            task_id, problem, solution, quality_score
        )
        
        return {
            'title': self._generate_title(task_id),
            'problem': problem,
            'solution': solution,
            'working_code': working_code,
            'usage': usage,
            'lessons': lessons,
            'quality_score': quality_score,
            'test_status': 'passed' if test_results.get('passed', False) else 'unknown'
        }
    
    def _read_file(self, filepath: Path) -> str:
        """ファイル読み込み"""
        if filepath.exists():
            return filepath.read_text(encoding='utf-8', errors='ignore')
        return ""
    
    def _extract_problem(self, readme: str, task_id: str) -> str:
        """問題を抽出"""
        # READMEから「問題」「課題」セクションを抽出
        problem_patterns = [
            r'## 問題.*?\n(.*?)(?=\n##|\Z)',
            r'## 課題.*?\n(.*?)(?=\n##|\Z)',
            r'## 概要.*?\n(.*?)(?=\n##|\Z)'
        ]
        
        for pattern in problem_patterns:
            match = re.search(pattern, readme, re.DOTALL)
            if match:
                return match.group(1).strip()[:500]
        
        # パターンが見つからない場合はタスクIDから推測
        return f"{task_id}の実装"
    
    def _extract_solution(self, readme: str, code: str) -> str:
        """解決策を抽出"""
        # READMEから「解決」「実装」セクションを抽出
        solution_patterns = [
            r'## 実装.*?\n(.*?)(?=\n##|\Z)',
            r'## 機能.*?\n(.*?)(?=\n##|\Z)'
        ]
        
        for pattern in solution_patterns:
            match = re.search(pattern, readme, re.DOTALL)
            if match:
                return match.group(1).strip()[:500]
        
        # コードから関数・クラスを抽出
        if 'class ' in code:
            return "クラスベースの実装"
        elif 'def ' in code:
            return "関数ベースの実装"
        else:
            return "スクリプト実装"
    
    def _extract_core_code(self, code: str, max_lines: int = 30) -> str:
        """最も重要なコード部分を抽出"""
        if not code:
            return "# コードなし"
        
        lines = code.split('\n')
        
        # インポート文を除外
        code_lines = [l for l in lines if not l.strip().startswith('import') 
                      and not l.strip().startswith('from')]
        
        # コメント行を除外
        code_lines = [l for l in code_lines if not l.strip().startswith('#')]
        
        # 空行を除外
        code_lines = [l for l in code_lines if l.strip()]
        
        # 最初のmax_lines行を取得
        core_lines = code_lines[:max_lines]
        
        return '\n'.join(core_lines)
    
    def _extract_usage(self, usage_file: Path, readme: str) -> str:
        """使い方を抽出"""
        # USAGE.mdがあればそれを使用
        if usage_file.exists():
            usage = self._read_file(usage_file)
            return usage[:300]
        
        # READMEから「使い方」セクションを抽出
        usage_patterns = [
            r'## 使い方.*?\n(.*?)(?=\n##|\Z)',
            r'## Usage.*?\n(.*?)(?=\n##|\Z)'
        ]
        
        for pattern in usage_patterns:
            match = re.search(pattern, readme, re.DOTALL)
            if match:
                return match.group(1).strip()[:300]
        
        return "詳細はREADME.mdを参照"
    
    def _generate_title(self, task_id: str) -> str:
        """タイトル生成"""
        # task_idをクリーンアップ
        title = task_id.replace('_', ' ').replace('-', ' ')
        return title[:100]
    
    def _generate_lessons(
        self,
        task_id: str,
        problem: str,
        solution: str,
        quality_score: float
    ) -> str:
        """学びを生成"""
        lessons = []
        
        if quality_score >= 9.0:
            lessons.append("✅ 高品質な実装パターン（9点以上）")
        
        if 'async' in solution.lower():
            lessons.append("✅ 非同期処理を活用")
        
        if 'test' in task_id.lower():
            lessons.append("✅ テスト駆動開発")
        
        if not lessons:
            lessons.append("✅ 動作確認済みの実装")
        
        return '\n'.join(lessons)


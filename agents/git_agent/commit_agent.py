#!/usr/bin/env python3
"""
Git Commit Agent - 自動品質チェック＋コミット
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict
import yaml

class CommitAgent:
    def __init__(self, config_path: str = "configs/git_workflows/commit_config.yaml"):
        self.project_root = Path(__file__).parent.parent.parent
        self.config = self._load_config(config_path)
        self.staged_files: List[Path] = []
        
    def _load_config(self, config_path: str) -> dict:
        full_path = self.project_root / config_path
        if not full_path.exists():
            return self._default_config()
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _default_config(self) -> dict:
        return {
            'excluded_dirs': ['_WIP', '_BACKUP', '_ARCHIVE', '__pycache__', '.git'],
            'quality_gates': {
                'compile_check': True,
                'linter': False,
                'formatter': False
            }
        }
    
    def list_commit_targets(self) -> List[Path]:
        """コミット対象ファイルをリスト"""
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        files = []
        for line in result.stdout.splitlines():
            if line:
                filepath = line[3:]
                if any(excluded in filepath for excluded in self.config['excluded_dirs']):
                    continue
                
                full_path = self.project_root / filepath
                if full_path.exists() and full_path.suffix == '.py':
                    files.append(full_path)
        
        self.staged_files = files
        return files
    
    def compile_check(self) -> Tuple[bool, List[str]]:
        """構文チェック"""
        errors = []
        for file in self.staged_files:
            result = subprocess.run(
                ['python3', '-m', 'py_compile', str(file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                errors.append(f"{file.name}: {result.stderr}")
        
        return len(errors) == 0, errors
    
    def commit(self, message: str) -> bool:
        """Git commit実行"""
        for file in self.staged_files:
            subprocess.run(['git', 'add', str(file)], cwd=self.project_root)
        
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 commit_agent.py 'コミットメッセージ'")
        sys.exit(1)
    
    agent = CommitAgent()
    agent.list_commit_targets()
    
    success, errors = agent.compile_check()
    if not success:
        print("❌ 構文エラーあり")
        sys.exit(1)
    
    if agent.commit(sys.argv[1]):
        print("✅ コミット成功")
        sys.exit(0)
    else:
        print("❌ コミット失敗")
        sys.exit(1)

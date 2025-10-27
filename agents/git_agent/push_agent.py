#!/usr/bin/env python3
"""
Git Push Agent - 安全なプッシュ
"""

import subprocess
import sys
from pathlib import Path

class PushAgent:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
    
    def get_current_branch(self) -> str:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def push(self, force: bool = False) -> bool:
        """プッシュ実行"""
        branch = self.get_current_branch()
        print(f"📍 現在のブランチ: {branch}")
        
        cmd = ['git', 'push', 'origin', branch]
        if force:
            cmd.append('--force')
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {branch} へのプッシュ成功")
            return True
        else:
            print(f"❌ プッシュ失敗: {result.stderr}")
            return False

if __name__ == "__main__":
    force = '--force' in sys.argv
    agent = PushAgent()
    success = agent.push(force=force)
    sys.exit(0 if success else 1)

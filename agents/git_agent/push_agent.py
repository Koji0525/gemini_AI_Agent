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
        """現在のブランチ名取得"""
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def check_uncommitted_changes(self) -> bool:
        """未コミット変更チェック"""
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip()) == 0
    
    def push(self, force: bool = False) -> bool:
        """プッシュ実行"""
        print("\n" + "="*70)
        print("🚀 Git Push Agent")
        print("="*70)
        
        # 現在のブランチ
        branch = self.get_current_branch()
        print(f"📍 現在のブランチ: {branch}")
        
        # 未コミット変更チェック
        if not self.check_uncommitted_changes():
            print("❌ 未コミットの変更があります")
            print("   先にコミットしてください")
            return False
        
        # プッシュ実行
        cmd = ['git', 'push', 'origin', branch]
        if force:
            cmd.append('--force')
            print("⚠️  強制プッシュを実行します")
        
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

#!/usr/bin/env python3
"""
Git Branch Agent - ブランチ管理
STEP 9-10に対応
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional
import re

class BranchAgent:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
    
    def get_current_branch(self) -> str:
        """現在のブランチ名"""
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def parse_version(self, branch_name: str) -> Optional[dict]:
        """ブランチ名からバージョン解析"""
        # v1.2.0-feature のパターン
        pattern = r'v(\d+)\.(\d+)\.(\d+)(?:-(.+))?'
        match = re.match(pattern, branch_name)
        
        if match:
            return {
                'major': int(match.group(1)),
                'minor': int(match.group(2)),
                'patch': int(match.group(3)),
                'feature': match.group(4) or ''
            }
        return None
    
    def increment_version(self, version: dict, level: str = 'patch') -> dict:
        """バージョンインクリメント"""
        new_version = version.copy()
        
        if level == 'major':
            new_version['major'] += 1
            new_version['minor'] = 0
            new_version['patch'] = 0
        elif level == 'minor':
            new_version['minor'] += 1
            new_version['patch'] = 0
        else:  # patch
            new_version['patch'] += 1
        
        return new_version
    
    def format_branch_name(self, version: dict) -> str:
        """ブランチ名フォーマット"""
        base = f"v{version['major']}.{version['minor']}.{version['patch']}"
        if version['feature']:
            return f"{base}-{version['feature']}"
        return base
    
    def create_and_switch(self, new_branch: str) -> bool:
        """新規ブランチ作成＋切り替え"""
        print("\n" + "="*70)
        print(f"🌿 新規ブランチ作成: {new_branch}")
        print("="*70)
        
        # ブランチ作成
        result = subprocess.run(
            ['git', 'checkout', '-b', new_branch],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ ブランチ作成＋切り替え成功: {new_branch}")
            return True
        else:
            print(f"❌ ブランチ作成失敗: {result.stderr}")
            return False
    
    def switch(self, branch: str) -> bool:
        """ブランチ切り替え"""
        print("\n" + "="*70)
        print(f"🔄 ブランチ切り替え: {branch}")
        print("="*70)
        
        result = subprocess.run(
            ['git', 'checkout', branch],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ ブランチ切り替え成功: {branch}")
            return True
        else:
            print(f"❌ ブランチ切り替え失敗: {result.stderr}")
            return False
    
    def auto_increment(self, level: str = 'patch', feature: str = '') -> bool:
        """自動バージョンアップ＋ブランチ作成"""
        current = self.get_current_branch()
        print(f"📍 現在のブランチ: {current}")
        
        version = self.parse_version(current)
        if not version:
            print("❌ 現在のブランチがバージョン形式ではありません")
            return False
        
        # バージョンインクリメント
        new_version = self.increment_version(version, level)
        if feature:
            new_version['feature'] = feature
        
        new_branch = self.format_branch_name(new_version)
        
        return self.create_and_switch(new_branch)

if __name__ == "__main__":
    agent = BranchAgent()
    
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python3 branch_agent.py switch <ブランチ名>")
        print("  python3 branch_agent.py new <新ブランチ名>")
        print("  python3 branch_agent.py auto [patch|minor|major] [feature名]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'switch' and len(sys.argv) >= 3:
        success = agent.switch(sys.argv[2])
    elif command == 'new' and len(sys.argv) >= 3:
        success = agent.create_and_switch(sys.argv[2])
    elif command == 'auto':
        level = sys.argv[2] if len(sys.argv) >= 3 else 'patch'
        feature = sys.argv[3] if len(sys.argv) >= 4 else ''
        success = agent.auto_increment(level, feature)
    else:
        print("❌ 不正なコマンド")
        success = False
    
    sys.exit(0 if success else 1)

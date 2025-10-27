#!/usr/bin/env python3
"""
Git Workflow 統合実行スクリプト
"""

import sys
import argparse
from commit_agent import CommitAgent
from push_agent import PushAgent
from branch_agent import BranchAgent

def main():
    parser = argparse.ArgumentParser(description='Git Workflow 自動化')
    parser.add_argument('--message', '-m', required=True, help='コミットメッセージ')
    parser.add_argument('--push', action='store_true', help='コミット後にプッシュ')
    parser.add_argument('--new-branch', help='プッシュ後に新ブランチ作成')
    parser.add_argument('--version-up', choices=['patch', 'minor', 'major'], help='自動バージョンアップ')
    parser.add_argument('--feature', help='フィーチャー名')
    
    args = parser.parse_args()
    
    print("🤖 Git Workflow 自動化システム")
    
    # コミット
    commit_agent = CommitAgent()
    commit_agent.list_commit_targets()
    success, errors = commit_agent.compile_check()
    
    if not success:
        print("❌ 構文エラー")
        return False
    
    if not commit_agent.commit(args.message):
        print("❌ コミット失敗")
        return False
    
    # プッシュ
    if args.push:
        push_agent = PushAgent()
        if not push_agent.push():
            print("❌ プッシュ失敗")
            return False
    
    # ブランチ操作
    if args.new_branch or args.version_up:
        branch_agent = BranchAgent()
        
        if args.version_up:
            if not branch_agent.auto_increment(args.version_up, args.feature or ''):
                return False
        elif args.new_branch:
            if not branch_agent.create_and_switch(args.new_branch):
                return False
    
    print("✅ すべての処理が完了")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

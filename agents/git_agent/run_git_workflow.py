#!/usr/bin/env python3
"""
Git Workflow 統合実行スクリプト
ワンコマンドでコミット→プッシュ→ブランチ切り替え
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
    
    print("="*70)
    print("🤖 Git Workflow 自動化システム")
    print("="*70)
    
    # STEP 1: コミット
    print("\n【1/3】コミット実行")
    commit_agent = CommitAgent()
    if not commit_agent.run(args.message):
        print("\n❌ コミット失敗 - 処理中断")
        return False
    
    # STEP 2: プッシュ（オプション）
    if args.push:
        print("\n【2/3】プッシュ実行")
        push_agent = PushAgent()
        if not push_agent.push():
            print("\n❌ プッシュ失敗 - 処理中断")
            return False
    
    # STEP 3: ブランチ切り替え（オプション）
    if args.new_branch or args.version_up:
        print("\n【3/3】ブランチ操作")
        branch_agent = BranchAgent()
        
        if args.version_up:
            if not branch_agent.auto_increment(args.version_up, args.feature or ''):
                print("\n❌ ブランチ作成失敗")
                return False
        elif args.new_branch:
            if not branch_agent.create_and_switch(args.new_branch):
                print("\n❌ ブランチ切り替え失敗")
                return False
    
    print("\n" + "="*70)
    print("✅ すべての処理が完了しました")
    print("="*70)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

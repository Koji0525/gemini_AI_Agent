#!/usr/bin/env python3
"""
Untracked ファイル警告ツール v1.0

【目的】
auto_commit_push 実行前に Untracked ファイルを検出して警告

【使用方法】
python3 agents/git_agent/untracked_warning.py

【推奨運用】
コミット前に必ず実行:
  python3 agents/git_agent/untracked_warning.py && \\
  SKIP_AUTO_REPAIR=true python3 agents/git_agent/auto_commit_push_v11_force_push.py
"""

import subprocess
import sys


def check_untracked():
    """Untracked ファイルをチェックして警告"""
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True
    )
    
    # 重要なファイル拡張子のみフィルタ
    important_extensions = ('.py', '.html', '.sh', '.yaml', '.yml', '.json', '.md')
    untracked = [
        f for f in result.stdout.strip().split('\n') 
        if f and f.endswith(important_extensions)
        and not any(skip in f for skip in ['__pycache__', '.pyc', 'node_modules'])
    ]
    
    if untracked:
        print("━" * 60)
        print("⚠️  警告: 以下のファイルは保存されません！")
        print("━" * 60)
        for f in untracked[:15]:
            print(f"  ❌ {f}")
        if len(untracked) > 15:
            print(f"  ... 他 {len(untracked) - 15} 件")
        print("")
        print("📋 保存するには:")
        print("   git add <ファイル名>")
        print("   または")
        print("   git add .")
        print("━" * 60)
        
        # ユーザーに確認
        print("")
        print("続行しますか？ (y/N): ", end="")
        try:
            response = input().strip().lower()
            if response != 'y':
                print("❌ 中断しました。git add してから再実行してください。")
                return False
        except EOFError:
            print("❌ 中断しました。")
            return False
        
        return True
    else:
        print("✅ 全ファイルが追跡されています（Untracked なし）")
        return True


def main():
    print("━" * 60)
    print("🔍 Untracked ファイルチェック")
    print("━" * 60)
    
    if not check_untracked():
        sys.exit(1)
    
    print("✅ チェック完了")


if __name__ == "__main__":
    main()

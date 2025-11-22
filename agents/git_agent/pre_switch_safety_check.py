#!/usr/bin/env python3
"""
アカウント/ブランチ切替前 安全確認ツール v1.0

【目的】
アカウントまたはブランチを切り替える前に、
全ての変更が保存されているか確認する

【使用タイミング】
- 無料枠の関係でアカウントを切り替える前
- 別ブランチに切り替える前
- Codespacesを終了する前

【使用方法】
python3 agents/git_agent/pre_switch_safety_check.py
"""

import subprocess
import sys
from datetime import datetime


def run_command(cmd):
    """コマンドを実行して結果を返す"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def check_all():
    """全ての安全チェックを実行"""
    print("=" * 60)
    print("🔒 アカウント/ブランチ切替前 安全確認")
    print(f"   実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_safe = True
    warnings = []
    
    # チェック1: 未コミットの変更
    print("\n📋 チェック1: 未コミットの変更")
    stdout, _ = run_command(["git", "status", "--porcelain"])
    if stdout:
        modified = [l for l in stdout.split('\n') if l.startswith(' M') or l.startswith('M ')]
        deleted = [l for l in stdout.split('\n') if l.startswith(' D') or l.startswith('D ')]
        added = [l for l in stdout.split('\n') if l.startswith('A ')]
        
        if modified:
            print(f"  ⚠️  変更されたファイル: {len(modified)}件")
            for f in modified[:5]:
                print(f"      {f}")
            warnings.append("未コミットの変更があります")
            all_safe = False
        if deleted:
            print(f"  ⚠️  削除されたファイル: {len(deleted)}件")
            warnings.append("削除されたファイルがあります")
            all_safe = False
        if added:
            print(f"  ✅ ステージ済みファイル: {len(added)}件")
    else:
        print("  ✅ 未コミットの変更なし")
    
    # チェック2: Untracked ファイル
    print("\n📋 チェック2: Untracked ファイル（保存されていない）")
    stdout, _ = run_command(["git", "ls-files", "--others", "--exclude-standard"])
    important_ext = ('.py', '.html', '.sh', '.yaml', '.yml', '.json', '.md')
    untracked = [
        f for f in stdout.split('\n') 
        if f and f.endswith(important_ext)
        and '__pycache__' not in f
    ]
    
    if untracked:
        print(f"  ❌ 保存されていないファイル: {len(untracked)}件")
        for f in untracked[:10]:
            print(f"      {f}")
        if len(untracked) > 10:
            print(f"      ... 他 {len(untracked) - 10}件")
        warnings.append(f"Untracked ファイルが {len(untracked)}件 あります")
        all_safe = False
    else:
        print("  ✅ Untracked ファイルなし")
    
    # チェック3: プッシュ状態
    print("\n📋 チェック3: リモートとの同期状態")
    stdout, _ = run_command(["git", "status", "-sb"])
    if "ahead" in stdout:
        print("  ⚠️  ローカルにプッシュされていないコミットがあります")
        warnings.append("プッシュされていないコミットがあります")
        all_safe = False
    elif "behind" in stdout:
        print("  ℹ️  リモートに新しいコミットがあります（pull推奨）")
    else:
        print("  ✅ リモートと同期済み")
    
    # チェック4: 現在のブランチとリモート
    print("\n📋 チェック4: 現在の状態")
    branch, _ = run_command(["git", "branch", "--show-current"])
    print(f"  ブランチ: {branch}")
    
    remote, _ = run_command(["git", "remote", "-v"])
    if remote:
        print(f"  リモート: {remote.split()[1]}")
    
    commit, _ = run_command(["git", "log", "-1", "--oneline"])
    print(f"  最新コミット: {commit}")
    
    # 結果サマリー
    print("\n" + "=" * 60)
    if all_safe:
        print("✅ 安全: 全ての変更が保存されています")
        print("   アカウント/ブランチの切り替えが可能です")
    else:
        print("❌ 警告: 以下の問題があります")
        for w in warnings:
            print(f"   - {w}")
        print("")
        print("📋 推奨アクション:")
        print("   1. git add . (全ファイルをステージング)")
        print("   2. git commit -m 'メッセージ'")
        print("   3. git push")
        print("   4. このツールを再実行して確認")
    print("=" * 60)
    
    return all_safe


def main():
    if not check_all():
        print("\n⚠️  切り替え前に上記の問題を解決してください")
        sys.exit(1)
    else:
        print("\n✅ 切り替え準備完了")


if __name__ == "__main__":
    main()

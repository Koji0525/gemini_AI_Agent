#!/usr/bin/env python3
"""
自動コミット＆プッシュ + CI結果自動確認（v08）
"""

import sys
import subprocess
import time
import json

def run_command(cmd, check=True):
    """コマンド実行"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ エラー: {' '.join(cmd)}")
        print(f"   {result.stderr}")
        sys.exit(1)
    return result

def check_gh_cli():
    """GitHub CLI の確認"""
    result = subprocess.run(['gh', '--version'], capture_output=True)
    return result.returncode == 0

def wait_for_workflow(timeout=300):
    """ワークフロー完了を待機"""
    print("\n🔄 CI実行を待機中...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = subprocess.run(
            ['gh', 'run', 'list', '--limit', '1', '--json', 'status,conclusion,name,url'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("⚠️  GitHub CLI エラー")
            return {}
        
        try:
            runs = json.loads(result.stdout)
            if not runs:
                time.sleep(5)
                continue
            
            run = runs[0]
            status = run.get('status')
            
            if status == 'in_progress' or status == 'queued':
                print(".", end="", flush=True)
                time.sleep(10)
                continue
            
            print("\n")
            return run
        
        except json.JSONDecodeError:
            time.sleep(5)
            continue
    
    print("\n⏱️  タイムアウト: CI実行に時間がかかっています")
    return {}

def main():
    if len(sys.argv) < 2:
        print("使用法: python3 auto_commit_push_v08_with_ci_check.py '✅ コミットメッセージ'")
        sys.exit(1)
    
    commit_msg = sys.argv[1]
    
    print("=" * 60)
    print("🚀 自動コミット＆プッシュ + CI確認")
    print("=" * 60)
    
    print("\n📦 変更をステージング...")
    run_command(['git', 'add', '.'])
    
    print("💾 コミット作成...")
    run_command(['git', 'commit', '-m', commit_msg])
    
    print("⬆️  リモートにプッシュ...")
    run_command(['git', 'push'])
    
    print("✅ プッシュ完了")
    
    if not check_gh_cli():
        print("\n⚠️  GitHub CLI が未インストール")
        print("   CI結果は手動で確認してください")
        return 0
    
    print("\n" + "=" * 60)
    print("🔍 CI実行結果を確認中")
    print("=" * 60)
    
    time.sleep(5)
    
    run_info = wait_for_workflow(timeout=300)
    
    if not run_info:
        print("\n⚠️  CI結果を取得できませんでした")
        return 0
    
    conclusion = run_info.get('conclusion')
    name = run_info.get('name')
    url = run_info.get('url')
    
    print("\n" + "=" * 60)
    print("📊 CI実行結果")
    print("=" * 60)
    print(f"ワークフロー: {name}")
    
    if conclusion == 'success':
        print("\n✅ 成功: すべてのチェックに合格しました")
        print("\n" + "=" * 60)
        return 0
    
    elif conclusion == 'failure':
        print("\n❌ 失敗: エラーが検出されました")
        print(f"\n🌐 詳細: {url}")
        print("\n📋 ログを確認:")
        print("   gh run view --log")
        print("\n" + "=" * 60)
        
        print("\n🔍 エラー詳細を取得中...")
        log_result = subprocess.run(
            ['gh', 'run', 'view', '--log'],
            capture_output=True,
            text=True
        )
        
        if log_result.returncode == 0:
            lines = log_result.stdout.split('\n')
            print("\n".join(lines[-50:]))
        
        return 1
    
    else:
        print(f"\n⚠️  状態: {conclusion}")
        print(f"🌐 詳細: {url}")
        return 0

if __name__ == "__main__":
    sys.exit(main())

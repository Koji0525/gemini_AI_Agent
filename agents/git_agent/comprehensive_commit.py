#!/usr/bin/env python3
"""
包括的コミットスクリプト - ファイル漏れ防止版
"""
import subprocess
import os

def get_all_changes():
    """すべての変更ファイルを取得"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    
    changes = []
    for line in result.stdout.strip().split('\n'):
        if line:
            # ステータスとファイル名を分離
            status = line[:2]
            filename = line[3:]
            changes.append((status, filename))
    
    return changes

def commit_all_changes():
    """すべての変更をコミット"""
    # すべての変更を追加
    subprocess.run(["git", "add", "-A"])
    
    # コミット
    result = subprocess.run(
        ["git", "commit", "-m", "📦 包括的コミット: すべての変更を確保"],
        capture_output=True, text=True
    )
    
    return result.returncode == 0

if __name__ == "__main__":
    changes = get_all_changes()
    print(f"🔍 検出された変更: {len(changes)}件")
    
    for status, filename in changes:
        print(f"  {status} {filename}")
    
    if changes and commit_all_changes():
        print("✅ 包括的コミット完了")
    else:
        print("ℹ️  コミットする変更なし")

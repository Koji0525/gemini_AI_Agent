#!/usr/bin/env python3
"""安全なコード修正ツール v2"""

import subprocess
import sys
import os
from pathlib import Path

def safe_modify_file(file_path, modifications):
    """安全にファイルを修正"""
    
    # 1. バックアップ作成
    backup_path = f"{file_path}.backup"
    Path(file_path).copy(backup_path)
    print(f"✅ バックアップ作成: {backup_path}")
    
    # 2. 修正前構文チェック
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", file_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ 修正前から構文エラー: {result.stderr}")
        return False
    
    # 3. 修正適用
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old, new in modifications:
            if old in content:
                content = content.replace(old, new)
                print(f"✅ 置換実行: {old[:50]}... → {new[:50]}...")
            else:
                print(f"⚠️  置換対象が見つかりません: {old[:50]}...")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    except Exception as e:
        print(f"❌ 修正中にエラー: {e}")
        # 4. エラー時はロールバック
        Path(backup_path).copy(file_path)
        print("✅ ロールバック完了")
        return False
    
    # 5. 修正後構文チェック
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", file_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ 修正後に構文エラー: {result.stderr}")
        # ロールバック
        Path(backup_path).copy(file_path)
        print("✅ ロールバック完了（構文エラー）")
        return False
    
    print("✅ 安全な修正完了")
    return True

if __name__ == "__main__":
    # 使用例
    modifications = [
        ("old_code", "new_code"),
    ]
    safe_modify_file("target.py", modifications)

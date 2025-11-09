#!/usr/bin/env python3
"""
ナレッジ管理システム実行ラッパー
プロジェクトルートからスクリプトを実行するための統一インターフェース
"""
import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print("使用方法: python run_knowledge_system.py <スクリプト名> [引数...]")
        print("利用可能なスクリプト:")
        scripts_dir = "knowledge_system/scripts"
        for script in os.listdir(scripts_dir):
            if script.endswith(".py") and not script.startswith("_"):
                print(f"  - {script}")
        return
    
    script_name = sys.argv[1]
    script_path = os.path.join("knowledge_system/scripts", script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ スクリプトが見つかりません: {script_path}")
        return
    
    # スクリプトを実行（プロジェクトルートから）
    args = [sys.executable, script_path] + sys.argv[2:]
    print(f"🚀 実行: {' '.join(args)}")
    result = subprocess.run(args, cwd=os.getcwd())
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())

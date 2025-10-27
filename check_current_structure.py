#!/usr/bin/env python3
"""
📁 現在のディレクトリ構造確認 - ファイルを移動せずに確認
"""

import os
import sys

def check_current_structure():
    print("📁 現在のディレクトリ構造確認")
    print("=" * 60)
    
    # 重要なファイルとディレクトリの存在確認
    critical_paths = [
        # メインファイル
        'run_multi_agent.py',
        'pm_agent.py', 
        'pm_system_prompts.py',
        'task_executor.py',
        
        # 重要なディレクトリ
        'core_agents/',
        'browser_control/',
        'wordpress/',
        'task_executor/',
        'configuration/',
        'data_models/',
        'tools/',
        'content_writers/',
        
        # 重要な個別ファイル
        'browser_control/browser_controller.py',
        'core_agents/review_agent.py',
        'core_agents/dev_agent.py',
        'core_agents/design_agent.py',
        'core_agents/content_writer_agent.py',
        'wordpress/wp_agent.py',
        'wordpress/wp_dev/wp_dev_agent.py',
        'wordpress/wp_dev/wp_acf_agent.py',
        'configuration/config_loader.py',
        'configuration/service_account.json',
    ]
    
    print("🔍 重要なファイルとディレクトリの存在確認:")
    print("-" * 50)
    
    existing_paths = []
    missing_paths = []
    
    for path in critical_paths:
        if os.path.exists(path):
            existing_paths.append(path)
            print(f"   ✅ {path}")
        else:
            missing_paths.append(path)
            print(f"   ❌ {path}")
    
    print(f"\n📊 統計:")
    print(f"   • 存在: {len(existing_paths)}個")
    print(f"   • 不在: {len(missing_paths)}個")
    print(f"   • 合計: {len(critical_paths)}個")
    
    # 実際のファイル構造を表示
    print(f"\n📁 実際のファイル構造:")
    print("-" * 50)
    
    directories_to_show = [
        '.', 'core_agents', 'browser_control', 'wordpress', 
        'task_executor', 'configuration'
    ]
    
    for directory in directories_to_show:
        if os.path.exists(directory):
            print(f"\n📂 {directory}/")
            try:
                if os.path.isdir(directory):
                    items = os.listdir(directory)
                    py_files = [f for f in items if f.endswith('.py')]
                    other_files = [f for f in items if not f.endswith('.py')]
                    
                    for py_file in sorted(py_files):
                        print(f"   🐍 {py_file}")
                    for other_file in sorted(other_files):
                        if not other_file.startswith('.'):
                            print(f"   📄 {other_file}")
                else:
                    print(f"   📄 {directory}")
            except Exception as e:
                print(f"   ⚠️ 読み込みエラー: {e}")
    
    return existing_paths, missing_paths

def main():
    existing, missing = check_current_structure()
    
    print(f"\n🎯 現在のシステム状態:")
    if len(missing) == 0:
        print("   ✅ 完全なシステムが存在します")
    elif len(existing) / (len(existing) + len(missing)) > 0.8:
        print("   ⚠️ ほぼ完全なシステムが存在します")
    else:
        print("   ❌ 重要なファイルが不足しています")

if __name__ == "__main__":
    main()
